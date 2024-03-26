from automation.workflow import Step, Job, Workflow


def test_step_script():
    step_conf = {"name": "test", "script": "echo 'hello world'"}
    step = Step(**step_conf)
    j = Job(name="test", steps=[step_conf], workflow=Workflow("root", {}, {}))
    step.job = j
    r = next(step.execute())
    assert r
    assert r.output == b"hello world\n"


# test with mocking
def test_step_script_with_fp_mock(fp):
    fp.register("ls", stdout=["test"])
    step_conf = {"name": "test", "script": "ls"}
    step = Step(**step_conf)
    j = Job(name="test", steps=[step_conf], workflow=Workflow("root", {}, {}))
    step.job = j
    r = next(step.execute())
    assert r
    assert r.output == b"test\n"
