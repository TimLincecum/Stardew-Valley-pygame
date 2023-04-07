# 引入所需模块和类
import pygame,sys
from settings import *
from level import Level

# 定义游戏类
class Game:
    def __init__(self):
        # 初始化 Pygame
        pygame.init()
        # 创建一个窗口对象并设置尺寸
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # 设置窗口标题
        pygame.display.set_caption('GLing evering')
        # 创建一个时钟对象
        self.clock = pygame.time.Clock()
        # 创建关卡对象
        self.level = Level()

    # 运行游戏循环
    def run(self):
        while True:
            # 检查事件队列中的所有事件
            for event in pygame.event.get():
                # 如果检测到关闭窗口事件，则退出程序
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # 计算增量时间
            dt = self.clock.tick() / 1000
            # 调用关卡对象的 run() 方法更新游戏状态
            self.level.run(dt)
            # 刷新显示
            pygame.display.update()

# 如果当前文件被直接运行，则执行以下语句
if __name__ == '__main__':
    # 创建一个游戏对象
    game = Game()
    # 运行游戏循环
    game.run()




###############################################################
#
# 　　　┏┓　　　┏┓
# 　　┏┛┻━━━┛┻┓
# 　　┃　　　　　　　 ┃
# 　　┃　　　━　　　 ┃
# 　　┃　┳┛　┗┳　┃
# 　　┃　　　　　　　 ┃
# 　　┃　　　┻　　　 ┃
# 　　┃　　　　　　　 ┃
# 　　┗━┓　　　┏━┛Codes are far away from bugs with the animal protecting
# 　　　　┃　　　┃    神兽保佑,代码无bug
# 　　　　┃　　　┃
# 　　　　┃　　　┗━━━┓
# 　　　　┃　　　　　 ┣┓
# 　　　　┃　　　　 ┏┛
# 　　　　┗┓┓┏━┳┓┏┛
# 　　　　　┃┫┫　┃┫┫
# 　　　　　┗┻┛　┗┻┛
#
#
###############################################################

# import pygame,sys
# from settings import *
# from level import Level

# class Game:
#     def __init__(self):
#         pygame.init #检查pygame包是否完整
#         self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
#         pygame.display.set_caption('GLing evering') #标题
#         self.clock = pygame.time.Clock()
#         self.level = Level()

#     def run(self): #检查游戏运行
#         while True:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     pygame.quit()
#                     sys.exit()
            
#             dt = self.clock.tick() / 1000
#             # 增量时间
#             self.level.run(dt)
#             pygame.display.update()

# if __name__ == '__main__':
#     game =  Game()
#     game.run()