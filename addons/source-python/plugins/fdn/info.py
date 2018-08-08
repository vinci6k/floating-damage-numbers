# ../fdn/info.py

# Source.Python
from plugins.manager import plugin_manager


__all__ = (
    'info',
)


info = plugin_manager.get_plugin_info(__name__)
