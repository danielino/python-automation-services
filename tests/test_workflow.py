from tempfile import NamedTemporaryFile

from automation.workflow import Workflow


# test workflow parser with yaml inline
def test_workflow_parser_inline_1():
    with NamedTemporaryFile("w") as f:
        f.write(
            """
workflow:
  agent: root
  parameters:
  jobs:
    - name: hello world
      steps:
        - name: run hello world
          script: echo "hello world"
        - name: run hello world 2
          script: echo "hello world"
        - name: run hello world 3
          script: echo "hello world"
        """
        )
        f.flush()

        w = Workflow.load(f.name)
        assert w is not None
        assert len(w.jobs) == 1
        assert len(w.jobs[0].steps) == 3


def test_workflow_parser_inline_2():
    with NamedTemporaryFile("w") as f:
        f.write(
            """
workflow:
  agent: root
  parameters:
  jobs:
    - name: hello world
      steps:
        - name: run hello world
          script: echo "hello world"
        - name: run hello world 2
          script: echo "hello world"
        - name: run hello world 3
          script: echo "hello world"
        """
        )
        f.flush()

        w = Workflow.load(f.name)
        assert w is not None
        assert len(w.jobs) == 1
        assert len(w.jobs[0].steps) == 3
        assert w.jobs[0].steps[0].name == "run hello world"


def test_workflow_parser_error():
    with NamedTemporaryFile("w") as f:
        f.write("error")
        f.flush()
        try:
            w = Workflow.load(f.name)
        except Exception as e:
            assert str(e) == "workflow error"
        else:
            assert False
