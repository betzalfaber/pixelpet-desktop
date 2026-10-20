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
        self.geometry("460x620")
        self.minsize(420, 570)
        self.configure(fg_color="#151923")
        self.pet = load_state()
        self.message = tk.StringVar(value="Your pet is happy to see you!")
        self._build()
        self.refresh()
        self.protocol("WM_DELETE_WINDOW", self.close)

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(22, 6))
        ctk.CTkLabel(header, text="PIXELPET", font=ctk.CTkFont(size=25, weight="bold"),
                     text_color="#A7F3D0").pack(anchor="w")
        ctk.CTkLabel(header, text="A tiny friend for your desktop",
                     text_color="#AAB2C0").pack(anchor="w")

        card = ctk.CTkFrame(self, corner_radius=22, fg_color="#222938")
        card.pack(fill="x", padx=24, pady=14)
        self.face = ctk.CTkLabel(card, text="🐱", font=ctk.CTkFont(family="Segoe UI Emoji", size=86))
        self.face.pack(pady=(20, 4))
        self.name_label = ctk.CTkLabel(card, text=self.pet.name, font=ctk.CTkFont(size=20, weight="bold"))
        self.name_label.pack()
        self.mood_label = ctk.CTkLabel(card, text="Happy", text_color="#A7F3D0")
        self.mood_label.pack(pady=(3, 16))

        self.bars = {}
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", padx=28, pady=4)
        for key, label in (("hunger", "Hunger"), ("happiness", "Happiness"), ("energy", "Energy")):
            row = ctk.CTkFrame(stats, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=label, width=94, anchor="w").pack(side="left")
            bar = ctk.CTkProgressBar(row, height=12, progress_color="#34D399", fg_color="#343C4B")
            bar.pack(side="left", fill="x", expand=True, padx=(8, 0))
            self.bars[key] = bar

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=24, pady=(18, 8))
        for col, (label, action) in enumerate((("🍎 Feed", self.feed), ("🎾 Play", self.play), ("💤 Sleep", self.sleep))):
            ctk.CTkButton(actions, text=label, height=42, command=action,
                          corner_radius=12, fg_color="#168568", hover_color="#117357").grid(
                              row=0, column=col, padx=5, pady=5, sticky="ew")
            actions.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(self, textvariable=self.message, wraplength=380,
                     text_color="#C7D0DF").pack(padx=24, pady=(5, 12))
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=24, pady=(0, 18))
        ctk.CTkButton(footer, text="Rename pet", width=110, command=self.rename,
                      fg_color="#343C4B", hover_color="#465166").pack(side="left")
        ctk.CTkButton(footer, text="Reset", width=80, command=self.reset,
                      fg_color="#343C4B", hover_color="#465166").pack(side="right")

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
        self.pet.energy = clamp(self.pet.energy + 30)
        self.pet.happiness = clamp(self.pet.happiness + 3)
        self.message.set(f"{self.pet.name} had a refreshing nap. 💤")
        self.after_action()

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

    def refresh(self):
        self.name_label.configure(text=self.pet.name)
        self.mood_label.configure(text=self.pet.mood)
        self.face.configure(text={"Happy": "😸", "Okay": "🐱", "Sleepy": "😴", "Hungry": "🙀"}.get(self.pet.mood, "🐱"))
        for key, bar in self.bars.items():
            bar.set(getattr(self.pet, key) / 100)

    def close(self):
        try: save_state(self.pet)
        except OSError: pass
        self.destroy()

if __name__ == "__main__":
    PixelPetApp().mainloop()
