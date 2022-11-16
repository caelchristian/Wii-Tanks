"""
Tanks.py contains constants and classes used for the Tanks Game
"""

from enum import Enum
import arcade
import numpy as np
import random

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
PLAYER_TRACK_COOLDOWN = 0.3
MINE_EXPLODE_TIME = 10
MAX_RICOCHETS = 2
MOVE_COOLDOWN = .5
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
        self.track_cooldown = PLAYER_TRACK_COOLDOWN
        self.can_track = False


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
        self.move_cooldown = MOVE_COOLDOWN
        self.move_rand_int = 0

    
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
    
    def move(self, physics_engine, barrier_list, player_position, obstacle_list):
        if(self.difficulty == Difficulty.EASY):
            # EASY tanks do not move
            pass
        elif(self.difficulty == Difficulty.MEDIUM):
            #TODO: Random movement for medium
            
            if self.move_cooldown < 0:
                self.move_rand_int = random.randint(1,5)
                self.move_cooldown = MOVE_COOLDOWN
                
                if arcade.check_for_collision_with_list(self,obstacle_list):
                    # tank is most likely hitting wall, change x or y direction
                    self.move_rand_int = {1 : 2, 2 : 1, 3 : 4, 4 : 3, 5: 5}[self.move_rand_int]
                
            # move up
            if self.move_rand_int == 1:
                physics_engine.apply_force(self, (0, 500))
            # move down
            if self.move_rand_int == 2:
                physics_engine.apply_force(self, (0, -500))
            # move left
            if self.move_rand_int == 3:
                physics_engine.apply_force(self, (-500, 0))
            # move right
            if self.move_rand_int == 4:
                physics_engine.apply_force(self, (500, 0))
                
        elif(self.difficulty == Difficulty.HARD):
            if self.path is None or self.path == [] or self.path_idx > len(self.path) - 1:
                self.path_idx = 0
                self.path = arcade.astar_calculate_path(self.position,
                                                player_position,
                                                barrier_list,
                                                diagonal_movement=False)
            



            # Keep path the same until you reach the end
            # If we are "at" the first element in the list
            # Go to the next one, keep track of which path idx we at
            if self.path is None:
                pass
            else:
                x, y = self.path[self.path_idx]
                
                x_diff = self.center_x - x
                y_diff = self.center_y - y
                if(abs(x_diff) < 10 and abs(y_diff) < 10):
                    self.path_idx += 1
                else:

                    if(abs(x_diff) >= 10):
                        if x_diff > 0:
                            physics_engine.apply_force(self, (-500, 0))
                        else:
                            physics_engine.apply_force(self, (500, 0))
                    else:
                        if y_diff > 0:
                            physics_engine.apply_force(self, (0, -500))
                        else:
                            physics_engine.apply_force(self, (0, 500))

            
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
        super().__init__(bullet_image, scale, hit_box_algorithm=None)
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
        super().__init__(image_source, scale, hit_box_algorithm=None)
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






        
        