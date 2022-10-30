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

        # Initialize sprite lists
        self.player_list = None
        self.bullet_list = None
        self.enemy_list = None
        self.enemy_turret_list = None
        self.obstacle_list = None
        self.exploded_tank_list = None
        self.mine_list = None
        
        # Initialize instance variables
        self.tanks_destroyed = 0
        self.end_level_time = 1
        self.game_over = False
        self.game_win = False
        self.physics_engine = None
        self.explosion_texture_list = []

        # Keypress tracking variables
        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False
        self.down_pressed: bool = False

        # Load the explosions from the sprite sheet
        self.explosion_texture_list = arcade.load_spritesheet(file_name="assets/explosions_sheet.png", sprite_width=130, sprite_height=130, columns=5, count=5)


    def setup(self):
        """ 
        Setup the sprite lists and place the sprites on the screen
        """
        # Load the sprites for the first level
        self.load_next_level()

        # Create the physics engine and add the player and obstacles sprites to it
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

    def load_next_level(self):
        """Clears all sprites and loads the next level of the game.
        """
        # Initialize all sprite lists to empty
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.enemy_turret_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()
        self.obstacle_list = arcade.SpriteList()
        self.exploded_tank_list = arcade.SpriteList()
        self.mine_list = arcade.SpriteList()

        # Load level from the tilemap
        layer_options = {"Obstacles" : {"use_spatial_hash": True},
                        "Enemies" : {"use_spatial_hash": True}}
        
        tile_map = arcade.load_tilemap("maps/level.tmx", layer_options=layer_options)

        # Load data from tilemap layers
        self.obstacle_list = tile_map.sprite_lists["Obstacles"]
        enemy_tiles = tile_map.sprite_lists["Enemies"]
        player_tile = tile_map.sprite_lists["Player"][0]
        
        # Create enemy tank objects with locations from the tilemap
        for tile in enemy_tiles:
            self.enemy_sprite = Tanks.EnemyTank("assets/tankBody_red.png", "assets/tankBlue_barrel_rotate.png", "assets/barricadeMetal.png", 1)
            self.enemy_sprite.center_x = tile.center_x
            self.enemy_sprite.center_y = tile.center_y
            self.enemy_list.append(self.enemy_sprite)
            self.enemy_turret_list.append(self.enemy_sprite.turret)
        
        # Create the player tank object and set its coordinates
        self.player_sprite = Tanks.PlayerTank("assets/tankBody_blue.png", "assets/tankBlue_barrel_rotate.png", "assets/barricadeMetal.png", 1)
        self.player_sprite.center_x = player_tile.center_x
        self.player_sprite.center_y = player_tile.center_y
        self.player_sprite.angle = 180
        self.player_list.append(self.player_sprite)
        self.player_list.append(self.player_sprite.turret)

    def on_draw(self):
        """
        Render the screen.
        """
        # Clear the frame to prepare for drawing sprites
        arcade.start_render()

        if not self.game_over:
            # Draw all sprite lists
            self.exploded_tank_list.draw()
            self.enemy_list.draw()
            self.enemy_turret_list.draw()
            self.mine_list.draw()
            self.bullet_list.draw()
            self.player_list.draw()
            self.explosions_list.draw()
            self.obstacle_list.draw()
            

            # Draw the scoreboard
            arcade.draw_text(text=f"Enemy Tanks Destroyed: {self.tanks_destroyed}", 
                        start_x=0, 
                        start_y=800,
                        font_size=24,
                        width=Tanks.SCREEN_WIDTH,
                        align="center")
        elif self.game_win:
            # Winning screen
            arcade.draw_text(text=f"You won the game! \nPress the escape key to exit.", 
                        start_x=0, 
                        start_y=400,
                        font_size=48,
                        color=arcade.color.BLACK,
                        width=Tanks.SCREEN_WIDTH,
                        align="center")
        else:
            # Winning screen
            arcade.draw_text(text=f"You lost the game! \nPress the escape key to exit.", 
                        start_x=0, 
                        start_y=400,
                        font_size=48,
                        color=arcade.color.BLACK,
                        width=Tanks.SCREEN_WIDTH,
                        align="center")
            
        

    def on_update(self, delta_time):
        """
        Updates all sprite lists and removes unnecessary sprites
        Partially from https://api.arcade.academy/en/2.6.0/examples/sprite_explosion_bitmapped.html
        """
        # Iterate the physics engine
        self.physics_engine.step()

        # Update the sprite lists
        self.player_list.update()
        self.bullet_list.update()
        self.enemy_list.update()
        self.explosions_list.update()
        self.exploded_tank_list.update()
        self.mine_list.update()

        # Update all the enemy tanks to know where the player is
        for enemy in self.enemy_list:
            if isinstance(enemy, Tanks.EnemyTank):
                enemy.player_x = self.player_sprite.center_x
                enemy.player_y = self.player_sprite.center_y
            
                if enemy.can_shoot:
                    # Make bullet
                    bullet = Tanks.Bullet("assets/bulletDark1_outline.png", 1)

                    # Get distances from enemy to player
                    x_diff = enemy.player_x - enemy.center_x
                    y_diff = enemy.player_y - enemy.center_y
                    # Get angle of bullet
                    angle = math.atan2(y_diff, x_diff)
                    bullet.angle = math.degrees(angle) - 90

                    # Offset so the bullet doesn't start inside the tank
                    bullet.center_x = enemy.center_x + math.cos(angle) * 60
                    bullet.center_y = enemy.center_y + math.sin(angle) * 60

                    # Apply force to the bullet using the physics engine
                    self.physics_engine.add_sprite(bullet,
                                                        friction=0.1,
                                                        mass = 0.5,
                                                        damping = 1,
                                                        collision_type = "bullet",
                                                        moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                                        elasticity = 1.0)
                    self.physics_engine.apply_force(bullet, (0, Tanks.BULLET_MOVE_FORCE))
                    
                    # Add the bullet to the sprite list to be drawn
                    self.bullet_list.append(bullet)
                    
                    enemy.cooldown = 1
                    enemy.can_shoot = False
                    
                    
                else:
                    # enemy on cooldown, remove delta time
                    enemy.cooldown -= delta_time
                    if enemy.cooldown < 0:
                        enemy.can_shoot = True
                

        # Apply forces to push player in direction of arrow keys
        # Set friction to 0 temporarily to make the player move faster
        if self.up_pressed:
            self.physics_engine.apply_force(self.player_sprite, (0, -Tanks.PLAYER_MOVE_FORCE))
            self.physics_engine.set_friction(self.player_sprite, 0)
        
        if self.down_pressed:
            self.physics_engine.apply_force(self.player_sprite, (0, Tanks.PLAYER_MOVE_FORCE))
            self.physics_engine.set_friction(self.player_sprite, 0)
        
        if self.left_pressed:
            self.physics_engine.apply_force(self.player_sprite, (Tanks.PLAYER_MOVE_FORCE, 0))
            self.physics_engine.set_friction(self.player_sprite, 0)
        
        if self.right_pressed:
            self.physics_engine.apply_force(self.player_sprite, (-Tanks.PLAYER_MOVE_FORCE, 0))
            self.physics_engine.set_friction(self.player_sprite, 0)

        # If no keys are pressed, set the friction to 1 to slow the tank down
        if not self.right_pressed and not self.left_pressed and not self.up_pressed and not self.down_pressed:
            self.physics_engine.set_friction(self.player_sprite, 1.0)

        # Explode all the mines in the mine list
        for mine in self.mine_list:
            if mine.timer(delta_time) >= mine.end_time:

                # Move it to location of the mine
                self.explosion_animation(mine.center_x, mine.center_y)

                # Remove the mine from the sprite list
                mine.remove_from_sprite_lists()

        # Check bullets for collision with enemies, obstacles and other bullets
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)

            # For every enemy that the player has hit, explode them
            for enemy in hit_list:
                # Move it to the location of the enemy x and y
                self.explosion_animation(enemy.center_x, enemy.center_y)

                # Add exploded enemy to exploded tank list
                self.exploded_tank_list.append(enemy.exploded)

                # Remove the enemy tank and the bullet
                enemy.remove_from_sprite_lists()
                enemy.turret.remove_from_sprite_lists()
                bullet.remove_from_sprite_lists()
                self.tanks_destroyed += 1
                
            if arcade.check_for_collision(bullet, self.player_sprite):
                # Move it to the location of the player
                self.explosion_animation(self.player_sprite.center_x, self.player_sprite.center_y)

                # Add exploded enemy to exploded tank list
                self.exploded_tank_list.append(self.player_sprite.exploded)

                # Remove the enemy tank and the bullet
                self.player_spriteplayer.remove_from_sprite_lists()
                self.player_spriteplayer.turret.remove_from_sprite_lists()
                bullet.remove_from_sprite_lists()
                # user doesn't win by default
                self.game_over = True

        # Check when bullets collide with walls
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.obstacle_list)
            if len(hit_list) > 0:
                bullet.num_ricochets += 1

        # Remove bullets if they collide with eachother
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.bullet_list)
            for b in hit_list:
                b.remove_from_sprite_lists()
                bullet.remove_from_sprite_lists()
        
        # If all enemy tanks are destroyed, the game will end in one second
        if len(self.enemy_list) == 0:
            self.end_level_time -= delta_time

        if self.end_level_time < 0:
            self.game_over = True
            
        if not self.player_sprite.can_shoot:
            # player on cooldown, remove delta time
            self.player_sprite.cooldown -= delta_time
            if self.player_sprite.cooldown < 0:
                self.player_sprite.can_shoot = True
            
        

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.
        List of keys: http://arcade.academy/arcade.key.html
        """

        # If the player presses an arrow key, set the keypress toggle variable
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

        elif key == arcade.key.SPACE:
            # Create the mine that is dropped
            self.mine = Tanks.Mine("assets/barrelBlack_top.png", 1)
            self.mine.center_x = self.player_sprite.center_x
            self.mine.center_y = self.player_sprite.center_y
            self.mine_list.append(self.mine)
            

        # If the game is over and they press escape, close the application
        if self.game_over and key == arcade.key.ESCAPE:
            arcade.close_window()

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        # If a player releases a key, unset the keypress toggle variable
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
        # If the turret is in a obstacle, don't shoot a bullet
        hit_list = arcade.check_for_collision_with_list(self.player_sprite.turret, self.obstacle_list)
        if len(hit_list) > 0:
            return None
        
        if self.player_sprite.can_shoot:
            # Make bullet
            bullet = Tanks.Bullet("assets/bulletDark1_outline.png", 1)

            # Position bullet at player's location
            start_x = self.player_sprite.center_x
            start_y = self.player_sprite.center_y

            # Angle the bullet travels
            x_diff = x - start_x
            y_diff = y - start_y
            angle = math.atan2(y_diff, x_diff)
            bullet.angle = math.degrees(angle) - 90

            # Offset so the bullet doesn't start inside the player tank
            bullet.center_x = start_x + math.cos(angle) * 60
            bullet.center_y = start_y + math.sin(angle) * 60

            # Apply force to the bullet using the physics engine
            self.physics_engine.add_sprite(bullet,
                                                friction=0.1,
                                                mass = 0.5,
                                                damping = 1,
                                                collision_type = "bullet",
                                                moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                                elasticity = 1.0)
            self.physics_engine.apply_force(bullet, (0, Tanks.BULLET_MOVE_FORCE))
            
            # Add the bullet to the sprite list to be drawn
            self.bullet_list.append(bullet)
            
            self.player_sprite.cooldown = 1
            self.player_sprite.can_shoot = False


    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        Not implemented yet.
        """
        pass

    def explosion_animation(self, x, y):
        """
        An explosion function that causes an explosion animation
        based on the x and y coordinates.
        """
        # Make the explosion
        explosion = Tanks.Explosion(self.explosion_texture_list)

        # Move it to location of the parameter x and y
        explosion.center_x = x
        explosion.center_y = y

        # Add to list of explosion sprites
        self.explosions_list.append(explosion)
        explosion.update()


def main():
    """ 
    Main method. Starts the Tank Game.
    """
    game = TankGame(Tanks.SCREEN_WIDTH, Tanks.SCREEN_HEIGHT, Tanks.SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()