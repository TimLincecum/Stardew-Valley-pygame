import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic,Water,WilldFlower,Tree,Interaction,Particle
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain,Sky
from random import randint
from menu import Menu

class Level :
    def __init__(self) :
        
        # get the display surface 获取显示
        self.display_surface = pygame.display.get_surface()

        # sprite groups ?精灵组
        # self.all_sprites = pygame.sprite.Group()
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.soil_layer = SoilLayer(self.all_sprites,self.collision_sprites)
        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset,self.player)

        # sky
        self.rain = Rain(self.all_sprites)
        # self.raining = False rain的开关
        self.raining = randint(0,10) > 3
        self.soil_layer.raining = self.raining
        self.sky = Sky()

        # shop
        self.menu = Menu(player = self.player, toggle_menu = self.toggle_shop)
        self.shop_active = False

        # music
        self.success = pygame.mixer.Sound('../audio/success.wav')
        self.success.set_volume(0.3)

        # 背景音乐
        self.music = pygame.mixer.Sound('../audio/嗨害嗨.wav')
        self.music.play(loops = -1)

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
            Tree(
                pos = (obj.x,obj.y),
                surf = obj.image,
                groups = [self.all_sprites,self.collision_sprites,self.tree_sprites],
                name = obj.name,
                player_add = self.player_add
                )  # ??? 确保这里不要调用，只想在内部调用

        # wildflowers
        for obj in tmx_data.get_layer_by_name('Decoration') :
            WilldFlower((obj.x,obj.y),obj.image,[self.all_sprites,self.collision_sprites])

        # collion tiles
        for x,y,surface in tmx_data.get_layer_by_name('Collision').tiles() :
            Generic((x * TILE_SIZE,y * TILE_SIZE), pygame.Surface((TILE_SIZE,TILE_SIZE)) , self.collision_sprites) # pos (x,y),surf,最后的参数self.collision_sprites改为👉更直观的看出边界[self.all_sprites,self.collision_sprites]


        # Player
        for obj in tmx_data.get_layer_by_name('Player') : # tmx文件中的初始位置，调用，使玩家位置不再卡在栏杆外
            if obj.name == 'Start' :
                self.player = Player(
                    pos = (obj.x,obj.y),
                    group = self.all_sprites,
                    collision_sprites = self.collision_sprites,
                    tree_sprites = self.tree_sprites, # 播放器再这个通用类之前运行，人物将在地板下 开始设置
                    interaction = self.interaction_sprites,
                    soil_layer = self.soil_layer,
                    toggle_shop = self.toggle_shop
                    )    
                
            if obj.name == 'Bed' :
                Interaction(pos = (obj.x,obj.y),
                            size = (obj.width,obj.height),
                            groups = self.interaction_sprites,
                            name = 'Bed' # obj.name
                            )
            if obj.name == 'Trader' :
                Interaction(pos = (obj.x,obj.y),
                            size = (obj.width,obj.height),
                            groups = self.interaction_sprites,
                            name = 'Trader' # obj.name
                            )
                
        Generic(
            pos = (0,0),
            surf = pygame.image.load('../graphics/world/ground.png').convert_alpha(),
            groups = self.all_sprites,
            z = LAYERS['ground']
            )

    def player_add(self,item) :

        self.player.item_inventory[item] += 1
        self.success.play()

    def toggle_shop(self) :

        self.shop_active = not self.shop_active

    def reset(self) : # 重置 需要一个过渡

        # plants
        self.soil_layer.update_plants()

        # soil
        self.soil_layer.remove_water()

        # randomize the rain
        self.raining = randint(0,10) > 3
        self.soil_layer.raining = self.raining
        if self.raining :
            self.soil_layer.water_all()

        # apples on the trees
        for tree in self.tree_sprites.sprites() :
            for apple in tree.apple_sprites.sprites() :
                apple.kill()
            tree.create_fruit()

        # sky
        self.sky.start_color = [255,255,255]

    def plant_collision(self) :
        if self.soil_layer.plant_sprites :
            for plant in self.soil_layer.plant_sprites.sprites() :
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox) :
                    self.player_add(plant.plant_type)
                    plant.kill()
                    Particle(plant.rect.topleft,plant.image,self.all_sprites,z = LAYERS['main']) # 粒子特效 pos, surf, groups, z
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P') # 删除原来的作物，以便播种下一次的作物
    # 这段代码实现了游戏中玩家与植物之间的碰撞检测和作物收获的逻辑。在 `plant_collision` 方法中，首先通过访问 `self.soil_layer.plant_sprites` 属性来获取所有的植物精灵组（Sprite Group）。然后，遍历这个精灵组中的每一个植物，如果该植物是可收获状态，且其矩形区域（hitbox）与玩家角色的矩形区域发生碰撞，则消除该植物对应的精灵，并释放资源（kill() 方法）。该方法通常会被包含在游戏主循环中，并以一定的频率进行调用，以保持游戏的正常运行。

    def run(self,dt) :
        # print("开始摆烂")

        # drawing logic
        self.display_surface.fill('red') #
        self.all_sprites.custom_draw(self.player)
        # self.all_sprites.draw(self.display_surface)

        # updates
        if self.shop_active :
            self.menu.update()
        else :
            self.all_sprites.update(dt)
            self.plant_collision() # 碰撞后收集

        # weather
        self.overlay.display()  ##注意缩进，缩进玩不明白写棒槌py
        # print(self.player.item_inventory)

        # rain
        if self.raining and not self.shop_active:
            self.rain.update() # 调用更新 然后更新耕地的瓦片

        # daytime
        self.sky.display(dt)

        # transition overlay
        if self.player.sleep :
            self.transition.play()
        # print(self.player.item_inventory) 测试收获
        # print(self.shop_active) 

class CameraGroup(pygame.sprite.Group) :
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

                    # 工具位置测试 定位 三个矩形
                    # if sprite == player :
                    #     pygame.draw.rect(self.display_surface,'red',offset_rect,5)
                    #     hitbox_rect = player.hitbox.copy()
                    #     hitbox_rect.center = offset_rect.center
                    #     pygame.draw.rect(self.display_surface,'green',hitbox_rect,5)
                    #     target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
                    #     pygame.draw.circle(self.display_surface,'blue',target_pos,5)