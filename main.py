"""
CS205 Final Project
Tanks Game (modeled after Wii Play Tanks)
Authored by: Cael Christian, Levi Putman, Olivia Wilson
"""

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

        self.explosion_texture_list = []

        columns = 5
        count = 5
        sprite_width = 130
        sprite_height = 130
        file_name = "assets/explosions_sheet.png"

        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False
        self.down_pressed: bool = False

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

        # Create the player tank and set its coordinates
        self.player_sprite = Tanks.PlayerTank("assets/tankBody_blue.png", "assets/tankBlue_barrel_rotate.png", 1)
        self.player_sprite.center_x = 120
        self.player_sprite.center_y = 128
        self.player_sprite.angle = 180
        self.player_list.append(self.player_sprite)
        self.player_list.append(self.player_sprite.turret)
        
        # Create the enemy tank and set its coordinates
        self.enemy_sprite = Tanks.EnemyTank("assets/tankBody_red.png", "assets/tankBlue_barrel_rotate.png", "assets/barricadeMetal.png", 1)
        self.enemy_sprite.center_x = Tanks.SCREEN_WIDTH - 115
        self.enemy_sprite.center_y = Tanks.SCREEN_HEIGHT - 128
        self.enemy_sprite.angle = 180
        self.enemy_list.append(self.enemy_sprite)
        self.enemy_list.append(self.enemy_sprite.turret)

        # Load level and obstacles (not sure if layer options are required here but used in documentation)
        tile_map = arcade.load_tilemap("maps/level.tmx", layer_options={"Obstacles": {"use_spatial_hash": True}})

        # Loads the tilemap layer "Obstacles" into a sprite list
        self.obstacle_list = tile_map.sprite_lists["Obstacles"]

        self.physics_engine = arcade.PymunkPhysicsEngine(damping=0.0001,
                                                         gravity=(0,0))

        self.physics_engine.add_sprite(self.player_sprite,
                                       mass=1.0,
                                       friction=1.0,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player")


        self.physics_engine.add_sprite_list(self.obstacle_list,
                                            friction = 0,
                                            collision_type="wall",
                                            elasticity = 1.0,
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)

    def on_draw(self):
        """
        Render the screen.
        """
        # Clear the frame to prepare for drawing sprites
        arcade.start_render()

        # Draw all sprite lists
        self.enemy_list.draw()
        self.player_list.draw()
        self.explosions_list.draw()
        self.obstacle_list.draw()
        self.exploded_tank_list.draw()
        self.bullet_list.draw()

    def on_update(self, delta_time):
        """
        Updates all sprite lists and removes unnecessary sprites
        Partially from https://api.arcade.academy/en/2.6.0/examples/sprite_explosion_bitmapped.html
        """
        # Update the sprite lists
        self.physics_engine.step()
        self.player_list.update()
        self.bullet_list.update()
        self.enemy_list.update()
        self.explosions_list.update()
        self.exploded_tank_list.update()

        self.enemy_sprite.player_x = self.player_sprite.center_x
        self.enemy_sprite.player_y = self.player_sprite.center_y

        if self.up_pressed:
            # Move the tank to the up
            self.physics_engine.apply_force(self.player_sprite, (0, -Tanks.PLAYER_MOVE_FORCE))
            # Face the tank sprite upward
            self.physics_engine.set_friction(self.player_sprite, 0)
        if self.down_pressed:
            # Move the tank to the down
            self.physics_engine.apply_force(self.player_sprite, (0, Tanks.PLAYER_MOVE_FORCE))
            # Face the tank sprite downward
            self.physics_engine.set_friction(self.player_sprite, 0)
        if self.left_pressed:
            # Move the tank to the left
            self.physics_engine.apply_force(self.player_sprite, (Tanks.PLAYER_MOVE_FORCE, 0))
            # Face the tank sprite to the left
            self.physics_engine.set_friction(self.player_sprite, 0)
        if self.right_pressed:
            # Move the tank to the right
            self.physics_engine.apply_force(self.player_sprite, (-Tanks.PLAYER_MOVE_FORCE, 0))
            # Face the tank sprite to the right
            self.physics_engine.set_friction(self.player_sprite, 0)

        if not self.right_pressed and not self.left_pressed and not self.up_pressed and not self.down_pressed:
            self.physics_engine.set_friction(self.player_sprite, 1.0)

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

                # Take off the turret and enemy tank, then add the exploded sprite
                self.enemy_sprite.remove_from_sprite_lists()
                self.enemy_sprite.turret.remove_from_sprite_lists()
                self.exploded_tank_list.append(self.enemy_sprite.exploded)

                # Hide the bullet
                bullet.remove_from_sprite_lists()


            if bullet.bottom > self.width or bullet.top < 0 or bullet.right < 0 or bullet.left > self.width:
                bullet.remove_from_sprite_lists()

        # Check when bullets collide with walls
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.obstacle_list)
            if len(hit_list) > 0:
                bullet.num_ricochets += 1


        # Remove bullets if they collide with eachother
        bs = []
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.bullet_list)
            for b in hit_list:
                b.remove_from_sprite_lists()
                bullet.remove_from_sprite_lists()
    

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.
        List of keys: http://arcade.academy/arcade.key.html
        """

        # If the player presses an arrow key, move the tank
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True


    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        # If a player releases a key, stop moving the player and turret
        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False


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
        bullet = Tanks.Bullet("assets/bulletDark1_outline.png", 1)

        # Position bullet at player's location
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y

        # Destination for bullet (location of mouse)
        dest_x = x
        dest_y = y

        # Angle the bullet travels
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        bullet.angle = math.degrees(angle) - 90

        bullet.center_x = start_x + math.cos(angle) * 60
        bullet.center_y = start_y + math.sin(angle) * 60

        # If the turret is in a obstacle, don't shoot a bullet
        hit_list = arcade.check_for_collision_with_list(self.player_sprite.turret, self.obstacle_list)
        if len(hit_list) == 0:
            # Shoot a bullet towards the mouse
            self.physics_engine.add_sprite(bullet,
                                                friction=0.1,
                                                mass = 0.5,
                                                damping = 1,
                                                collision_type = "bullet",
                                                moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                                elasticity = 1.0)
            self.physics_engine.apply_force(bullet, (0, 8000))
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