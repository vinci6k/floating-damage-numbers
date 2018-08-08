# ../fdn/core/floating_number.py

# Python
import random

# Source.Python
from mathlib import Vector
from entities.entity import Entity
from entities.constants import SolidType, SolidFlags, CollisionGroup
from listeners import OnEntityDeleted

# Floating Damage Numbers
from .colors import INVISIBLE
from .constants import FL_EDICT_ALWAYS


random_velocity = [-40, -20, 20, 40]
# Dictionary used to store FloatingNumber instances.
number_instances = {}


class FloatingNumber:
    """Class used to create a 'point_worldtext' entity with movement.
    
    Args:
        origin (Vector): Position of the FloatingNumber.
        angle (QAngle): Angle of the FloatingNumber.
        number (str): Number that the 'point_worldtext' entity will display.
        size (int): Size of the number.
        color (int): Color (long value) of the number. 
        recipient (int): Userid of the player that's supposed to see
            the FloatingNumber.

    Attributes:
        world_text (Entity): Instance of the 'point_worldtext' entity.
        decoy (Entity): Instance of the 'decoy_projectile' entity.
    """

    def __init__(self, origin, angle, number, size, color, recipient):
        """Initialize the object."""
        self.recipient = recipient
        self.world_text = None
        self.decoy = None

        self.create(origin, angle, str(number), int(size), color)

    def create(self, origin, angle, number, size, color):
        """Create and combine a 'decoy_projectile' and a 'point_worldtext' to
        represent the FloatingNumber entity.

        The 'decoy_projectile' is used to add movement / animation to the 
        'point_worldtext'.
        """
        # Create and setup the 'decoy_projectile'.
        self.decoy = Entity.create('decoy_projectile')
        self.decoy.spawn()
        self.decoy.gravity = 0.23
        self.decoy.color = INVISIBLE
        # Remove the 'decoy_projectile' bounce sound.
        self.decoy.set_property_uchar('movecollide', 0)
        # Make the decoy not solid.
        self.decoy.solid_type = SolidType.NONE
        self.decoy.solid_flags = SolidFlags.NOT_SOLID
        self.decoy.collision_group = CollisionGroup.NONE

        # Create and setup the 'point_worldtext'.
        self.world_text = Entity.create('point_worldtext')
        self.world_text.text = number
        self.world_text.text_size = size
        self.world_text.text_color = color

        # Calculate the offset for centering the 'point_worldtext' on the
        # 'decoy_projectile'.
        offset_y = 0.3 * size * (len(number) + 0.733)
        offset_z = size * 0.58

        # Parent the 'point_worldtext' to the 'decoy_projectile' and apply
        # the above calculated offset.
        self.world_text.set_parent(self.decoy, -1)
        self.world_text.teleport(Vector(0, offset_y, -offset_z), None, None)
        # Strip the FL_EDICT_ALWAYS flag from the 'point_worldtext' after
        # setting the parent, otherwise hiding the entity in the SetTransmit
        # hook won't work.
        self.state_flags = self.state_flags ^ FL_EDICT_ALWAYS

        self.decoy.teleport(
            origin, 
            angle, 
            Vector(
                random.choice(random_velocity), 
                random.choice(random_velocity), 
                65
                )
            )
        # Remove the 'decoy_projectile' after a short delay.
        # Since the 'point_worldtext' is parented to the 'decoy_projectile', it
        # will also get removed.
        self.decoy.delay(0.5, self.decoy.remove)

        # Add the FloatingNumber instance to the dictionary.
        number_instances[self.world_text.index] = self

    def get_state_flags(self):
        """Shortcut for getting the edict flags of the 'point_worldtext'."""
        return self.world_text.edict.state_flags

    def set_state_flags(self, flag):
        """Shortcut for setting the edict flags of the 'point_worldtext'."""
        self.world_text.edict.state_flags = flag

    state_flags = property(get_state_flags, set_state_flags)


@OnEntityDeleted
def on_entity_deleted(base_entity):
    try:
        index = base_entity.index
    except ValueError:
        return

    # Is this index tied to a FloatingNumber instance?
    if index in number_instances:
        del number_instances[index]
