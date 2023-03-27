import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic,Water,WilldFlower,Tree,Interaction
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition

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

        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset,self.player)

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
                    interaction = self.interaction_sprites
                    )    
                
            if obj.name == 'Bed' :
                Interaction(pos = (obj.x,obj.y),
                            size = (obj.width,obj.height),
                            groups = self.interaction_sprites,
                            name = 'Bed' # obj.name
                            )
            
        Generic(
            pos = (0,0),
            surf = pygame.image.load('../graphics/world/ground.png').convert_alpha(),
            groups = self.all_sprites,
            z = LAYERS['ground']
            )

    def player_add(self,item) :

        self.player.item_inventory[item] += 1

    def reset(self) : # 需要一个过渡

        # apples on the trees
        for tree in self.tree_sprites.sprites() :
            for apple in tree.apple_sprites.sprites() :
                apple.kill()
            tree.create_fruit()

    def run(self,dt) :
        # print("开始摆烂")
        self.display_surface.fill('red') #
        # self.all_sprites.draw(self.display_surface)
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)

        self.overlay.display()  ##注意缩进，缩进玩不明白写棒槌py
        # print(self.player.item_inventory)

        if self.player.sleep :
            self.transition.play()

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
                    if sprite == player :
                        pygame.draw.rect(self.display_surface,'red',offset_rect,5)
                        hitbox_rect = player.hitbox.copy()
                        hitbox_rect.center = offset_rect.center
                        pygame.draw.rect(self.display_surface,'green',hitbox_rect,5)
                        target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
                        pygame.draw.circle(self.display_surface,'blue',target_pos,5)