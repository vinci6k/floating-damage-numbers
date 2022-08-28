# ../fdn/fdn.py

# Source.Python
from engines.trace import ContentMasks, GameTrace, Ray, engine_trace
from entities import CheckTransmitInfo, TakeDamageInfo
from entities.constants import WORLD_ENTITY_INDEX, DamageTypes
from entities.entity import Entity
from entities.helpers import index_from_pointer
from entities.hooks import EntityCondition, EntityPreHook
from events import Event
from listeners import OnLevelEnd
from mathlib import Vector
from players.helpers import userid_from_edict

# Floating Damage Numbers
from .core.colors import WHITE, RED, YELLOW
from .core.config import world_damage, wall_bangs
from .core.constants import FL_EDICT_ALWAYS, DISTANCE_MULTIPLIER
from .core.floating_number import FloatingNumber, number_instances
from .core.players import PlayerFDN, player_instances


is_point_worldtext = EntityCondition.equals_entity_classname(
    'point_worldtext')


def load():
    """Called when the plugin gets loaded."""
    PlayerFDN.initialize_all_players()


@EntityPreHook(is_point_worldtext, 'set_transmit')
def pre_set_transmit(stack_data):
    """Hides 'point_worldtext' entities that are part of FloatingNumbers for
    everyone except the specified recipient.
    """
    index = index_from_pointer(stack_data[0])

    try:
        # Does this index belong to a FloatingNumber instance?
        floating_number = number_instances[index]
    except KeyError:
        # Nope, don't go further.
        return None

    info = CheckTransmitInfo._obj(stack_data[1])
    # Strip the FL_EDICT_ALWAYS flag from the 'point_worldtext'.
    floating_number.state_flags = floating_number.state_flags ^ FL_EDICT_ALWAYS

    # Is this the recipient of the FloatingNumber entity?
    if floating_number.recipient == userid_from_edict(info.client):
        # Show the entity.
        return None
    else:
        # If not, hide the entity.
        return False


@Event('player_activate')
def player_activate(event):
    """Makes sure the newly connected player gets a Player instance."""
    player_instances.from_userid(event['userid'])


@EntityPreHook(EntityCondition.is_player, 'on_take_damage_alive')
def on_take_damage_alive_pre(stack_data):
    """Creates a FloatingNumber when a player takes damage."""
    # Get the Player instance of the victim.
    player_v = player_instances[index_from_pointer(stack_data[0])]
    # Get the CTakeDamageInfo instance.
    info = TakeDamageInfo._obj(stack_data[1])
    # Get the index of the entity that caused the damage.
    index_a = info.attacker

    # Did the player take damage from the world?
    if index_a == 0:
        # Are damage numbers disabled for world damage (world_damage set to 0)?
        if not world_damage.get_int():
            return

        number_origin = player_v.get_number_origin()
        unique_data = []

        for player in player_instances.values():
            # There's no need for bots to see the FloatingNumber.
            if player.is_bot():
                continue

            # Is the player not looking at the position where the
            # FloatingNumber is going to spawn?
            if not player.is_in_fov(target=number_origin):
                continue

            distance = number_origin.get_distance(player.origin)
            # Add this player's unique data to the list.
            unique_data.append({
                'angle': player.view_angle,
                'size': 10 + distance * DISTANCE_MULTIPLIER,
                'recipient': player.userid
                })

        # Will no one be able to see this FloatingNumber?
        if not unique_data:
            # Don't bother spawning it.
            return

        FloatingNumber.world_damage(
            origin=number_origin,
            # Since `info.damage` is a float, convert it to an integer before
            # converting it to a string to get rid of the decimal part.
            number=str(int(info.damage)),
            color=WHITE,
            unique_data=unique_data
            )

    # Or from a player?
    else:
        try:
            # Try to get the Player instance of the attacker.
            player_a = player_instances[index_a]
        except KeyError:
            # Damage was caused indirectly (grenade, projectile).
            try:
                # Try to get a Player instance again, but this time using the
                # the owner inthandle of the entity that caused the damage.
                player_a = player_instances.from_inthandle(
                    Entity(info.inflictor).owner_handle)
            except KeyError:
                # KeyError: not a player or invalid owner inthandle (-1).
                return

        # Is the attacker a bot?
        if player_a.is_bot():
            return

        # Self inflicted damage?
        if player_v is player_a:
            return

        number_origin = player_v.get_number_origin()
        velocity = None

        # Did the bullet go through another entity before hitting the player?
        if info.penetrated and wall_bangs.get_int():
            # Let's check if that entity is the world.
            trace = GameTrace()
            engine_trace.clip_ray_to_entity(
                # Create a Ray() from the attacker's eyes to the hit position.
                Ray(player_a.eye_location, info.position),
                ContentMasks.ALL,
                Entity(WORLD_ENTITY_INDEX),
                trace
            )

            # Is this an actual wall-bang (bullet went through world)?
            if trace.did_hit():
                # Calculate the directional vector from the wall to the player.
                from_wall = trace.start_position - trace.end_position
                # Calculate the offset for the FloatingNumber's new origin.
                origin_offset = 10 + from_wall.length * 0.01
                # Normalize it.
                # Vector(368.52, 40.71, -7.77) -> Vector(0.99, 0.10, -0.02)
                from_wall.normalize()
                # Change the origin of the FloatingNumber so it spawns in front
                # of the wall where the wall-bang took place.
                number_origin = trace.end_position + origin_offset * from_wall

                right, up = Vector(), Vector()
                from_wall.get_vector_vectors(right, up)

                velocity = from_wall * 25 + (
                    right * 35 * player_a.next_direction)
                # If the bullet went through something else (another player)
                # before hitting the wall, adjust how high the FloatingNumber
                # gets pushed.
                velocity.z = 75 * info.penetrated

        distance = number_origin.get_distance(player_a.origin)
        # TODO: Figure out a better way to allow other plugins to change the
        # color of the FloatingNumber. Or hardcode the colors to unused
        # DamageTypes (e.g. AIRBOAT = YELLOW, PHYSGUN = BLUE)?
        color = YELLOW if info.type == DamageTypes.AIRBOAT else WHITE

        FloatingNumber(
            origin=number_origin,
            number=str(int(info.damage)),
            # Change the color if it's a headshot.
            color=RED if player_v.last_hitgroup == 1 else color,
            angle=player_a.view_angle,
            # Increase the size depending on the distance.
            size=10 + distance * DISTANCE_MULTIPLIER,
            recipient=player_a.userid,
            velocity=velocity
        )


@OnLevelEnd
def changing_map():
    """Clean up plugin data after a map change."""
    number_instances.clear()
