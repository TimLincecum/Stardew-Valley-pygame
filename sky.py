import pygame
from settings import *
from support import import_folder
from sprites import Generic
from random import randint,choice

class Drop(Generic) :
    def __init__(self, pos, moving, surf, groups, z):
        super().__init__(pos, surf, groups, z)

        # general setup 一般设置
        self.lifetime = randint(400,500)
        self.start_time = pygame.time.get_ticks()

        # moving
        self.moving = moving
        if self.moving :
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2,4)
            self.speed = randint(200,250)

    def update(self,dt) :
        # movement
        if self.moving :
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = (round(self.pos.x),round(self.pos.y))

        # timer
        if pygame.time.get_ticks()-self.start_time >= self.lifetime :
            self.kill()

class Rain :
    def __init__(self, all_sprites) :
        self.all_sprites = all_sprites
        self.rain_drops = import_folder('../graphics/rain/drops/')
        self.rain_floor = import_folder('../graphics/rain/floor/')
        self.floor_w,self.floor_h =  pygame.image.load('../graphics/world/ground.png').get_size() # 获取整张地图大小 下雨雨滴的地图覆盖

    def create_floor(self) :
        Drop(
            pos = (randint(0,self.floor_w),randint(0,self.floor_h)), # (0 -> w of the map  is  X ,)
            moving = False,
            surf = choice(self.rain_floor),
            groups = self.all_sprites,
            z = LAYERS['rain floor']
            )

    def create_drops(self) :
        Drop(pos = (randint(0,self.floor_w),randint(0,self.floor_h)), # (0 -> w of the map  is  X ,)
            moving = True,
            surf = choice(self.rain_drops),
            groups = self.all_sprites,
            z = LAYERS['rain drops']
            )


    def update(self) : # 创建更新
        self.create_drops()
        self.create_floor()