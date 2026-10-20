import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from pet_logic import PetState, load_state, save_state, clamp

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class PixelPetApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PixelPet — Desktop Pet")
        self.geometry("460x640")
        self.minsize(420, 580)
        self.configure(fg_color="#151923")
        self.pet = load_state()
        self.message = tk.StringVar(value=f"{self.pet.name} is happy to see you!")
        
        self._build()
        self.refresh()
        
        # Start passive decay timer (every 8,000 ms = 8 seconds)
        self.after(8000, self.auto_decay)
        self.protocol("WM_DELETE_WINDOW", self.close)

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 4))
        
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="PIXELPET", font=ctk.CTkFont(size=25, weight="bold"),
                     text_color="#A7F3D0").pack(anchor="w")
        ctk.CTkLabel(title_box, text="A tiny friend for your desktop",
                     text_color="#AAB2C0").pack(anchor="w")

        # Pin / Always on top toggle
        self.pin_var = ctk.BooleanVar(value=False)
        self.pin_switch = ctk.CTkSwitch(header, text="Pin", variable=self.pin_var, 
                                        command=self.toggle_pin, width=40, font=ctk.CTkFont(size=12))
        self.pin_switch.pack(side="right", anchor="ne")

        card = ctk.CTkFrame(self, corner_radius=22, fg_color="#222938")
        card.pack(fill="x", padx=24, pady=12)
        self.face = ctk.CTkLabel(card, text="🐱", font=ctk.CTkFont(family="Segoe UI Emoji", size=86))
        self.face.pack(pady=(16, 2))
        self.name_label = ctk.CTkLabel(card, text=self.pet.name, font=ctk.CTkFont(size=20, weight="bold"))
        self.name_label.pack()
        self.mood_label = ctk.CTkLabel(card, text="Happy", text_color="#A7F3D0")
        self.mood_label.pack(pady=(2, 14))

        self.bars = {}
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", padx=28, pady=4)
        for key, label in (("hunger", "Hunger"), ("happiness", "Happiness"), ("energy", "Energy")):
            row = ctk.CTkFrame(stats, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=label, width=94, anchor="w").pack(side="left")
            bar = ctk.CTkProgressBar(row, height=12, progress_color="#34D399", fg_color="#343C4B")
            bar.pack(side="left", fill="x", expand=True, padx=(8, 0))
            self.bars[key] = bar

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=24, pady=(16, 6))
        for col, (label, action) in enumerate((("🍎 Feed", self.feed), ("🎾 Play", self.play), ("💤 Sleep", self.sleep))):
            ctk.CTkButton(actions, text=label, height=42, command=action,
                          corner_radius=12, fg_color="#168568", hover_color="#117357").grid(
                              row=0, column=col, padx=5, pady=5, sticky="ew")
            actions.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(self, textvariable=self.message, wraplength=380,
                     text_color="#C7D0DF").pack(padx=24, pady=(4, 10))
        
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=24, pady=(0, 16))
        ctk.CTkButton(footer, text="Rename pet", width=110, command=self.rename,
                      fg_color="#343C4B", hover_color="#465166").pack(side="left")
        ctk.CTkButton(footer, text="Reset", width=80, command=self.reset,
                      fg_color="#343C4B", hover_color="#465166").pack(side="right")

    def toggle_pin(self):
        self.attributes("-topmost", self.pin_var.get())

    def feed(self):
        if self.pet.hunger >= 100:
            self.message.set(f"{self.pet.name} is full already!")
            return
        self.pet.hunger = clamp(self.pet.hunger + 25)
        self.pet.happiness = clamp(self.pet.happiness + 5)
        self.message.set(f"Yum! {self.pet.name} enjoyed a snack. 🍎")
        self.after_action()

    def play(self):
        if self.pet.energy < 15:
            self.message.set(f"{self.pet.name} is too sleepy to play. Try Sleep!")
            return
        self.pet.happiness = clamp(self.pet.happiness + 18)
        self.pet.energy = clamp(self.pet.energy - 15)
        self.pet.hunger = clamp(self.pet.hunger - 8)
        self.message.set(f"That was fun! {self.pet.name} is smiling. 🎾")
        self.after_action()

    def sleep(self):
        if self.pet.energy >= 100:
            self.message.set(f"{self.pet.name} is wide awake!")
            return
        self.pet.energy = clamp(self.pet.energy + 30)
        self.pet.happiness = clamp(self.pet.happiness + 3)
        self.message.set(f"{self.pet.name} had a refreshing nap. 💤")
        self.after_action()

    def auto_decay(self):
        """Passively lowers stats and alerts the user if pet needs care."""
        self.pet.tick()
        if self.pet.hunger < 20:
            self.message.set(f"{self.pet.name} is starving! Please feed them.")
        elif self.pet.energy < 20:
            self.message.set(f"{self.pet.name} is exhausted and needs sleep.")
        self.refresh()
        self.after(8000, self.auto_decay)

    def rename(self):
        dialog = ctk.CTkInputDialog(text="What should your pet be called?", title="Rename PixelPet")
        name = dialog.get_input()
        if name and name.strip():
            self.pet.name = name.strip()[:24]
            self.message.set(f"Meet {self.pet.name}! A lovely name.")
            self.after_action()

    def reset(self):
        if messagebox.askyesno("Reset PixelPet", "Reset stats and rename your pet to Pixel?"):
            self.pet = PetState()
            self.message.set("A fresh start! Say hello to your new friend.")
            self.after_action()

    def after_action(self):
        self.refresh()
        try:
            save_state(self.pet)
        except OSError:
            self.message.set("Could not save progress. Check folder permissions.")

    def _get_status_color(self, val):
        if val > 50: return "#34D399"  # Green
        if val > 25: return "#FBBF24"  # Amber
        return "#F87171"               # Red

    def refresh(self):
        self.name_label.configure(text=self.pet.name)
        self.mood_label.configure(text=self.pet.mood)
        self.face.configure(text={"Happy": "😸", "Okay": "🐱", "Sleepy": "😴", "Hungry": "🙀"}.get(self.pet.mood, "🐱"))
        
        for key, bar in self.bars.items():
            val = getattr(self.pet, key)
            bar.set(val / 100)
            bar.configure(progress_color=self._get_status_color(val))

    def close(self):
        try: save_state(self.pet)
        except OSError: pass
        self.destroy()

if __name__ == "__main__":
    PixelPetApp().mainloop()