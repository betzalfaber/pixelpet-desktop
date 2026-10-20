from dataclasses import dataclass, asdict
import json, os
from pathlib import Path

APP_DIR = Path(os.environ.get("PIXELPET_HOME", Path.home() / ".pixelpet"))
STATE_FILE = APP_DIR / "pet_state.json"

def clamp(value):
    return max(0, min(100, int(value)))

@dataclass
class PetState:
    name: str = "Pixel"
    hunger: int = 70
    happiness: int = 75
    energy: int = 80

    def __post_init__(self):
        self.name = (str(self.name).strip() or "Pixel")[:24]
        self.hunger = clamp(self.hunger)
        self.happiness = clamp(self.happiness)
        self.energy = clamp(self.energy)

    @property
    def mood(self):
        if self.energy < 25: return "Sleepy"
        if self.hunger < 25: return "Hungry"
        if self.happiness < 30: return "Okay"
        return "Happy"

    def tick(self):
        """Simulates passive stat decay over time."""
        self.hunger = clamp(self.hunger - 1)
        self.energy = clamp(self.energy - 1)
        # Happiness drops faster if pet is starving or exhausted
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
            hunger=data.get("hunger", 70),
            happiness=data.get("happiness", 75),
            energy=data.get("energy", 80))
    except (OSError, ValueError, TypeError):
        return PetState()