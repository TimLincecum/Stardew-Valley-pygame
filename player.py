import pygame
from settings import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite) :
    def __init__(self,pos,group,collision_sprites,tree_sprites,interaction,soil_layer, toggle_shop) :
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
        self.hitbox = self.rect.copy().inflate((-126,-70)) # 创建自己的hitbox命中框
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

        # inventory 存货清单,玩家库存
        self.item_inventory = {
            'wood' : 20,
            'apple' : 20,
            'corn' : 20,
            'tomato' : 20
        }
        self.seed_inventory = { 
        'corn' : 5,
        'tomato' : 5
        }
        self.money = 200

        # interaction
        self.tree_sprites = tree_sprites
        self.interaction = interaction
        self.sleep = False
        self.soil_layer = soil_layer
        self.toggle_shop = toggle_shop

        # sound
        self.watering = pygame.mixer.Sound('../audio/嗨害嗨.wav')
        self.watering.set_volume(0.3)

    def use_tool(self) :
        # pass
        # print(self.selected_tool)

        # print('tool use') 加入soil_layer后，不必打印语句了，pass改为soil_layer，直接调用，这样就可以使用或定位它，方法是get_hit

        if self.selected_tool == 'hoe' :
            self.soil_layer.get_hit(self.target_pos)

        if self.selected_tool == 'axe' :
            for tree in self.tree_sprites.sprites() :
                if tree.rect.collidepoint(self.target_pos) :
                    tree.damage()

        if self.selected_tool == 'water' :
            self.soil_layer.water(self.target_pos)
            self.watering.play()

    def get_target_pos(self) :

        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
        # 举个栗子,现在是一个播放器，玩家在正中间，我们希望使用工具，假如玩家向左看，那么我希望玩家的工具使用是在左边一个身位并向下一点点的位置,也就是玩家的斜下方      更新它  别忘了!!!!!

    def use_seed(self) : # 种子
        # pass

        if self.seed_inventory[self.selected_seed] > 0 :
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
            self.seed_inventory[self.selected_seed] -= 1
        
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

        if not self.timers['tool use'].active and not self.sleep: # 玩家不移动时，允许走动并使用工具
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

            if keys[pygame.K_RETURN] :
                # self.toggle_shop()
                collided_interaction_sprites = pygame.sprite.spritecollide(self,self.interaction,False) # sprite, group, dokill
                if collided_interaction_sprites :
                    if collided_interaction_sprites[0].name == 'Trader' : # name是在sprites中定义的
                        # pass
                        self.toggle_shop()
                    else :
                        self.status = 'left_idle'
                        self.sleep = True
          
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

    def collision(self,direction) : # collide 碰撞
        for sprite in self.collision_sprites.sprites() :
            if hasattr(sprite,'hitbox') : # hasattr() 函数用于判断对象是否包含对应的属性
                if sprite.hitbox.colliderect(self.hitbox) :
                    if direction == 'horizontal' : # 左右碰撞
                        if self.direction.x > 0 : # moving right
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0 : # moving left
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
            
                    if  direction == 'vertical' : # 上下碰撞
                        if self.direction.y > 0 : # moving up
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0 : # moving down
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery
                        # 下方的collision不能忘记写
    # def collision(self,direction) : 
    # # 遍历所有需要进行碰撞检测的sprite列表
    # for sprite in self.collision_sprites.sprites() :
    #     if hasattr(sprite,'hitbox') :  # 如果该sprite具有hitbox属性
    #         if sprite.hitbox.colliderect(self.hitbox) : # 判断两个矩形是否相交
    #             if direction == 'horizontal' : # 左右碰撞
    #                 if self.direction.x > 0 : # 向右移动
    #                     self.hitbox.right = sprite.hitbox.left # 修改自身hitbox右侧位置
    #                 if self.direction.x < 0 : # 向左移动
    #                     self.hitbox.left = sprite.hitbox.right # 修改自身hitbox左侧位置
    #                 self.rect.centerx = self.hitbox.centerx # 修改sprite图像中心点位置
    #                 self.pos.x = self.hitbox.centerx # 修改sprite实际位置
    
    #             if  direction == 'vertical' : # 上下碰撞
    #                 if self.direction.y > 0 : # 向上移动
    #                     self.hitbox.bottom = sprite.hitbox.top # 修改自身hitbox底部位置
    #                 if self.direction.y < 0 : # 向下移动
    #                     self.hitbox.top = sprite.hitbox.bottom # 修改自身hitbox顶部位置
    #                 self.rect.centery = self.hitbox.centery # 修改sprite图像中心点位置
    #                 self.pos.y = self.hitbox.centery # 修改sprite实际位置

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
        self.collision('vertical')
        
    def update(self,dt) : # 每一帧调用一次，检测输入
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()


        self.move(dt) # 和帧速度率无关
        self.animate(dt)