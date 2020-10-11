import pygame
import sys
import numpy as np
import random as ra
import math as ma


class Society:
    def __init__(self):
        # self.person_core = person_core
        # 以下数据取值均为0到1
        self.propagation_probability = 0.9  # 传播概率
        self.person_move_probability = 0.9  # 人群移动概率
        self.total_random_propagation_probability = 0.1  # 全随机传播概率，模拟无意中接触感染人群的人
        self.bed_sum = 0.1  # 1代表可以容纳所有人，0代表无法容纳所有人
        self.incubation_period = 0.8  # 潜伏期时长，0代表立即发病，1代表永不发病
        self.response_speed = 0.1  # 医院找出病患响应速度，0代表永不响应，1代表立即响应
        self.treat_speed = 0.1  # 医院治疗的速度，0代表永不治疗，1代表立即治疗
        self.dead_speed = 0.5  # 死亡速度,0代表无法致死，1代表立即死亡
        self.init_disease = 10  # 初始病患,也代表当前病患
        self.var_dict = {'传播概率': 'propagation_probability', '人群出行概率': 'person_move_probability',
                         '全随机传播概率': 'total_random_propagation_probability', '床位': 'bed_sum',
                         '潜伏期时': 'incubation_period', ' 医院找寻速度': 'response_speed',
                         '医院治疗速度': 'treat_speed', '病毒危害性': 'dead_speed', '初始病患': 'init_disease',
                         '初始患病人数': 'init_disease'}
        # 以下数据取值不定
        self.time_max = 2
        # self.time_max = AllControl.fps / 60  # 每次更新的总时间
        self.time_now = self.time_max  # 当前时间
        self.person_state_dict = {}  # 人群按不同状态划分
        self.person_grad = 25  # 人群相距可传播距离
        self.all_person = []  # 所有人对象
        self.ues_time = 0  # 所用时间
        self.information = []  # 传播信息显示
        self.max_information_num = 20  # 传播信息总数

    def init_person(self):
        self.ues_time = 0
        for person in self.all_person:
            person.set_state('吃瓜群众')
            person.pos = person.init_pos.copy()
        for i in range(int(self.init_disease)):
            person = ra.choice(self.all_person)
            person.set_state('确诊')
        self.set_state_dict()

    def join_information(self, information):
        self.information.append(information)
        if len(self.information) > self.max_information_num:
            self.information.pop(0)

    def var(self, title, num):
        var = self.var_dict[title]
        exec('self.{} = {}'.format(var, num))

    def set_state_dict(self):
        for state in Person.state_list:
            self.person_state_dict[state] = []
        for person in self.all_person:
            self.person_state_dict[person.state].append(person)

    def reset_person_state(self):
        # 模拟传播
        self.join_information('开始新一轮传播...')
        self.join_information('正在估计人群流动意向...')
        person_move = ra.random()
        if person_move <= self.person_move_probability:
            self.join_information('由于人群移动临近传播...')
            for i in range(int(len(self.all_person) * person_move)):
                person = ra.choice(self.all_person)
                person.random_move()
            for person in self.person_state_dict['潜伏期人群']:
                person.infected_near_person(if_all=False, propagation_probability=self.propagation_probability)
            for person in self.person_state_dict['确诊']:
                self.join_information('正在估计床位...')
                m = ra.random()
                if m < self.bed_sum:
                    self.join_information('床位允许，该患者入院...')
                    person.if_isolated = True  # 被隔离
                    self.join_information('患者{}已被隔离...'.format(person.name))
                    self.join_information('患者坐标：{}'.format(person.pos))
                else:
                    person.infected_near_person(if_all=False, propagation_probability=self.propagation_probability)
                    self.join_information('床位空缺，该患者向周围人传播...')
                    self.join_information('该患者周围人数为{}人...'.format(len(person.near_person_list)))
        else:
            self.join_information('正在估计全随机传播...')
            k = ra.random()  # 全随机传播
            if k <= self.total_random_propagation_probability:
                self.join_information('由于偶然行为有人被感染...')
                for i in range(int(k * len(self.person_state_dict['吃瓜群众']))):
                    person = ra.choice(self.person_state_dict['吃瓜群众'])
                    t = ra.random()
                    if t <= self.propagation_probability:
                        person.set_state('潜伏期人群')
                    else:
                        person.set_state('疑似症状')
            self.join_information('无人在偶然事件中被传播...')
        k = ra.random()
        self.join_information('相关部门正在搜查...')
        if k <= self.response_speed:
            self.join_information('查出疑似症状...')
            for person in self.person_state_dict['疑似症状']:
                t = ra.random()
                if t <= self.propagation_probability:
                    person.set_state('确诊')
                    self.join_information('患者{}已被确诊...'.format(person.name))
                    self.join_information('患者坐标{}...'.format(person.pos))
                    m = ra.random()
                    if m < self.bed_sum:
                        self.join_information('床位充足患者{}已被隔离...'.format(person.name))
                        person.if_isolated = True  # 被隔离
                else:
                    person.set_state('吃瓜群众')
        self.join_information('潜伏期人群正在活跃...')
        for person in self.person_state_dict['潜伏期人群']:
            k = ra.random()
            if k > self.incubation_period:
                person.set_state('确诊')
                self.join_information('潜伏期患者{}已被确诊...'.format(person.name))
                m = ra.random()
                if m < self.bed_sum:
                    person.if_isolated = True  # 被隔离
                    self.join_information('床位充足患者{}已被隔离...'.format(person.name))
        self.join_information('正在治疗患者...')
        for person in self.person_state_dict['确诊']:
            k = ra.random()
            if k <= self.treat_speed:
                person.treat()
                self.join_information('患者{}已经治愈...'.format(person.name))
            else:
                t = ra.random()
                if t < self.dead_speed:
                    person.dead()
                    self.join_information('患者{}已死亡...'.format(person.name))
        k = len(self.person_state_dict['疑似症状']) + len(self.person_state_dict['确诊'])
        self.set_state_dict()
        t = len(self.person_state_dict['疑似症状']) + len(self.person_state_dict['确诊'])
        if k != t:
            self.ues_time += 1

    def infected(self):
        # 传染
        if self.time_now != 0:
            self.time_now -= 1
        else:
            self.time_now = self.time_max
            self.reset_person_state()


class Person:
    state_list = ['吃瓜群众', '疑似症状', '潜伏期人群', '确诊', '治愈', '死亡']
    color_dict = {'吃瓜群众': (255, 255, 255), '疑似症状': (255, 255, 0), '潜伏期人群': (255, 0, 255), '确诊': (255, 0, 0),
                  '治愈': (0, 255, 0),
                  '死亡': (0, 0, 255)}

    def __init__(self, pos, name):
        self.init_pos = list(pos)
        self.pos = list(pos)
        self.state = '吃瓜群众'
        self.color = Person.color_dict[self.state]
        self.near_person_list = []  # 与其临近的人
        self.if_isolated = False  # 是否被隔离
        self.name = name
        self.move_pos = (ra.randint(-1, 1), ra.randint(-1, 1))

    def set_state(self, new_state):
        self.state = new_state
        self.color = Person.color_dict[self.state]
        if new_state == '吃瓜群众':
            self.if_isolated = False

    def random_move(self):
        self.pos = [self.pos[0] + self.move_pos[0], self.pos[1] + self.move_pos[1]]

    def __sub__(self, other):
        # 返回两人物间距离
        dis = ma.sqrt((self.pos[0] - other.pos[0]) ** 2 + (self.pos[1] - other.pos[1]) ** 2)
        return dis

    def infected_near_person(self, if_all=False, propagation_probability=0):
        # 感染周围人群
        if self.if_isolated:
            return None
        else:
            if if_all:
                for others in self.near_person_list:
                    if others.state == '吃瓜群众' or others.state == '疑似症状':
                        others.set_state('潜伏期人群')
            else:
                for others in self.near_person_list:
                    if others.state == '吃瓜群众' or others.state == '疑似症状':
                        k = ra.random()
                        if k <= propagation_probability:
                            others.set_state('潜伏期人群')

    def treat(self):
        # 被治疗
        self.set_state('治愈')

    def dead(self):
        # 死亡
        self.set_state('死亡')


class Component:
    word_color = (255, 255, 255)

    def __init__(self, pos):
        self.pos = pos
        self.font = pygame.font.SysFont('SimHei', 15)


class News(Component):
    def __init__(self, pos, news, news_color=Component.word_color):
        super(News, self).__init__(pos)
        self.news = news
        self.word_color = news_color

    def draw(self, screen):
        news = self.font.render(self.news, True, self.word_color)
        screen.blit(news, self.pos)


class Slider(Component):
    def __init__(self, pos, title, left_news, right_news, init_num: float = 50.0, max_num=100,
                 if_normal=False, if_appear_normal_num=True):
        super(Slider, self).__init__(pos)
        self.max_num = max_num
        if if_normal:
            self.now_normal_num = init_num
            self.now_num = self.now_normal_num * self.max_num
        else:
            self.now_num = init_num
            self.now_normal_num = self.now_num / self.max_num  # 归一化的值
        self.if_appear_normal_num = if_appear_normal_num
        self.long = 150  # 总长度
        self.title = title
        self.left_news = News((pos[0], pos[1] + 20), left_news)
        if self.if_appear_normal_num:
            self.news = News((pos[0], pos[1] - 30), title + '：' + str(self.now_normal_num))
        else:
            self.news = News((pos[0], pos[1] - 30), title + '：' + str(self.now_num))
        self.right_news = News((pos[0] + self.long - 50, pos[1] + 20), right_news)
        self.line_color = (255, 255, 255)
        self.slider_color = (255, 255, 255)
        self.range_color = (255, 255, 255)  # 边界框颜色
        self.range_rect = (pos[0] - 20, pos[1] - 40, self.long + 50, 80)
        self.slider_radius = 5
        self.if_move = False

    def draw(self, screen, mouse_pos):
        if self.if_move:
            num = self.max_num * (mouse_pos[0] - self.pos[0]) / self.long
            self.set_num(int(num))
        self.left_news.draw(screen)
        self.right_news.draw(screen)
        self.news.draw(screen)
        pygame.draw.line(screen, self.line_color, self.pos, (self.pos[0] + self.long, self.pos[1]))
        pygame.draw.circle(screen, self.slider_color, (self.pos[0] + int(self.now_normal_num * self.long), self.pos[1]),
                           self.slider_radius)
        pygame.draw.rect(screen, self.range_color, self.range_rect, 1)

    def set_num(self, new_num, if_normal_num=False):
        if not if_normal_num:
            if new_num < 0:
                self.now_num = 0
            elif new_num > self.max_num:
                self.now_num = self.max_num
            else:
                self.now_num = new_num
            self.now_normal_num = self.now_num / self.max_num
        else:
            if new_num < 0:
                self.now_num = 0
            elif new_num > 1:
                self.now_num = self.max_num
            else:
                self.now_num = self.max_num * new_num
        self.news.news = self.title + '：' + str(self.now_normal_num)
        if self.if_appear_normal_num:
            self.news.news = self.title + '：' + str(self.now_normal_num)
        else:
            self.news.news = self.title + '：' + str(self.now_num)

    def deal_event(self, event_type, event_pos):
        range_left = self.range_rect[0]
        range_right = self.range_rect[1]
        range_long = self.range_rect[2]
        range_height = self.range_rect[3]
        if event_type == '左键按下':
            if 0 <= event_pos[0] - range_left <= range_long and \
                    0 <= event_pos[1] - range_right <= range_height:
                self.if_move = True
                return self.title
        elif event_type == '左键放开':
            self.if_move = False
            return self.title
        return None


class AllControl:
    fps = 60

    def __init__(self):
        self.size = 1400, 600
        self.screen = pygame.display.set_mode(self.size)
        self.fps = AllControl.fps
        self.mouse_pos = (0, 0)
        self.clock = pygame.time.Clock()
        self.city_num = 5  # 城市中心数
        self.person_sum = 2000
        self.person_move_range = (50, 50, 900, 500)
        self.society = Society()
        self.component_dict = {'News': [], 'Slider': []}
        self.font = pygame.font.SysFont('SimHei', 15)
        self.person_core = []
        for i in range(self.city_num):
            self.person_core.append((ra.randint(300, 700), ra.randint(100, 500)))
        self.get_normal_distribution_list_pos()
        self.init()

    def init(self):
        title = News((450, 20), '模拟感染图')
        self.component_dict['News'].append(title)
        title = News((60, 60), '总数：' + str(self.person_sum))
        self.component_dict['News'].append(title)
        title = News((60, 80), '所用传播周期：' + str(self.society.ues_time))
        self.component_dict['News'].append(title)
        slider_title_dict = {'传播概率': ['不传播', '极易传播', 0.9], '人群出行概率': ['均不出行', '随意出行', 0.9],
                             '全随机传播概率': ['不随机传播', '易随机传播', 0.1], '床位': ['无任何床位', '无限制', 0.1],
                             '潜伏期时': ['时间极短', '时间极长', 0.8], ' 医院找寻速度': ['不寻找', '瞬间寻找', 0.1],
                             '医院治疗速度': ['不治疗', '瞬间治疗', 0.1], '病毒危害性': ['无危害', '立即致死', 0.5],
                             '初始患病人数': ['0人', '100人', 0.1]}
        i = 0
        for titles in slider_title_dict.keys():
            if titles == '初始患病人数':
                appear = False
            else:
                appear = True
            slider = Slider((1000 + 210 * int(i / 7), 50 + 80 * (i % 7)), titles, slider_title_dict[titles][0],
                            slider_title_dict[titles][1], init_num=slider_title_dict[titles][2], if_normal=True,
                            if_appear_normal_num=appear)
            self.component_dict['Slider'].append(slider)
            i += 1
        i = 0
        for key in Person.color_dict.keys():
            new = News((60 + i * 150, 530), key + '：' + str(len(self.society.person_state_dict[key])),
                       Person.color_dict[key])
            self.component_dict['News'].append(new)
            i += 1

    def draw(self):
        pygame.draw.rect(self.screen, (255, 255, 255), (1190, 169, 200, 402), 1)
        k = 0
        for i in self.society.information:
            n = self.font.render(i, True, (255, 255, 255))
            self.screen.blit(n, (1200, 170 + k * 20))
            k += 1
        for new in self.component_dict['News']:
            word = new.news.split('：')
            if word[0] in self.society.person_state_dict.keys():
                new.news = word[0] + '：' + str(len(self.society.person_state_dict[word[0]]))
            elif word[0] == '所用传播周期':
                new.news = '所用传播周期：' + str(self.society.ues_time)
        pygame.draw.rect(self.screen, (255, 255, 255), self.person_move_range, 1)
        for state in Person.state_list:
            for person in self.society.person_state_dict[state]:
                pygame.draw.circle(self.screen, person.color, person.pos, 1)
        for value in self.component_dict.values():
            if len(value) == 0:
                continue
            for com in value:
                if type(com) is Slider:
                    com.draw(self.screen, self.mouse_pos)
                else:
                    com.draw(self.screen)
        self.society.infected()

    def deal_event(self, event_type):
        for sl in self.component_dict['Slider']:
            event_title = sl.deal_event(event_type, self.mouse_pos)
            if event_title is not None:
                if event_title == '初始患病人数':
                    num = sl.now_num
                else:
                    num = sl.now_normal_num
                self.society.var(event_title, num)
                if event_type == '左键放开':
                    self.society.init_person()

    def get_normal_distribution_list_pos(self):
        x = self.fun_x()
        y = self.fun_y()
        person_list = []
        for i in range(self.person_sum):
            pos = (int(x[i]), int(y[i]))
            person = Person(pos, str(i+1) + '号')
            person_list.append(person)
        for person in person_list:
            for others in person_list:
                if others is person:
                    continue
                else:
                    dis = person - others
                    if dis <= self.society.person_grad:
                        person.near_person_list.append(others)
            self.society.all_person.append(person)
        self.society.init_person()

    def fun_x(self):
        result_list = []
        for i in range(self.city_num):
            miu = self.person_core[i][0]  # 期望
            sigma = self.person_move_range[2] / 8  # 标准差
            result_list += list(np.random.normal(miu, sigma, int(self.person_sum / self.city_num)))
        return result_list

    def fun_y(self):
        result_list = []
        for i in range(self.city_num):
            miu = self.person_core[i][1]  # 期望
            sigma = self.person_move_range[3] / 6  # 标准差
            result_list += list(np.random.normal(miu, sigma, int(self.person_sum / self.city_num)))
        return result_list


def main():
    pygame.init()
    pygame.display.set_caption("疫情模拟  正在生成模型，请稍等...")
    control = AllControl()
    pygame.display.set_caption("疫情模拟")
    while True:
        control.screen.fill((0, 0, 0))
        control.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                # buttons
                control.mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # button  左1 右3 向下5 向上4
                if event.button == 1:
                    control.deal_event('左键按下')
                elif event.button == 5:
                    control.deal_event('滑轮向下')
                elif event.button == 4:
                    control.deal_event('滑轮向下')
            elif event.type == pygame.MOUSEBUTTONUP:
                # button
                if event.button == 1:
                    control.deal_event('左键放开')
            elif event.type == pygame.KEYDOWN:
                # key
                pass
        control.clock.tick(control.fps)
        pygame.display.update()


main()
