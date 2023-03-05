import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic,Water,WilldFlower,Tree
from pytmx.util_pygame import load_pygame
from support import *

class Level :
    def __init__(self) :
        
        # get the display surface 获取显示
        self.display_surface = pygame.display.get_surface()

        # sprite groups ?精灵组
        # self.all_sprites = pygame.sprite.Group()
        self.all_sprites = GameraGroup()
        self.collision_sprites = pygame.sprite.Group()

        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self) :

        tmx_data = load_pygame('../data/map.tmx')

        # house
        for layer in ['HouseFloor' , 'HouseFurnitureBottom'] :
            for x , y, surface in tmx_data.get_layer_by_name(layer).tiles() :
                Generic((x * TILE_SIZE,y * TILE_SIZE), surface, self.all_sprites, LAYERS['house bottom'])     #(pos,surface,groups,z)
        
        for layer in ['HouseWalls' , 'HouseFurnitureTop'] :
            for x , y, surface in tmx_data.get_layer_by_name(layer).tiles() :
                Generic((x * TILE_SIZE,y * TILE_SIZE), surface, self.all_sprites)

        # Fence
        for x, y, surface in tmx_data.get_layer_by_name('Fence').tiles() :
            Generic((x * TILE_SIZE,y * TILE_SIZE),surface,[self.all_sprites,self.collision_sprites])
        
        # water
        water_frames = import_folder('../graphics/water')
        for x, y, surface in tmx_data.get_layer_by_name('Water').tiles() :
            Water((x * TILE_SIZE,y * TILE_SIZE), water_frames, self.all_sprites) # 水不用self.collision_sprites

        # trees
        for obj in tmx_data.get_layer_by_name('Trees') :
            Tree((obj.x,obj.y),obj.image,[self.all_sprites,self.collision_sprites],obj.name)

        # wildflowers
        for obj in tmx_data.get_layer_by_name('Decoration') :
            WilldFlower((obj.x,obj.y),obj.image,[self.all_sprites,self.collision_sprites])

        self.player = Player((640,360),self.all_sprites,self.collision_sprites)    #播放器再这个通用类之前运行，人物将在地板下 开始设置
        Generic(
            pos = (0,0),
            surf = pygame.image.load('../graphics/world/ground.png').convert_alpha(),
            groups = self.all_sprites,
            z = LAYERS['ground']
            )
        

    def run(self,dt) :
        # print("开始摆烂")
        self.display_surface.fill('red') #
        # self.all_sprites.draw(self.display_surface)
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)

        self.overlay.display()  ##注意缩进，缩进玩不明白写棒槌py

class GameraGroup(pygame.sprite.Group) :
    def __init__(self) :
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self,player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites() , key = lambda sprite : sprite.rect.centery) : # ? p10 26:30    绘制贴图的先后顺序
                if sprite.z == layer :
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    
                    self.display_surface.blit(sprite.image,offset_rect)