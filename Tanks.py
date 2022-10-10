import arcade
import numpy as np

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class Player(arcade.Sprite):
    """ Player Class """

    def update(self):
        """ Move the player """
        # Move player.
        # Remove these lines if physics engine is moving player.
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1

class Turret(arcade.Sprite):
    """ Turret Class """
    def __init__(self, image_source, scale=1):
        super().__init__(image_source, scale, hit_box_algorithm="None")
        self.target_x = 0
        self.target_y = 0

    def update(self):
        """ Move the turret """
        # Remove these lines if physics engine is moving player.
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1
        
        # Turret follows mouse
        width = (self.target_x - self.center_x) 
        height = (self.target_y - self.center_y)
        if width > 0:
            self.angle = np.degrees(np.arctan(height / width)) + 270
        elif width < 0:
            self.angle = np.degrees(np.arctan(height / width)) + 90