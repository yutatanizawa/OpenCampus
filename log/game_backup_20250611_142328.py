import pygame
import sys

# --- Game Settings ---
GRAVITY = 1.0  # Doubled gravity
JUMP_STRENGTH = -25.0  # Doubled jump strength
OBSTACLE_SIZE = [20, 80]  # Doubled obstacle height
DINO_COLOR = (0, 0, 0)
SPEED_MULTIPLIER = 1.0

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

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not state["game_over"] and not paused:
                    if event.key == pygame.K_SPACE and state["on_ground"]:
                        state["vel_y"] = JUMP_STRENGTH
                        state["on_ground"] = False
                elif event.key == pygame.K_r:
                    state = reset_game()
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

            pygame.draw.circle(screen, DINO_COLOR, (state["dino"].x + 20, state["dino"].y + 20), 20)
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

if __name__ == "__main__":
    run_game()