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
ENEMY_SHOOT_COOLDOWN = 5
MINE_EXPLODE_TIME = 10
MAX_RICOCHETS = 2

class PlayerTank(arcade.Sprite):
    """
    Player Tank Class. Inherits from arcade.Sprite to allow setting textures
    """
    def __init__(self, tank_image, turret_image, exploded_tank_image, scale=1):
        super().__init__(tank_image, scale, hit_box_algorithm="Simple")
        self.turret = arcade.Sprite(turret_image, scale)
        self.exploded = arcade.Sprite(exploded_tank_image, scale)
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
    
    def __init__(self, tank_image, turret_image, exploded_tank_image, scale=1):
        super().__init__(tank_image, scale, hit_box_algorithm="Simple")
        self.turret = arcade.Sprite(turret_image, scale)
        self.exploded = arcade.Sprite(exploded_tank_image, scale)
        self.player_x = 0
        self.player_y = 0
        self.can_shoot = False
        self.cooldown = ENEMY_SHOOT_COOLDOWN

    
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




        
        