import pygame as ga
import sys
import random as ra


class Button:
    init_color = (255, 255, 255)
    running_color = (0, 255, 0)
    word_size = 15

    def __init__(self, name, pos, if_change_color, init_state: bool = False):
        self.name = name
        self.font = ga.font.SysFont('SimHei', 15)
        self.pos = pos
        self.state = init_state
        self.if_change_color = if_change_color
        self.size = len(name) * Button.word_size + 10, Button.word_size + 10
        self.rect = (pos[0], pos[1], self.size[0], self.size[1])
        self.color = Button.running_color if init_state and if_change_color else Button.init_color
        self.label = self.font.render(self.name, True, self.color)
        self.word_pos = (pos[0] + 5, pos[1] + 5)

    def reverse_state(self):
        self.state = not self.state
        if self.if_change_color:
            self.color = Button.running_color if self.state else Button.init_color
            self.label = self.font.render(self.name, True, self.color)

    def draw(self, screen: ga.Surface):
        ga.draw.rect(screen, Button.init_color, self.rect, 1)
        screen.blit(self.label, self.word_pos)


class CellAutomaton:
    class LifeCell:
        def __init__(self, pos, state=False):
            self.state = state  # False为死亡
            self.num_state = 1 if self.state else 0
            self.next_state = state
            self.pos = pos
            self.radius = 5

        def change_state(self, new_state: bool):
            self.next_state = new_state

        def draw(self, screen: ga.Surface):
            if self.state:
                ga.draw.circle(screen, (255, 255, 255), self.pos, self.radius)
            self.state = self.next_state
            self.num_state = 1 if self.state else 0

    class Fish:
        def __init__(self, pos):
            self.true_pos = pos  # 鱼的真实位置
            self.pos = (int(self.true_pos[0]) % 1200 + 100, int(self.true_pos[1]) % 500 + 50)  # 屏幕位置
            self.abs_pos = (0, 0)  # 鱼的数组位置
            self.speed = (2 * ra.random() - 1, 2 * ra.random() - 1)  # 该鱼运动方向
            self.abs_speed = self.speed[0] ** 2 + self.speed[1] ** 2
            self.next_speed = self.speed
            self.if_king = False  # 是否为领路者
            self.king = None  # 该鱼所追随的对象
            self.get_abs_pos()

        def rand_fast(self):  # 获得更快的速度
            self.next_speed = (1.5 * (2 * ra.random() - 1), 1.5 * (2 * ra.random() - 1))  # 该鱼运动方向

        def get_next_speed(self):
            if self.if_king:
                if ra.random() < 0.01:
                    self.rand_fast()
            if self.king is None:
                self.speed = self.next_speed
            else:
                """speed = (self.king.true_pos[0] - self.true_pos[0],
                         self.king.true_pos[1] - self.true_pos[1])"""
                speed = (int(self.king.true_pos[0]) % 1200 - int(self.true_pos[0]) % 1200,
                         int(self.king.true_pos[1]) % 500 - int(self.true_pos[1]) % 500)
                m = (speed[0] ** 2 + speed[1] ** 2) ** 0.5
                try:
                    self.speed = (speed[0] / m, speed[1] / m)
                except ZeroDivisionError:
                    self.speed = (speed[0], speed[1])
            self.pos = (int(self.true_pos[0]) % 1200 + 100, int(self.true_pos[1]) % 500 + 50)

        def rand_speed(self):
            self.next_speed = (2 * ra.random() - 1, 2 * ra.random() - 1)  # 该鱼运动方向

        def get_abs_pos(self):
            x = int(self.true_pos[0] - 100) % 50
            y = int(self.true_pos[1] - 50) % 50
            self.abs_pos = (x, y)

        def draw(self, screen: ga.Surface):
            ga.draw.circle(screen, (255, 0, 0) if self.if_king else (255, 255, 255), self.pos, 5)
            self.true_pos = (self.true_pos[0] + self.speed[0], self.true_pos[1] + self.speed[1])
            self.get_next_speed()
            self.get_abs_pos()

    def __init__(self, name):
        self.size = 1000, 500
        self.rect = (100, 50, 1000, 500)
        self.color = (255, 255, 255)
        self.if_run = False
        self.name = name
        self.cell_world = []  # 元胞环境
        self.fish_dict = {}  # 鱼群位置字典
        self.if_mouse_in_here = False  # False代表鼠标不在环境内
        self.if_cross_screen = True  # 是否会跨屏运行
        self.fish_state = None  # 鱼群行为
        self.if_see_line = False  # 是否可视追踪
        self.init_data()

    def init_data(self):
        if self.name == '生命游戏':
            self.cell_world = []  # 元胞环境
            for i in range(self.size[0] // 10):
                line_world = []
                for j in range(self.size[1] // 10):
                    line_world.append(CellAutomaton.LifeCell((i * 10 + 105, j * 10 + 55)))
                self.cell_world.append(line_world)
        elif self.name == '群体行为':
            self.cell_world = []  # 元胞环境
            for i in range(25):
                for j in range(10):
                    self.cell_world.append(CellAutomaton.Fish((i * 50 + 105, j * 50 + 55)))

    def rand_fish_king(self):  # 随机生成一个领路鱼
        fish = ra.choice(self.cell_world)
        fish.if_king = True
        fish.king = None
        fish.rand_fast()

    def get_fish_dict(self):  # 刷新鱼群字典
        self.fish_dict = {}
        for fish in self.cell_world:
            k = self.fish_dict.get(fish.abs_pos)
            if k is None:
                self.fish_dict[fish.abs_pos] = [fish]
            else:
                self.fish_dict[fish.abs_pos].append(fish)

    def init_fish(self):
        for k in self.cell_world:
            k.rand_speed()
            k.if_king = False
            k.king = None

    def init_life_cell(self):
        for k in self.cell_world:
            for cell in k:
                cell.change_state(False)

    def glider(self):
        self.init_life_cell()
        glider_list = [(50, 20), (50, 22), (51, 21), (51, 22), (49, 22)]
        for x, y in glider_list:
            self.cell_world[x][y].change_state(True)

    def l_wss(self):
        self.init_life_cell()
        glider_list = [(50, 20), (50, 22), (51, 23), (52, 23), (53, 23), (54, 23), (54, 22), (54, 21), (53, 20)]
        for x, y in glider_list:
            self.cell_world[x][y].change_state(True)

    def gos(self):
        self.init_life_cell()
        glider_list = [(57, 0), (56, 1), (56, 2), (55, 2), (54, 3),
                       (53, 3), (55, 4), (56, 4), (56, 5), (59, 0),
                       (59, 1), (58, 3), (59, 5), (57, 6), (48, 3),
                       (47, 3), (47, 4), (48, 4), (59, 6), (62, 5),
                       (62, 6), (63, 5), (62, 7), (63, 7), (64, 7),
                       (63, 8), (64, 8), (65, 7), (65, 6), (66, 6),
                       (67, 6), (66, 4), (67, 3), (67, 2), (73, 3),
                       (74, 2), (75, 3), (73, 4), (74, 4), (73, 5),
                       (74, 5), (73, 6), (74, 6), (73, 7), (74, 8),
                       (75, 7), (76, 6), (76, 5), (76, 4), (77, 5),
                       (81, 5), (82, 5), (81, 6), (82, 6)]
        for x, y in glider_list:
            self.cell_world[x][y].change_state(True)

    def draw(self, screen: ga.Surface):
        if self.name == '群体行为':
            if self.if_see_line:
                for m in self.cell_world:
                    m.draw(screen)
                    if m.king is not None:
                        ga.draw.line(screen, (255, 255, 255), m.pos, m.king.pos)
            else:
                for m in self.cell_world:
                    m.draw(screen)
            self.get_fish_dict()
            if self.fish_state == '聚合群体':
                for fish in self.cell_world:
                    if not fish.if_king:
                        continue
                    fish_list = self.fish_dict[fish.abs_pos]
                    if len(fish_list) == 1:
                        continue
                    for fish_here in fish_list:
                        if fish_here != fish and fish_here.king is None:
                            fish_here.king = fish
            return None
        ga.draw.rect(screen, self.color, self.rect, 1)
        for m in self.cell_world:
            for a in m:
                a.draw(screen)
        x = 0
        for k in self.cell_world:
            y = 0
            for cell in k:
                if self.if_run:
                    if not self.if_cross_screen:
                        left_x = x - 1
                        right_x = x + 1
                        top_y = y - 1
                        low_y = y + 1
                    else:
                        left_x = ((x - 1) + 100) % 100
                        right_x = ((x + 1) + 100) % 100
                        top_y = ((y - 1) + 50) % 50
                        low_y = ((y + 1) + 50) % 50
                    num = -1 * self.cell_world[x][y].num_state
                    for a in [left_x, x, right_x]:
                        for b in [top_y, y, low_y]:
                            try:
                                if a == -1 or b == -1:
                                    continue
                                num += self.cell_world[a][b].num_state * 2
                            except IndexError:
                                num += 0
                    if num in [5, 6, 7]:
                        cell.change_state(True)
                    else:
                        cell.change_state(False)
                y += 1
            x += 1


class Mind:
    def __init__(self):
        self.size = 1400, 600
        self.clock = ga.time.Clock()
        self.screen = ga.display.set_mode(self.size)
        self.fps = 60
        self.time_max = self.fps
        self.time_now = 0  # 当前时间
        self.if_time_run = False  # 时间开关
        self.speed = 3  # 速率控制
        self.button_dict = {}  # 按钮字典
        self.automaton = CellAutomaton('生命游戏')
        self.abs_mouse_pos = (0, 0)  # 鼠标相对坐标
        self.changing = False  # 用于控制鼠标激活细胞
        self.ready_button = None  # 当前所准备的按钮
        self.log = []  # 记录列表
        self.init_data()

    def init_data(self):
        if self.automaton.name == '生命游戏':
            self.button_dict = {'生命游戏': Button('生命游戏', (0, 50), True, True),
                                '群体行为': Button('群体行为', (0, 100), True, False),
                                '开始运行': Button('开始运行', (1200, 50), True, False),
                                '逐帧运行': Button('逐帧运行', (1300, 50), False, False),
                                '跨屏运行': Button('跨屏运行', (1100, 50), True, True),
                                '初始化': Button(' 初始化', (1200, 100), False, False),
                                '滑翔机': Button(' 滑翔机', (1200, 150), False, False),
                                '轻型飞机': Button('轻型飞机', (1200, 200), False, False),
                                '高斯帕': Button('高斯帕滑翔机枪', (1200, 250), False, False)}
            self.automaton.init_data()
        elif self.automaton.name == '群体行为':
            self.button_dict = {'生命游戏': Button('生命游戏', (0, 50), True, False),
                                '群体行为': Button('群体行为', (0, 100), True, True),
                                '初始群体': Button('初始群体', (1320, 50), False, False),
                                '聚合群体': Button('聚合群体', (1320, 100), False, False),
                                '可视追踪': Button('可视追踪', (1320, 150), True, False)}
            self.automaton.init_data()

    def draw(self):
        mouse_pos = ga.mouse.get_pos()
        if self.automaton.name == '生命游戏':
            x = (mouse_pos[0] - self.automaton.rect[0]) // 10
            y = (mouse_pos[1] - self.automaton.rect[1]) // 10
            self.abs_mouse_pos = (x, y)
            max_x = self.automaton.size[0] // 10
            max_y = self.automaton.size[1] // 10
            if (0 <= x < max_x) and (0 <= y < max_y):
                self.automaton.if_mouse_in_here = True
            else:
                self.automaton.if_mouse_in_here = False
            if self.changing and self.automaton.if_mouse_in_here:
                self.automaton.cell_world[x][y].change_state(True)
        in_button = False
        for key, value in self.button_dict.items():
            value.draw(self.screen)
            x = mouse_pos[0] - value.rect[0]
            y = mouse_pos[1] - value.rect[1]
            if 0 <= x <= value.size[0] and 0 <= y <= value.size[1]:
                self.ready_button = value
                in_button = True
        if not in_button:
            self.ready_button = None
        self.automaton.draw(self.screen)

    def deal_event(self, event_type):
        if event_type == 'MOUSE_LEFT_DOWN':
            self.log.append(self.abs_mouse_pos)
            if self.automaton.if_mouse_in_here:
                self.changing = True
            if self.ready_button is not None:
                if self.ready_button.name == '开始运行':
                    self.ready_button.reverse_state()
                    if self.ready_button.state:
                        self.automaton.if_run = True
                    else:
                        self.automaton.if_run = False
                elif self.ready_button.name == ' 初始化':
                    self.automaton.init_life_cell()
                elif self.ready_button.name == ' 滑翔机':
                    self.automaton.glider()
                elif self.ready_button.name == '轻型飞机':
                    self.automaton.l_wss()
                elif self.ready_button.name == '逐帧运行':
                    self.automaton.if_run = True
                    self.automaton.draw(self.screen)
                    self.automaton.if_run = False
                elif self.ready_button.name == '高斯帕滑翔机枪':
                    self.automaton.gos()
                elif self.ready_button.name == '跨屏运行':
                    self.ready_button.reverse_state()
                    self.automaton.if_cross_screen = self.ready_button.state
                elif self.ready_button.name == '群体行为' or self.ready_button.name == '生命游戏':
                    self.ready_button.reverse_state()
                    if self.ready_button.name == '群体行为':
                        name = '生命游戏'
                    else:
                        name = '群体行为'
                    self.button_dict[name].reverse_state()
                    if self.button_dict['生命游戏'].state:
                        self.automaton.name = '生命游戏'
                    elif self.button_dict['群体行为'].state:
                        self.automaton.name = '群体行为'
                    self.init_data()
                elif self.ready_button.name == '初始群体':
                    self.automaton.init_fish()
                    self.automaton.fish_state = None
                    self.automaton.if_see_line = False
                elif self.ready_button.name == '聚合群体':
                    self.automaton.fish_state = '聚合群体'
                    self.automaton.rand_fish_king()
                elif self.ready_button.name == '可视追踪':
                    self.ready_button.reverse_state()
                    self.automaton.if_see_line = self.ready_button.state

        elif event_type == 'MOUSE_LEFT_UP':
            self.changing = False
        elif event_type == 'MOUSE_RIGHT_DOWN':
            if self.abs_mouse_pos in self.log:
                self.log.remove(self.abs_mouse_pos)
            if self.automaton.if_mouse_in_here:
                self.automaton.cell_world[self.abs_mouse_pos[0]][self.abs_mouse_pos[1]].change_state(False)
        elif event_type == 'KEY_SPACE':
            print(self.log)


def run():
    ga.init()
    ga.display.set_caption("生命游戏")
    mind = Mind()
    while True:
        mind.screen.fill((0, 0, 0))
        mind.draw()
        for event in ga.event.get():
            if event.type == ga.QUIT:
                sys.exit()
            elif event.type == ga.MOUSEMOTION:
                # buttons
                mind.mouse_pos = event.pos
            elif event.type == ga.MOUSEBUTTONDOWN:
                # button  左1 右3 向下5 向上4
                if event.button == 1:
                    mind.deal_event('MOUSE_LEFT_DOWN')
                elif event.button == 3:
                    mind.deal_event('MOUSE_RIGHT_DOWN')
                elif event.button == 4:
                    pass
            elif event.type == ga.MOUSEBUTTONUP:
                # button
                if event.button == 1:
                    mind.deal_event('MOUSE_LEFT_UP')
            elif event.type == ga.KEYDOWN:
                # 空格32
                mind.deal_event('KEY_SPACE')
        mind.clock.tick(mind.fps)
        ga.display.update()


run()
