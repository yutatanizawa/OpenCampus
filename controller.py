import tkinter as tk
from tkinter import simpledialog, messagebox
from threading import Thread
import subprocess
import os, re
import sys
import time
import traceback
from openai import OpenAI

# --- Settings ---
GAME_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "game.py"))
LOG_DIR = os.path.join(os.path.dirname(GAME_FILE_PATH), "log")
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# --- Backup/Restore ---
def save_backup_code():
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(GAME_FILE_PATH, "r") as f:
            code = f.read()
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(LOG_DIR, f"game_backup_{timestamp}.py")
        with open(backup_path, "w") as f:
            f.write(code)
        print(f"Backup saved: {backup_path}")
    except Exception as e:
        print(f"Error saving backup: {e}")

def restore_latest_backup():
    try:
        backups = [f for f in os.listdir(LOG_DIR) if f.startswith("game_backup_") and f.endswith(".py")]
        if not backups:
            print("No backup found.")
            return False
        latest = max(backups, key=lambda f: os.path.getmtime(os.path.join(LOG_DIR, f)))
        backup_path = os.path.join(LOG_DIR, latest)
        with open(backup_path, "r") as f:
            code = f.read()
        with open(GAME_FILE_PATH, "w") as f:
            f.write(code)
        print(f"Restored backup: {backup_path}")
        return True
    except Exception as e:
        print(f"Error restoring backup: {e}")
        return False

# --- AI Code Modification ---
def ai_modify_code(prompt):
    save_backup_code()
    try:
        with open(GAME_FILE_PATH, "r") as f:
            current_code = f.read()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for modifying Python game code."},
                {"role": "user", "content": f"The current game.py code is:\n\n{current_code}\n\nModify it based on the following instruction:\n{prompt}\n\nPlease output only the modified full Python code. Do not include any explanations or comments unless they are part of the code itself."}
            ],
            max_tokens=3000,
            temperature=0.7
        )
        lines = response.choices[0].message.content.strip().splitlines()
        if lines and "```python" in lines[0].lower():
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        new_code = "\n".join(lines)
        with open(GAME_FILE_PATH, "w") as f:
            f.write(new_code)
        return True, ""
    except Exception as e:
        tb = traceback.format_exc()
        return False, f"{e}\n{tb}"

# --- Game Process Management ---
game_process = None

def start_game():
    global game_process
    if game_process and game_process.poll() is None:
        messagebox.showinfo("Info", "Game is already running.")
        return
    try:
        game_process = subprocess.Popen([sys.executable, GAME_FILE_PATH])
        print("Game started.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start game: {e}")

def stop_game():
    global game_process
    if game_process and game_process.poll() is None:
        game_process.terminate()
        game_process.wait()
        print("Game stopped.")

def restart_game():
    stop_game()
    time.sleep(1)
    start_game()
    # Check if game started successfully
    time.sleep(2)
    if game_process.poll() is not None:
        messagebox.showerror("Error", "Game failed to start. Restoring latest backup...")
        if restore_latest_backup():
            start_game()
            time.sleep(2)
            if game_process.poll() is not None:
                messagebox.showerror("Error", "Even after restoring backup, the game failed to start.")
            else:
                messagebox.showinfo("Restored", "Backup restored and game started.")
        else:
            messagebox.showerror("Error", "No backup available to restore.")

# --- Tkinter UI ---
def ai_modify_action():
    prompt = simpledialog.askstring("AI Code Modification", "Enter your instruction for code modification (e.g., Double the jump strength):")
    if not prompt:
        return
    ok = messagebox.askyesno("Confirmation", "Do you want to execute AI code modification?\n(If it fails, the latest backup will be restored automatically.)")
    if not ok:
        return
    success, err = ai_modify_code(prompt)
    if success:
        messagebox.showinfo("Success", "AI code modification completed. The game will restart.")
        restart_game()
    else:
        messagebox.showerror("Error", f"AI modification failed: {err}\nRestoring from backup.")
        if restore_latest_backup():
            messagebox.showinfo("Restored", "Restored from backup. The game will restart.")
            restart_game()
        else:
            messagebox.showerror("Restore Failed", "Failed to restore from backup. Please fix manually.")

def on_close():
    stop_game()
    root.destroy()

# --- Live View Variables ---
live_vars = {
    "Gravity": 0.0,
    "Jump Strength": 0.0,
    "Obstacle Width": 0,
    "Obstacle Height": 0,
    "Dino Color": "(0, 0, 0)",
    "Speed Multiplier": 0.0,
}

def update_live_vars_from_code():
    try:
        with open(GAME_FILE_PATH, "r") as f:
            code = f.read()
        # Extract values using regex
        patterns = {
            "Gravity": r"GRAVITY\s*=\s*([-\d\.]+)",
            "Jump Strength": r"JUMP_STRENGTH\s*=\s*([-\d\.]+)",
            "Obstacle Width": r"OBSTACLE_SIZE\s*=\s*\[([-\d\.]+),\s*([-\d\.]+)\]",
            "Obstacle Height": r"OBSTACLE_SIZE\s*=\s*\[([-\d\.]+),\s*([-\d\.]+)\]",
            "Dino Color": r"DINO_COLOR\s*=\s*\(([\d\s,]+)\)",
            "Speed Multiplier": r"SPEED_MULTIPLIER\s*=\s*([-\d\.]+)",
        }
        for key, pat in patterns.items():
            m = re.search(pat, code)
            if m:
                if key == "Obstacle Width":
                    live_vars[key] = float(m.group(1))
                elif key == "Obstacle Height":
                    live_vars[key] = float(m.group(2))
                elif key == "Dino Color":
                    live_vars[key] = f"({m.group(1)})"
                else:
                    live_vars[key] = float(m.group(1))
    except Exception as e:
        print(f"Error updating live vars: {e}")

def refresh_live_view():
    update_live_vars_from_code()
    for key, var in live_vars.items():
        live_labels[key].config(text=f"{key}: {var}")

def open_live_view():
    global live_labels
    live_view = tk.Toplevel()
    live_view.title("LIVE View - Game Settings")
    live_labels = {}
    for key in live_vars:
        lbl = tk.Label(live_view, text=f"{key}: {live_vars[key]}", font=("Arial", 12))
        lbl.pack(anchor="w")
        live_labels[key] = lbl
    def periodic_refresh():
        if not live_view.winfo_exists():
            return
        refresh_live_view()
        live_view.after(1000, periodic_refresh)
    periodic_refresh()

def open_backup_manager():
    try:
        backups = sorted(
            [f for f in os.listdir(LOG_DIR) if f.startswith("game_backup_") and f.endswith(".py")],
            key=lambda f: os.path.getmtime(os.path.join(LOG_DIR, f)),
            reverse=True
        )
        if not backups:
            messagebox.showinfo("No Backups", "No backups were found.")
            return

        backup_win = tk.Toplevel()
        backup_win.title("Backup Management")

        listbox = tk.Listbox(backup_win, width=50, height=15)
        listbox.pack(padx=10, pady=10)

        for b in backups:
            listbox.insert(tk.END, b)

        def load_selected_backup():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("No selection", "Please select a backup to restore.")
                return
            backup_name = listbox.get(selection[0])
            backup_path = os.path.join(LOG_DIR, backup_name)

            try:
                with open(backup_path, "r") as f:
                    code = f.read()
                with open(GAME_FILE_PATH, "w") as f:
                    f.write(code)
                messagebox.showinfo("Restore Complete", f"{backup_name} has been restored. The game will now restart.")
                restart_game()
                backup_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restore: {e}")

        tk.Button(backup_win, text="Restore Selected Backup", command=load_selected_backup).pack(pady=(0,10))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve the list of backups: {e}")


root = tk.Tk()
root.title("Dino Game Controller")
root.protocol("WM_DELETE_WINDOW", on_close)

tk.Button(root, text="Start Game", command=start_game, width=20).pack(pady=5)
tk.Button(root, text="Stop Game", command=stop_game, width=20).pack(pady=5)
tk.Button(root, text="Restart Game", command=restart_game, width=20).pack(pady=5)
tk.Button(root, text="AI Code Modify", command=ai_modify_action, width=20).pack(pady=5)
tk.Button(root, text="Exit", command=on_close, width=20).pack(pady=5)
tk.Button(root, text="LIVE View", command=open_live_view, width=20).pack(pady=5)
tk.Button(root, text="load backup", command=open_backup_manager, width=20).pack(pady=5)


root.mainloop()