import logging
import os
import subprocess
import typing
from abc import abstractmethod

import yaml
from easydict import EasyDict

from automation.config import ConfigManager
from automation.workflow import Workflow

logging.basicConfig(level=logging.DEBUG)


def main():
    c = ConfigManager()
    w = Workflow.load("./tests/pipelines/basic.yml")
    for task in w.execute():
        count = 0
        for job in task["result"]:
            logging.info(f"executed step {task['job']}::{task['step']}")
            print(job.__dict__)
            count += 1


if __name__ == "__main__":
    main()
