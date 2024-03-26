import logging
import subprocess

from automation.workflow.plugins.plugin import Plugin


class DockerPlugin(Plugin):
    logger = logging.getLogger("DockerPlugin")

    def __init__(self, config):
        self.config = config
        self._validate_config_fields()

    def _get_docker_command(self):
        action = self.config.get("action")
        image = self.config.get("image")
        command = self.config.get("command")
        background = self.config.get("background", False)
        options = ["-d"] if background else []
        return f"docker {action} {' '.join(options)} {image} {command}"

    def _validate_config_fields(self):
        mandatory_fields = ["action", "image", "command"]
        if not all(field in self.config for field in mandatory_fields):
            raise ValueError(
                f"Docker config should contain 'action', 'image' and 'command'"
            )

    def run(self):
        command = self._get_docker_command()
        self.logger.debug(f"running command: {command}")
        yield subprocess.run(
            command,
            shell=True,
            check=False,
            capture_output=True,
        )
