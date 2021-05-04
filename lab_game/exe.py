import cx_Freeze

executables = [cx_Freeze.Executable("game.py")]

files = ["wall.jpeg"]

for i in range(1, 5):
    files.append(f"portal_{i}.png")
    if i < 3:
        files.append(f"player_stand_{i}.png")
        files.append(f"player_walk_{i}.png")


cx_Freeze.setup(
    name="Labirint",
    options={"build_exe": {"packages": ["arcade"], "include_files": files}},
    executables=executables)
