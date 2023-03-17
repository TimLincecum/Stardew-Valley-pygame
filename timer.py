import pygame

class Timer :
    def __init__(self,duration,func = None) :
        self.duration = duration
        self.func = func
        self.start_time = 0
        self.active = False

    def activate(self) :
        self.active = True
        self.start_time = pygame.time.get_ticks()
    
    def deactivate(self) :
        self.active = False
        self.start_time = 0

    def update(self) :
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration :
            # self.deactivate() 如果在这里，每次运行后都会归零，下面的判断不会生效
            if self.func and self.start_time != 0 :
                self.func()
            self.deactivate()   # 开始判断