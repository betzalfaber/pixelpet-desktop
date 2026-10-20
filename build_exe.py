import PyInstaller.__main__

if __name__ == "__main__":
    PyInstaller.__main__.run([
        "main.py",
        "--name=PixelPet",
        "--onefile",
        "--noconsole",
        "--collect-all=customtkinter",
        "--clean",
    ])
    print("\n✅ Build complete! Your standalone executable is at: dist/PixelPet.exe")