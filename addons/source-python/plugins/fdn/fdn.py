# ../fdn/fdn.py

# Source.Python
import memory
from entities import CheckTransmitInfo
from entities.helpers import index_from_pointer
from entities.hooks import EntityCondition, EntityPreHook
from events import Event
from listeners import OnLevelEnd
from players.helpers import userid_from_edict

# Floating Damage Numbers
from .core.colors import WHITE, RED
from .core.config import world_damage
from .core.constants import FL_EDICT_ALWAYS, OFFSET_STAND, OFFSET_DUCK
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
    """Creates a FloatingNumber when a player takes damage."""
    userid_a = event['attacker']
    userid_v = event['userid']
    
    # Self inflicted damage or world damage (world_damage set to 0)?
    if userid_a == userid_v or (userid_a == 0 and not world_damage.get_int()):
        return

    player_v = player_instances.from_userid(userid_v)

    # Get the player height.
    offset = OFFSET_DUCK if player_v.is_ducked else OFFSET_STAND
    number_origin = player_v.origin + offset
    damage = str(event['dmg_health'])

    # Was the damage caused by the world? (falling, drowning, crushing)
    if userid_a == 0:
        unique_data = []

        for player in player_instances.values():
            # There's no need for bots to see the FloatingNumber.
            if 'BOT' in player.steamid or player.is_fake_client():
               continue

            # Is the player not looking at the position where the
            # FloatingNumber is going to spawn?
            if not player.is_in_fov(target=number_origin):
                continue

            distance = number_origin.get_distance(player.origin)
            # Add this player's unique data to the list.
            unique_data.append({
                'angle': player.view_angle, 
                'size': 10 + (4 * (distance / 200)),
                'recipient': player.userid
                })

        # Will no one be able to see this FloatingNumber?
        if not unique_data:
            # Don't bother spawning it.
            return

        FloatingNumber.world_damage(
            origin=number_origin,
            number=damage,
            color=WHITE,
            unique_data=unique_data
            )
    
    # Or was it caused by another player?
    else:
        player_a = player_instances.from_userid(userid_a)
        # Is the attacker a bot?
        if 'BOT' in player_a.steamid or player_a.is_fake_client():
            return

        distance = number_origin.get_distance(player_a.origin)
        FloatingNumber(
            origin=number_origin,
            number=damage,
            # Change the color if it's a headshot.
            color=RED if event['hitgroup'] == 1 else WHITE,
            angle=player_a.view_angle,
            # Increase the size depending on the distance.
            size=10 + (4 * (distance / 200)),
            recipient=player_a.userid
        )


@OnLevelEnd
def changing_map():
    """Clean up plugin data after a map change."""
    number_instances.clear()
