import logging
import typing
from enum import IntEnum

import yaml
from easydict import EasyDict


class WorkflowManager:
    pass


# @TODO: implement execution status
class StepExecutionResult:
    def __init__(
        self,
        name: str,
        output: typing.Any,
        error=typing.Union[typing.Any, None],
        status=None,
        exit_code=None,
        operation=None,
    ):
        self.name = name
        self.output = output
        self.error = error
        self.status = status
        self.exit_code = exit_code
        self.operation = operation


class Step:
    """
    a step is a list of actions to be executed in order
    """

    def __init__(self, name: str, job: typing.Union[typing.Any, None] = None, **kwargs):
        self.name = name
        self.job = job
        self.plugin_name: str = list(kwargs.keys())[0]
        for item in kwargs:
            setattr(self, item, kwargs[item])

        if "register" in kwargs:
            self.job.workflow.add_registers(kwargs["register"], None)

    def execute(self):
        """
        this method search in current global scope for a class that match plugin name (ScriptPlugin, DockerPlugin, etc)
        then instantiate it and run it
        each step is executed and a StepExecutionStatus is yielded

        :yield: StepExecutionStatus
        """
        _status = StepExecutionResult(self.name, None)
        try:
            cl = globals()[f"{self.plugin_name.capitalize()}Plugin"]
            result = cl(getattr(self, self.plugin_name)).run()
            if "register" in self.__dict__:
                self.job.workflow.add_registers(self.register, [])
            for item in result:
                _status = StepExecutionResult(
                    self.name, item.stdout, None, None, item.returncode
                )
                yield _status
        except KeyError:
            _status.error = f"plugin {self.plugin_name} not found."
            _status.exit_code = 1
            yield _status
            # raise NotImplementedError(f"plugin {self.plugin_name} not found.")
        except Exception as e:
            _status.error = f"plugin {self.plugin_name} failed."
            _status.status = str(e)
            _status.exit_code = 2
            yield _status
            # raise CalledProcessError(f"plugin {self.plugin_name} failed.")
        if "register" in self.__dict__:
            self.job.workflow._registers[self.register].append(_status.stdout)
        # @TODO: implement execution status


class Job:
    """
    a job is a list of steps
    """

    def __init__(self, name, steps, workflow):
        self.name = name
        self.workflow = workflow
        self.steps = [Step(**step, job=self) for step in steps]


class WorkflowStatus(IntEnum):
    NOT_STARTED = 0x01
    STARTED = 0x02
    EXIT_SUCCESS = 0x03
    EXIT_FAILURE = 0x04


class Workflow:
    """
    a workflow is a list of jobs
    it can be executed by a remote runner
    """

    def __init__(self, agent, parameters, jobs):
        self.agent = agent
        self._parameters = parameters
        self._registers = {}
        self.steps = []
        self.jobs = [Job(**job, workflow=self) for job in jobs]
        self.status = WorkflowStatus.NOT_STARTED

    @property
    def registers(self):
        return self._registers

    # add registers
    def add_registers(self, key, value):
        self._registers[key] = value

    # @TODO: share registers between steps
    # @TODO: manage agents job sharing
    def execute(self):
        """
        yield each step of each job. each action is executed in order
        clients of this api must iterate over the generator to execute the workflow
        this is necessary in order to allow workflow's execution to be paused and resumed and shared between agents
        :return:
        """
        self.status = WorkflowStatus.STARTED
        for job in self.jobs:
            logging.info(f"executing job {job.name}")
            for step in job.steps:
                logging.info(f"executing step {step.name}")
                yield {"job": job.name, "step": step.name, "result": step.execute()}
        self.status = WorkflowStatus.EXIT_SUCCESS

    @staticmethod
    def load(path: str):
        try:
            with open(path) as f:
                workflow = EasyDict(yaml.safe_load(f)).workflow
                return Workflow(workflow.agent, workflow.parameters, workflow.jobs)
        except FileNotFoundError:
            raise FileNotFoundError(f"file {path} not found")
        except Exception:
            raise Exception("workflow error")
