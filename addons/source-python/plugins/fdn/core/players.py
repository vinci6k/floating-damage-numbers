# ../fdn/core/players.py

# Source.Python
from core import PLATFORM
from entities.helpers import index_from_edict
from memory import DataType, Convention
from players import PlayerGenerator
from players.dictionary import PlayerDictionary
from players.entity import Player


# Offset for CBaseCombatCharacter::IsInFieldOfView(const Vector &pos).
# More information about the function: https://git.io/JfUSM
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

        self.last_direction = 1

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

    @property
    def next_direction(self):
        self.last_direction = -self.last_direction
        return self.last_direction

    def get_number_origin(self):
        """Returns the spawn position for the FloatingNumber based on the
        player's current height."""
        number_origin = self.origin
        # Adjust the origin according to player height.
        number_origin.z += self.maxs.z + (5 * self.model_scale)
        return number_origin


# Dictionary used to store Player instances.
player_instances = PlayerDictionary(PlayerFDN)
