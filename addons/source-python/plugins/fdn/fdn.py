# ../fdn/fdn.py

# Source.Python
import memory
from events import Event
from entities import CheckTransmitInfo
from entities.hooks import EntityCondition, EntityPreHook
from entities.helpers import index_from_pointer
from players.helpers import userid_from_edict
from listeners import OnLevelEnd

# Floating Damage Numbers
from .core.colors import WHITE, RED
from .core.players import player_instances
from .core.constants import FL_EDICT_ALWAYS, OFFSET_STAND, OFFSET_DUCK
from .core.floating_number import FloatingNumber, number_instances


is_point_worldtext = EntityCondition.equals_entity_classname(
    'point_worldtext')


@EntityPreHook(is_point_worldtext, 'set_transmit')
def pre_set_transmit(stack_data):
    """Hide 'point_worldtext' entities that are part of FloatingNumbers for
    everyone except the specified recipient.
    """
    index = index_from_pointer(stack_data[0])

    # Is this not a FloatingNumber entity?
    if index not in number_instances:
        return None

    floating_number = number_instances[index]
    info = memory.make_object(CheckTransmitInfo, stack_data[1])
    # Strip the FL_EDICT_ALWAYS flag from the 'point_worldtext'.
    floating_number.state_flags = floating_number.state_flags ^ FL_EDICT_ALWAYS

    # Is this the recipient of the FloatingNumber entity?
    if floating_number.recipient == userid_from_edict(info.client):
        # Show the entity.
        return None
    else:
        # If not, hide the entity.
        return False


@Event('player_hurt')
def player_hurt(event):
    """Create a FloatingNumber only when a player takes damage from another 
    player.
    """
    userid_a = event['attacker']
    userid_v = event['userid']
    
    # Self inflicted or world (falling, drowning) damage?
    if userid_a in (userid_v, 0):
        return

    player_a = player_instances.from_userid(userid_a)
    # Is the attacker a bot?
    if 'BOT' in player_a.steamid or player_a.is_fake_client():
        return

    player_v = player_instances.from_userid(userid_v)

    # Get the distance between the two players.
    distance = player_v.origin.get_distance(player_a.origin)
    # Get the player height.
    offset = OFFSET_DUCK if player_v.is_ducked else OFFSET_STAND
    
    FloatingNumber(
        origin=player_v.origin + offset,
        angle=player_a.view_angle,
        number=event['dmg_health'],
        # Change the color if it's a headshot.
        color=RED if event['hitgroup'] == 1 else WHITE,
        # Increase the size depending on the distance.
        size=10 + (4 * (distance / 200)),
        recipient=userid_a
        )


@OnLevelEnd
def changing_map():
    """Clean up plugin data after a map change."""
    number_instances.clear()
