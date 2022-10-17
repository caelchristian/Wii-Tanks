"""
Tanks.py contains constants and classes used for the Tanks Game
"""

from enum import Enum
import arcade
import numpy as np

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Tank Game"
MOVEMENT_SPEED = 3
BULLET_SPEED = 5
EXPLOSION_TEXTURE_COUNT = 60


class Color(Enum):
    """Enum for EnemyTank class.
    Each color correlates to a different color tank.
    Depending on the color, different attributes will
    be loaded when constructing a EnemyTank.

    Args:
        Enum (enum): Color of tank.
    """
    BROWN: 1
    GREY: 2
    TEAL: 3
    YELLOW: 4
    RED: 5
    GREEN: 6
    PURPLE: 7
    WHITE: 8
    BLACK: 9

class Player(arcade.Sprite):
    """
    Player Tank Class. Inherits from arcade.Sprite to allow setting textures
    """

    def update(self):
        """
        Updates the Player Tank sprite 
        """
        # Move player
        self.center_x += self.change_x
        self.center_y += self.change_y


class Turret(arcade.Sprite):
    """ 
    Player Turret (Gun) Class. Inherits from arcade.Sprite to allow setting textures
    """
    def __init__(self, image_source, scale=1):
        """Constructor for the Turret class

        Args:
            image_source (_type_): file path of the sprite image
            scale (int, optional): scales the sprite. Defaults to 1.
        """
        super().__init__(image_source, scale, hit_box_algorithm="None")
        self.target_x = 0
        self.target_y = 0

    def update(self):
        """ 
        Updates the turret sprite 
        """
        # Move the turret
        self.center_x += self.change_x
        self.center_y += self.change_y
        
        # Turret always points towards the mouse
        width = (self.target_x - self.center_x) 
        height = (self.target_y - self.center_y)
        if width > 0:
            self.angle = np.degrees(np.arctan(height / width)) + 90
        elif width < 0:
            self.angle = np.degrees(np.arctan(height / width)) + 270
            
            
class EnemyTank(arcade.Sprite):
    """ 
    Parent class of all enemy tanks. Inherits from arcade.Sprite to allow setting textures
    """
    def __init__(self, image_source, scale=1):
        """Constructor for the EnemyTank class

        Args:
            image_source (_type_): file path of the sprite image
            scale (int, optional): scales the sprite. Defaults to 1.
        """
        super().__init__(image_source, scale, hit_box_algorithm="None")
        self.target_x = 0
        self.target_y = 0

    
    def update(self):
        """ Move the turret to point at player tank.
        Eventually this will update depending on enemy tank's
        attribute's. Tanks will not be able to see through walls.
        
        Enums:
            Color: Brown, Grey, Teal, Yellow, Red, Green, Purple, White, Black
            First appearance: Mission #
            Movement: Stationary, Slow, Normal, Fast
            Behaviour: Passive, Defensive, Active, Incautious, Offensive
            Bullet speed: Slow, Normal, Fast
            Fire rate: Slow, Normal, Fast
            Max Bullets 1-5
            Max Mines: 2-4
            Ricochets: 0-2
        """
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
        
        
        # IN-PROGRESS
        # Turret follows player
        # Will look very similar to turret follows mouse logic, 
        # mouse position will be replaced with player position.
        
        # width_to_player = (self.player_sprite - self.center_x) 
        # height_to_player = (self.target_y - self.center_y)
        # if width_to_player > 0:
        #     self.angle = np.degrees(np.arctan(height_to_player / width_to_player)) + 270
        # elif height_to_player < 0:
        #     self.angle = np.degrees(np.arctan(height_to_player / width_to_player)) + 90
            
class Explosion(arcade.Sprite):
    """ 
    Class for explosions. Inherits from arcade.Sprite to allow setting textures
    """
    def __init__(self, explosion_texture_list):
        super().__init__()

        # Start at the first frame
        self.current_texture = 0
        self.textures = explosion_texture_list

    def update(self):
        # Update to the next frame
        self.current_texture += 1
        if self.current_texture < len(self.textures):
            self.set_texture(self.current_texture)
        else:
            self.remove_from_sprite_lists()