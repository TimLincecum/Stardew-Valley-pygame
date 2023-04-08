import pygame
from settings import *

class Overlay :
    def __init__(self,player):
        # 初始化道具和种子覆盖层类
        # general setup
        self.display_surface = pygame.display.get_surface() # 获取当前显示窗口表面对象
        self.player = player # 要涉及到的玩家实例

        # imports
        overlay_path = '../graphics/overlay/'    # 存储路径 道具和种子图片文件的存储路径
        # 创建包含所有道具、种子图片 Surface 对象的字典
        self.tools_surf = {tool : pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in player.tools}    #surface
        self.seeds_surf = {seed : pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha() for seed in player.seeds}
        # print(self.tools_surf) 得到具有键值对的字典 输出包含所有道具 Surface 对象的字典
        # print(self.seeds_surf) 输出包含所有种子 Surface 对象的字典

    def display(self) :  #注意缩进，缩进玩不明白写棒槌py
        # 显示道具和种子覆盖层
        # tool
        tool_surf = self.tools_surf[self.player.selected_tool] # 获取选中道具对应的 Surface 对象
        tool_rect = tool_surf.get_rect(midbottom = OVERLAY_POSITIONS['tool']) # 根据指定位置计算道具的矩形范围
        self.display_surface.blit(tool_surf,tool_rect)   #(0,0) 左上 在当前显示窗口表面对象上绘制道具图像

        # seed
        seed_surf = self.seeds_surf[self.player.selected_seed] # 获取选中种子对应的 Surface 对象
        seed_rect = seed_surf.get_rect(midbottom = OVERLAY_POSITIONS['seed']) # 根据指定位置计算种子的矩形范围
        self.display_surface.blit(seed_surf,seed_rect) # 在当前显示窗口表面对象上绘制种子图像