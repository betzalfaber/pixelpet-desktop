from dataclasses import dataclass, asdict
import json, os
from pathlib import Path

APP_DIR = Path(os.environ.get("PIXELPET_HOME", Path.home() / ".pixelpet"))
STATE_FILE = APP_DIR / "pet_state.json"

SKINS = ["Cat", "Dino", "Ghost", "Slime"]

def clamp(value, low=0, high=100):
    return max(low, min(high, int(value)))

@dataclass
class PetState:
    name: str = "Pixel"
    hunger: int = 75
    happiness: int = 80
    energy: int = 85
    xp: int = 0
    level: int = 1
    coins: int = 25
    skin: str = "Cat"

    def __post_init__(self):
        self.name = (str(self.name).strip() or "Pixel")[:24]
        self.hunger = clamp(self.hunger)
        self.happiness = clamp(self.happiness)
        self.energy = clamp(self.energy)
        self.xp = max(0, int(self.xp))
        self.level = max(1, int(self.level))
        self.coins = max(0, int(self.coins))
        if self.skin not in SKINS:
            self.skin = "Cat"

    @property
    def xp_needed(self):
        return self.level * 50

    @property
    def mood(self):
        if self.energy < 25: return "Sleepy"
        if self.hunger < 25: return "Hungry"
        if self.happiness < 30: return "Sad"
        if self.happiness > 85 and self.hunger > 70: return "Ecstatic"
        return "Happy"

    def gain_rewards(self, xp_amount, coin_amount=0):
        self.xp += xp_amount
        self.coins += coin_amount
        leveled_up = False
        while self.xp >= self.xp_needed:
            self.xp -= self.xp_needed
            self.level += 1
            self.coins += 15
            leveled_up = True
        return leveled_up

    def tick(self):
        self.hunger = clamp(self.hunger - 1)
        self.energy = clamp(self.energy - 1)
        penalty = 2 if (self.hunger < 25 or self.energy < 25) else 1
        self.happiness = clamp(self.happiness - penalty)

def save_state(state, path=None):
    target = Path(path) if path is not None else STATE_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")

def load_state(path=None):
    target = Path(path) if path is not None else STATE_FILE
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(data, dict): return PetState()
        return PetState(
            name=data.get("name", "Pixel"),
            hunger=data.get("hunger", 75),
            happiness=data.get("happiness", 80),
            energy=data.get("energy", 85),
            xp=data.get("xp", 0),
            level=data.get("level", 1),
            coins=data.get("coins", 25),
            skin=data.get("skin", "Cat"),
        )
    except (OSError, ValueError, TypeError):
        return PetState()