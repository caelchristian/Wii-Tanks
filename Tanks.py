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
EXPLOSION_TEXTURE_COUNT = 60
PLAYER_MOVE_FORCE = 1500
ENEMY_MOVE_FORCE = 500
BULLET_MOVE_FORCE = 8000
PLAYER_SHOOT_COOLDOWN = 1
PLAYER_MINE_COOLDOWN = 5
EASY_ENEMY_SHOOT_COOLDOWN = 7
MEDIUM_ENEMY_SHOOT_COOLDOWN = 5
HARD_ENEMY_SHOOT_COOLDOWN = 3 
ENEMY_REACTION_TIME = 2
PLAYER_TRACK_COOLDOWN = 0.3
MOVE_COOLDOWN = 1
MINE_EXPLODE_TIME = 3
MAX_RICOCHETS = 2
END_LEVEL_TIME = 2
SCREEN_TITLE = "Tank Game"
EXPLODED_TANK_IMAGE = "assets/barricadeMetal.png"
ENEMY_TANK_BARREL = "assets/tankBlack_barrel_rotate.png"

class Difficulty(Enum):
    """ Enum type for difficulty of enemy tanks
    """
    EASY = 1
    MEDIUM = 2
    HARD = 3

class Direction(Enum):
    """ Enum type for the direction of sprites
    """
    DOWN = 0
    LEFT = 1
    UP = 2
    RIGHT = 3

class PlayerTank(arcade.Sprite):
    """ Class for the Player's Tank
    """
    def __init__(self, tank_image, turret_image, scale=1):
        """ Constructor for Player tank class

        Args:
            tank_image (str): Image path for the tank body
            turret_image (str): Image path for the tank turret
            scale (int, optional): Sprite scale factor. Defaults to 1.
        """
        super().__init__(tank_image, scale, hit_box_algorithm="Simple")
        self.turret = arcade.Sprite(turret_image, scale)
        self.exploded = arcade.Sprite(EXPLODED_TANK_IMAGE, scale)
        self.target_x = 0
        self.target_y = 0
        self.can_shoot = True
        self.can_track = True
        self.can_mine = True
        self.cooldown = PLAYER_SHOOT_COOLDOWN
        self.track_cooldown = PLAYER_TRACK_COOLDOWN
        self.mine_cooldown = PLAYER_MINE_COOLDOWN

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
    """  Class for all Enemy (computer) tanks
    """
    def __init__(self, tank_image, difficulty, cooldown, scale=1):
        """ Constructor for the Enemy tanks

        Args:
            tank_image (str): Image path for the tank body
            difficulty (str): Image path for the tank turret
            cooldown (str): The cooldown for how often the tank can shoot
            scale (int, optional): Sprite scale factor. Defaults to 1.
        """
        super().__init__(tank_image + "1.png", scale, hit_box_algorithm="Simple")
        self.texture_list = [arcade.load_texture(f"{tank_image}{i}.png") for i in range(4)]
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
        self.reaction_time = ENEMY_REACTION_TIME
        self.direction = 0

    def update(self):
        """ Update the enemy tank
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
        """ Moves the enemy tank based on its difficulty

        Args:
            physics_engine: The PyMonk physics engine
            barrier_list: The AStar Barrier List of blocking objects
            player_position: The position of the player
            obstacle_list: List of blocking sprites
        """
        if self.difficulty == Difficulty.EASY:
            # Easy tanks do not move
            pass
        else:
            # Calculate path to player tank
            if self.difficulty == Difficulty.HARD and (self.path is None or self.path == [] or self.path_idx > len(self.path) - 1):
                self.path_idx = 0
                self.path = arcade.astar_calculate_path(self.position,
                                                player_position,
                                                barrier_list,
                                                diagonal_movement=False)
            
            if self.difficulty == Difficulty.MEDIUM or self.path is None:
                # Medium tanks move randomly always
                # Hard tanks move randomly if they fail to find a path to the player
                if self.move_cooldown < 0:
                    self.move_rand_int = random.randint(1,5)
                    self.move_cooldown = MOVE_COOLDOWN
                    
                    if arcade.check_for_collision_with_list(self,obstacle_list):
                        # Tank is most likely hitting wall, change x or y direction to move the opposite way
                        self.move_rand_int = {1 : 2, 2 : 1, 3 : 4, 4 : 3, 5: 5}[self.move_rand_int]
                    
                # Move up, down, left or right based on the random int
                if self.move_rand_int == 1:
                    physics_engine.apply_force(self, (0, ENEMY_MOVE_FORCE))
                    self.texture = self.texture_list[Direction.UP.value]
                    self.direction = Direction.UP
                elif self.move_rand_int == 2:
                    physics_engine.apply_force(self, (0, -ENEMY_MOVE_FORCE))
                    self.texture = self.texture_list[Direction.DOWN.value]
                    self.direction = Direction.DOWN
                elif self.move_rand_int == 3:
                    physics_engine.apply_force(self, (-ENEMY_MOVE_FORCE, 0))
                    self.texture = self.texture_list[Direction.LEFT.value]
                    self.direction = Direction.LEFT
                elif self.move_rand_int == 4:
                    physics_engine.apply_force(self, (ENEMY_MOVE_FORCE, 0))
                    self.texture = self.texture_list[Direction.RIGHT.value]
                    self.direction = Direction.RIGHT
                else:
                    # Random chance to not move at all
                    pass
            else:
                # Hard tanks follow the AStar path
                x, y = self.path[self.path_idx]
                
                x_diff = self.center_x - x
                y_diff = self.center_y - y

                # If we are within 10 pixels of the destination, move to next point in the path
                if abs(x_diff) < 10 and abs(y_diff) < 10:
                    self.path_idx += 1
                else:
                    # Move in the direction specified by the path
                    if abs(x_diff) >= 10:
                        if x_diff > 0:
                            physics_engine.apply_force(self, (-ENEMY_MOVE_FORCE, 0))
                            self.texture = self.texture_list[Direction.LEFT.value]
                            self.direction = Direction.LEFT
                        else:
                            physics_engine.apply_force(self, (ENEMY_MOVE_FORCE, 0))
                            self.texture = self.texture_list[Direction.RIGHT.value]
                            self.direction = Direction.RIGHT
                    else:
                        if y_diff > 0:
                            physics_engine.apply_force(self, (0, -ENEMY_MOVE_FORCE))
                            self.texture = self.texture_list[Direction.DOWN.value]
                            self.direction = Direction.DOWN
                        else:
                            physics_engine.apply_force(self, (0, ENEMY_MOVE_FORCE))
                            self.texture = self.texture_list[Direction.UP.value]
                            self.direction = Direction.UP
            
class Explosion(arcade.Sprite):
    """ 
    Class for explosions 
    """
    def __init__(self, texture_list):
        """ Constructor for the explosions

        Args:
            texture_list: List of textures for the explosion animation
        """
        super().__init__()

        # Start at the first frame of the animation
        self.current_texture = 0
        self.textures = texture_list

    def update(self):
        """ Updates the explosion sprite
        """
        # Move to the next frame of the animation. Remove the sprite once animation finishes
        self.current_texture += 1
        if self.current_texture < len(self.textures):
            self.set_texture(self.current_texture)
        else:
            self.remove_from_sprite_lists()

class Bullet(arcade.Sprite):
    """
    Class for Bullet objects
    """
    def __init__(self, bullet_image, scale=1):
        """ Constructor for Bullets

        Args:
            bullet_image (str): Image path for the bullet
            scale (int, optional): Sprite scale factor. Defaults to 1.
        """
        super().__init__(bullet_image, scale, hit_box_algorithm=None)
        self.num_ricochets = 0

    def update(self):
        """ Updates the Bullet sprite
        """
        # Remove the bullet sprite if it has bounced too many times
        if self.num_ricochets > MAX_RICOCHETS:
            self.remove_from_sprite_lists()

class Mine(arcade.Sprite):
    """ 
    Class for the mines.
    """

    def __init__(self, image_source, scale=1):
        """Constructor for the Mine class

        Args:
            image_source (str): Image path for the mine
            scale (int, optional): Sprite scale factor. Defaults to 1.
        """
        super().__init__(image_source, scale)
        self.total_time = 0
        self.end_time = MINE_EXPLODE_TIME

    def timer(self, delta_time):
        """ Updates the timer for the mine explosion

        Args:
            delta_time (float): the amount of time passes since last update

        Returns:
            float: the total time passed
        """
        self.total_time += delta_time
        return self.total_time