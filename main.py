"""
Starting Template
"""
import arcade
import Tanks
import sys
import math
import numpy as np

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"

MOVEMENT_SPEED = 3
BULLET_SPEED = 5


class MyGame(arcade.Window):
    """
    Main application class.
    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.WHEAT)

        self.background = None

        # If you have sprite lists, you should create them here,
        # and set them to None
        self.player_list = None
        self.bullet_list = None
        self.enemy_list = None

    def setup(self):
        # Create the Sprite lists
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()

        # Set up the player, specifically placing it at these coordinates.
        image_source = "assets/tankBody_blue.png"
        self.player_sprite = Tanks.Player(image_source, 1)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.player_list.append(self.player_sprite)
        self.player_sprite.angle = 180
        
        # Create EnemyTank (and set position to middle of screen)
        self.enemy_sprite = Tanks.EnemyTank("assets/tank_red.png")
        self.enemy_sprite.center_x = SCREEN_WIDTH - 64
        self.enemy_sprite.center_y = SCREEN_HEIGHT - 128
        self.enemy_list.append(self.enemy_sprite)
        self.enemy_sprite.angle = 180

        image_source = "assets/tankBlue_barrel_rotate.png"
        self.turret_sprite = Tanks.Turret(image_source, 1)
        self.turret_sprite.center_x = 64
        self.turret_sprite.center_y = 128
        self.player_list.append(self.turret_sprite)
        

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        # Call draw() on all your sprite lists below
        self.bullet_list.draw()
        self.enemy_list.draw()
        self.player_list.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        self.player_list.update()

        self.bullet_list.update()
        for bullet in self.bullet_list:
            if bullet.bottom > self.width or bullet.top < 0 or bullet.right < 0 or bullet.left > self.width:
                bullet.remove_from_sprite_lists()
                
        self.enemy_list.update()
        
        pass
    

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.
        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """

        # If the player presses a key, update the speed
        if key == arcade.key.UP:
            self.player_sprite.change_y = MOVEMENT_SPEED
            self.turret_sprite.change_y = MOVEMENT_SPEED
            self.player_sprite.angle = 180
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -MOVEMENT_SPEED
            self.turret_sprite.change_y = -MOVEMENT_SPEED
            self.player_sprite.angle = 0
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
            self.turret_sprite.change_x = -MOVEMENT_SPEED
            self.player_sprite.angle = 270
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED
            self.turret_sprite.change_x = MOVEMENT_SPEED
            self.player_sprite.angle = 90


    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        # If a player releases a key, zero out the speed.
        # This doesn't work well if multiple keys are pressed.
        # Use 'better move by keyboard' example if you need to
        # handle this.
        
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
            self.turret_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0
            self.turret_sprite.change_x = 0
        
        pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """

        self.turret_sprite.target_x = x
        self.turret_sprite.target_y = y


        pass

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
        bullet.change_x = math.cos(angle) * BULLET_SPEED
        bullet.change_y = math.sin(angle) * BULLET_SPEED

        self.bullet_list.append(bullet)

        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()