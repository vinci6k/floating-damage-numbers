# ../fdn/core/config.py

# Source.Python
from config.manager import ConfigManager

# Floating Damage Numbers
from ..info import info

__all___ = (
    'world_damage',
    )


# Create a config file in the '../cfg/source.python/fdn' folder.
with ConfigManager(f'{info.name}/config.cfg', f'{info.name}_') as config:
    config.header = f'{info.verbose_name} Settings'

    world_damage = config.cvar(
        'world_damage', 0, 
        'Create damage numbers for world damage? (falling, drowning, crushing)'
        )
