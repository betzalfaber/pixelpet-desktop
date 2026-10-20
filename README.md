# PixelPet — Virtual Desktop Pet

A tiny desktop companion built with Python and CustomTkinter. Feed your pet, play with it, help it rest, and save progress between sessions.

## Features
- Modern dark desktop interface
- Feed, play, and sleep actions
- Hunger, happiness, and energy meters
- Mood and pet face change based on stats
- Rename your pet and reset stats with confirmation
- Save and restore pet state as JSON
- Unit tests for state, mood, and persistence

## Requirements
- Windows 10/11
- Python 3.10 or newer
- pip

## Run on Windows
Open PowerShell in this project folder.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

If PowerShell blocks activation, use Command Prompt and run:
```bat
.venv\Scripts\activate.bat
```

## Run tests
```powershell
python -m unittest discover -s tests -v
```
The tests do not need the graphical interface to open.

## Save data
By default, state is saved at `%USERPROFILE%\.pixelpet\pet_state.json`.
Set `PIXELPET_HOME` to use another save directory.

## Project structure
```text
pixelpet-desktop/
├── main.py
├── pet_logic.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
└── tests/
    └── test_pet_logic.py
```

## Publish to GitHub
Create an empty repository named `pixelpet-desktop`, then run:

```bash
git init
git add .
git commit -m "Build PixelPet desktop companion"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/pixelpet-desktop.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username.

## Future improvements
- Add pixel-art sprites and animations
- Minimize to system tray
- Add multiple pet skins
- Package as a Windows executable with PyInstaller

## License
MIT
