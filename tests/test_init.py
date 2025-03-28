from pytest_console_scripts import ScriptRunner

PACKAGE = 'mosaic'


def test_mosaic(script_runner: ScriptRunner):
    script_runner.run('mosaic --version', shell=True, check=True)
    assert script_runner.run('mosaic', shell=True).returncode != 0
    assert script_runner.run('mosaic free', shell=True).returncode != 0
    assert script_runner.run('mosaic remove', shell=True).returncode != 0
