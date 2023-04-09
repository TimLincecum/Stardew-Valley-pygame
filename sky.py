import pygame
from settings import *
from support import import_folder
from sprites import Generic
from random import randint,choice

class Sky :
    def __init__(self) :
        self.display_surface = pygame.display.get_surface()
        self.full_surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT)) # 一个全黑的在屏幕顶部
        self.start_color = [255,255,255]
        self.end_color = (38,101,189)

    def display(self,dt) :
        for index,value in enumerate(self.end_color) :
            if self.start_color[index] > value :
                self.start_color[index] -= 2 * dt # 天黑的速度
            
        self.full_surf.fill(self.start_color)
        self.display_surface.blit(self.full_surf, (0,0), special_flags = pygame.BLEND_RGBA_MULT)

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