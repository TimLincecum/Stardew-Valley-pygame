import pygame
from settings import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite) :
    def __init__(self,pos,group,collision_sprites) :
        super().__init__(group)

        self.import_assets()
        # p4
        self.status = 'down'  # 这是下划线 keyerror
        self.frame_index = 0

        # general setup 基本设置
        # self.image = pygame.Surface((32,64)) w,h  ?
        self.image = self.animations[self.status][self.frame_index]

        # self.image.fill('green') 摆脱 ?
        self.rect = self.image.get_rect(center = pos) #    xy来自矩形
        # self.hitbox = self.rect.copy().inflate((-126,-70)) 👇 collisions (w,h) p11
        self.z = LAYERS['main'] #   z的单独变量

        # movement attributes 运动属性
        self.direction = pygame.math.Vector2() #x,y 默认0,0
        self.pos = pygame.math.Vector2(self.rect.center) #浮点数 平常存储用self.rect，但存储的是整数，相同时间增量就需要独立的方式定义
        self.speed = 200

        # collision
        self.hitbox = self.rect.copy().inflate((-126,-70))
        self.collision_sprites = collision_sprites

        # timers
        self.timers = {
            'tool use' : Timer(350,self.use_tool),
            'tool switch' : Timer(200),
            'seed use' : Timer(350,self.use_seed),
            'seed switch' : Timer(200)
        }

        # tools
        self.tools = ['axe','water','hoe']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]
        # self.selected_tool = 'water'

        # seeds
        self.seeds = ['corn','tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

    def use_tool(self) :
        pass
        # print(self.selected_tool)

    def use_seed(self) :
        pass

    def import_assets(self) : # 获取贴图
        self.animations = {'up': [],'down': [],'left': [],'right': [],
						   'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
						   'right_hoe':[],'left_hoe':[],'up_hoe':[],'down_hoe':[],
						   'right_axe':[],'left_axe':[],'up_axe':[],'down_axe':[],
						   'right_water':[],'left_water':[],'up_water':[],'down_water':[]}

        for animation in self.animations.keys() :
            full_path = '../graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)
        # print(self.animations)

    def animate(self,dt) : #    防止超出
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]) :
            self.frame_index = 0
        
        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers['tool use'].active : # 玩家不移动时，允许走动并使用工具
            # 方向 directions
            if keys[pygame.K_UP] :
                # print('up')
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN] :
                # print('down')
                self.direction.y = 1
                self.status = 'down'
            # 方向归零
            else:
                self.direction.y = 0


            if keys[pygame.K_RIGHT] :
                # print('right')
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT] :
                # print('left')
                self.direction.x = -1
                self.status = 'left'
            # 
            else:
                self.direction.x = 0

            # print(self.direction)

            # tool use
            if keys[pygame.K_SPACE] :
                # time for tool use
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # change tool
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                print(self.tool_index)
                self.tool_index += 1
                # if tool index > length of tools => tool index = 0
                self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
                self.selected_tool = self.tools[self.tool_index] # 会显示获取列表索引超出范围

            # seeds use
            if keys[pygame.K_LCTRL] :
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0
                # print('use seed')

            # change seed
            if keys[pygame.K_e] and not self.timers['seed switch'].active:
                self.timers['seed switch'].activate()
                print(self.seed_index)
                self.seed_index += 1
                self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
                self.selected_seed = self.seeds[self.seed_index]
                # print(self.selected_seed)

              
    def get_status(self) :
        # 如果玩家并未移动
        if self.direction.magnitude() == 0 :
            # 将 _idle 添加到 状态(status)
            # self.status += '_idle'
            self.status = self.status.split('_')[0] + '_idle'   # ?

        # tool use
        if self.timers['tool use'].active :
            # print('tool is being used') 空格调试
            # self.status = 'right_axe'
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def update_timers(self) :
        for timer in self.timers.values() :
            timer.update()

    def collision(self,direction) : # collide
        for sprite in self.collision_sprites.sprites() :
            if hasattr(sprite,'hitbox') : # hasattr() 函数用于判断对象是否包含对应的属性
                if sprite.hitbox.colliderect(self.hitbox) :
                    if direction == 'horizontal' :
                        if self.direction.x > 0 : # moving right
                            self.hitbox.right = self.hitbox.left
                        if self.direction.x < 0 : # moving left
                            self.hitbox.left = self.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx


    def move(self,dt) :
        # horizontal movement 归一化向量 
        # 向着非xy移动会有不同的速度，大概速率再1.4左右,需要保证向量总为1
        if self.direction.magnitude() > 0 : # ~0.7
            self.direction = self.direction.normalize()
        # print(self.direction)

        #  horizontal movement  水平移动
        self.pos.x += self.direction.x * self.speed * dt # 方向*网点速度*时间增量
        self.hitbox.centerx = round(self.pos.x) #   round四舍五入
        self.rect.centerx = self.hitbox.centerx # self.rect.centerx = self.position.x
        self.collision('horizontal')

        #  vertical movement    垂直移动
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        
    def update(self,dt) : # 每一帧调用一次，检测输入
        self.input()
        self.get_status()
        self.update_timers()
        self.move(dt) # 和帧速度率无关
        self.animate(dt)