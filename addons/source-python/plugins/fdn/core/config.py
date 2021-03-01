# ../fdn/core/config.py

# Source.Python
from config.manager import ConfigManager

# Floating Damage Numbers
from ..info import info


__all__ = (
    'world_damage',
    'wall_bangs'
    )


# Create a config file in the '../cfg/source-python/fdn' folder.
with ConfigManager(f'{info.name}/config.cfg', f'{info.name}_') as config:
    config.header = f'{info.verbose_name} Settings'

    world_damage = config.cvar(
        'world_damage', 0, 
        'Create damage numbers for world damage? (falling, drowning, crushing)'
        )

    wall_bangs = config.cvar(
        'wall_bangs', 0,
        'Make damage numbers for damage dealt through walls more visible?'
    )
