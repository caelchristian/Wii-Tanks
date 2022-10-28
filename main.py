"""
CS205 Final Project
Tanks Game (modeled after Wii Play Tanks)
Authored by: Cael Christian, Levi Putman, Olivia Wilson
"""

from xml.etree.ElementInclude import include
import arcade
import Tanks
import math

class TankGame(arcade.Window):
    """
    Main class for the TankGame. Contains all necessary sprites and
    event driven functions to play the game.
    """

    def __init__(self, width: int, height: int, title: str):
        """Constructor for TankGame class

        Args:
            width (int): width of the game window
            height (int): height of the game window
            title (str): title of the game window
        """
        # Initialize super class
        super().__init__(width, height, title)

        # Set the background color
        arcade.set_background_color(arcade.color.WHEAT)

        # Initialize sprite lists to None
        self.player_list = None
        self.bullet_list = None
        self.enemy_list = None
        self.physics_engine = None
        self.obstacle_list = None
        self.exploded_tank_list = None
        
        # Sprites
        self.player_sprite = None
        self.closest_sprite = None
        
        self.scene = None

        self.explosion_texture_list = []

        columns = 5
        count = 5
        sprite_width = 130
        sprite_height = 130
        file_name = "assets/explosions_sheet.png"

        # Load the explosions from a sprite sheet
        self.explosion_texture_list = arcade.load_spritesheet(file_name, sprite_width, sprite_height, columns, count)

        

    def setup(self):
        """ 
        Setup the sprite lists and place the sprites on the screen
        """
        # Create the Sprite lists
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()
        self.obstacle_list = arcade.SpriteList()
        self.exploded_tank_list = arcade.SpriteList()
        
        # Initialize sprites
        self.player_sprite = Tanks.PlayerTank("assets/tankBody_blue.png", "assets/tankBlue_barrel_rotate.png", 1)
        self.closest_sprite = arcade.Sprite()
        
        # Add player sprite and turret to player_list
        self.player_list.append(self.player_sprite)
        self.player_list.append(self.player_sprite.turret)
        
        # Load first level
        self.load_next_level()
        
        # Collision Physics Engine blocks player from clipping through tiles
        self.obstacle_collision_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=0, walls=self.obstacle_list)
        
        
    def load_next_level(self):
        layer_options = {"Obstacles" : {"use_spatial_hash": True},
                         "Enemies" : {"use_spatial_hash": True}}
        
        # Load level and obstacles (not sure if layer options are required here but used in documentation)
        tile_map = arcade.load_tilemap("maps/level.tmx", layer_options=layer_options)

        # Loads tilemap layers into respective sprite list
        self.obstacle_list = tile_map.sprite_lists["Obstacles"]
        self.enemy_tiles = tile_map.sprite_lists["Enemies"] 
        
        # TODO: Find how to get image path from tileset
        # for now using "assets/tankBody_red.png"
        
        # Convert Sprites into EnemyTanks
        for tile in self.enemy_tiles:
            # type(arcade.tilemap.tilemap._get_image_source(tile, self.enemy_list))
            self.enemy_sprite = Tanks.EnemyTank("assets/tankBody_red.png", "assets/tankBlue_barrel_rotate.png", "assets/barricadeMetal.png", 1)
            self.enemy_sprite.center_x = tile.center_x
            self.enemy_sprite.center_y = tile.center_y
            self.enemy_sprite.angle = 180
            self.enemy_list.append(self.enemy_sprite)
            self.enemy_list.append(self.enemy_sprite.turret)
        
        self.player_sprite_list = tile_map.sprite_lists["Player"]
        
        # Create the player tank and set its coordinates
        self.player_sprite.center_x = self.player_sprite_list[0].center_x
        self.player_sprite.center_y = self.player_sprite_list[0].center_y
        self.player_sprite.angle = 180
        # self.explodables_list = tile_map.sprite_lists["Explodables"]
        
        # Set attributes for enemy tanks and player
        
        
        

    def on_draw(self):
        """
        Render the screen.
        """
        # Clear the frame to prepare for drawing sprites
        arcade.start_render()

        # Draw all sprite lists
        self.enemy_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()
        self.explosions_list.draw()
        self.obstacle_list.draw()
        self.exploded_tank_list.draw()
        

    def on_update(self, delta_time):
        """
        Updates all sprite lists and removes unnecessary sprites
        Partially from https://api.arcade.academy/en/2.6.0/examples/sprite_explosion_bitmapped.html
        """
        # Update the sprite lists
        # self.physics_engine.update()
        self.obstacle_collision_engine.update()
        self.player_list.update()
        self.bullet_list.update()
        self.enemy_list.update()
        self.explosions_list.update()
        self.exploded_tank_list.update()

        self.enemy_sprite.player_x = self.player_sprite.center_x
        self.enemy_sprite.player_y = self.player_sprite.center_y

        # If the bullet goes off the screen, remove it from the sprite lists
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)

            if len(hit_list) > 0:

                # Make the explosion
                explosion = Tanks.Explosion(self.explosion_texture_list)

                # Move it to location of the enemy tank
                explosion.center_x = hit_list[0].center_x
                explosion.center_y = hit_list[0].center_y

                # Add to list of explosion sprites
                self.explosions_list.append(explosion)

                explosion.update()
                
                # # The closest enemy sprite to the bullet is the sprite that should be removed
                # closest_sprite_distance = 0.0
                
                for enemy in self.enemy_list:
                    if bullet.collides_with_sprite(enemy):
                        # Take off the turret and enemy tank
                        index = self.enemy_list.index(enemy)
                        self.enemy_list[index].remove_from_sprite_lists()
                        self.enemy_list[index].turret.remove_from_sprite_lists()
                        
                        
                
                #     # Hypotenuse
                #     distance_bullet_to_enemy = math.sqrt(math.pow((enemy.center_x - bullet.center_x), 2)
                #                                          + math.pow((enemy.center_y - bullet.center_y), 2))
                #     if distance_bullet_to_enemy < closest_sprite_distance:
                #         self.closest_sprite = enemy
                
                # add the exploded sprite
                self.exploded_tank_list.append(self.enemy_sprite.exploded)

                # Hide the bullet
                bullet.remove_from_sprite_lists()


            if bullet.bottom > self.width or bullet.top < 0 or bullet.right < 0 or bullet.left > self.width:
                bullet.remove_from_sprite_lists()
                
        # if all enemies are dead
        if not self.enemy_list:
            # Clear spritelists
            self.bullet_list = arcade.SpriteList()
            self.enemy_list = arcade.SpriteList()
            self.explosions_list = arcade.SpriteList()
            self.obstacle_list = arcade.SpriteList()
            self.exploded_tank_list = arcade.SpriteList()
                        
            self.load_next_level()
    

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.
        List of keys: http://arcade.academy/arcade.key.html
        """

        # If the player presses an arrow key, move the tank
        if key == arcade.key.UP:
            # Move the tank to the up
            self.player_sprite.change_y = Tanks.MOVEMENT_SPEED
            # Face the tank sprite upward
            self.player_sprite.angle = 180

        elif key == arcade.key.DOWN:
            # Move the tank to the down
            self.player_sprite.change_y = -Tanks.MOVEMENT_SPEED
            # Face the tank sprite downward
            self.player_sprite.angle = 0

        elif key == arcade.key.LEFT:
            # Move the tank to the left
            self.player_sprite.change_x = -Tanks.MOVEMENT_SPEED
            # Face the tank sprite to the left
            self.player_sprite.angle = 270

        elif key == arcade.key.RIGHT:
            # Move the tank to the right
            self.player_sprite.change_x = Tanks.MOVEMENT_SPEED
            # Face the tank sprite to the right
            self.player_sprite.angle = 90


    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        # If a player releases a key, stop moving the player and turret
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0


    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        # Set the target of the player's turret to the mouse location
        self.player_sprite.target_x = x
        self.player_sprite.target_y = y


    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        # Make bullet
        bullet = arcade.Sprite("assets/bulletDark1_outline.png", 1)

        # Position bullet at player's location
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y

        bullet.center_x = start_x
        bullet.center_y = start_y

        # Destination for bullet (location of mouse)
        dest_x = x
        dest_y = y

        # Angle the bullet travels
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        bullet.angle = math.degrees(angle) - 90

        # Velocity
        bullet.change_x = math.cos(angle) * Tanks.BULLET_SPEED
        bullet.change_y = math.sin(angle) * Tanks.BULLET_SPEED

        # Add the bullet to the sprite list to be drawn
        self.bullet_list.append(bullet)


    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        Not implemented yet.
        """
        pass


def main():
    """ 
    Main method. Starts the Tank Game.
    """
    game = TankGame(Tanks.SCREEN_WIDTH, Tanks.SCREEN_HEIGHT, Tanks.SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()