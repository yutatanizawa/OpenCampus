import pygame
import tkinter as tk
from threading import Thread, Event
import random

# What the setting is
GRAVITY = 0.5
JUMP_STRENGTH = -50  # Changed from -10 to -50
OBSTACLE_SIZE = [20, 40]
DINO_COLOR = (0, 0, 0)
SPEED_MULTIPLIER = 1.0
COLOR_OPTIONS = [(0,0,0), (0,128,0), (0,0,255), (255,165,0)]
COLOR_INDEX = 0

exit_event = Event()

def get_game_code():
    return f"""# Dino Game Code Snapshot
GRAVITY = {GRAVITY}
JUMP_STRENGTH = {JUMP_STRENGTH}
OBSTACLE_SIZE = {tuple(OBSTACLE_SIZE)}
DINO_COLOR = {DINO_COLOR}
SPEED_MULTIPLIER = {round(SPEED_MULTIPLIER, 2)}
"""

def run_game():
    global GRAVITY, JUMP_STRENGTH, OBSTACLE_SIZE, DINO_COLOR, SPEED_MULTIPLIER

    pygame.init()
    screen = pygame.display.set_mode((800, 300))
    pygame.display.set_caption("Dino Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    paused = False

    def reset_game():
        return {
            "dino": pygame.Rect(50, 260, 40, 40),
            "vel_y": 0,
            "on_ground": True,
            "obstacles": [],
            "spawn_timer": 0,
            "score": 0,
            "speed": 5 * SPEED_MULTIPLIER,
            "speed_multiplier": SPEED_MULTIPLIER,
            "game_over": False,
        }

    state = reset_game()

    while not exit_event.is_set():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_event.set()
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if not state["game_over"] and not paused:
                    if event.key == pygame.K_SPACE and state["on_ground"]:
                        state["vel_y"] = JUMP_STRENGTH
                        state["on_ground"] = False
                elif event.key == pygame.K_r:
                    state = reset_game()
                    update_code_window()
            if event.type == pygame.ACTIVEEVENT:
                if event.state == 1:
                    paused = not event.gain

        if not paused:
            screen.fill((255, 255, 255))

            if not state["game_over"]:
                state["vel_y"] += GRAVITY
                state["dino"].y += int(state["vel_y"])
                if state["dino"].y >= 260:
                    state["dino"].y = 260
                    state["vel_y"] = 0
                    state["on_ground"] = True

                state["spawn_timer"] += 1
                if state["spawn_timer"] > 90:
                    state["spawn_timer"] = 0
                    obs_w, obs_h = OBSTACLE_SIZE
                    state["obstacles"].append(pygame.Rect(800, 300 - obs_h, obs_w, obs_h))

                new_obstacles = []
                for obs in state["obstacles"]:
                    obs.x -= int(state["speed"])
                    if obs.x + obs.width > 0:
                        new_obstacles.append(obs)
                    pygame.draw.rect(screen, (255, 0, 0), obs)
                state["obstacles"] = new_obstacles

                for obs in state["obstacles"]:
                    if state["dino"].colliderect(obs):
                        state["game_over"] = True

                state["score"] += 1
                if state["score"] % 100 == 0:
                    state["speed"] *= 1.1
                    state["speed_multiplier"] *= 1.1
                    update_code_window()

            pygame.draw.rect(screen, DINO_COLOR, state["dino"])  # Changed to draw a rectangle
            score_text = font.render(f"Score: {state['score']}", True, (0, 0, 0))
            screen.blit(score_text, (10, 10))

            if state["game_over"]:
                msg = font.render("Game Over - Press R to Restart", True, (255, 0, 0))
                screen.blit(msg, (250, 120))
        else:
            pause_msg = font.render("Paused (click game window to resume)", True, (128, 128, 128))
            screen.fill((230, 230, 230))
            screen.blit(pause_msg, (180, 140))

        pygame.display.flip()
        clock.tick(60)

# Here to control the game
def update_code_window():
    code_text.delete("1.0", tk.END)
    code_text.insert(tk.END, get_game_code())

def change_jump(delta):
    global JUMP_STRENGTH
    JUMP_STRENGTH = max(-30, min(-2, JUMP_STRENGTH + delta))
    update_code_window()

def change_obstacle(delta):
    OBSTACLE_SIZE[0] = max(10, OBSTACLE_SIZE[0] + delta)
    OBSTACLE_SIZE[1] = max(10, OBSTACLE_SIZE[1] + delta)
    update_code_window()

def change_speed(delta):
    global SPEED_MULTIPLIER
    SPEED_MULTIPLIER = max(0.1, round(SPEED_MULTIPLIER + delta, 2))
    update_code_window()

def cycle_color(direction):
    global DINO_COLOR, COLOR_INDEX
    COLOR_INDEX = (COLOR_INDEX + direction) % len(COLOR_OPTIONS)
    DINO_COLOR = COLOR_OPTIONS[COLOR_INDEX]
    update_code_window()

def on_close_all():
    exit_event.set()
    root.destroy()
    code_window.destroy()
    pygame.quit()

# Game Changing bottom

root = tk.Tk()
root.title("Dino Controls")
root.protocol("WM_DELETE_WINDOW", on_close_all)

def add_button_row(label, inc_func, dec_func):
    frame = tk.Frame(root)
    frame.pack(fill='x')
    tk.Label(frame, text=label, width=20).pack(side='left')
    tk.Button(frame, text="+", command=inc_func).pack(side='left')
    tk.Button(frame, text="-", command=dec_func).pack(side='left')

add_button_row("Jump Strength", lambda: change_jump(-2), lambda: change_jump(2))
add_button_row("Obstacle Size", lambda: change_obstacle(5), lambda: change_obstacle(-5))
add_button_row("Speed Multiplier", lambda: change_speed(0.1), lambda: change_speed(-0.1))
add_button_row("Dino Color", lambda: cycle_color(1), lambda: cycle_color(-1))

# The window that can show the change of code
code_window = tk.Toplevel()
code_window.title("Live Code View")
code_window.protocol("WM_DELETE_WINDOW", on_close_all)
code_text = tk.Text(code_window, height=15, width=60)
code_text.pack()
update_code_window()

# Start game
game_thread = Thread(target=run_game)
game_thread.start()

# Continue to run the game until it end
root.mainloop()
exit_event.set()