"""
Item class for KEPLER ISOLATION game
"""


class Item:
    def __init__(
        self,
        name: str,
        aliases: str,
        description: str,
        portable: bool = True,
        wearable: bool = False,
        worn: bool = False,
        readable_text: str | None = None,
        use_effect: str | None = None,
        install_target: str | None = None,
        sound_on_use: int = 0,
        required_for_win: bool = False,
    ):
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
        # Non-None only for synthetic NPCs: {"profile": str, "name": str, "lines": list[str]}
        self.synthetic_data: dict | None = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Item({self.name})"

    @staticmethod
    def _norm(s: str) -> str:
        return "".join(c for c in s.lower() if c.isalnum() or c == " ").strip()

    def matches_name(self, name: str) -> bool:
        n = self._norm(name)
        if n == self._norm(self.name):
            return True
        for alias in self.aliases:
            if n == self._norm(alias):
                return True
        return False
