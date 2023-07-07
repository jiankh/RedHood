import pygame
from tiles import Tile, StaticTile, AnimatedTile
from settings import tile_size, screen_width
from player import Player
from particles import ParticleEffect
from support import import_csv_layout, import_cut_graphics
from enemy import Enemy

class Level:
    def __init__(self, level_data, surface):
        #level setup
        self.display_surface = surface
        self.level_data = level_data
        self.setup_level(level_data)
        self.world_shift = 0
        self.current_x = 0

        #DUST
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        #PLAYER
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)

        #LEVEL LOADING
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')
        
        background_layout = import_csv_layout(level_data['background'])
        self.background_sprites = self.create_tile_group(background_layout, 'background')

        #GRASS SETUP
        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')

        #BACKGROUND TREES/ DECOR
        decor_layout = import_csv_layout(level_data['backDecor'])
        self.decor_sprites = self.create_tile_group(decor_layout, 'backDecor')
        
        #Spikes
        spikes_layout = import_csv_layout(level_data['spikes'])
        self.spikes_sprites = self.create_tile_group(spikes_layout, 'spikes')

        #Arrows Layout
        arrows_layout = import_csv_layout(level_data['arrows'])
        self.arrows_sprites = self.create_tile_group(arrows_layout, 'arrows')

        #ENEMY
        enemies_layout = import_csv_layout(level_data['enemies'])
        self.enemies_sprites = self.create_tile_group(enemies_layout, 'enemies')

        #CONSTRAINTS
        constraints_layout = import_csv_layout(level_data['constraints'])
        self.constraints_sprites = self.create_tile_group(constraints_layout, 'constraints')

    def player_setup(self, layout):
        for row_index, row in enumerate(layout):
            for col_index,val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size

                if val == '0': #PLAYER
                    player_sprite = Player( x, y, self.display_surface, self.create_jump_particle)
                    self.player.add(player_sprite)

                if val == '1': # GOAL
                    end_surface = pygame.image.load('../graphics/character/end.png').convert_alpha()
                    sprite = StaticTile(tile_size,x,y,end_surface)
                    self.goal.add(sprite)

    def create_tile_group(self,layout,type):
        sprite_group = pygame.sprite.Group()
        
        for row_index, row in enumerate(layout):
            for col_index,val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size                 

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics('../graphics/terrain/terrain.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'background':
                        background_tile_list = import_cut_graphics('../graphics/SET1_bakcground_day1.png')
                        tile_surface = background_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    

                    if type == 'grass':
                        grass_tile_list = import_cut_graphics('../graphics/terrain/terrain.png') #same image as terrain
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'backDecor':
                        decor_tile_list = import_cut_graphics('../graphics/terrain/terrain.png') #same image as terrain
                        tile_surface = decor_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'spikes':
                        spikes_tile_list = import_cut_graphics('../graphics/terrain/terrain.png') #same image as terrain
                        tile_surface = spikes_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    

                    if type == 'arrows':
                        if val == '0': sprite = AnimatedTile(tile_size,x,y, '../graphics/items/arrows')
                        if val == '1': sprite = AnimatedTile(tile_size,x,y, '../graphics/items/arrows_gold')

                    if type == 'enemies':
                        sprite = Enemy(tile_size,x,y)

                    if type == 'constraints':
                        sprite = Tile(tile_size,x,y)
                        

                    sprite_group.add(sprite)

        return sprite_group



    def create_jump_particle(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10,5)
        else: 
            pos +=  pygame.math.Vector2(10,-5)
        jump_particle_sprite = ParticleEffect(pos,'jump')
        self.dust_sprite.add(jump_particle_sprite)

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
           self.player_on_ground = True 
        else:
            self.player_on_ground = False

    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right: #offset to make it look better
                offset = pygame.math.Vector2(5,15)
            else:
                offset = pygame.math.Vector2(-5,15)

            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset , 'land')
            self.dust_sprite.add(fall_dust_particle)

    def setup_level(self, layout):
        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        #loop to get each specific cell in the layout map
        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size

                if cell == 'X':
                    tile = Tile(tile_size, x, y)
                    self.tiles.add(tile)  #add the tile to the group

                if cell == 'P':
                    player_sprite = Player(x,y, self.display_surface, self.create_jump_particle)
                    self.player.add(player_sprite)

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < (screen_width/3) and direction_x < 0: #stop player from moving beyond this and scroll the map instead
            self.world_shift = 8
            player.speed = 0
        elif player_x > (screen_width - (screen_width/3)) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed

        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0: ##moving left
                    player.rect.left = sprite.rect.right #colliding left 
                    player.on_left = True
                    self.current_x = player.rect.left #check see if hugging a wall or not
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False

        if player.on_right and (player.rect.left > self.current_x or player.direction.x <= 0):
            player.on_right = False

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0: 
                    player.rect.bottom = sprite.rect.top 
                    player.direction.y = 0 #cancels gravity when touch the floor
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0 #cacnels move so doesnt stick to the top of tile
                    player.on_celing = True
        
        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0:
            player.on_celing = False

    def enemy_collision_constraints(self):
        for enemy in self.enemies_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraints_sprites, False):
                enemy.reverse()

    def run(self):

        #background
        self.background_sprites.draw(self.display_surface)
        self.background_sprites.update(self.world_shift)

        #TERRAIN
        self.terrain_sprites.draw(self.display_surface)
        self.terrain_sprites.update(self.world_shift)
        

        #DECOR/ BG Trees
        self.decor_sprites.update(self.world_shift)
        self.decor_sprites.draw(self.display_surface)

        #Spikes
        self.spikes_sprites.update(self.world_shift)
        self.spikes_sprites.draw(self.display_surface)
        

        #Enemy
        self.enemies_sprites.update(self.world_shift)
        self.constraints_sprites.update(self.world_shift) #CONSTRAINTS
        self.enemy_collision_constraints()
        self.enemies_sprites.draw(self.display_surface)

        

        #GRASS
        self.grass_sprites.update(self.world_shift)
        self.grass_sprites.draw(self.display_surface)

        #Arrows
        self.arrows_sprites.update(self.world_shift)
        self.arrows_sprites.draw(self.display_surface)

        #Player SPRITE
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        
        

        #DUST PARTICLES
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        #Level Tiles
        # self.tiles.update(self.world_shift)
        # self.tiles.draw(self.display_surface)
        self.scroll_x()

        #Player
        pygame.draw.rect(self.display_surface, (255,0,0), self.player.sprite.rect, 2)
        self.player.update()
        self.horizontal_movement_collision()
        self.get_player_on_ground() #before vert
        self.vertical_movement_collision()
        self.create_landing_dust() #after vert
        self.player.draw(self.display_surface)

        
        
        
        