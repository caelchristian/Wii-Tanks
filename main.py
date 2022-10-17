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

        self.explosion_texture_list = []

        columns = 5
        count = 60
        sprite_width = 130
        sprite_height = 130
        file_name = "assets/explosion1.png"

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

        # Create the player tank and set its coordinates
        self.player_sprite = Tanks.Player("assets/tankBody_blue.png", 1)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.player_sprite.angle = 180
        self.player_list.append(self.player_sprite)
        
        # Create the enemy tank and set its coordinates
        self.enemy_sprite = Tanks.EnemyTank("assets/tank_red.png")
        self.enemy_sprite.center_x = Tanks.SCREEN_WIDTH - 64
        self.enemy_sprite.center_y = Tanks.SCREEN_HEIGHT - 128
        self.enemy_sprite.angle = 180
        self.enemy_list.append(self.enemy_sprite)

        # Create the sprite for the player tanks turret (gun)
        image_source = "assets/tankBlue_barrel_rotate.png"
        self.turret_sprite = Tanks.Turret(image_source, 1)
        self.turret_sprite.center_x = 64
        self.turret_sprite.center_y = 128
        self.player_list.append(self.turret_sprite)

        # Create the sprite for the blockade
        image_source = "assets/crateWood.png"
        self.obstacle_sprite = Tanks.Obstacle(image_source, 1, explodable=False)
        self.obstacle_sprite.center_x = 200
        self.obstacle_sprite.center_y = 200
        self.obstacle_list.append(self.obstacle_sprite)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=0, walls=self.obstacle_list
        )
        

    def on_draw(self):
        """
        Render the screen.
        """
        # Clear the frame to prepare for drawing sprites
        arcade.start_render()

        # Draw all sprite lists
        self.bullet_list.draw()
        self.enemy_list.draw()
        self.player_list.draw()
        self.explosions_list.draw()
        self.obstacle_list.draw()

    def on_update(self, delta_time):
        """
        Updates all sprite lists and removes unnecessary sprites
        """
        # Update the sprite lists
        self.physics_engine.update()
        self.player_list.update()
        self.turret_sprite.update_center(self.player_sprite.center_x, self.player_sprite.center_y)
        self.bullet_list.update()
        self.enemy_list.update()

        # If the bullet goes of the screen, remove it from the sprite lists
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)

            if len(hit_list) > 0:

                # Make the explosion
                explosion = Tanks.Explosion(self.explosion_texture_list)

                # Move it to location of the enemy tank
                explosion.center_x = hit_list[0].center_x
                explosion.center_y = hit_list[0].center_y

                explosion.update()

                # Add to list of explosion sprites
                self.explosions_list.append(explosion)

                # Hide the bullet
                bullet.remove_from_sprite_lists()


            if bullet.bottom > self.width or bullet.top < 0 or bullet.right < 0 or bullet.left > self.width:
                bullet.remove_from_sprite_lists()
    

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.
        List of keys: http://arcade.academy/arcade.key.html
        """

        # If the player presses an arrow key, move the tank
        if key == arcade.key.UP:
            # Move the tank to the up
            self.player_sprite.change_y = Tanks.MOVEMENT_SPEED
            self.turret_sprite.change_y = Tanks.MOVEMENT_SPEED
            # Face the tank sprite upward
            self.player_sprite.angle = 180

        elif key == arcade.key.DOWN:
            # Move the tank to the down
            self.player_sprite.change_y = -Tanks.MOVEMENT_SPEED
            self.turret_sprite.change_y = -Tanks.MOVEMENT_SPEED
            # Face the tank sprite downward
            self.player_sprite.angle = 0

        elif key == arcade.key.LEFT:
            # Move the tank to the left
            self.player_sprite.change_x = -Tanks.MOVEMENT_SPEED
            self.turret_sprite.change_x = -Tanks.MOVEMENT_SPEED
            # Face the tank sprite to the left
            self.player_sprite.angle = 270

        elif key == arcade.key.RIGHT:
            # Move the tank to the right
            self.player_sprite.change_x = Tanks.MOVEMENT_SPEED
            self.turret_sprite.change_x = Tanks.MOVEMENT_SPEED
            # Face the tank sprite to the right
            self.player_sprite.angle = 90


    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        # If a player releases a key, stop moving the player and turret
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
            self.turret_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0
            self.turret_sprite.change_x = 0


    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        # Set the target of the player's turret to the mouse location
        self.turret_sprite.target_x = x
        self.turret_sprite.target_y = y


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