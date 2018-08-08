# ../fdn/core/constants.py

# Source.Python
from mathlib import Vector


__all__ = (
    'FL_EDICT_ALWAYS',
    'OFFSET_DUCK',
    'OFFSET_STAND'
    )


# Edict flag used for making sure an entity gets transmitted to all clients
# no matter what. If an entity has this flag, attempting to hide it in the 
# SetTransmit hook will not work.
FL_EDICT_ALWAYS = 1<<3

OFFSET_DUCK = Vector(0, 0, 54)
OFFSET_STAND = Vector(0, 0, 70)
