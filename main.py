import random
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from pet_logic import PetState, SKINS, load_state, save_state, clamp

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# Color Palettes for 8-Bit Skins
PALETTES = {
    "Cat":   {"B": "#38BDF8", "S": "#BAE6FD", "E": "#0F172A", "P": "#F472B6", "W": "#FFFFFF"},
    "Dino":  {"B": "#34D399", "S": "#FEF08A", "E": "#064E3B", "P": "#F87171", "W": "#FFFFFF"},
    "Ghost": {"B": "#E2E8F0", "S": "#94A3B8", "E": "#1E293B", "P": "#C084FC", "W": "#FFFFFF"},
    "Slime": {"B": "#A855F7", "S": "#E9D5FF", "E": "#3B0764", "P": "#F43F5E", "W": "#FFFFFF"},
}

SPRITES = {
    "Cat": [
        "  BB        BB  ",
        " BPPB      BPPB ",
        " BPPBBBBBBBBPPB ",
        "BBBBBBBBBBBBBBBB",
        "BBBWEEBBBBWEEBBB",
        "BBBBBBBBBBBBBBBB",
        "BBBBBBBPBBBBBBBB",
        "BBBBBBPBPBBBBBBB",
        " BBBBBBBBBBBBBB ",
        "  BBBBBBBBBBBB  ",
        " BSSSSSSSSSSSSB ",
        "BSSSSSSSSSSSSSSB",
        "BSSSSSSSSSSSSSSB",
        " BBBBBBBBBBBBBB ",
        "  BB        BB  ",
    ],
    "Dino": [
        "    BBBBBBBB    ",
        "   PBBBBBBBBBB  ",
        "  PBBBWWEEBBBB  ",
        "   BBBBBBBBBBB  ",
        "   BBBBBBBB     ",
        "  PBBBBBBBBBBBB ",
        " PBBBBSSSSSSSSB ",
        "  BBBBBBBBBBBB  ",
        " BSSSSSSSSSSSSB ",
        "BSSSSSSSSSSSSB  ",
        "BBBBBBBBBBBBBB  ",
        " BBBBBBBBBBBB   ",
        "  BBBB    BBBB  ",
        "  BBBB    BBBB  ",
        "  SSSS    SSSS  ",
    ],
    "Ghost": [
        "    BBBBBBBB    ",
        "  BBBBBBBBBBBB  ",
        " BBBBBBBBBBBBBB ",
        "BBBBBBBBBBBBBBBB",
        "BBBWEEBBBBWEEBBB",
        "BBBWEEBBBBWEEBBB",
        "BBBBBBBBBBBBBBBB",
        "BBBBPBBBBBBPBBBB",
        "BBBBBBBBBBBBBBBB",
        "BBBBSSSSSSSSBBBB",
        "BBBBSSSSSSSSBBBB",
        "BBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBB",
        "BB BBBB  BBBB BB",
        "B   BB    BB   B",
    ],
    "Slime": [
        "                ",
        "      BBBB      ",
        "    BBBBBBBB    ",
        "  BBBBWWWWBBBB  ",
        " BBBBWWBBBBBBBB ",
        "BBBBBBBBBBBBBBBB",
        "BBBWEEBBBBWEEBBB",
        "BBBBBBBBBBBBBBBB",
        "BBBBPBBBBBBPBBBB",
        "BBBBBBPPPPBBBBBB",
        "BSSSSSSSSSSSSSSB",
        "BSSSSSSSSSSSSSSB",
        " BBBBBBBBBBBBBB ",
        "  BBBBBBBBBBBB  ",
        "                ",
    ]
}

def render_pet_on_canvas(canvas, pet, anim_frame, particles, bg_shadow="#0F141C", flip=False):
    """Shared pixel art renderer for both Dashboard and Transparent Desktop Overlay."""
    canvas.delete("all")
    skin = pet.skin if pet.skin in SPRITES else "Cat"
    grid = SPRITES[skin]
    palette = PALETTES[skin]

    pixel_size = 7
    offset_x = 34
    offset_y = 24 + (3 if anim_frame % 2 == 1 else 0)
    is_blinking = (anim_frame % 7 == 0) or (pet.mood == "Sleepy")

    if bg_shadow:
        canvas.create_oval(52, 132, 128, 142, fill=bg_shadow, outline="")

    for r, row_str in enumerate(grid):
        cols = list(reversed(row_str)) if flip else list(row_str)
        for c, ch in enumerate(cols):
            if ch == " ":
                continue
            if ch in ("E", "W") and is_blinking:
                color = palette["B"]
            else:
                color = palette.get(ch, "#FFFFFF")

            # Alternate feet movement on bottom row
            dy = -2 if (r == len(grid) - 1 and (c + anim_frame) % 2 == 0) else 0
            x1 = offset_x + c * pixel_size
            y1 = offset_y + r * pixel_size + dy
            canvas.create_rectangle(x1, y1, x1 + pixel_size, y1 + pixel_size, fill=color, outline="")

    # Draw Floating Particles
    for p in particles:
        canvas.create_text(p["x"], p["y"], text=p["text"], fill=p["color"], font=("Segoe UI", 10, "bold"))


class DesktopOverlay(tk.Toplevel):
    """Frameless, transparent Windows overlay where the pet walks directly on the desktop."""
    TRANSPARENT_KEY = "#010203"

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.overrideredirect(True)  # Frameless border
        self.attributes("-topmost", True)
        self.config(bg=self.TRANSPARENT_KEY)

        # Apply Windows chroma-key transparency
        try:
            self.wm_attributes("-transparentcolor", self.TRANSPARENT_KEY)
        except tk.TclError:
            pass

        # Spawn near bottom-right corner above taskbar
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.x_pos = sw - 240
        self.y_pos = sh - 220
        self.geometry(f"180x165+{self.x_pos}+{self.y_pos}")

        self.canvas = tk.Canvas(self, width=180, height=165, bg=self.TRANSPARENT_KEY, highlightthickness=0, cursor="fleur")
        self.canvas.pack()

        # Bind Mouse Drag, Petting, and Context Menu
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.do_drag)
        self.canvas.bind("<Double-Button-1>", lambda e: self.app.exit_overlay_mode())
        self.canvas.bind("<Button-3>", self.show_context_menu)

        # Right-Click Popup Menu
        self.menu = tk.Menu(self, tearoff=0, bg="#1E293B", fg="#F8FAFC", activebackground="#10B981")
        self.menu.add_command(label="📊 Open Dashboard", command=self.app.exit_overlay_mode)
        self.menu.add_separator()
        self.menu.add_command(label="🍎 Quick Feed", command=self.app.feed)
        self.menu.add_command(label="🎾 Quick Play", command=self.app.play)
        self.menu.add_command(label="💤 Quick Nap", command=self.app.sleep)
        self.menu.add_separator()
        self.menu.add_command(label="❌ Quit PixelPet", command=self.app.close)

        self.roam_dir = -1
        self.is_dragging = False
        self.after(90, self.roam_step)

    def start_drag(self, event):
        self.is_dragging = True
        self._drag_x = event.x
        self._drag_y = event.y
        self.app.pet_click(event)

    def do_drag(self, event):
        self.x_pos = self.winfo_pointerx() - self._drag_x
        self.y_pos = self.winfo_pointery() - self._drag_y
        self.geometry(f"+{self.x_pos}+{self.y_pos}")

    def show_context_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def roam_step(self):
        if not self.winfo_exists():
            return
        # Gentle horizontal walking if not sleeping or being dragged
        if not self.is_dragging and self.app.pet.mood != "Sleepy":
            if random.random() < 0.04:
                self.roam_dir *= -1
            if random.random() < 0.45:
                sw = self.winfo_screenwidth()
                self.x_pos = max(20, min(sw - 200, self.x_pos + self.roam_dir * 2))
                self.geometry(f"+{self.x_pos}+{self.y_pos}")
        self.is_dragging = False
        self.after(120, self.roam_step)


class PixelPetApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PixelPet — Desktop Companion")
        self.geometry("470x760")
        self.minsize(440, 720)
        self.configure(fg_color="#0F141C")

        self.pet = load_state()
        self.message = tk.StringVar(value=f"Click {self.pet.name} to pet, or launch Desktop Mode!")
        self.anim_frame = 0
        self.particles = []
        self.overlay = None

        self._build()
        self.refresh()

        self.after(420, self.animate_loop)
        self.after(8000, self.auto_decay)
        self.protocol("WM_DELETE_WINDOW", self.close)

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(16, 6))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="PIXELPET", font=ctk.CTkFont(size=24, weight="bold"),
                     text_color="#6EE7B7").pack(anchor="w")
        ctk.CTkLabel(title_box, text="Animated Windows Companion",
                     font=ctk.CTkFont(size=12), text_color="#94A3B8").pack(anchor="w")

        right_box = ctk.CTkFrame(header, fg_color="transparent")
        right_box.pack(side="right")

        self.pin_var = ctk.BooleanVar(value=True)
        self.attributes("-topmost", True)
        ctk.CTkSwitch(right_box, text="Always on Top", variable=self.pin_var,
                      command=self.toggle_pin, width=40, progress_color="#10B981").pack(anchor="e", pady=(0, 6))

        self.skin_menu = ctk.CTkOptionMenu(
            right_box, values=SKINS, width=105, height=26,
            fg_color="#1E293B", button_color="#334155",
            command=self.change_skin
        )
        self.skin_menu.set(self.pet.skin)
        self.skin_menu.pack(anchor="e")

        # Hero Pet Card
        card = ctk.CTkFrame(self, corner_radius=20, fg_color="#18202F", border_width=1, border_color="#28354A")
        card.pack(fill="x", padx=24, pady=8)

        badge_row = ctk.CTkFrame(card, fg_color="transparent")
        badge_row.pack(fill="x", padx=16, pady=(12, 0))

        self.level_badge = ctk.CTkLabel(
            badge_row, text="LVL 1", font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#065F46", text_color="#A7F3D0", corner_radius=8, padx=10, pady=2
        )
        self.level_badge.pack(side="left")

        self.coin_badge = ctk.CTkLabel(
            badge_row, text="Coins: 25", font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#3B2F1E", text_color="#FDE047", corner_radius=8, padx=10, pady=2
        )
        self.coin_badge.pack(side="right")

        self.canvas = tk.Canvas(card, width=180, height=150, bg="#18202F", highlightthickness=0, cursor="hand2")
        self.canvas.pack(pady=(2, 2))
        self.canvas.bind("<Button-1>", self.pet_click)

        self.name_label = ctk.CTkLabel(card, text=self.pet.name, font=ctk.CTkFont(size=20, weight="bold"))
        self.name_label.pack()

        self.mood_label = ctk.CTkLabel(card, text="Happy", font=ctk.CTkFont(size=13, weight="bold"), text_color="#6EE7B7")
        self.mood_label.pack(pady=(0, 6))

        xp_frame = ctk.CTkFrame(card, fg_color="transparent")
        xp_frame.pack(fill="x", padx=28, pady=(0, 14))
        self.xp_label = ctk.CTkLabel(xp_frame, text="XP: 0 / 50", font=ctk.CTkFont(size=11), text_color="#94A3B8")
        self.xp_label.pack(anchor="w")
        self.xp_bar = ctk.CTkProgressBar(xp_frame, height=7, progress_color="#38BDF8", fg_color="#0F172A")
        self.xp_bar.pack(fill="x", pady=(2, 0))

        # Desktop Overlay Mode Launch Button
        ctk.CTkButton(
            self, text="🐾Float on Desktop (Transparent Pet Mode)", height=38,
            corner_radius=12, fg_color="#0284C7", hover_color="#0369A1",
            font=ctk.CTkFont(size=13, weight="bold"), command=self.enter_overlay_mode
        ).pack(fill="x", padx=24, pady=(4, 8))

        # Stat Bars
        self.bars = {}
        self.val_labels = {}
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", padx=26, pady=4)

        for key, label in (("hunger", "Hunger"), ("happiness", "Happiness"), ("energy", "Energy")):
            row = ctk.CTkFrame(stats, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=label, width=80, anchor="w", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
            bar = ctk.CTkProgressBar(row, height=12, progress_color="#34D399", fg_color="#1E293B")
            bar.pack(side="left", fill="x", expand=True, padx=10)
            val_lbl = ctk.CTkLabel(row, text="80%", width=40, anchor="e", font=ctk.CTkFont(size=12), text_color="#94A3B8")
            val_lbl.pack(side="right")
            self.bars[key] = bar
            self.val_labels[key] = val_lbl

        # Action Buttons
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=22, pady=(10, 4))
        btn_specs = [
            ("Feed (+XP)", self.feed, "#059669", "#047857"),
            ("Play (+Coins)", self.play, "#2563EB", "#1D4ED8"),
            ("Sleep (+Rest)", self.sleep, "#7C3AED", "#6D28D9"),
        ]
        for col, (label, action, color, hover) in enumerate(btn_specs):
            ctk.CTkButton(
                actions, text=label, height=40, command=action,
                corner_radius=10, fg_color=color, hover_color=hover,
                font=ctk.CTkFont(size=13, weight="bold")
            ).grid(row=0, column=col, padx=4, sticky="ew")
            actions.grid_columnconfigure(col, weight=1)

        # Shop Buttons
        shop = ctk.CTkFrame(self, fg_color="transparent")
        shop.pack(fill="x", padx=22, pady=(4, 6))
        ctk.CTkButton(
            shop, text="Buy Sushi (10 Coins)", height=32,
            fg_color="#1E293B", hover_color="#334155", text_color="#FDE047",
            command=self.buy_sushi
        ).grid(row=0, column=0, padx=4, sticky="ew")
        ctk.CTkButton(
            shop, text="Energy Potion (15 Coins)", height=32,
            fg_color="#1E293B", hover_color="#334155", text_color="#38BDF8",
            command=self.buy_potion
        ).grid(row=0, column=1, padx=4, sticky="ew")
        shop.grid_columnconfigure(0, weight=1)
        shop.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, textvariable=self.message, wraplength=400,
                     font=ctk.CTkFont(size=13), text_color="#E2E8F0").pack(padx=24, pady=(4, 8))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=26, pady=(0, 14))
        ctk.CTkButton(footer, text="Rename Pet", width=110, height=30, command=self.rename,
                      fg_color="#1E293B", hover_color="#334155").pack(side="left")
        ctk.CTkButton(footer, text="Reset", width=80, height=30, command=self.reset,
                      fg_color="#3F1D28", hover_color="#581C2F", text_color="#FDA4AF").pack(side="right")

    def enter_overlay_mode(self):
        """Hides the main window and spawns the transparent floating pet on the desktop."""
        self.withdraw()
        if self.overlay is None or not self.overlay.winfo_exists():
            self.overlay = DesktopOverlay(self)

    def exit_overlay_mode(self):
        """Closes overlay and restores the main dashboard."""
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.destroy()
        self.overlay = None
        self.deiconify()
        self.lift()

    def spawn_particle(self, text, color="#F472B6"):
        self.particles.append({
            "x": random.randint(45, 135),
            "y": random.randint(30, 60),
            "text": text,
            "color": color,
            "life": 5
        })

    def animate_loop(self):
        self.anim_frame += 1
        if self.pet.mood == "Sleepy" and self.anim_frame % 3 == 0:
            self.spawn_particle("Zzz", "#93C5FD")

        # Update particle positions
        remaining = []
        for p in self.particles:
            p["y"] -= 5
            p["life"] -= 1
            if p["life"] > 0:
                remaining.append(p)
        self.particles = remaining

        # Render on whichever view is active
        if self.overlay and self.overlay.winfo_exists():
            flip = self.overlay.roam_dir > 0
            render_pet_on_canvas(self.overlay.canvas, self.pet, self.anim_frame, self.particles, bg_shadow=None, flip=flip)
            # Subtle name tag under pet on desktop
            self.overlay.canvas.create_text(
                90, 148, text=f"{self.pet.name} (Lv.{self.pet.level})",
                fill="#A7F3D0", font=("Segoe UI", 9, "bold")
            )
        else:
            render_pet_on_canvas(self.canvas, self.pet, self.anim_frame, self.particles, bg_shadow="#0F141C")

        self.after(420, self.animate_loop)

    def pet_click(self, event):
        self.pet.happiness = clamp(self.pet.happiness + 4)
        leveled = self.pet.gain_rewards(xp_amount=5, coin_amount=1)
        self.spawn_particle("♥ +5 XP", "#F472B6")
        if leveled:
            self.message.set(f"🎉 LEVEL UP! {self.pet.name} reached Level {self.pet.level}!")
        else:
            self.message.set(f"{self.pet.name} loves attention! (+5 XP, +1 Coin)")
        self.after_action()

    def change_skin(self, new_skin):
        self.pet.skin = new_skin
        self.spawn_particle("✨ Skin!", "#FDE047")
        self.after_action()

    def toggle_pin(self):
        self.attributes("-topmost", self.pin_var.get())

    def feed(self):
        if self.pet.hunger >= 100:
            self.message.set(f"{self.pet.name} is completely full!")
            return
        self.pet.hunger = clamp(self.pet.hunger + 25)
        self.pet.happiness = clamp(self.pet.happiness + 5)
        leveled = self.pet.gain_rewards(xp_amount=12, coin_amount=2)
        self.spawn_particle("+25 Food", "#34D399")
        self.message.set(f"🎉 LEVEL UP to {self.pet.level}!" if leveled else f"Yum! {self.pet.name} enjoyed a meal.")
        self.after_action()

    def play(self):
        if self.pet.energy < 15:
            self.message.set(f"{self.pet.name} is too tired! Let them sleep.")
            return
        self.pet.happiness = clamp(self.pet.happiness + 20)
        self.pet.energy = clamp(self.pet.energy - 15)
        self.pet.hunger = clamp(self.pet.hunger - 8)
        leveled = self.pet.gain_rewards(xp_amount=18, coin_amount=6)
        self.spawn_particle("+6 Coins!", "#FDE047")
        self.message.set(f"🎉 LEVEL UP to {self.pet.level}!" if leveled else "Fun game! (+18 XP, +6 Coins)")
        self.after_action()

    def sleep(self):
        if self.pet.energy >= 100:
            self.message.set(f"{self.pet.name} is already wide awake!")
            return
        self.pet.energy = clamp(self.pet.energy + 35)
        self.pet.happiness = clamp(self.pet.happiness + 4)
        self.pet.gain_rewards(xp_amount=8, coin_amount=1)
        self.spawn_particle("Zzz +Rest", "#A78BFA")
        self.message.set(f"{self.pet.name} feels refreshed! (+35 Energy)")
        self.after_action()

    def buy_sushi(self):
        if self.pet.coins < 10:
            self.message.set("Need 10 coins! Play with your pet to earn more.")
            return
        self.pet.coins -= 10
        self.pet.hunger = 100
        self.pet.happiness = clamp(self.pet.happiness + 15)
        self.spawn_particle("Sushi!", "#F43F5E")
        self.message.set(f"Bought Deluxe Sushi! {self.pet.name} is 100% full!")
        self.after_action()

    def buy_potion(self):
        if self.pet.coins < 15:
            self.message.set("Need 15 coins for an Energy Potion!")
            return
        self.pet.coins -= 15
        self.pet.energy = 100
        self.spawn_particle("MAX ENERGY!", "#38BDF8")
        self.message.set(f"ZAP! {self.pet.name}'s energy is 100% restored!")
        self.after_action()

    def auto_decay(self):
        self.pet.tick()
        if self.pet.hunger < 20:
            self.message.set(f"Alert: {self.pet.name} is hungry!")
        elif self.pet.energy < 20:
            self.message.set(f"Alert: {self.pet.name} is sleepy!")
        self.refresh()
        self.after(8000, self.auto_decay)

    def rename(self):
        dialog = ctk.CTkInputDialog(text="Enter a new name for your pet:", title="Rename PixelPet")
        name = dialog.get_input()
        if name and name.strip():
            self.pet.name = name.strip()[:24]
            self.message.set(f"Renamed companion to {self.pet.name}!")
            self.after_action()

    def reset(self):
        if messagebox.askyesno("Reset PixelPet", "Reset level, coins, and stats back to default?"):
            self.pet = PetState()
            self.skin_menu.set(self.pet.skin)
            self.message.set("Fresh start! Say hello to Pixel.")
            self.after_action()

    def after_action(self):
        self.refresh()
        try:
            save_state(self.pet)
        except OSError:
            self.message.set("Could not save progress.")

    def _get_status_color(self, val):
        if val > 55: return "#10B981"
        if val > 25: return "#F59E0B"
        return "#EF4444"

    def refresh(self):
        self.name_label.configure(text=self.pet.name)
        self.mood_label.configure(text=f"Mood: {self.pet.mood}")
        self.level_badge.configure(text=f"LVL {self.pet.level}")
        self.coin_badge.configure(text=f"Coins: {self.pet.coins}")
        self.xp_label.configure(text=f"XP: {self.pet.xp} / {self.pet.xp_needed}")
        self.xp_bar.set(self.pet.xp / self.pet.xp_needed)

        for key, bar in self.bars.items():
            val = getattr(self.pet, key)
            bar.set(val / 100)
            bar.configure(progress_color=self._get_status_color(val))
            self.val_labels[key].configure(text=f"{val}%")

    def close(self):
        try:
            save_state(self.pet)
        except OSError:
            pass
        self.destroy()

if __name__ == "__main__":
    PixelPetApp().mainloop()