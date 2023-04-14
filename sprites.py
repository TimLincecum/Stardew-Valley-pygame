import pygame
from settings import *
from random import randint,choice
from timer import Timer

# pygame.sprite.Sprite 是一个 Pygame 内置的精灵类，是所有精灵类的基类。它提供了一些基础的属性和方法，使得继承它的子类可以更加简单地实现其他高级功能。
# image：表示精灵图像的表面。
# rect：表示精灵位置和大小的矩形。
# mask：表示精灵的碰撞区域的掩码，用于进行像素级别的碰撞检测。
# groups：表示精灵所在的精灵组。
# add()：将精灵添加到指定的精灵组中。
# remove()：将精灵从指定的精灵组中移除。
# kill()：从所有精灵组中移除该精灵，并清空其引用（以便垃圾回收）。

class Generic(pygame.sprite.Sprite) :
    def __init__(self,pos,surf,groups,z = LAYERS['main']) :
        super().__init__(groups)
        self.image = surf # 图像表面
        self.rect = self.image.get_rect(topleft = pos) # 矩形范围
        self.z = z # 图层顺序
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2,-self.rect.height * 0.75) # ? 碰撞箱

class Interaction(Generic) :
    def __init__(self, pos, size, groups, name):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups)
        self.name = name # 具体交互元素名称

class Water(Generic) :
    def __init__(self, pos, frames, groups) :

        # 动画参数 animation setup
        self.frames = frames 
        self.frame_index = 0

        # 精灵初始化 sprite setup
        super().__init__(pos = pos,
                       surf = self.frames[self.frame_index],
                       groups = groups,
                       z = LAYERS['water'])
        
    def animate(self,dt) :
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames) :
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self,dt) :
        self.animate(dt)

class WilldFlower(Generic) :
    def __init__(self,pos,surf,groups) :
        super().__init__(pos,surf,groups)
        self.hitbox = self.rect.copy().inflate(-20,-self.rect.height * 0.9) # 碰撞箱

class Particle(Generic) : # 粒子特效
    def __init__(self, pos, surf, groups, z, duration = 200) :
        super().__init__(pos, surf, groups, z)
        # 开始时间和持续时间
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

        ## 去除黑色背景 white surface
        mask_surf = pygame.mask.from_surface(self.image) # 蒙版表面
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey((0,0,0)) # 摆脱的颜色是黑色，所以元组的值未0,0,0
        self.image = new_surf

    def update(self,dt) : # 半秒后消失....？
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration :
            self.kill()

class Tree(Generic) :
    def __init__(self, pos, surf, groups, name, player_add):
        super().__init__(pos, surf, groups)

        # 树属性 tree attributes
        self.health = 5
        self.alive = True
        # 残株表面
        stump_path = f'../graphics/stumps/{"small" if name == "Small" else "large"}.png' 
        self.stump_surf = pygame.image.load(stump_path).convert_alpha()
        # self.invul_timer = Timer(200)

        # apple
        self.apple_surf = pygame.image.load('../graphics/fruit/apple.png')
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

        self.player_add = player_add

        # sounds 音效
        self.axe_sound = pygame.mixer.Sound('../audio/嗨害嗨.wav') # 记得调用更新 play sound

    def damage(self) : 
        # damaging the tree 对树造成伤害
        self.health -= 1

        # play sound
        self.axe_sound.play()

        # remove an apple 摧毁苹果树
        if len(self.apple_sprites.sprites()) > 0 :
            random_apple = choice(self.apple_sprites.sprites())
            Particle(
                     pos = random_apple.rect.topleft, # 和苹果一样的位置
                     surf = random_apple.image,
                     groups = self.groups()[0], 
                     z = LAYERS['fruit']
                     ) # 调用粒子特效
            self.player_add('apple')
            random_apple.kill()
        
    def check_death(self) :
        if self.health <= 0 :
            # print('dead')
            Particle(self.rect.topleft, self.image, self.groups()[0], LAYERS['fruit'], 400) # ??? 生成粒子特效
            self.image = self.stump_surf # 残株表面
            # 更新矩形范围
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10,-self.rect.height * 0.6) # w,h
            # 设置标志
            self.alive = False
            # 增加玩家资源
            self.player_add('wood')
    
    def update(self,dt) :
        if self.alive:
            self.check_death()

    def create_fruit(self) : # 苹果的建立
        for pos in self.apple_pos :
            if randint(0,10) < 2 :
                x = pos[0] + self.rect.left
                y = pos[1] + self.rect.top
                Generic( # 添加苹果精灵到分组中
                    pos = (x,y),
                    surf = self.apple_surf,
                    groups=[self.apple_sprites,self.groups()[0]],
                    z = LAYERS['fruit']
                    )   # pos , surf , group