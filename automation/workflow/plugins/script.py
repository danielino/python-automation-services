import logging
import subprocess

from .plugin import Plugin


class ScriptPlugin(Plugin):
    logger = logging.getLogger("ScriptPlugin")

    def __init__(self, command):
        self.logger.debug("initializing script plugin")
        self.command = command

    def _run_script(self, script):
        self.logger.debug(f"Running command: {script}")
        try:
            yield subprocess.run(script, shell=True, check=False, capture_output=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error running script: {e}")
            return e

    def _setup(self):
        command_list = self.command
        if type(self.command) == str:
            command_list = [self.command]
        return command_list

    def run(self):
        command_list = self._setup()
        for script in command_list:
            yield from self._run_script(script)
