# ../fdn/core/constants.py


__all__ = (
    'FL_EDICT_ALWAYS',
    )


# Edict flag used for making sure an entity gets transmitted to all clients
# no matter what. If an entity has this flag, attempting to hide it in the 
# SetTransmit hook will not work.
FL_EDICT_ALWAYS = 1<<3


DISTANCE_MULTIPLIER = 0.019
