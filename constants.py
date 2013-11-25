# Constants and defines

PY3 = False
from sys import version_info as SYS_V_INFO
if SYS_V_INFO[0] >= 3: PY3 = True
SYS_V_INFO = None

#
#   Token
#
#       ...x .... Data 1 - CMD 0
#
#       Cmd:
#       ...0 x... Set 1 - Get 0
#       ...0 .xxx Opcode
#
#       Data:
#       .... x... Precoded
#       ...1 .xxx Opcode
#

# Command
COMMAND = 0

SET = 8
GET = 0

# Only get
PING = 0
FPS = 1

# Only set
CLEAN = 0
STORE = 1

# Get and set
SPEED = 2
DIMM = 3
HEIGHT = 4
WIDTH = 5
DEPTH = 6
TOTAL_WIDTH = 7

# Data
DATA = 0x10

PRECODED = 8

# Opcodes
WRITE_COLUMN = 0
WRITE_SECTION = 1
BURST = 2
INTERLACED_BURST = 3
