# ../fdn/core/floating_number.py

# Python
import random

# Source.Python
from entities.constants import SolidType, SolidFlags, CollisionGroup
from entities.entity import Entity
from listeners import OnEntityDeleted
from mathlib import Vector, QAngle

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
        number (str): Number that the 'point_worldtext' entity will display.
        color (int): Color (long value) of the number. 
        angle (QAngle): Angle of the FloatingNumber.
        size (int): Size of the number.
        recipient (int): Userid of the player that's supposed to see
            the FloatingNumber.
        **kwargs (dict): Additional keyword arguments.

    Attributes:
        world_text (Entity): Instance of the 'point_worldtext' entity.
        decoy (Entity): Instance of the 'decoy_projectile' entity.
    """

    def __init__(self, origin, number, color, angle, size, recipient, **kwargs):
        """Initializes the object."""
        self.recipient = recipient
        self.world_text = None
        self.decoy = None

        self.create(
            origin, number, color, angle, int(size),
            kwargs.get('without_decoy', False)
            )

    @classmethod
    def world_damage(cls, origin, number, color, unique_data):
        """Creates a single 'decoy_projectile' and attaches one or more
        'point_worldtext' entities to it, all with different recipients."""

        # Create the first FloatingNumber and store the decoy instance.
        decoy = cls(origin, number, color, **unique_data.pop()).decoy

        # Go through all the given data.
        for data in unique_data:
            # Create a FloatingNumber without a 'decoy_projectile'.
            num = FloatingNumber(origin, number, color, **data, no_decoy=True)
            # Parent it to the decoy of the first FloatingNumber.
            num.world_text.set_parent(decoy, -1)
            # Apply the correct offset and rotation.
            num.world_text.teleport(
                origin=calculate_offset(number, data['size'], data['angle']), 
                angle=data['angle'], 
                velocity=None
                )

            num.state_flags = num.state_flags ^ FL_EDICT_ALWAYS

    def create(self, origin, number, color, angle, size, without_decoy=False):
        """Creates and combines a 'decoy_projectile' and a 'point_worldtext' to
        represent the FloatingNumber entity.

        The 'decoy_projectile' is used to add movement / animation to the 
        'point_worldtext'.
        """
        # Create and setup the 'point_worldtext'.
        self.world_text = Entity.create('point_worldtext')
        self.world_text.text = number
        self.world_text.text_size = size
        self.world_text.text_color = color

        # Add the FloatingNumber instance to the dictionary.
        number_instances[self.world_text.index] = self

        # Don't go further if we don't need a 'decoy_projectile'.
        if without_decoy:
            return

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
        # Parent the 'point_worldtext' to the 'decoy_projectile'.
        self.world_text.set_parent(self.decoy, -1)
        self.world_text.teleport(calculate_offset(number, size), None, None)
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


def calculate_offset(number, size, angle=None):
    """Calculates the offset for the centering the 'point_worldtext' entity on 
    the 'decoy_projectile'.
    
    Args:
        number (str): Number that the 'point_worldtext' entity will display.
        size (int): Size of the number.
        angle (QAngle): Angle of the number.
        
    Returns:
        Vector: Offset for centering the 'point_worldtext' entity on a
            'decoy_projectile' based on the given arguments.
    """
    offset_x = 0
    offset_y = 0.3 * size * (len(number) + 0.733)
    offset_z = size * -0.58

    if angle is not None:
        # Get the forward direction of the given 'angle'.
        forward = Vector()
        QAngle.get_angle_vectors(angle, forward, None, None)

        # Adjust the offsets.
        offset_x = offset_y * -forward[1]
        offset_y *= forward[0]

    return Vector(offset_x, offset_y, offset_z)


