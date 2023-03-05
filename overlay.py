import pygame
from settings import *

class Overlay :
    def __init__(self,player):
        
        # general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player

        # imports
        overlay_path = '../graphics/overlay/'    # 存储路径
        self.tools_surf = {tool : pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in player.tools}    #surface
        self.seeds_surf = {seed : pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha() for seed in player.seeds}
        # print(self.tools_surf) 得到具有键值对的字典
        # print(self.seeds_surf)

    def display(self) :  #注意缩进，缩进玩不明白写棒槌py

        # tool
        tool_surf = self.tools_surf[self.player.selected_tool]
        tool_rect = tool_surf.get_rect(midbottom = OVERLAY_POSITIONS['tool'])
        self.display_surface.blit(tool_surf,tool_rect)   #(0,0) 左上

        # seed
        seed_surf = self.seeds_surf[self.player.selected_seed]
        seed_rect = seed_surf.get_rect(midbottom = OVERLAY_POSITIONS['seed'])
        self.display_surface.blit(seed_surf,seed_rect)