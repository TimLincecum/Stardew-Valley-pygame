import pygame

class Timer :
    def __init__(self,duration,func = None) :
        # 持续时间和回调函数
        self.duration = duration
        self.func = func
        # 开始时间和是否激活标志
        self.start_time = 0
        self.active = False

    def activate(self) :
        self.active = True
        self.start_time = pygame.time.get_ticks()
    
    def deactivate(self) :
        self.active = False
        self.start_time = 0

    def update(self) :
        # 判断是否结束
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration :
            # self.deactivate() 如果在这里，每次运行后都会归零，下面的判断不会生效
            if self.func and self.start_time != 0 : # 可选的回调函数
                self.func()
            self.deactivate()   # 开始判断 停止计时器