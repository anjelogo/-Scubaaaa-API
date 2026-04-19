import logging
import serial

logger = logging.getLogger(__name__)

# Maps logical command → what the Arduino actually expects given its wiring
# Maps logical command → what the Arduino actually expects given its wiring
_REMAP = {"F": "L", "B": "R", "L": "F", "R": "B", "S": "S", "X": "X", "Z": "Z", "C": "C"}

VALID_COMMANDS = set(_REMAP)
SPEED_COMMANDS = {"F", "B", "L", "R"}
DEFAULT_SPEED = 200

_port: serial.Serial | None = None


def init_serial(device: str, baud: int = 9600) -> None:
    global _port
    _port = serial.Serial(device, baud, timeout=1)
    logger.info("Serial opened: %s @ %d baud", device, baud)


def send_command(cmd: str, speed: int | None = None) -> bool:
    if cmd not in VALID_COMMANDS:
        logger.warning("Ignored unknown command: %s", cmd)
        return False
    if _port is None or not _port.is_open:
        logger.error("Serial port not open")
        return False

    wire_cmd = _REMAP[cmd]
    if cmd in SPEED_COMMANDS:
        s = speed if speed is not None else DEFAULT_SPEED
        payload = f"{wire_cmd}{s}\n"
    else:
        payload = f"{wire_cmd}\n"

    _port.write(payload.encode())
    logger.info("Serial >> %s", payload.strip())
    return True
