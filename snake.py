"""Snake implemented with pyxel.

This is the game of snake in pyxel version!

Try and collect the tasty apples without running
into the side or yourself.

Controls are the arrow keys ← ↑ → ↓

Q: Quit the game
R: Restart the game

Created by Marcus Croucher in 2018.
Updated By Tarkorr in 2022.
"""

from collections import namedtuple, deque
from random import randint
import pyxel

Point = namedtuple("Point", ["x", "y"])  # Convenience class for coordinates

#############
# Constants #
#############

WIDTH = 40
HEIGHT = 50

TEXT_DEATH = ["GAME OVER", "(Q)UIT", "(R)ESTART"]
HEIGHT_SCORE = pyxel.FONT_HEIGHT
HEIGHT_DEATH = 5

UP = Point(0, -1)
DOWN = Point(0, 1)
RIGHT = Point(1, 0)
LEFT = Point(-1, 0)

START = Point(5, 5 + HEIGHT_SCORE)

###################
# The game itself #
###################


class Snake:
    """The class that sets up and runs the game."""

    def __init__(self):
        """Initiate pyxel, set up initial game variables, and run."""

        pyxel.init(WIDTH, HEIGHT, fps=10, quit_key=pyxel.KEY_Q, title="Snake !")
        self.music = Music()
        self.col = Colors()
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        """Initiate key variables (direction, snake, apple, score, etc.)"""

        self.direction = RIGHT
        self.snake = deque()
        self.snake.append(START)
        self.death = False
        self.score = 0
        self.generate_apple()
        self.music.start_music()

    ##############
    # Game logic #
    ##############

    def update(self):
        """Update logic of game. Updates the snake and checks for scoring/win condition."""

        if not self.death:
            self.update_direction()
            self.update_snake()
            self.check_death()
            self.check_apple()

        if pyxel.btn(pyxel.KEY_Q):
            pyxel.quit()

        if pyxel.btnp(pyxel.KEY_R):
            self.reset()
            
        if pyxel.btnp(pyxel.KEY_T):
            self.snake.append(self.popped_point)
            self.score += 1

    def update_direction(self):
        """Watch the keys and change direction."""

        if   pyxel.btn(pyxel.KEY_UP)    and self.direction is not DOWN:  self.direction = UP
        elif pyxel.btn(pyxel.KEY_DOWN)  and self.direction is not UP:    self.direction = DOWN
        elif pyxel.btn(pyxel.KEY_LEFT)  and self.direction is not RIGHT: self.direction = LEFT
        elif pyxel.btn(pyxel.KEY_RIGHT) and self.direction is not LEFT:  self.direction = RIGHT 

    def update_snake(self):
        """Move the snake based on the direction."""

        old_head = self.snake[0]
        new_head = Point(old_head.x + self.direction.x, old_head.y + self.direction.y)
        self.snake.appendleft(new_head)
        self.popped_point = self.snake.pop()

    def check_apple(self):
        """Check whether the snake is on an apple."""

        if self.snake[0] == self.apple:
            self.score += 1
            self.music.sfx_apple()
            self.snake.append(self.popped_point)
            self.generate_apple()

    def generate_apple(self):
        """Generate an apple randomly."""
        snake_pixels = set(self.snake)

        self.apple = self.snake[0]
        while self.apple in snake_pixels:
            x = randint(0, WIDTH - 1)
            y = randint(HEIGHT_SCORE + 1, HEIGHT - 1)
            self.apple = Point(x, y)

    def check_death(self):
        """Check whether the snake has died (out of bounds or doubled up.)"""

        head = self.snake[0]
        if head.x < 0 or head.y <= HEIGHT_SCORE or head.x >= WIDTH or head.y >= HEIGHT:
            self.death_event()
        elif len(self.snake) != len(set(self.snake)):
            self.death_event()

    def death_event(self):
        """Kill the game (bring up end screen)."""
        self.music.sfx_death()
        self.music.stop_music()
        self.death = True  # Check having run into self

    ##############
    # Draw logic #
    ##############

    def draw(self):
        """Draw the background, snake, score, and apple OR the end screen."""

        if not self.death:
            self.draw_background()
            self.draw_snake()
            self.draw_score()
            pyxel.rect(self.apple.x, self.apple.y, 1, 1, col=self.col.apple_color)

        else:
            self.draw_death()
    
    def draw_background(self):
        for x in range(WIDTH + 1):
            for y in range(HEIGHT + 1):
                pyxel.rect(x, y, 1, 1, self.col.background1_color if (x-y)%2==0 else self.col.background2_color)
    
    def draw_snake(self):
        """Draw the snake with a distinct head by iterating through deque."""

        for i, point in enumerate(self.snake):
            if i == 0:
                colour = self.col.head_color
            else:
                colour = self.col.body_color
            pyxel.rect(point.x, point.y, 1, 1, col=colour)

    def draw_score(self):
        """Draw the score at the top."""

        score = "{:04}".format(self.score)
        pyxel.rect(0, 0, WIDTH, HEIGHT_SCORE + 1, self.col.background_score_color)
        pyxel.text(1, 1, score, self.col.score_color_fade)
        pyxel.text(0, 1, score, self.col.score_color)
        

    def draw_death(self):
        """Draw a blank screen with some text."""

        pyxel.cls(col=self.col.death_color)
        display_text = TEXT_DEATH[:]
        display_text.insert(1, "{:04}".format(self.score))
        for i, text in enumerate(display_text):
            y_offset = (pyxel.FONT_HEIGHT + 2) * i
            text_x = self.center_text(text, WIDTH)
            pyxel.text(text_x+1, HEIGHT_DEATH + y_offset, text,self.col.death_text_color_fade)
            pyxel.text(text_x, HEIGHT_DEATH + y_offset, text, self.col.death_text_color)

    @staticmethod
    def center_text(text, page_width, char_width=pyxel.FONT_WIDTH):
        """Helper function for calcuating the start x value for centered text."""
        
        text_width = len(text) * char_width
        return (page_width - text_width) // 2


###########################
# Music and sound effects #
###########################

class Colors:
    def __init__(self):
        pyxel.colors[0] = 0x0F3A00  # head_snake
        pyxel.colors[1] = 0x1D5200  # body_snake
        pyxel.colors[2] = 0xB81800  # apple
        pyxel.colors[3] = 0x81dc4a  # background_1
        pyxel.colors[4] = 0x63c02e  # background_2
        pyxel.colors[5] = 0x5DF1FF  # score_txt
        pyxel.colors[6] = 0x00b2ff  # score_bg
        pyxel.colors[7] = 0x554244  # GameOver_txt
        pyxel.colors[8] = 0x3c2c2e  # GameOver_bg
        pyxel.colors[9] = 0x008cb1  # score_txt_fade
        pyxel.colors[10] = 0x271811 # GameOver_txt_fade
        
        self.head_color = 0
        self.body_color = 1
        
        self.apple_color = 2
        self.background1_color = 3
        self.background2_color = 4
        
        self.score_color = 5
        self.score_color_fade = 9
        self.background_score_color = 6
        
        self.death_text_color = 7
        self.death_text_color_fade = 10
        self.death_color = 8

class Music:
    def __init__(self):
        """Define sound and music."""

        # Sound effects
        pyxel.sound(0).set(
            notes="c3e3g3c4c4",
            tones="s",
            volumes="4",
            effects=("n" * 4 + "f"),
            speed=7
        )
        pyxel.sound(1).set(
            notes="f3 b2 f2 b1  f1 f1 f1 f1",
            tones="p",
            volumes=("4" * 4 + "4321"),
            effects=("n" * 7 + "f"),
            speed=9
        )

        melody1 = (
            "c3 c3 c3 d3 e3 r e3 r"
            + ("r" * 8)
            + "e3 e3 e3 f3 d3 r c3 r"
            + ("r" * 8)
            + "c3 c3 c3 d3 e3 r e3 r"
            + ("r" * 8)
            + "b2 b2 b2 f3 d3 r c3 r"
            + ("r" * 8)
        )

        melody2 = (
            "rrrr e3e3e3e3 d3d3c3c3 b2b2c3c3"
            + "a2a2a2a2 c3c3c3c3 d3d3d3d3 e3e3e3e3"
            + "rrrr e3e3e3e3 d3d3c3c3 b2b2c3c3"
            + "a2a2a2a2 g2g2g2g2 c3c3c3c3 g2g2a2a2"
            + "rrrr e3e3e3e3 d3d3c3c3 b2b2c3c3"
            + "a2a2a2a2 c3c3c3c3 d3d3d3d3 e3e3e3e3"
            + "f3f3f3a3 a3a3a3a3 g3g3g3b3 b3b3b3b3"
            + "b3b3b3b4 rrrr e3d3c3g3 a2g2e2d2"
        )

        # Music
        pyxel.sound(2).set(
            notes=melody1 * 2 + melody2 * 2,
            tones="s",
            volumes=("3"),
            effects=("nnnsffff"),
            speed=20,
        )

        harmony1 = (
            "a1 a1 a1 b1  f1 f1 c2 c2"
            "c2 c2 c2 c2  g1 g1 b1 b1" * 3
            + "f1 f1 f1 f1 f1 f1 f1 f1 g1 g1 g1 g1 g1 g1 g1 g1"
        )
        harmony2 = (
            ("f1" * 8 + "g1" * 8 + "a1" * 8 + ("c2" * 7 + "d2")) * 3
            + "f1" * 16
            + "g1" * 16
        )

        pyxel.sound(3).set(
            notes=harmony1 * 2 + harmony2 * 2,
            tones="t", 
            volumes="5", 
            effects="f", 
            speed=20
        )
        pyxel.sound(4).set(
            notes=("f0 r a4 r  f0 f0 a4 r" "f0 r a4 r   f0 f0 a4 f0"),
            tones="n",
            volumes="6622 6622 6622 6426",
            effects="f",
            speed=20,
        )

    def sfx_apple(self):
        """Play apple collection sound."""
        pyxel.play(ch=0, snd=0)

    def sfx_death(self):
        """Play death collection sound."""
        pyxel.play(ch=0, snd=1)

    def start_music(self):
        """Start all music tracks (channels 1 - 3)."""
        music_tracks = [2, 3, 4]
        for ch, snd in enumerate(music_tracks):
            pyxel.play(ch=(ch + 1), snd=snd, loop=True)

    def stop_music(self):
        """Stop all music tracks (channels 1 - 3)."""
        for ch in range(1,4):
            pyxel.stop(ch=ch)


if __name__ == "__main__":
    Snake()
