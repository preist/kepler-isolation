"""
Item class for THE THIN AIR game
"""

class Item:
    def __init__(self, name: str, aliases: str, description: str, portable: bool = True, wearable: bool = False, worn: bool = False, readable_text: str = None, use_effect: str = None, install_target: str = None, sound_on_use: int = 0, required_for_win: bool = False):
        self.name = name
        self.aliases = aliases.split(",") if isinstance(aliases, str) else aliases
        self.description = description
        self.portable = portable
        self.wearable = wearable
        self.worn = worn
        self.readable_text = readable_text
        self.use_effect = use_effect
        self.install_target = install_target  # What this item can be installed on
        self.sound_on_use = sound_on_use  # Sound level when used (0-4)
        self.required_for_win = required_for_win
        
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return f"Item({self.name})"
        
    def matches_name(self, name: str) -> bool:
        if name.lower() == self.name.lower():
            return True
        for alias in self.aliases:
            if name.lower() == alias.lower():
                return True
        return False