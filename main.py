import logging
import os
import subprocess
import sys

from dotenv import load_dotenv

load_dotenv()
DEBUG = "--debug" in sys.argv or os.getenv("DEBUG", "False").lower() == "true"
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="[%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

RCLONE_COMMANDS = []
RCLONE_CONFIG_PATH = os.getenv("RCLONE_CONFIG_PATH", False)

try:
    count = 1
    while count:
        rclone_cmd = os.getenv(f"RCLONE_CMD_{count}")
        if rclone_cmd:
            log.debug(f"Found rclone command{count}: {rclone_cmd}")
            RCLONE_COMMANDS.append(rclone_cmd)
            count += 1
        else:
            count = 0
    log.debug(f"Found {RCLONE_COMMANDS} rclone commands")
except Exception as e:
    log.error(e)
    sys.exit(1)


def rclone(args):
    log.debug(f"Running rclone {' '.join(args)}")
    if RCLONE_CONFIG_PATH:
        args = ["--config", RCLONE_CONFIG_PATH, *args]
    log.debug(f"Running rclone {' '.join(args)}")
    process = subprocess.run(["rclone", *args], capture_output=True, text=True)
    if process.returncode != 0 and DEBUG:
        log.warning(process.stdout)
        log.warning(process.stderr)
    return process.returncode


def main():
    total_cmd = len(RCLONE_COMMANDS)
    success = 0
    for i, cmd in enumerate(RCLONE_COMMANDS):
        log.info(f"Running command [{i+1}/{total_cmd}]")
        cmd_code = rclone(cmd.split(" "))
        if cmd_code != 0:
            log.error(f"Command [{i+1}/{total_cmd}] failed")
        else:
            success += 1
            log.info(f"Command [{i+1}/{total_cmd}] finished successfully")
    log.info(f"Finished [{success}/{total_cmd}] commands successfully")


if __name__ == "__main__":
    if len(RCLONE_COMMANDS) == 0:
        log.error("No rclone commands found")
    else:
        log.info(f"Found {len(RCLONE_COMMANDS)} rclone commands")
        main()
