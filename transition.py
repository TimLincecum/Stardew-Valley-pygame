import pygame
from settings import *

# 黑夜到白天的度过
class Transition :
    def __init__(self, reset, player) :

        # setup 设置显示表面、重置函数和玩家对象
        self.display_surface = pygame.display.get_surface()
        self.reset = reset
        self.player = player

        # overlay image     创建黑色图像，改变透明度  创建黑色叠加表面，并初始化颜色和速度属性
        self.image = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.color = 255
        self.speed = -2

    def play(self) :
        # 1.call reset
        # 2.wake up the player
        # 3.set the speed to -2 at the end of the transition

        self.color += self.speed # 更新颜色属性和黑色表面

        if self.color <= 0 :
            self.speed *= -1
            self.color = 0
            self.reset()
        if self.color > 255 :
            self.color = 255
            self.player.sleep = False
            self.speed = -2

        self.image.fill((self.color, self.color, self.color)) # r,g,b 填充黑色表面
        self.display_surface.blit(self.image, (0,0), special_flags = pygame.BLEND_RGBA_MULT)