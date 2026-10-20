import tempfile
import unittest
from pathlib import Path
from pet_logic import PetState, clamp, load_state, save_state

class PetLogicTests(unittest.TestCase):
    def test_stats_are_clamped(self):
        pet = PetState(hunger=120, happiness=-5, energy=55)
        self.assertEqual((pet.hunger, pet.happiness, pet.energy), (100, 0, 55))
        self.assertEqual(clamp(-3), 0)
        self.assertEqual(clamp(140), 100)

    def test_mood_priority(self):
        self.assertEqual(PetState(energy=10, hunger=5).mood, "Sleepy")
        self.assertEqual(PetState(energy=80, hunger=10).mood, "Hungry")
        self.assertEqual(PetState(happiness=20).mood, "Okay")
        self.assertEqual(PetState().mood, "Happy")

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            original = PetState(name="Mochi", hunger=45, happiness=88, energy=60)
            save_state(original, path)
            self.assertEqual(load_state(path), original)

    def test_missing_or_invalid_save_uses_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.json"
            self.assertEqual(load_state(path), PetState())
            path.write_text("{broken", encoding="utf-8")
            self.assertEqual(load_state(path), PetState())

if __name__ == "__main__":
    unittest.main()
