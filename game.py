import pygame
import sys
import random

# --- Game Settings ---
GRAVITY = 1.0
JUMP_STRENGTH = -22.5  # Changed to 0.9 of the previous jump strength
OBSTACLE_SIZE = [40, 160]  # Doubled the width and height of the obstacle
SPEED_MULTIPLIER = 1.0
CHARACTER_IMAGE_PATH = "/mnt/c/workspace/OpenCampus/image/character.png"

def run_game():
    global GRAVITY, JUMP_STRENGTH, OBSTACLE_SIZE, SPEED_MULTIPLIER

    pygame.init()
    screen = pygame.display.set_mode((800, 300))
    pygame.display.set_caption("Dino Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    # Load character image
    try:
        character_img = pygame.image.load(CHARACTER_IMAGE_PATH).convert_alpha()
        character_img = pygame.transform.scale(character_img, (80, 80))  # Doubled the size
    except Exception as e:
        print(f"Error loading character image: {e}")
        pygame.quit()
        sys.exit()

    paused = False

    def reset_game():
        return {
            "dino": pygame.Rect(50, 220, 80, 80),  # Adjusted the y position for the new size
            "vel_y": 0,
            "on_ground": True,
            "obstacles": [],
            "spawn_timer": 0,
            "score": 0,
            "speed": 5 * SPEED_MULTIPLIER,
            "speed_multiplier": SPEED_MULTIPLIER,
            "game_over": False,
            "obstacle_frequency": random.uniform(0.5, 2.0) * 90
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
            if state["score"] < 1000:
                screen.fill((255, 255, 255))
                obstacle_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                score_color = (0, 0, 0)
            else:
                screen.fill((0, 0, 0))
                obstacle_color = (255, 255, 255)
                score_color = (255, 255, 255)

            if not state["game_over"]:
                state["vel_y"] += GRAVITY
                state["dino"].y += int(state["vel_y"])
                if state["dino"].y >= 220:  # Adjusted for new size
                    state["dino"].y = 220
                    state["vel_y"] = 0
                    state["on_ground"] = True

                state["spawn_timer"] += 1
                if state["spawn_timer"] > state["obstacle_frequency"]:
                    state["spawn_timer"] = 0
                    obs_w = OBSTACLE_SIZE[0]
                    obs_h = OBSTACLE_SIZE[1] if state["score"] < 1000 else int(OBSTACLE_SIZE[1] * 1.65)
                    state["obstacles"].append((pygame.Rect(800, 300 - obs_h, obs_w, obs_h), obstacle_color))

                new_obstacles = []
                for obs, color in state["obstacles"]:
                    obs.x -= int(state["speed"])
                    if obs.x + obs.width > 0:
                        new_obstacles.append((obs, color))
                    pygame.draw.rect(screen, color, obs)
                state["obstacles"] = new_obstacles

                for obs, _ in state["obstacles"]:
                    if state["dino"].colliderect(obs):
                        state["game_over"] = True

                state["score"] += 1
                if state["score"] % 100 == 0:
                    state["speed"] *= 1.1
                    state["speed_multiplier"] *= 1.1

                if state["score"] >= 1000:
                    JUMP_STRENGTH = JUMP_STRENGTH * 1.5
                    SPEED_MULTIPLIER = 1.5
                    msg = font.render("Hard Mode On", True, (255, 165, 0))
                    screen.blit(msg, (300, 10))

            # Draw character image instead of a circle
            screen.blit(character_img, state["dino"])

            score_text = font.render(f"Score: {state['score']}", True, score_color)
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