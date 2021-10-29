import subprocess
from logging import Logger, getLogger

def executeCommand(commands: list[str]) -> int:
    logger: Logger = getLogger(__name__)
    logger.debug(f"""executing command: {commands}""")
    result: subprocess.CompletedProcess = subprocess.run(commands, capture_output=True)
    if result.stdout:
        logger.info("\n" + result.stdout.decode("cp932"))
    if result.stderr:
        logger.warn("\n" + result.stderr.decode("cp932"))
    logger.debug(f"""command executing finished: {commands}""")
    return result.returncode
