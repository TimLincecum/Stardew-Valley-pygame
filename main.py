import pygame,sys
from settings import *
from level import Level

class Game:
    def __init__(self):
        pygame.init #检查pygame包是否完整
        self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        pygame.display.set_caption('GLing evering') #标题
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self): #检查游戏运行
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            dt = self.clock.tick() / 1000
            # 增量时间
            self.level.run(dt)
            pygame.display.update()

if __name__ == '__main__':
    game =  Game()
    game.run()