# ../fdn/core/players.py

# Source.Python
from core import PLATFORM
from entities.helpers import index_from_edict
from mathlib import Vector
from memory import DataType, Convention
from players import PlayerGenerator
from players.dictionary import PlayerDictionary
from players.entity import Player


# Offset for CBaseCombatCharacter::IsInFieldOfView(const Vector &pos).
IS_IN_FIELD_OF_VIEW_OFFSET = 273 if PLATFORM == 'windows' else 274


class PlayerFDN(Player):
    """Extended Player class.

    Args:
        index (int): A valid player index.
        caching (bool): Check for a cached instance?
    """

    def __init__(self, index, caching=True):
        """Initializes the object."""
        super().__init__(index, caching)

    @staticmethod
    def initialize_all_players():
        """Creates Player instances for all players on the server."""
        for edict in PlayerGenerator():
            player_instances[index_from_edict(edict)]

    def is_in_fov(self, target):
        """Checks if the given target position is within the player's field of 
        view.

        Args:
            target (Vector): A valid point (x, y, z) within the game world.

        Returns:
            bool: True if the given Vector is within the player's field of
                view, False otherwise.
        """
        IsInFieldOfView = self.make_virtual_function(
            IS_IN_FIELD_OF_VIEW_OFFSET,
            Convention.THISCALL,
            (DataType.POINTER, DataType.POINTER),
            DataType.BOOL
            )

        return IsInFieldOfView(self, target)


# Dictionary used to store Player instances.
player_instances = PlayerDictionary(PlayerFDN)
