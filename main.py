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
        self.set_mouse_visible(False)

        # Initialize sprite lists
        self.player_list = None
        self.bullet_list = None
        self.enemy_list = None
        self.enemy_turret_list = None
        self.obstacle_list = None
        self.exploded_tank_list = None
        self.mine_list = None
        self.tracks_list = None
        self.all_obstacles = None
        
        # Initialize instance variables
        self.tanks_destroyed = 0
        self.end_level_time = Tanks.END_LEVEL_TIME
        self.transition_time = 2
        self.physics_engine = None
        self.explosion_texture_list = []
        self.astar_barrier_list = None
        
        # status variables
        self.game_lost = False
        self.game_over = False
        self.round_over = False
        self.round_lost = False
        self.level_num = 1
        self.level_num_max = 10
        self.player_lives = 3
        self.max_player_lives = 5

        # Keypress tracking variables
        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False
        self.down_pressed: bool = False
        self.direction = 0

        # Load the explosions from the sprite sheet
        self.explosion_texture_list = arcade.load_spritesheet(file_name="assets/explosions_sheet.png", sprite_width=130, sprite_height=130, columns=5, count=5)
        self.player_texture_list = [arcade.load_texture(f"assets/tankBody_blue{i}.png") for i in range(4)]

        # Used for dynamically referencing next move audio file "sounds/move1-4.wav"
        self.move_num_dict = {}
        self.total_moves = 0
        self.player = None

        # Play level music
        self.load_sounds()
        self.player = self.music.play(volume=.5)
        
        # load tank icon (this should prolly go somewhere else)
        self.tank_icon = arcade.load_texture("assets/tank_icon.png")
        
    def load_sounds(self):
        """ Loads the sound files
        """
        self.shoot1 = arcade.sound.load_sound("sounds/shoot1.wav", )
        self.shoot2 = arcade.sound.load_sound("sounds/shoot2.wav")
        self.explode1 = arcade.sound.load_sound("sounds/explode1.wav")
        self.explode2 = arcade.sound.load_sound("sounds/explode2.wav")
        self.richochet1 = arcade.sound.load_sound("sounds/richochet1.wav")
        self.richochet2 = arcade.sound.load_sound("sounds/richochet2.wav")
        self.move = arcade.load_sound("sounds/move.wav")
        
        # Game sfx
        self.whistle = arcade.load_sound("sounds/whistle.wav")
        self.round_start = arcade.load_sound("sounds/Round Start.wav")
        self.round_fail = arcade.load_sound("sounds/Round Failure.wav")
        self.round_win = arcade.load_sound("sounds/Round Win.wav")
        self.round_fail = arcade.load_sound("sounds/Round Failure.wav")
        self.results = arcade.load_sound("sounds/Results.wav")
        self.round_fail = arcade.load_sound("sounds/Round Failure.wav")
        
        # Load music each level
        if self.level_num < 9:
            self.music = arcade.load_sound(f"sounds/Variation {self.level_num}.wav")
        else:
            self.music = arcade.load_sound(f"sounds/Variation 9.wav")
        
    def setup(self):
        """ 
        Initialize sprite lists, load next tilemap, and place the sprites on the screen.
        """
        # Load the sprites for the level
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.enemy_turret_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()
        self.obstacle_list = arcade.SpriteList()
        self.breakable_obstacle_list = arcade.SpriteList()
        self.explodables_list = arcade.SpriteList()
        self.exploded_tank_list = arcade.SpriteList()
        self.mine_list = arcade.SpriteList()
        self.tracks_list = arcade.SpriteList()
        self.all_obstacles = arcade.SpriteList()
        
        # Load level from the tilemap
        layer_options = {"Obstacles" : {"use_spatial_hash": True},
                        "Breakable Obstacles" : {"use_spatial_hash": True},
                        "Explodables" : {"use_spatial_hash": True},
                        "Easy Enemies" : {"use_spatial_hash": True},
                        "Medium Enemies" : {"use_spatial_hash": True},
                        "Hard Enemies" : {"use_spatial_hash": True}}
        
        tile_map = arcade.load_tilemap(f"maps/level{self.level_num}.tmx", layer_options=layer_options, hit_box_algorithm="None")

        # Load data from tilemap layers
        self.obstacle_list = tile_map.sprite_lists["Obstacles"]
        self.breakable_obstacle_list = tile_map.sprite_lists["Breakable Obstacles"]
        self.explodables_list = tile_map.sprite_lists["Explodables"]
        easy_enemy_tiles = tile_map.sprite_lists["Easy Enemies"]
        medium_enemy_tiles = tile_map.sprite_lists["Medium Enemies"]
        hard_enemy_tiles = tile_map.sprite_lists["Hard Enemies"]
        player_tile = tile_map.sprite_lists["Player"][0]
        
        # Create enemy tank objects with locations from the tilemap
        for tile in easy_enemy_tiles:
            self.add_enemy_tank(tile.center_x, tile.center_y, Tanks.Difficulty.EASY)
            
        for tile in medium_enemy_tiles:
            self.add_enemy_tank(tile.center_x, tile.center_y, Tanks.Difficulty.MEDIUM)
            
        for tile in hard_enemy_tiles:
            self.add_enemy_tank(tile.center_x, tile.center_y, Tanks.Difficulty.HARD)
        
        # Create the player tank object and set its coordinates
        self.player_sprite = Tanks.PlayerTank("assets/tankBody_blue1.png", "assets/tankBlue_barrel_rotate.png", .8)
        self.player_sprite.center_x = player_tile.center_x
        self.player_sprite.center_y = player_tile.center_y
        self.player_sprite.angle = 180
        self.player_list.append(self.player_sprite)
        self.player_list.append(self.player_sprite.turret)
        
        # Add the crosshair
        self.crosshair_sprite = arcade.Sprite("assets/crosshair.png", 0.1)
        self.crosshair_sprite.center_x = 200
        self.crosshair_sprite.center_y = 200
        
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
        
        self.physics_engine.add_sprite_list(self.breakable_obstacle_list,
                                            friction = 0,
                                            collision_type="breakable wall",
                                            elasticity = 1.0,
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)
        
        self.physics_engine.add_sprite_list(self.explodables_list,
                                            friction = 0,
                                            collision_type="explodables",
                                            elasticity = 1.0,
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)
    
        # Barrier list for AStar search
        for barrier in self.obstacle_list:
            self.all_obstacles.append(barrier)
        for barrier in self.breakable_obstacle_list:
            self.all_obstacles.append(barrier)
        for barrier in self.explodables_list:
            self.all_obstacles.append(barrier)

        self.astar_barrier_list = arcade.AStarBarrierList(moving_sprite=self.player_sprite,
                                                          blocking_sprites=self.all_obstacles,
                                                          grid_size=56,
                                                          left=-112,
                                                          right=Tanks.SCREEN_WIDTH,
                                                          bottom=-112,
                                                          top=Tanks.SCREEN_HEIGHT)
        
        for enemy in self.enemy_list:
            self.physics_engine.add_sprite(enemy,
                                       mass=1.0,
                                       friction=1.0,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player")
        
        self.load_sounds()

    def on_draw(self):
        """
        Render the screen.
        """
        # Clear the frame to prepare for drawing sprites
        arcade.start_render()

        if not self.game_over and not self.round_over:
            # Draw all sprite lists
            self.tracks_list.draw()
            self.exploded_tank_list.draw()
            self.mine_list.draw()
            self.enemy_list.draw()
            self.enemy_turret_list.draw()
            self.bullet_list.draw()
            self.player_list.draw()
            self.obstacle_list.draw()
            self.explodables_list.draw()
            self.breakable_obstacle_list.draw()
            self.explosions_list.draw()
            self.crosshair_sprite.draw()
            
            # Draw the scoreboard
            arcade.draw_text(text=f"Enemy Tanks Destroyed: {self.tanks_destroyed}", 
                        start_x=0, 
                        start_y=800,
                        font_size=24,
                        font_name="Kenney Mini Square",
                        width=Tanks.SCREEN_WIDTH,
                        align="center")
                        
            # Display round won during transition time
            if self.end_level_time < Tanks.END_LEVEL_TIME and not self.round_lost and not self.round_over:
                arcade.draw_text(text=f"Mission Cleared!", 
                                start_x=0, 
                                start_y=400,
                                font_size=48,
                                font_name="Kenney Mini Square",
                                color=arcade.color.BLACK,
                                width=Tanks.SCREEN_WIDTH,
                                align="center")
            
        # if they finish game (win or lose) display results
        elif self.game_over:
            arcade.draw_text(text=f"Results:\n",
                            start_x=0, 
                            start_y=600,
                            font_size=58,
                            font_name="Kenney Mini Square",
                            color=arcade.color.BLACK,
                            width=Tanks.SCREEN_WIDTH,
                            align="center",
                            )
            
            arcade.draw_text(text=f"Tanks destroyed: {self.tanks_destroyed}\n" +
                             f"Levels cleared: {self.level_num-1}/{self.level_num_max}",
                            start_x=0, 
                            start_y=500,
                            font_size=42,
                            font_name="Kenney Mini Square",
                            color=arcade.color.BLACK,
                            width=Tanks.SCREEN_WIDTH,
                            align="center",
                            )
            
            arcade.draw_text(text=f"Press the escape key to exit.",
                start_x=0, 
                start_y=100,
                font_size=32,
                font_name="Kenney Mini Square",
                color=arcade.color.BLACK,
                width=Tanks.SCREEN_WIDTH,
                align="center")

            # Winning Screen
            if not self.game_lost:
                arcade.draw_text(text=f"You won the game!", 
                            start_x=0, 
                            start_y=700,
                            font_size=48,
                            font_name="Kenney Mini Square",
                            color=arcade.color.BLACK,
                            width=Tanks.SCREEN_WIDTH,
                            align="center")
                
        # Transition screen
        elif self.round_over:
            # display next level numbers, num of enemy tanks, and lives remaining
            arcade.draw_text(text=f"Mission {self.level_num}", 
                            start_x=0, 
                            start_y=700,
                            font_size=48,
                            font_name="Kenney Mini Square",
                            color=arcade.color.BLACK,
                            width=Tanks.SCREEN_WIDTH,
                            align="center"
                            )
            arcade.draw_text(text=f"Tanks destroyed: {self.tanks_destroyed}",
                            start_x=0, 
                            start_y=500,
                            font_size=42,
                            font_name="Kenney Mini Square",
                            color=arcade.color.BLACK,
                            width=Tanks.SCREEN_WIDTH,
                            align="center",
                            )
            arcade.draw_text(text=f" x {self.player_lives}", 
                        start_x=40, 
                        start_y=230,
                        font_size=48,
                        font_name="Kenney Mini Square",
                        color=arcade.color.BLACK,
                        width=Tanks.SCREEN_WIDTH,
                        align="center")
            arcade.draw_text(text=f"Press enter to continue.", 
                        start_x=40, 
                        start_y=50,
                        font_size=48,
                        font_name="Kenney Mini Square",
                        color=arcade.color.BLACK,
                        width=Tanks.SCREEN_WIDTH,
                        align="center")
            arcade.draw_texture_rectangle(center_x=500, center_y=250, width=100, height=50 ,texture=self.tank_icon)
            if self.level_num == self.level_num_max:
                arcade.draw_text(text="Final level!", 
                        start_x=0, 
                        start_y=400,
                        font_size=48,
                        font_name="Kenney Mini Square",
                        color=arcade.color.BLACK,
                        width=Tanks.SCREEN_WIDTH,
                        align="center")

    def update_player(self, delta_time):
        """ Moves the player according to keys pressed

        Args:
            delta_time (float): the amount of time passes since last update
        """
        # Apply forces to push player in direction of keys
        # Set friction to 0 temporarily to make the player move faster
        if self.player_sprite in self.player_list and not self.round_over:
            if self.direction == Tanks.Direction.UP and self.up_pressed:
                self.physics_engine.apply_force(self.player_sprite, (0, -Tanks.PLAYER_MOVE_FORCE))
                self.physics_engine.set_friction(self.player_sprite, 0)
                self.player_sprite.texture = self.player_texture_list[self.direction.value]
                self.lay_tracks(180, self.player_sprite.center_x, self.player_sprite.center_y - 10, delta_time, self.player_sprite)

            if self.direction == Tanks.Direction.DOWN and self.down_pressed:
                self.physics_engine.apply_force(self.player_sprite, (0, Tanks.PLAYER_MOVE_FORCE))
                self.physics_engine.set_friction(self.player_sprite, 0)
                self.player_sprite.texture = self.player_texture_list[self.direction.value]
                self.lay_tracks(180, self.player_sprite.center_x, self.player_sprite.center_y + 10, delta_time, self.player_sprite)

            if self.direction == Tanks.Direction.LEFT and self.left_pressed:
                self.physics_engine.apply_force(self.player_sprite, (Tanks.PLAYER_MOVE_FORCE, 0))
                self.physics_engine.set_friction(self.player_sprite, 0)
                self.player_sprite.texture = self.player_texture_list[self.direction.value]
                self.lay_tracks(90, self.player_sprite.center_x + 10, self.player_sprite.center_y, delta_time, self.player_sprite)
                
            if self.direction == Tanks.Direction.RIGHT and self.right_pressed:
                self.physics_engine.apply_force(self.player_sprite, (-Tanks.PLAYER_MOVE_FORCE, 0))
                self.physics_engine.set_friction(self.player_sprite, 0)
                self.player_sprite.texture = self.player_texture_list[self.direction.value]
                self.lay_tracks(90, self.player_sprite.center_x - 10, self.player_sprite.center_y, delta_time, self.player_sprite)
                
            # If no keys are pressed, set the friction to 1 to slow the tank down
            if not self.right_pressed and not self.left_pressed and not self.up_pressed and not self.down_pressed:
                self.physics_engine.set_friction(self.player_sprite, 1.0)

    def update_enemies(self, delta_time):
        """ Updates enemies and causes them to shoot bullets

        Args:
            delta_time (float): time passed since last update
        """
        for enemy in self.enemy_list:
            enemy.player_x = self.player_sprite.center_x
            enemy.player_y = self.player_sprite.center_y

            enemy.move(self.physics_engine, self.astar_barrier_list, self.player_sprite.position, self.obstacle_list)

            # Shoot bullet if the player tank is in sight of the enemy
            if arcade.has_line_of_sight(enemy.position, self.player_sprite.position, walls=self.obstacle_list) and \
                arcade.has_line_of_sight(enemy.position, self.player_sprite.position, walls=self.breakable_obstacle_list):
                enemy.reaction_time -= delta_time

            if enemy.can_shoot and enemy.reaction_time < 0:
                self.shoot_bullet(enemy.center_x, enemy.center_y, enemy.player_x, enemy.player_y)
                enemy.reaction_time = Tanks.ENEMY_REACTION_TIME
                    
                # Reset the shoot cooldown
                if(enemy.difficulty == Tanks.Difficulty.EASY):
                    enemy.cooldown = Tanks.EASY_ENEMY_SHOOT_COOLDOWN
                elif(enemy.difficulty == Tanks.Difficulty.MEDIUM):
                    enemy.cooldown = Tanks.MEDIUM_ENEMY_SHOOT_COOLDOWN
                elif(enemy.difficulty == Tanks.Difficulty.HARD):
                    enemy.cooldown = Tanks.HARD_ENEMY_SHOOT_COOLDOWN

                enemy.can_shoot = False
                
            else:
                # Enemy on cooldown, reduce the cooldown
                enemy.cooldown -= delta_time
                if enemy.cooldown < 0:
                    enemy.can_shoot = True
                    
            enemy.move_cooldown -= delta_time
        
    def update_mines(self, delta_time):
        """ Updates the mine objects

        Args:
            delta_time (float): time passed since last update
        """
        # Reduce the time to explosion for all mines
        for mine in self.mine_list:
            hit_list = arcade.check_for_collision_with_list(mine, self.bullet_list)
            if len(hit_list) > 0:
                hit_list[0].remove_from_sprite_lists()

            if mine.timer(delta_time) >= mine.end_time or len(hit_list) > 0:
                self.explosion_animation(mine.center_x, mine.center_y)
                mine.remove_from_sprite_lists()
                
        for enemy in self.enemy_list:
            mine_death_enemy_list = arcade.check_for_collision_with_list(enemy, self.explosions_list)
            for mine in mine_death_enemy_list:
                if len(mine_death_enemy_list) > 0:
                    self.exploded_tank_list.append(enemy.exploded)
                    enemy.remove_from_sprite_lists()
                    enemy.turret.remove_from_sprite_lists()
                    self.tanks_destroyed += 1

        if len(self.player_list) > 0:
            mine_death_player_list = arcade.check_for_collision_with_list(self.player_sprite, self.explosions_list)
            if len(mine_death_player_list) > 0:
                self.player_sprite.remove_from_sprite_lists()
                self.player_sprite.turret.remove_from_sprite_lists()
                self.round_lost = True
                self.player_lives -= 1

        for obstacle in self.breakable_obstacle_list:
            hit_list = arcade.check_for_collision_with_list(obstacle, self.explosions_list)
            if len(hit_list) > 0:
                obstacle.remove_from_sprite_lists()
    
    def update_bullets(self):
        """ Checks all of the bullets to see if they have collided with tanks or walls
        """
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)

            # For every enemy that the player has hit, explode them
            for enemy in hit_list:
                self.explosion_animation(enemy.center_x, enemy.center_y)
                self.exploded_tank_list.append(enemy.exploded)
                enemy.remove_from_sprite_lists()
                enemy.turret.remove_from_sprite_lists()
                bullet.remove_from_sprite_lists()
                self.tanks_destroyed += 1
                
            # Lose if player gets hit
            if arcade.check_for_collision(bullet, self.player_sprite):
                self.player_sprite.remove_from_sprite_lists()
                self.player_sprite.turret.remove_from_sprite_lists()
                bullet.remove_from_sprite_lists()
                self.player_sprite.can_shoot = False
                self.explosion_animation(self.player_sprite.center_x, self.player_sprite.center_y)
                self.round_lost = True
                self.player_lives -= 1
                
            # Increment ricochets if wall hit
            hit_list = arcade.check_for_collision_with_list(bullet, self.obstacle_list)
            if len(hit_list) > 0:
                bullet.num_ricochets += 1
                    
            # Explode if an explodable is hit
            for explodable in self.explodables_list:
                if arcade.check_for_collision(bullet,explodable):
                    self.explosion_animation(explodable.center_x, explodable.center_y)
                    explodable.remove_from_sprite_lists()
                    bullet.remove_from_sprite_lists()
                
        # Remove bullets if they collide with eachother
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.bullet_list)
            for b in hit_list:
                self.explosion_animation(b.center_x, b.center_y)
                b.remove_from_sprite_lists()
                bullet.remove_from_sprite_lists()
                
    def update_delta_time(self, delta_time):
        """ Updates all time based functionality
        
        Args:
            delta_time (float): time passed since last update
        """
        # If all enemy tanks are destroyed OR the player dies, start transition timer
        if not self.round_over and (len(self.enemy_list) == 0 or self.round_lost):
            # only play round win/lose jingle once
            if self.end_level_time == Tanks.END_LEVEL_TIME:
                arcade.stop_sound(self.player)
                if self.round_lost:
                    self.player = self.round_fail.play(volume=.5)
                else:
                    self.player = self.round_win.play(volume=.5)
            
            self.end_level_time -= delta_time
            
        if self.level_num > self.level_num_max and self.player_lives > 0:
            self.game_over = True
            self.game_lost = False

        if self.player_lives <= 0:
            self.game_over = True
            self.game_lost = True

        # if transition time over
        if self.end_level_time < 0:
            self.round_over = True
            if not self.round_lost and not self.game_over:
                self.level_num += 1
                if self.level_num > self.level_num_max:
                    self.game_over = True
                    self.game_lost = False
            self.end_level_time = Tanks.END_LEVEL_TIME

            if self.game_over or self.level_num > self.level_num_max:
                self.player = self.results.play(volume=.5)
            else:
                self.player = self.round_start.play(volume=.5)
            
            # Clear the screen
            self.bullet_list = arcade.SpriteList()
            self.enemy_list = arcade.SpriteList()
            self.mine_list = arcade.SpriteList()
            
        if not self.player_sprite.can_shoot:
            # Player shoot on cooldown, remove delta time
            self.player_sprite.cooldown -= delta_time
            # Stops player from shooting after death
            if self.player_sprite.cooldown < 0 and self.end_level_time == Tanks.END_LEVEL_TIME:
                self.player_sprite.can_shoot = True
        
        if not self.player_sprite.can_mine:
            self.player_sprite.mine_cooldown -= delta_time
            if self.player_sprite.mine_cooldown < 0:
                self.player_sprite.can_mine = True

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
    
        # Call all custom update functions
        self.update_player(delta_time)
        self.update_enemies(delta_time)
        self.update_mines(delta_time)
        self.update_delta_time(delta_time)
        self.update_bullets()
        
    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.
        List of keys: http://arcade.academy/arcade.key.html
        """
        # Keys for movement
        if key == arcade.key.W:
            self.up_pressed = True
            self.direction = Tanks.Direction.UP
        elif key == arcade.key.S:
            self.down_pressed = True
            self.direction = Tanks.Direction.DOWN
        elif key == arcade.key.A:
            self.left_pressed = True
            self.direction = Tanks.Direction.LEFT
        elif key == arcade.key.D:
            self.right_pressed = True
            self.direction = Tanks.Direction.RIGHT
        elif key == arcade.key.SPACE and not self.round_over:
            # Create the mine that is dropped
            if self.player_sprite.can_mine:
                self.mine = Tanks.Mine("assets/barrelBlack_top.png", 1)
                self.mine.center_x = self.player_sprite.center_x
                self.mine.center_y = self.player_sprite.center_y
                self.mine_list.append(self.mine)
                self.player_sprite.can_mine = False
                self.player_sprite.mine_cooldown = Tanks.PLAYER_MINE_COOLDOWN
        # If the game is over and they press escape, close the application
        elif self.game_over and key == arcade.key.ESCAPE:
            arcade.close_window()
        elif self.round_over and key == arcade.key.ENTER and not self.game_over:
            self.setup()
            self.round_lost = False
            self.round_over = False
            # play level music
            self.player = arcade.sound.play_sound(self.music)
            
    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        # If a player releases a key, unset the keypress toggle variable
        if key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.D:
            self.right_pressed = False

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        # Set the target of the player's turret to the mouse location
        self.player_sprite.target_x = x
        self.player_sprite.target_y = y
        
        # Set crosshair to follow mouse location
        self.crosshair_sprite.center_x = x
        self.crosshair_sprite.center_y = y

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        # If the turret is in a obstacle, don't shoot a bullet
        if not self.round_over:
            hit_list = arcade.check_for_collision_with_list(self.player_sprite.turret, self.obstacle_list)
            if len(hit_list) == 0:
                if self.player_sprite.can_shoot:
                    self.shoot_bullet(start_x = self.player_sprite.center_x,
                                    start_y = self.player_sprite.center_y,
                                    target_x = x,
                                    target_y = y)
                    
                    # Reset the players cooldown
                    self.player_sprite.cooldown = Tanks.PLAYER_SHOOT_COOLDOWN
                    self.player_sprite.can_shoot = False

    def explosion_animation(self, x, y):
        """ Creates an explosion animation based on the x and y coordinates.

        Args:
            x (int): the x coordinate for the animation
            y (int): the y coordinate for the animation
        """
        explosion = Tanks.Explosion(self.explosion_texture_list)
        explosion.center_x = x
        explosion.center_y = y
        self.explosions_list.append(explosion)
        arcade.play_sound(self.explode1, volume=.5)
        explosion.update()
    
    def shoot_bullet(self, start_x, start_y, target_x, target_y):
        """ Creates a Bullet sprite and launches it towards the targer

        Args:
            start_x (int): starting x coordinate
            start_y (int): starting y coordinate
            target_x (int): target x coordinate
            target_y (int): target y coordinate
        """
        bullet = Tanks.Bullet("assets/bullet.png", 0.35)

        # Angle the bullet travels
        x_diff = target_x - start_x
        y_diff = target_y - start_y
        angle = math.atan2(y_diff, x_diff)
        bullet.angle = math.degrees(angle) - 90

        # Offset so the bullet doesn't start inside the tank
        bullet.center_x = start_x + math.cos(angle) * 65
        bullet.center_y = start_y + math.sin(angle) * 65

        # Apply force to the bullet using the physics engine
        self.physics_engine.add_sprite(bullet,
                                            friction=0.1,
                                            mass = 0.5,
                                            damping = 1,
                                            collision_type = "bullet",
                                            moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                            elasticity = 1.0)
        self.physics_engine.apply_force(bullet, (0, Tanks.BULLET_MOVE_FORCE))
        self.bullet_list.append(bullet)
        arcade.play_sound(self.shoot2, volume=.8)
            
    def add_enemy_tank(self, x, y, difficulty):
        """ Adds an enemy tank to the board

        Args:
            x (int): the x coordinate for the tank
            y (int): the y coordinate for the tank
            difficulty (Tanks.difficulty): The difficulty of the tank
        """
        if(difficulty == Tanks.Difficulty.EASY):
            image = "assets/tankBody_red"
            cooldown = Tanks.EASY_ENEMY_SHOOT_COOLDOWN
        elif(difficulty == Tanks.Difficulty.MEDIUM):
            image = "assets/tankBody_green"
            cooldown = Tanks.MEDIUM_ENEMY_SHOOT_COOLDOWN
        elif(difficulty == Tanks.Difficulty.HARD):
            image = "assets/tankBody_dark"
            cooldown = Tanks.HARD_ENEMY_SHOOT_COOLDOWN

        self.enemy_sprite = Tanks.EnemyTank(image, difficulty, cooldown, 0.8)
        self.enemy_sprite.center_x = x
        self.enemy_sprite.center_y = y
        self.enemy_list.append(self.enemy_sprite)
        self.enemy_turret_list.append(self.enemy_sprite.turret)

    def lay_tracks(self, angle_value, center_x, center_y, delta_time, sprite):
        """ Lays a track sprite at the given location and given angle

        Args:
            angle_value (float): the angle of the track
            center_x (int): the x coordinate for the track
            center_y (int): the y coordinate for the track
            delta_time (float): time passed since last update
        """

        # Add tracks sprite at the correct angle and behind the player or enemy sprite
        if sprite.can_track:
            # Add tracks sprite at the correct angle and behind the player or enemy sprite
            self.tracks_sprite = arcade.Sprite("assets/tracksSmall.png", 0.5)
            self.tracks_sprite.angle = angle_value
            self.tracks_sprite.center_x = center_x
            self.tracks_sprite.center_y = center_y
            self.tracks_list.append(self.tracks_sprite)
            
            arcade.play_sound(self.move, volume=.2)

            # Reset the track cooldown
            sprite.track_cooldown = 0.3
            sprite.can_track = False

        else:
            sprite.track_cooldown -= delta_time
            if sprite.track_cooldown < 0:
                sprite.can_track = True



def main():
    """ 
    Main method. Starts the Tank Game.
    """
    game = TankGame(Tanks.SCREEN_WIDTH, Tanks.SCREEN_HEIGHT, Tanks.SCREEN_TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
