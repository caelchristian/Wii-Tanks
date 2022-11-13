"""
Tanks.py contains constants and classes used for the Tanks Game
"""

from enum import Enum
import arcade
import numpy as np

# Constants
SCREEN_WIDTH = 1120
SCREEN_HEIGHT = 840
SCREEN_TITLE = "Tank Game"
EXPLOSION_TEXTURE_COUNT = 60
PLAYER_MOVE_FORCE = 1500
BULLET_MOVE_FORCE = 8000
PLAYER_SHOOT_COOLDOWN = 1
EASY_ENEMY_SHOOT_COOLDOWN = 7
MEDIUM_ENEMY_SHOOT_COOLDOWN = 5
HARD_ENEMY_SHOOT_COOLDOWN = 3 
MINE_EXPLODE_TIME = 10
MAX_RICOCHETS = 2
EXPLODED_TANK_IMAGE = "assets/barricadeMetal.png"
ENEMY_TANK_BARREL = "assets/tankBlack_barrel_rotate.png"

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

class PlayerTank(arcade.Sprite):
    """
    Player Tank Class. Inherits from arcade.Sprite to allow setting textures
    """
    def __init__(self, tank_image, turret_image, scale=1):
        super().__init__(tank_image, scale, hit_box_algorithm="Simple")
        self.turret = arcade.Sprite(turret_image, scale)
        self.exploded = arcade.Sprite(EXPLODED_TANK_IMAGE, scale)
        self.target_x = 0
        self.target_y = 0
        self.can_shoot = False
        self.cooldown = PLAYER_SHOOT_COOLDOWN


    def update(self):
        """
        Updates the Player Tank sprite 
        """
        
        # Turret always stays with the tank
        self.turret.center_x = self.center_x
        self.turret.center_y = self.center_y

        # Turret always points towards the mouse
        width = (self.target_x - self.center_x) 
        height = (self.target_y - self.center_y)
        if width > 0:
            self.turret.angle = np.degrees(np.arctan(height / width)) + 90
        elif width < 0:
            self.turret.angle = np.degrees(np.arctan(height / width)) + 270
            
class EnemyTank(arcade.Sprite):
    """ 
    Parent class of all enemy tanks. Inherits from arcade.Sprite to allow setting textures
    """
    
    def __init__(self, tank_image, difficulty, cooldown, scale=1):
        super().__init__(tank_image, scale, hit_box_algorithm="Simple")
        self.turret = arcade.Sprite(ENEMY_TANK_BARREL, scale)
        self.exploded = arcade.Sprite(EXPLODED_TANK_IMAGE, scale)
        self.player_x = 0
        self.player_y = 0
        self.path = []
        self.path_idx = 0
        self.difficulty = difficulty
        self.can_shoot = False
        self.cooldown = cooldown

    
    def update(self):
        """ Move the turret to point at player tank.
        """
        
        # Turret always stays with the tank
        self.turret.center_x = self.center_x
        self.turret.center_y = self.center_y

        # Invisible exploded sprite always stays with the tank
        self.exploded.center_x = self.center_x
        self.exploded.center_y = self.center_y

        # Turret always points towards the player
        width = (self.player_x - self.center_x) 
        height = (self.player_y - self.center_y)
        if width > 0:
            self.turret.angle = np.degrees(np.arctan(height / width)) + 90
        elif width < 0:
            self.turret.angle = np.degrees(np.arctan(height / width)) + 270
    
    def move(self):
        if(self.difficulty == Difficulty.EASY):
            self.cooldown = EASY_ENEMY_SHOOT_COOLDOWN
        elif(self.difficulty == Difficulty.MEDIUM):
            self.cooldown = MEDIUM_ENEMY_SHOOT_COOLDOWN
        elif(self.difficulty == Difficulty.HARD):
            self.cooldown = HARD_ENEMY_SHOOT_COOLDOWN

            
class Explosion(arcade.Sprite):
    """ 
    Class for explosions. Inherits from arcade.Sprite to allow setting textures
    """
    def __init__(self, texture_list):
        super().__init__()

        # Start at the first frame
        self.current_texture = 0
        self.textures = texture_list


    def update(self):

        # Update to the next frame of the animation. If we are at the end
        # of our frames, then delete this sprite.
        self.current_texture += 1
        if self.current_texture < len(self.textures):
            self.set_texture(self.current_texture)
        else:
            self.remove_from_sprite_lists()

class Bullet(arcade.Sprite):
    """
    Bullet class. Inherits from arcade.Sprite to allow setting textures
    """
    def __init__(self, bullet_image, scale=1):
        super().__init__(bullet_image, scale, hit_box_algorithm="Simple")
        self.num_ricochets = 0

    # Remove the bullet sprite if it has bounced too many times
    def update(self):
        if self.num_ricochets > MAX_RICOCHETS:
            self.remove_from_sprite_lists()

class Obstacle(arcade.Sprite):
    """ 
    Class for the obstacles. 
    """
    def __init__(self, image_source, scale=1, explodable=False):
        """Constructor for the Obstacle class

        Args:
            image_source (str): file path of the sprite image
            scale (int, optional): scales the sprite. Defaults to 1.
        """
        super().__init__(image_source, scale, hit_box_algorithm="Simple")
        self.explodable = explodable


class Mine(arcade.Sprite):
    """ 
    Class for the mines.
    """

    def __init__(self, image_source, scale=1):
        """Constructor for the Mine class

        Args:
            image_source (str): file path of the sprite image
            scale (int, optional): scales the sprite. Defaults to 1.
        """
        super().__init__(image_source, scale)
        self.total_time = 0
        self.end_time = MINE_EXPLODE_TIME

    def timer(self, delta_time):
        self.total_time += delta_time
        return self.total_time






        
        