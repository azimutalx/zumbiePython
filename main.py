import pgzrun
import random
import os

# Centralize the game window on the monitor
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Game screen size
WIDTH = 800
HEIGHT = 600
FPS_BAT = 5
FPS_ZOMBIE = 1

# Colors
BLACK = (0, 0, 0)
BROWN = (71, 34, 18)
RED = (212, 47, 47)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Game states
game_started = False  # The game starts in the menu
sound_on = True  # The sound is on by default

# Load music
sounds.background.set_volume(0.3)  # Set initial volume for the background music
sounds.background.play()  # Play background music

# Menu button positions
start_button_pos = (400, 300)
toggle_sound_button_pos = (400, 400)
exit_button_pos = (400, 500)


class Moon:
    """Moon class for the sky decoration."""
    def __init__(self):
        self.actor = Actor('moon200')
        self.actor.pos = (680, 120)

    def draw(self):
        self.actor.draw()


class HauntedHouse:
    """HauntedHouse class for houses in the background."""
    def __init__(self):
        self.actor = Actor('houses300')
        self.actor.pos = (400, 350)

    def draw(self):
        self.actor.draw()


class Ghost:
    """Ghost class for the floating ghosts."""
    def __init__(self):
        self.actor = Actor('ghost100')
        self.actor.pos = (900, 250)

    def update(self):
        self.actor.x -= 5
        if self.actor.x < -50:
            self.actor.x = random.randint(900, 5000)
            self.actor.y = random.randint(150, 350)

    def draw(self):
        self.actor.draw()


class Bat:
    """Bat class for the flying bats."""
    def __init__(self):
        self.actor = Actor('bat1')
        self.actor.pos = (900, 200)
        self.images = ['bat1', 'bat2', 'bat3', 'bat4']
        self.image_index = 0
        self.animation_timeout = 0  # To control the animation
        self.descending = False

    def animate(self):
        self.actor.image = self.images[self.image_index]
        self.image_index = (self.image_index + 1) % len(self.images)

    def update(self, obstacles):
        self.actor.left += random.randint(-1, 1)
        self.actor.top += random.randint(-1, 1)
        self.actor.x -= 5  # Increase basic speed

        if self.actor.x < -50:
            self.actor.x = random.randint(1000, 1500)
            self.actor.y = random.randint(100, 250)
            self.descending = False

        # Check if the bat should descend
        if self.actor.x in [600, 550] and not self.descending:
            if not any(abs(self.actor.x - spike.actor.x) < 100 for spike in obstacles):
                self.descending = True

        if self.descending:
            self.actor.y += 5
            if self.actor.y >= 480:  # Ensure the bat stays at y position 480 or 490
                self.actor.y = random.choice([480, 490])
                self.descending = False

        # Accelerate when at y position 480 or 490
        if self.actor.y in [480, 490]:
            self.actor.x -= 10  # Increase acceleration speed

        # Control the animation
        self.animation_timeout += 1
        if self.animation_timeout > FPS_BAT:
            self.animate()
            self.animation_timeout = 0

    def draw(self):
        self.actor.draw()


class Zombie:
    """Zombie class for the player character."""
    def __init__(self):
        self.actor = Actor('walk1')
        self.actor.pos = (100, 470)
        self.images = ['walk1', 'walk2', 'walk3', 'walk4', 'walk5', 'walk6', 'walk7', 'walk8', 'walk9', 'walk10']
        self.image_index = 0
        self.velocity = 0
        self.gravity = 1
        self.animation_timeout = 0  # To control the animation

    def animate(self):
        self.actor.image = self.images[self.image_index]
        self.image_index = (self.image_index + 1) % len(self.images)

    def update(self):
        if keyboard.up and self.actor.y == 470:
            self.velocity = -18
            if sound_on:
                sounds.jump.play()  # Play jump sound when the zombie jumps
        self.actor.y += self.velocity
        self.velocity += self.gravity

        if self.actor.y > 470:
            self.actor.y = 470
            self.velocity = 0

        # Control the animation
        self.animation_timeout += 1
        if self.animation_timeout > FPS_ZOMBIE:
            self.animate()
            self.animation_timeout = 0

    def draw(self):
        self.actor.draw()


class Spike:
    """Spike class for obstacles."""
    def __init__(self):
        self.actor = Actor('spikes70x70')
        self.actor.pos = (900, 475)

    def update(self):
        self.actor.x -= 8

    def draw(self):
        self.actor.draw()


class Game:
    """Game class for managing the game logic."""
    def __init__(self):
        self.moon = Moon()
        self.houses = HauntedHouse()
        self.ghosts = Ghost()
        self.bat = Bat()
        self.zombie = Zombie()
        self.obstacles = []
        self.obstacles_timeout = 0
        self.score = 0
        self.game_over = False

    def update(self):
        if not self.game_over:
            self.zombie.update()
            self.bat.update(self.obstacles)
            self.ghosts.update()
            self.obstacles_timeout += 1

            if self.obstacles_timeout > random.randint(60, 7000):
                spike = Spike()
                self.obstacles.append(spike)
                self.obstacles_timeout = 0

            for spike in self.obstacles:
                spike.update()
                if self.zombie.actor.colliderect(spike.actor):
                    self.game_over = True
                    if sound_on:
                        sounds.gameover.play()

            if self.zombie.actor.colliderect(self.ghosts.actor):
                if sound_on:
                    sounds.collect.play()
                self.ghosts.actor.pos = (random.randint(900, 5000), random.randint(150, 350))
                self.score += 10  # Increase score by 10 points

            if self.zombie.actor.colliderect(self.bat.actor):
                self.score -= 5
                if sound_on:
                    sounds.damage.play()  # Play damage sound when the bat collides with the zombie
                self.bat.actor.pos = (random.randint(1000, 1500), random.randint(100, 250))
                self.bat.descending = False

    def draw(self):
        screen.clear()
        screen.draw.filled_rect(Rect(0, 0, WIDTH, 500), BLACK)
        screen.draw.filled_rect(Rect(0, 500, WIDTH, HEIGHT), BROWN)

        if self.game_over:
            screen.fill((0, 0, 0))
            screen.draw.text("Game Over", (200, 200), color=RED, fontname='creepster', fontsize=100)
            screen.draw.text(f"Score: {self.score}", (300, 300), color=WHITE, fontname='creepster', fontsize=60)
            screen.draw.text("Press Enter or Space to return to the menu", (80, 400), color=WHITE, fontname='creepster', fontsize=40)
        else:
            self.moon.draw()
            self.houses.draw()
            self.bat.draw()
            self.zombie.draw()
            self.ghosts.draw()
            screen.draw.text(f"Score: {self.score}", (20, 20), color=RED, fontname='creepster', fontsize=60)
            for spike in self.obstacles:
                spike.draw()


# Create the game object
game = Game()


def start_game():
    """Start the game."""
    global game_started
    game_started = True


def toggle_sound():
    """Switch between sound on and off."""
    global sound_on
    sound_on = not sound_on
    if sound_on:
        sounds.background.set_volume(0.3)  # Set the volume back on
        sounds.background.play()  # Ensure the music is playing
    else:
        sounds.background.stop()  # Stop the music


def exit_game():
    """Close the game."""
    exit()


def reset_game():
    """Reset the game and return to the main menu after Game Over."""
    global game, game_started
    game = Game()  # Recreate the game object to restart the game
    game_started = False  # Return to the main menu


def update():
    """Main update function."""
    if game_started:
        if not game.game_over:
            game.update()
        elif game.game_over and (keyboard.RETURN or keyboard.SPACE):
            reset_game()  # Reset the game and return to the menu when Enter or Space is pressed


def draw():
    """Main draw function."""
    if not game_started:
        # Draw the initial menu
        screen.clear()
        screen.fill((0, 0, 0))
        bg_image = Actor('zombie')
        bg_image.pos = (400, 300)

        # Draw the menu background
        bg_image.draw()

        # Draw the button texts
        screen.draw.text("Play", start_button_pos, color=RED, fontname='creepster', fontsize=60, anchor=(0.5, 0.5))
        screen.draw.text("Sound: ON" if sound_on else "Sound: OFF", toggle_sound_button_pos, color=RED, fontname='creepster', fontsize=40, anchor=(0.5, 0.5))
        screen.draw.text("Exit", exit_button_pos, color=RED, fontname='creepster', fontsize=60, anchor=(0.5, 0.5))
    else:
        # Draw the game if it has started
        game.draw()


def on_mouse_down(pos):
    """Handle mouse clicks for menu buttons."""
    if (start_button_pos[0] - 50 < pos[0] < start_button_pos[0] + 50 and
            start_button_pos[1] - 30 < pos[1] < start_button_pos[1] + 30):
        start_game()  # Start the game
    elif (toggle_sound_button_pos[0] - 50 < pos[0] < toggle_sound_button_pos[0] + 50 and
          toggle_sound_button_pos[1] - 30 < pos[1] < toggle_sound_button_pos[1] + 30):
        toggle_sound()  # Toggle the sound
    elif (exit_button_pos[0] - 50 < pos[0] < exit_button_pos[0] + 50 and
          exit_button_pos[1] - 30 < pos[1] < exit_button_pos[1] + 30):
        exit_game()  # Exit the game


# Bind events to Pygame Zero
pgzrun.go()