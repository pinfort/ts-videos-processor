import subprocess
from logging import Logger, getLogger

def executeCommand(commands: list[str], timeout: int =600) -> int:
    logger: Logger = getLogger(__name__)
    logger.info(f"""executing command: {commands}""")
    result: subprocess.CompletedProcess = subprocess.run(commands, capture_output=True, timeout=timeout)
    if result.stdout:
        logger.debug(result.stdout.decode("cp932"))
    if result.stderr:
        logger.warn(result.stderr.decode("cp932"))
    logger.info(f"""command executing finished: {commands}""")
    return result.returncode
