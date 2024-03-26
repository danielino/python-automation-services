from subprocess import CompletedProcess

from automation.workflow.plugins import ScriptPlugin


def test_script_plugin_init():
    plugin = ScriptPlugin("ls")
    assert plugin.command == "ls"


def test_setup_single_command():
    plugin = ScriptPlugin("ls")
    command_list = plugin._setup()
    assert command_list == ["ls"]


def test_setup_multiple_commands():
    plugin = ScriptPlugin(["ls", "pwd"])
    command_list = plugin._setup()
    assert command_list == ["ls", "pwd"]


def test_run_single_command(fake_process):
    plugin = ScriptPlugin("ls")
    fake_process.register_subprocess(["ls"], stdout="file1\nfile2\n")

    result = list(plugin.run())

    assert isinstance(result[0], CompletedProcess)
    assert result[0].stdout == b"file1\nfile2\n"


def test_run_multiple_commands(fake_process):
    commands = ["ls", "pwd"]
    plugin = ScriptPlugin(commands)
    fake_process.register_subprocess(["ls"], stdout="file1\nfile2\n")
    fake_process.register_subprocess(["pwd"], stdout="/home/user")

    result = list(plugin.run())

    assert len(result) == 2
    assert isinstance(result[0], CompletedProcess)
    assert isinstance(result[1], CompletedProcess)
    assert result[0].stdout == b"file1\nfile2\n"
    assert result[1].stdout == b"/home/user"
