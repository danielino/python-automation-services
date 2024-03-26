import subprocess

from .plugin import Plugin


class GitPlugin(Plugin):
    def __init__(self, config):
        self.config = config

    def run(self):
        for item in ["action", "url", "branch", "path"]:
            if item not in self.config:
                raise ValueError(f"missing {item} in git_clone config")
        yield subprocess.run(
            f"git clone {self.config['url']}",
            shell=True,
            check=False,
            capture_output=True,
        )
