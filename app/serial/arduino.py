import logging
import serial

logger = logging.getLogger(__name__)

# Maps logical command → what the Arduino actually expects given its wiring
_REMAP = {"F": "L", "B": "R", "L": "F", "R": "B", "S": "S"}

VALID_COMMANDS = set(_REMAP)

_port: serial.Serial | None = None


def init_serial(device: str, baud: int = 9600) -> None:
    global _port
    _port = serial.Serial(device, baud, timeout=1)
    logger.info("Serial opened: %s @ %d baud", device, baud)


def send_command(cmd: str) -> bool:
    if cmd not in VALID_COMMANDS:
        logger.warning("Ignored unknown command: %s", cmd)
        return False
    if _port is None or not _port.is_open:
        logger.error("Serial port not open")
        return False
    _port.write((_REMAP[cmd] + "\n").encode())
    logger.info("Serial >> %s", cmd)
    return True
