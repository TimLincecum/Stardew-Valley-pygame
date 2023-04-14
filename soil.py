import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import *
from random import choice

class SoilTile(pygame.sprite.Sprite) :
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil']

class WaterTile(pygame.sprite.Sprite) :
    def __init__(self,pos,surf,groups) :
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil water']

class Plant(pygame.sprite.Sprite) : # 种植
    def __init__(self, plant_type, groups, soil, check_watered) :
    # plant_type 是植物的类型，用于查找正确的图像帧。
    # groups 是此植物所属的精灵组。
    # soil 是此植物种植在哪块土地上。
    # check_watered 是一个回调函数，用于检查该植物附近的水砖块是否被浇水过
        super().__init__(groups)

        # setup
        self.plant_type = plant_type
        self.frames = import_folder(f'../graphics/fruit/{plant_type}')
        self.soil = soil
        self.check_watered = check_watered
        
        # plant growing
        self.age = 0 # 成熟度
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[plant_type]

        # sprite setup
        self.image = self.frames[self.age]
        self.y_offset = -16 if plant_type == 'corn' else -8
        self.rect = self.image.get_rect(midbottom = soil.rect.midbottom + pygame.math.Vector2(0,self.y_offset))
        self.z = LAYERS['ground plant']
        self.harvestable = False # 是否可收获
    
    def grow(self) :
        if self.check_watered(self.rect.center) :
            self.age += self.grow_speed

            # if the plant age > 0
            if int(self.age) > 0 :
                self.z = LAYERS['main']
                self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * 0.4) # x,y 需要加入collision_sprites 

            if self.age >= self.max_age :
                self.age = self.max_age
                self.harvestable = True

            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom = self.soil.rect.midbottom + pygame.math.Vector2(0,self.y_offset))


class SoilLayer :
    def __init__(self, all_sprites, collision_sprites) :

        # sprite groups
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites 
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()

        # graphics
        self.soil_surf = pygame.image.load('../graphics/soil/o.png')
        self.water_surf = pygame.image.load('../graphics/soil_water/0.png')

        self.create_soil_grid()
        self.create_hit_rects()

        # sounds
        self.hoe_sound = pygame.mixer.Sound('../audio/hoe.wav')
        self.hoe_sound.set_volume(0.1)

        self.plant_sound = pygame.mixer.Sound('../audio/plant.wav')
        self.plant_sound.set_volume(0.2)

    # requirements
    # if the area is farmable
    # if the soil has been watered
    # if the soil has a plant
    def create_soil_grid(self) :
        # 创建列表在耕种区域，取分可耕种与否
        ground = pygame.image.load('../graphics/world/ground.png')
        # 获取瓷砖数量
        h_tiles,v_tiles = ground.get_width() // TILE_SIZE,ground.get_height() // TILE_SIZE
        # print(h_tiles) 50
        # print(v_tiles) 40
        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)] # 获取瓷砖为列表
        # print(self.grid)
        for x,y,_surf in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles() :
            self.grid[y][x].append('F')
        # print(self.grid) 可耕种的地方被标记为[F] 不可耕种则为[]

        # for row in self.grid :
        #     print(row) 

    def create_hit_rects(self) :
        self.hit_rects = []
        for index_row,row in enumerate(self.grid) :
            for index_col,cell in enumerate(row) :
                if 'F' in cell :
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    rect = pygame.Rect(x,y,TILE_SIZE,TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self,point) :
        for rect in self.hit_rects :
            if rect.collidepoint(point) :

                self.hoe_sound.play()

                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                if 'F' in self.grid[y][x] :
                    # print('farmable')
                    self.grid[y][x].append('X') # 告诉我们在这块瓷砖上我们有一块土壤
                    self.create_soil_tiles()
                    if self.raining :
                        self.water_all()
    
    def water(self,target_pos) :
        for soil_sprites in self.soil_sprites.sprites() :
            if soil_sprites.rect.collidepoint(target_pos) :

                # 1.add an entry to the soil grid -> 'W'
                x = soil_sprites.rect.x // TILE_SIZE
                y = soil_sprites.rect.y // TILE_SIZE
                self.grid[y][x].append('W')

                pos = soil_sprites.rect.topleft
                # surf = choice(self.water_surf)
                surf = self.water_surf
                # 2.create a water sprite 创造浇过水的耕地
                WaterTile(pos, surf, groups = [self.all_sprites,self.soil_sprites])
                # 1.copy the position from the soil sprite
                # 2.for the surface -> import the folder '../graphics/soil_water'
                # 3.random select one surface
                # 4.create one  more group 'water_sprites'

    def water_all(self) :
        for index_row,row in enumerate(self.grid) :
            for index_col,cell in enumerate(row) :
                if 'X' in cell and 'W' not in cell : # 检查是否有瓦片，并且未浇水(没有'W')
                    cell.append('W')
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    WaterTile((x,y), self.water_surf, groups = [self.all_sprites,self.soil_sprites])

    def remove_water(self) : # 水的消失
        
        # destory all water sprites
        for sprite in self.water_sprites.sprites() :
            sprite.kill()

        # clean up the grid
        for row in self.grid :
            for cell in row :
                if 'W' in cell:
                    cell.remove('W')

    def check_watered(self, pos) :
        x = pos[0] // TILE_SIZE
        y = pos[1] // TILE_SIZE
        cell = self.grid[y][x]
        is_watered = 'W' in cell
        return is_watered

    def plant_seed(self, target_pos, seed) : # 播种
        for soil_sprite in self.soil_sprites.sprites() :
            if soil_sprite.rect.collidepoint(target_pos) :
                self.plant_sound.play()

                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE

                if 'P' not in self.grid[y][x] :
                    self.grid[y][x].append('P') # plant
                    Plant(plant_type = seed, groups = [self.all_sprites,self.plant_sprites, self.collision_sprites], soil = soil_sprite, check_watered = self.check_watered)

    def update_plants(self) :
        for plant in self.plant_sprites.sprites() :
            plant.grow()

    def create_soil_tiles(self) :
        self.soil_sprites.empty() # 在前面赋值x的地方创建一个土壤瓦片
        for index_row,row in enumerate(self.grid) :
            for index_col,cell in enumerate(row) :
                if 'X' in cell :
                    SoilTile(pos =(index_col * TILE_SIZE,index_row * TILE_SIZE),
                             surf = self.soil_surf,
                             groups = [self.all_sprites,self.soil_sprites]
                            )