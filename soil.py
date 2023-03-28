import pygame
from settings import *
from pytmx.util_pygame import load_pygame
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

class SoilLayer :
    def __init__(self, all_sprites) :

        # sprite groups
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()

        # graphics
        self.soil_surf = pygame.image.load('../graphics/soil/o.png')
        self.water_surf = pygame.image.load('../graphics/soil_water/0.png')

        self.create_soil_grid()
        self.create_hit_rects()

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
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                if 'F' in self.grid[y][x] :
                    # print('farmable')
                    self.grid[y][x].append('X') # 告诉我们在这块瓷砖上我们有一块土壤
                    self.create_soil_tiles()
    
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

    def remove_water(self) : # 水的消失
        
        # destory all water sprites
        for sprite in self.water_sprites.sprites() :
            sprite.kill()

        # clean up the grid
        for row in self.grid :
            for cell in row :
                if 'W' in cell:
                    cell.remove('W')

    def create_soil_tiles(self) :
        self.soil_sprites.empty() # 在前面赋值x的地方创建一个土壤瓦片
        for index_row,row in enumerate(self.grid) :
            for index_col,cell in enumerate(row) :
                if 'X' in cell :
                    SoilTile(pos =(index_col * TILE_SIZE,index_row * TILE_SIZE),
                             surf = self.soil_surf,
                             groups = [self.all_sprites,self.soil_sprites]
                            )