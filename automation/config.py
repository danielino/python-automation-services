import json
import logging
import os
import pathlib
from typing import Union

import jsonschema
import yaml
from easydict import EasyDict
from easydict import EasyDict as edict

logger = logging.getLogger("ConfigManager")

cwd = os.getcwd()


def get_search_path(search_paths, glob_expression):
    paths = []
    for path in search_paths:
        paths.extend(
            list(pathlib.Path(path).expanduser().glob(glob_expression))
        )  # noqa: E501
    return list(filter(lambda x: x.stat().st_size > 0, paths))


CONFIG_SEARCH_PATH = os.environ.get(
    "CONFIG_PATH",
    get_search_path([cwd, f"{cwd}/config", "~", "/etc/automation"], "automation.y*ml"),
)


class NoConfigurationAvailable(Exception):
    pass


class ValidationError(Exception):
    pass


class ConfigManager:
    def __init__(
        self,
        path: str = None,
        validate: bool = False,
        schema: Union[str, pathlib.Path] = None,
        search_paths: list = CONFIG_SEARCH_PATH,
    ):
        self.validate = validate
        self.schema = schema
        self.search_paths = search_paths
        if path:
            self.search_paths = [path]
        self.config = self.search_configs()

    def _validate(self, item: pathlib.PosixPath) -> bool:
        # validate schema
        if not self.schema:
            return True
        schema = json.loads(pathlib.Path(self.schema).read_text())
        if item.name.endswith(".json"):
            instance = json.loads(pathlib.Path(item).read_text())
        elif item.name.endswith(".yaml") or item.name.endswith(".yml"):
            instance = yaml.safe_load(pathlib.Path(item).read_text())
        else:
            raise Exception(f"format not supported for file {item}")
        jsonschema.validate(instance=instance, schema=schema)

    def search_configs(self) -> EasyDict:
        for item in self.search_paths:
            logger.debug("searching for configuration file at %s" % item)
            if os.path.isfile(item):
                logger.debug("found configuration file at %s" % item)
                if self.validate:
                    try:
                        logger.debug(f"validating configuration file {item}")
                        self._validate(pathlib.Path(item))
                    except Exception:
                        logger.exception("configuration file is not valid")
                        raise
                return ConfigManager.load(item)
        logger.error("configuration file not found")
        raise NoConfigurationAvailable("configuration file not found")

    @staticmethod
    def load(file_name, method="yaml"):
        """
        load file content as python dict
        :param file_name:
        :param method: yaml|json
        :return:
        """
        mapper = {"yaml": yaml.safe_load, "json": json.load}
        if method not in mapper.keys():
            raise NotImplementedError()

        with open(file_name) as fp:
            return edict(mapper[method](fp))
