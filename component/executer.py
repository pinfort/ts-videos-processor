import subprocess

def executeCommand(commands: list[str]) -> int:
    result: subprocess.CompletedProcess = subprocess.run(commands)
    return result.returncode
