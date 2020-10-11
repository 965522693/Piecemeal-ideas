import pygame as ga
import sys
import random as ra


class Mind:

    def __init__(self):
        self.size = 1400, 600
        self.clock = ga.time.Clock()
        self.screen = ga.display.set_mode(self.size)
        self.fps = 60
        self.buttons = {'left': [], 'right': [], 'other': []}  # 按钮字典
        self.labels = {}  # 标签字典
        self.bars = {}  # 旋钮字典
        self.setting_bar = None  # 正在调整的滑块
        self.running_sort = {'left': AllSort(None, None, None), 'right': AllSort(None, None, None)}  # 正在运行的左右排序算法
        self.lines = {'left': [], 'right': []}  # 线字典
        self.if_running_sort = {'left': False, 'right': False}  # 记录左右两边是否排序
        self.line_num = 550  # 单边线总数
        self.time_max = self.fps
        self.time_now = 0  # 当前时间
        self.if_time_run = False  # 时间开关
        self.speed = 3  # 速率控制
        self.init_data()

    def init_data(self):
        # 功能按键
        self.buttons['other'].append(Button('将序列随机', (0, 50), left_right=-1, can_long=False))
        self.buttons['other'].append(Button('将序列随机', (self.size[0], 50), left_right=1, can_long=False))
        self.labels['左趟数'] = Label('左躺数', '躺数:0', (0, 0))
        self.labels['左比较次数'] = Label('左比较次数', '比较次数:0', (0, 20))
        self.labels['左算法提示'] = Label('左算法提示', '', (150, 0))
        self.labels['右趟数'] = Label('右躺数', '右躺数:0', (1250, 0))
        self.labels['右比较次数'] = Label('右比较次数', '比较次数:0', (1250, 20))
        self.labels['右算法提示'] = Label('右算法提示', '', (1100, 0))
        self.labels['当前速率'] = Label('当前速率', '当前速率:' + str(61 - self.speed),
                                    (self.size[0] // 2 + 150, self.size[1] - 25))
        self.bars['速率调节'] = Bar('速率调节', '减缓', '加快', (self.size[0]//2, self.size[1] - 20), 200)
        name_list = ['插入排序', '希尔排序', '冒泡排序', '快速排序']
        i = 0
        for name in name_list:
            self.buttons['left'].append(Button(name, (0, 50 + 50 * (i + 1)), left_right=-1))
            self.buttons['right'].append(Button(name, (self.size[0], 50 + 50 * (i + 1)), left_right=1))
            i += 1
        for aline in range(self.line_num):
            self.lines['left'].append(Line(aline + 1, self.size[0] // 2, aline, False))
            self.lines['right'].append(Line(aline + 1, self.size[0] // 2, aline, True))

    def regard_time(self):  # 更新时间
        if not self.if_time_run:
            return None
        self.time_now += 1
        self.time_now %= self.time_max

    def reset_time(self, if_run):  # 更改时间状态
        self.if_time_run = if_run
        self.time_now = 0

    def begin_sort(self):  # 开始排序
        for value in self.running_sort.values():
            if value.name is None:
                return None
        if not self.if_time_run:
            self.reset_time(True)
        self.regard_time()
        if self.time_now % self.speed != 0:
            return None
        if not self.if_running_sort['left']:
            self.if_running_sort['left'], self.lines['left'], times = self.running_sort['left'].sort_fun.step_result()
            self.labels['左比较次数'].reset_label('比较次数:' + str(times[0]))
            self.labels['左趟数'].reset_label('趟数:' + str(times[1]))
        if not self.if_running_sort['right']:
            self.if_running_sort['right'], self.lines['right'], times = self.running_sort[
                'right'].sort_fun.step_result()
            self.labels['右比较次数'].reset_label('比较次数:' + str(times[0]))
            self.labels['右趟数'].reset_label('趟数:' + str(times[1]))
        if self.if_running_sort['right'] and self.if_running_sort['left']:
            self.rand_this()
            self.reset_time(False)
            self.running_sort = {'left': AllSort(None, None, None), 'right': AllSort(None, None, None)}  # 清空正在运行的算法
            self.if_running_sort = {'left': False, 'right': False}

    def draw(self):
        self.begin_sort()
        self.deal_bar_event()
        for value in self.buttons.values():
            for button in value:
                button.draw(self.screen)
        for value in self.lines.values():
            for line in value:
                line.draw(self.screen)
        for value in self.labels.values():
            value.draw(self.screen)
        ga.draw.line(self.screen, (60, 60, 60), (self.size[0] // 2, 0), (self.size[0] // 2, self.size[1]), 2)
        for value in self.bars.values():
            value.draw(self.screen)

    def rand_this(self):
        if not self.if_time_run:
            return None
        for value in self.buttons.values():
            for button in value:
                if button.state:
                    button.change_state(False)
                    break

    def deal_event(self, event_pos, event):
        if event == 'MOUSE_LEFT_DOWN':
            for key, value in self.buttons.items():
                for button in value:
                    if 0 <= event_pos[0] - button.draw_pos[0] <= button.size[0] \
                            and 0 <= event_pos[1] - button.draw_pos[1] <= button.size[1]:
                        button.change_state(not button.state)
                        if not button.state:
                            if key == 'left' or key == 'right':
                                self.running_sort[key] = AllSort(None, None, None)
                            break
                        else:
                            if key == 'left' or key == 'right':
                                self.running_sort[key] = AllSort(button.name, self.lines[key], self.screen)
                                self.labels[('左' if key == 'left' else '右') + '算法提示'].reset_label(button.name)
                        if key == 'other':  # 处理功能按钮事件
                            if button.state:
                                button.change_state(False)
                                if button.name == '将序列随机' and not self.if_time_run:
                                    which = 'left' if button.left_right == -1 else 'right'
                                    ra.shuffle(self.lines[which])
                                    i = 0
                                    for line in self.lines[which]:
                                        line.change_pos(i)
                                        i += 1
                            break
                        for shut in value:
                            if shut != button and shut.state:
                                shut.change_state(False)
                                break
                        break
                else:
                    continue
                return None
            for key, value in self.bars.items():
                if value.judge_if_in(event_pos):
                    self.setting_bar = value
                    return None
        elif event == 'MOUSE_LEFT_UP':
            if self.setting_bar is not None:
                self.setting_bar.init_turn_pos()
                self.setting_bar = None

    def deal_bar_event(self):
        if self.setting_bar is None:
            return None
        if self.time_now % 30 != 0:  # 调节频率控制
            return None
        self.setting_bar.set_turn_pos()
        if self.setting_bar.name == '速率调节':
            self.speed -= self.setting_bar.now_turn_index
            if self.speed < 1:
                self.speed = 1
            elif self.speed > 60:
                self.speed = 60
            self.labels['当前速率'].reset_label('当前速率:' + str(61 - self.speed))


class AllSort:
    Sort_List = ['插入排序', '希尔排序', '冒泡排序', '快速排序']

    def __init__(self, name, sort_list, screen):
        self.name = name
        self.sort_fun = None
        self.sort_list = sort_list  # 排序列表
        self.screen = screen
        self.init_data()

    def init_data(self):
        if self.name == '插入排序':
            self.sort_fun = InsertSort(self.name, self.sort_list)
        elif self.name == '希尔排序':
            self.sort_fun = XiErSort(self.name, self.sort_list)
        elif self.name == '快速排序':
            self.sort_fun = QuitSort(self.name, self.sort_list)
        elif self.name == '冒泡排序':
            self.sort_fun = BullSort(self.name, self.sort_list)


class InsertSort:
    def __init__(self, name, sort_list):
        self.i = 1
        self.comparison_times = 0  # 比较次数
        self.times = 0  # 算法执行趟数
        self.name = name
        self.sort_list = sort_list  # 排序列表
        self.num = self.sort_list[self.i]

    def step_result(self):
        self.times += 1
        for j in range(self.i-1, -1, -1):
            line = self.sort_list[j]
            self.comparison_times += 1
            if self.num.length < line.length:
                self.sort_list[j+1], self.sort_list[j] = self.sort_list[j], self.sort_list[j+1]
            else:
                break
        m = 0
        for lx in self.sort_list:
            lx.change_pos(m)
            m += 1
        if self.i == len(self.sort_list) - 1:
            return True, self.sort_list, (self.comparison_times, self.times)
        self.i += 1
        self.num = self.sort_list[self.i]
        return False, self.sort_list, (self.comparison_times, self.times)


class BullSort:
    def __init__(self, name, sort_list):
        self.i = 0
        self.n = len(sort_list)
        self.comparison_times = 0  # 比较次数
        self.times = 0  # 算法执行趟数
        self.name = name
        self.sort_list = sort_list  # 排序列表

    def step_result(self):
        self.times += 1
        if_turn = False
        for j in range(self.n - 1, self.i, -1):
            line = self.sort_list[j]
            line_before = self.sort_list[j - 1]
            self.comparison_times += 1
            if line.length < line_before.length:
                self.sort_list[j - 1], self.sort_list[j] = self.sort_list[j], self.sort_list[j - 1]
                if_turn = True
        if (not if_turn) or (self.i == self.n - 2):
            return True, self.sort_list, (self.comparison_times, self.times)
        self.i += 1
        m = 0
        for lx in self.sort_list:
            lx.change_pos(m)
            m += 1
        return False, self.sort_list, (self.comparison_times, self.times)


class XiErSort:
    def __init__(self, name, sort_list):
        self.n = len(sort_list)
        self.xi_er_i = len(sort_list)//2
        self.comparison_times = 0  # 比较次数
        self.times = 0  # 算法执行趟数
        self.name = name
        self.sort_list = sort_list  # 排序列表

    def step_result(self):
        self.times += 1
        for j in range(self.xi_er_i, self.n, self.xi_er_i):
            for x in range(j - self.xi_er_i, -1, -self.xi_er_i):
                line = self.sort_list[x]
                self.comparison_times += 1
                if self.sort_list[x+self.xi_er_i].length < line.length:
                    self.sort_list[x + self.xi_er_i], self.sort_list[x] = self.sort_list[x], self.sort_list[
                        x + self.xi_er_i]
                else:
                    break
        m = 0
        for lx in self.sort_list:
            lx.change_pos(m)
            m += 1
        if self.xi_er_i == 1:
            return True, self.sort_list, (self.comparison_times, self.times)
        self.xi_er_i //= 2
        return False, self.sort_list, (self.comparison_times, self.times)


class QuitSort:
    def __init__(self, name, sort_list):
        self.n = len(sort_list)
        self.comparison_times = 0  # 比较次数
        self.times = 0  # 算法执行趟数
        self.name = name
        self.sort_list = sort_list  # 排序列表
        self.range_list = [(0, self.n - 1)]  # 待处理范围

    def find_k(self, begin, end):
        # 找列表中第一个元素的真实位置
        k = begin
        while begin < end:
            while self.sort_list[k].length < self.sort_list[end].length:
                self.comparison_times += 1
                end -= 1
            self.sort_list[k],  self.sort_list[end] = self.sort_list[end], self.sort_list[k]
            k = end
            while self.sort_list[k].length > self.sort_list[begin].length:
                self.comparison_times += 1
                begin += 1
            self.sort_list[k], self.sort_list[begin] = self.sort_list[begin], self.sort_list[k]
            k = begin
        return k

    def step_result(self):
        self.times += 1
        if len(self.range_list) == 0:
            return True, self.sort_list, (self.comparison_times, self.times)
        """
        now_range = self.range_list[0]
        self.range_list.pop(0)
        k = self.find_k(now_range[0], now_range[1])
        if k - 1 > now_range[0]:
            self.range_list.append((now_range[0], k - 1))
        if k + 1 < now_range[1]:
            self.range_list.append((k + 1, now_range[1]))
        """
        new_range = []
        while len(self.range_list) != 0:
            now_range = self.range_list[0]
            self.range_list.pop(0)
            k = self.find_k(now_range[0], now_range[1])

            if k - 1 > now_range[0]:
                new_range.append((now_range[0], k - 1))
            if k + 1 < now_range[1]:
                new_range.append((k + 1, now_range[1]))
        self.range_list = new_range
        m = 0
        for lx in self.sort_list:
            lx.change_pos(m)
            m += 1
        return False, self.sort_list, (self.comparison_times, self.times)


class Bar:
    def __init__(self, name, left_name, right_name, pos, length, lie=True):
        self.name = name
        self.left_name = left_name
        self.right_name = right_name
        self.length = length
        self.pos = pos  # 滑块中心位置
        self.lie = lie  # 滑块是否水平
        self.turn_radius = 5  # 旋钮半径
        if self.lie:
            right_pos = (pos[0] + length // 2 + 5, pos[1] - 5)
            left_pos = (pos[0] - len(left_name) * 15 - 5 - length // 2, pos[1] - 5)
            self.begin_pos = (pos[0] - length // 2, pos[1])
            self.end_pos = (pos[0] + length // 2, pos[1])
            self.judge_range_x = length // 2  # 鼠标位置与pos[0]相差后的最大值
            self.judge_range_y = self.turn_radius  # 鼠标位置与pos[1]相差后的最大值
        else:
            right_pos = (pos[0] - (len(right_name) * 15) // 2, pos[1] + length // 2 + 5)
            left_pos = (pos[0] - (len(left_name) * 15) // 2, pos[1] - length // 2 - 20)
            self.begin_pos = (pos[0], pos[1] - length // 2)
            self.end_pos = (pos[0], pos[1] + length // 2)
            self.judge_range_x = self.turn_radius  # 鼠标位置与pos[0]相差后的最大值
            self.judge_range_y = length // 2  # 鼠标位置与pos[1]相差后的最大值
        self.turn_pos = pos  # 调整旋钮当前位置
        self.left_label = Label(name, left_name, left_pos)
        self.right_label = Label(name, right_name, right_pos)
        self.now_turn_index = 0  # 分别取值-1,-2,0,1,2
        self.abs_turn_max = 2  # 旋钮取值最大值

    def judge_if_in(self, mouse_pos):  # 判断鼠标位置是否在该按钮位置上
        x = True if abs(mouse_pos[0] - self.pos[0]) <= self.judge_range_x else False
        y = True if abs(mouse_pos[1] - self.pos[1]) <= self.judge_range_y else False
        return x and y  # 若为真则在该旋钮上

    def init_turn_pos(self):
        self.turn_pos = self.pos
        self.now_turn_index = 0

    def set_turn_pos(self):
        x, y = ga.mouse.get_pos()
        if self.lie:
            k = (2 * self.abs_turn_max * (x - self.pos[0]) // self.length)
            if k < 0:
                index = -2 if k < -3 else k + 1
            else:
                index = 2 if k > 2 else k
            self.turn_pos = (index * self.length // (2 * self.abs_turn_max) + self.pos[0], self.pos[1])
        else:
            k = (2 * self.abs_turn_max * (y - self.pos[1]) // self.length)
            if k < 0:
                index = -2 if k < -3 else k + 1
            else:
                index = 2 if k > 2 else k
            self.turn_pos = (self.pos[0], index * self.length // (2 * self.abs_turn_max) + self.pos[1])
        self.now_turn_index = index

    def draw(self, screen):
        self.left_label.draw(screen)
        self.right_label.draw(screen)
        ga.draw.line(screen, (255, 255, 255), self.begin_pos, self.end_pos)
        ga.draw.circle(screen, (255, 255, 255), self.turn_pos, self.turn_radius)


class Line:
    def __init__(self, length, pos_x, index, left_right=False, color=(255, 255, 255), width=1):
        self.width = width  # 线的宽度
        self.color = color
        self.length = length  # 线的长度
        self.index = index
        self.pos = (pos_x, 0)
        self.left_right = left_right  # False代表左 True代表右
        self.begin_pos = (0, 0)
        self.end_pos = (0, 0)
        self.change_pos(index)

    def change_pos(self, index):
        # 基于该元素在数组中的新位置该表pos
        self.begin_pos = (self.pos[0], index + 20 + self.width)
        self.end_pos = (self.pos[0] + (self.length if self.left_right else (-self.length)), index + 20 + self.width)

    def draw(self, screen):
        ga.draw.line(screen, self.color, self.begin_pos, self.end_pos, self.width)


class Label:
    def __init__(self, name, word, pos, color=(255, 255, 255)):
        self.font = ga.font.SysFont('SimHei', 15)
        self.name = name
        self.pos = pos
        self.color = color
        self.word = word
        self.label = self.font.render(self.word, True, self.color)

    def reset_label(self, new_word):
        self.word = new_word
        self.label = self.font.render(self.word, True, self.color)

    def draw(self, screen):
        screen.blit(self.label, self.pos)


class Button:
    def __init__(self, name, pos, can_long=True, word_color=(255, 255, 255), left_right=-1):
        self.font = ga.font.SysFont('SimHei', 15)
        self.state = False  # False为收缩状态， True为展开状态
        self.can_long = can_long  # 是否可以收缩
        self.word_color = word_color  # 提示信息颜色
        self.name = name
        self.pos = pos  # 按钮坐标
        self.label = self.font.render(self.name, True, self.word_color)
        size = (10 + len(self.name) * 15, 25)
        self.size = size  # 初始尺寸
        self.size_max = (70 + size[0], size[1])  # 最大尺寸
        self.left_right = left_right  # -1为居左 0为居中 1 为居右 居左则向右伸展 居右则向左伸展
        self.draw_pos = pos
        self.change_state(self.state)

    def change_state(self, new_state):
        self.state = new_state
        if self.state:
            if self.can_long:
                if self.left_right == -1:
                    self.label = self.font.render(self.name + '  Running', True, self.word_color)
                    self.draw_pos = self.pos
                else:
                    self.label = self.font.render('Running  ' + self.name, True, self.word_color)
                    self.draw_pos = (self.pos[0] - self.size_max[0], self.pos[1])
            else:
                if self.left_right == -1:
                    self.draw_pos = self.pos
                else:
                    self.draw_pos = (self.pos[0] - self.size[0], self.pos[1])
                self.label = self.font.render(self.name, True, self.word_color)
        else:
            self.label = self.font.render(self.name, True, self.word_color)
            if self.left_right == -1:
                self.draw_pos = self.pos
            else:
                self.draw_pos = (self.pos[0] - self.size[0], self.pos[1])

    def draw(self, screen):
        if self.state:
            if self.can_long:
                ga.draw.rect(screen, (255, 255, 255),
                             (self.draw_pos[0], self.draw_pos[1], self.size_max[0], self.size_max[1]), 1)
            else:
                ga.draw.rect(screen, (255, 255, 255),
                             (self.draw_pos[0], self.draw_pos[1], self.size[0], self.size[1]), 1)
        else:
            ga.draw.rect(screen, (255, 255, 255), (self.draw_pos[0], self.draw_pos[1], self.size[0], self.size[1]), 1)
        screen.blit(self.label, (self.draw_pos[0] + 5, self.draw_pos[1] + 5))


def run():
    ga.init()
    ga.display.set_caption("排序算法对比")
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
                    mind.deal_event(event.pos, 'MOUSE_LEFT_DOWN')
                elif event.button == 5:
                    pass
                elif event.button == 4:
                    pass
            elif event.type == ga.MOUSEBUTTONUP:
                # button
                if event.button == 1:
                    mind.deal_event(event.pos, 'MOUSE_LEFT_UP')
            elif event.type == ga.KEYDOWN:
                # key
                pass
        mind.clock.tick(mind.fps)
        ga.display.update()


run()
