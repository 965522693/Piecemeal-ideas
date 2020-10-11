import pygame
import sys
import socket
import _thread
import random


class Mind:
    level_now = 0  # 当前层次
    size = 1200, 800  # 尺寸
    fps = 60

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(Mind.size)
        self.time_max = Mind.fps
        self.time_now = 0  # 当前时间
        self.if_run = True  # 时间开关
        self.button_dict = {}
        self.exit_box_dict = {}
        self.label_dict = {}
        self.exit_box_now = None  # 当前正在编辑的输入框
        self.room = None  # 房间
        self.player_id = 0  # 玩家在房间中的id
        self.init_data()

    def init_data(self):
        self.button_dict = {
            ('创建房间', (-1, 0)): Button('创建房间', '创建房间', (400, 200)),
            ('加入房间', (-1, 0)): Button('加入房间', '加入房间', (400, 250)),
            ('确认', (-1, 1)): Button('确认', '确认', (400, 250)),
            ('开始', (-1, 2)): Button('开始', '开始', (100, 200)),
            ('加入', (-1, 3)): Button('加入', '加入', (400, 300))
        }
        self.exit_box_dict = {
            ('房间号', (-1, 1)): EditBox('输入房间号', '输入房间号', (400, 200)),
            ('已存在房间号', (-1, 3)): EditBox('输入房间号', '输入房间号', (400, 200)),
            ('房间ip', (-1, 3)): EditBox('输入房间ip', '输入房间ip', (400, 250)),
            ('我的id', (-1, 3)): EditBox('我的id', '我的id', (400, 150)),
        }
        self.switch_level(Mind.level_now)
        self.exit_box_dict[('房间ip', (-1, 3))].input_content('192.168.3.6')
        self.exit_box_dict[('我的id', (-1, 3))].input_content('8888')
        self.exit_box_dict[('已存在房间号', (-1, 3))].input_content('9999')
        self.exit_box_dict[('房间号', (-1, 1))].input_content('9999')

    def switch_level(self, level):  # 切换层次并刷新显示
        Mind.level_now = level
        for key, buttons in self.button_dict.items():
            if Mind.level_now not in key[1]:
                buttons.if_draw = False
            else:
                buttons.if_draw = True
        for key, exit_box in self.exit_box_dict.items():
            if Mind.level_now not in key[1]:
                exit_box.if_draw = False
            else:
                exit_box.if_draw = True

    def draw_exit_box(self):
        for key, exit_box in self.exit_box_dict.items():
            exit_box.draw(self.screen)

    def draw_button(self):
        for key, buttons in self.button_dict.items():
            buttons.draw(self.screen)

    def draw_player(self):
        if Mind.level_now == 4:
            self.room.player_draw(self.screen)

    def draw_label(self):
        if len(self.label_dict) == 0:
            return None
        for key, label in self.label_dict.items():
            label.draw(self.screen)

    def draw_room(self):
        if Mind.level_now == 2 and self.room is not None:
            self.room.draw(self.screen)

    def update_time(self):
        if self.if_run:
            self.time_now = (self.time_now + 1) % self.time_max

    def draw(self):
        self.update_time()
        self.draw_button()
        self.draw_exit_box()
        self.draw_label()
        self.draw_room()
        self.draw_player()

    def deal_button_event(self, button_name):
        if button_name == '创建房间':
            self.switch_level(1)
        elif button_name == '确认':
            self.switch_level(2)
            ip = socket.gethostbyname(socket.gethostname())
            room_id = self.exit_box_dict[('房间号', (-1, 1))].content
            self.label_dict = {
                ('ip地址', (-1, 2)): Label('ip地址', 'ip地址:' + ip, (100, 100)),
                ('房间号', (-1, 2)): Label('房间号', '房间号:' + room_id, (100, 150))
            }
            self.room = Room(ip, int(room_id))
            Room.boss_id = int(room_id)
            Room.boss_ip = ip
        elif button_name == '加入房间':
            self.switch_level(3)
        elif button_name == '加入':
            self.switch_level(2)
            self.button_dict.pop(('开始', (-1, 2)))
            ip = socket.gethostbyname(socket.gethostname())
            room_id = self.exit_box_dict[('我的id', (-1, 3))].content
            self.room = Room(ip, str(room_id))
            to_ip = self.exit_box_dict[('房间ip', (-1, 3))].content
            to_room_id = self.exit_box_dict[('已存在房间号', (-1, 3))].content
            self.room.send_info('000', to_ip, str(to_room_id))
            Room.boss_id = int(to_room_id)
            Room.boss_ip = to_ip
        elif button_name == '开始':
            self.switch_level(4)
            self.label_dict.clear()
            for key, room in list(self.room.all_info_dict.items())[1:]:
                self.room.send_info('002', key[0], key[1])

    def deal_event(self, event_type):
        if event_type == 'MOUSE_LEFT_DOWN':
            if Mind.level_now == 4:
                self.room.deal_control('G')  # 攻击指令
            for key, buttons in self.button_dict.items():
                if buttons.judge_rect() and buttons.if_draw:
                    self.deal_button_event(buttons.name)
                    break
            for key, exit_box in self.exit_box_dict.items():
                if exit_box.judge_rect() and exit_box.if_draw:
                    self.exit_box_now = exit_box
                    break
        elif event_type == 'MOUSE_LEFT_UP':
            if Mind.level_now == 4:
                self.room.deal_control('G_U')  # 取消攻击
        elif event_type in ('W', 'S', 'A', 'D', 'W_U', 'S_U', 'A_U', 'D_U') and self.room is not None:
            self.room.deal_control(event_type)
        elif (type(event_type) is int and 0 <= event_type <= 9) or event_type == '.':
            if self.exit_box_now is not None and self.exit_box_now.if_draw:
                self.exit_box_now.input_content(str(event_type))
        elif event_type == '退格键':
            if self.exit_box_now is not None and self.exit_box_now.if_draw:
                self.exit_box_now.del_content()


class Label:
    def __init__(self, name, label, pos, font_size=30):
        self.name = name
        self.label = label
        self.pos = pos
        self.font = pygame.font.SysFont('SimHei', font_size)
        self.label = self.font.render(self.label, True, (0, 0, 0))

    def draw(self, screen: pygame.Surface):
        screen.blit(self.label, self.pos)


class EditBox:
    Inputting_color = (0, 0, 255)
    Free_color = (0, 0, 0)

    def __init__(self, name, label, pos):
        self.name = name
        self.label_word = label
        self.pos = pos
        self.if_inputting = False
        self.label = Label(name, label, (pos[0] + 5, pos[1] + 5))
        self.rect = (pos[0], pos[1], self.get_rect_size(), 40)
        self.line_begin_pos = (self.rect[0] + self.rect[2], self.rect[1] + self.rect[3])
        self.line_end_pos = (self.line_begin_pos[0] + 100, self.line_begin_pos[1])
        self.content = ''  # 所记录的内容
        self.content_pos = (self.line_begin_pos[0] + 2, self.rect[1] + 2)
        self.content_label = Label(name, self.content, self.content_pos)
        self.judge_rect_x = (self.rect[0], self.line_end_pos[0])
        self.judge_rect_y = (self.rect[1], self.line_end_pos[1])
        self.if_draw = True  # 是否显示

    def del_content(self):
        self.content = self.content[:-1]
        self.content_label = Label(self.name, self.content, self.content_pos)

    def input_content(self, word):
        self.content += word
        self.content_label = Label(self.name, self.content, self.content_pos)

    def get_rect_size(self):
        size = 0
        for a in self.label_word:
            if 'a' <= a <= 'z' or 'A' <= a <= 'Z':
                size += 15
            else:
                size += 30
        return int(size + 10)

    def judge_rect(self):
        # 当位置准确时返回true 否则返回false
        x, y = pygame.mouse.get_pos()
        if self.judge_rect_x[0] <= x <= self.judge_rect_x[1] and self.judge_rect_y[0] <= y <= self.judge_rect_y[1]:
            self.if_inputting = True
            return True
        self.if_inputting = False
        return False

    def draw(self, screen: pygame.Surface):
        if not self.if_draw:
            return None
        self.label.draw(screen)
        pygame.draw.rect(screen, EditBox.Inputting_color if self.if_inputting else EditBox.Free_color, self.rect, 1)
        pygame.draw.line(screen, EditBox.Inputting_color if self.if_inputting else EditBox.Free_color,
                         self.line_begin_pos, self.line_end_pos)
        self.content_label.draw(screen)


class Button:
    word_color = (0, 0, 0)
    rect_color = (0, 0, 0)

    def __init__(self, name, show_name, pos):
        self.name = name
        self.show_name = show_name
        self.pos = pos
        self.font = pygame.font.SysFont('SimHei', 30)
        self.label = self.font.render(self.name, True, Button.word_color)
        self.word_rect_width = 10
        self.word_pos = (pos[0] + self.word_rect_width, pos[1] + self.word_rect_width)
        self.rect = (pos[0], pos[1], len(self.show_name) * 30 + self.word_rect_width * 2,
                     30 + self.word_rect_width * 2)
        self.if_draw = True  # 是否显示

    def judge_rect(self):
        x, y = pygame.mouse.get_pos()
        if 0 < x - self.pos[0] < self.rect[2] and 0 < y - self.pos[1] < self.rect[3]:
            return True
        else:
            return False

    def draw(self, screen: pygame.Surface):
        if not self.if_draw:
            return None
        pygame.draw.rect(screen, Button.rect_color, self.rect, 1)
        screen.blit(self.label, self.word_pos)


class Bullet:  # 子弹类
    # 不同子弹类型的属性字典 fire_speed是开火速度
    bullet_info_dict = {'手枪': {'hurt': 5, 'fire_speed': 20, 'img': pygame.image.load("图片素材/手枪.png")},
                        '冲锋枪': {'hurt': 1, 'fire_speed': 8, 'img': pygame.image.load("图片素材/冲锋枪.png")},
                        '回旋镖': {'hurt': 5, 'fire_speed': 30, 'img': pygame.image.load("图片素材/回旋镖.png")},
                        '激光': {'hurt': 20, 'fire_speed': 120, 'img': pygame.image.load("图片素材/激光.png")},
                        '狙击': {'hurt': 20, 'fire_speed': 50, 'img': pygame.image.load("图片素材/狙击.png")},
                        '量子': {'hurt': 5, 'fire_speed': 20, 'img': pygame.image.load("图片素材/量子.png")},
                        '霰弹枪': {'hurt': 5, 'fire_speed': 60, 'img': pygame.image.load("图片素材/霰弹枪.png")},
                        '炸弹': {'hurt': 30, 'fire_speed': 30, 'img': pygame.image.load("图片素材/炸弹.png")}}
    bullet_name_ready = ['手枪', '冲锋枪', '回旋镖', '激光', '狙击', '量子', '霰弹枪']

    def __init__(self, pos, move_direction=(0, 0), bullet_type='手枪', time=-1):
        # 子弹位置和方向和子弹类型, time参数是对于需要及时的子弹类型在服务器通信时需要用到
        self.pos = list(pos)
        self.move_direction = move_direction
        self.speed = (0, 0)
        self.hurt = 0  # 伤害
        self.radius = 0  # 子弹半径
        self.color = (0, 0, 0)
        self.bullet_type = bullet_type
        self.time = time  # 对于需要及时的子弹来说， -1代表不需要计时
        self.end_pos = (-1, -1)  # 对于需要控制最终位置的子弹来说， -1代表不需要考虑
        self.para = []  # 辅助变量，对于特殊枪械需要
        self.if_draw = True  # 是否绘制
        self.init_data()

    def init_data(self):
        self.hurt = Bullet.bullet_info_dict[self.bullet_type]['hurt']
        PlayerInfo.hurt_speed = Bullet.bullet_info_dict[self.bullet_type]['fire_speed']  # 每10帧攻击一次
        if self.bullet_type == '手枪':
            self.speed = (5, 5)
            self.radius = 5
            self.color = (0, 0, 0)
        elif self.bullet_type == '冲锋枪':
            self.speed = (10, 10)
            self.radius = 3
            self.color = (random.randint(0, 240), random.randint(0, 240), random.randint(0, 240))
        elif self.bullet_type == '回旋镖':
            self.time = 90  # 时间到后自动向反向移动
            self.speed = (5, 5)
            self.radius = 5
            self.color = (random.randint(0, 240), random.randint(0, 240), random.randint(0, 240))
        elif self.bullet_type == '激光':
            self.time = 0 if self.time == -1 else self.time
            self.speed = (20, 20)
            self.radius = 5
            self.color = (255, 0, 0)
            self.para = [0, 0]
            self.para[0] = int(self.move_direction[0] * self.speed[0] * self.time + self.pos[0])
            self.para[1] = int(self.move_direction[1] * self.speed[1] * self.time + self.pos[1])
            # 终点位置
        elif self.bullet_type == '狙击':
            self.speed = (5, 5)
            self.radius = 10
            self.color = (0, 0, 255)
        elif self.bullet_type == '量子':
            self.time = 0 if self.time == -1 else self.time
            self.para = [1, 5]  # 分别是时间增量和上一帧子弹大小
            self.speed = (3, 3)
            self.radius = 5
            self.color = (0, 0, 0)
        elif self.bullet_type == '霰弹枪':
            self.time = random.randint(20, 60) if self.time == -1 else self.time
            m = (60 - self.time) * random.choice([-1, 1]) / 200
            self.move_direction = (self.move_direction[0], self.move_direction[1] + m)
            distance = (self.move_direction[0] ** 2 + self.move_direction[1] ** 2) ** 0.5
            self.move_direction = (self.move_direction[0] / distance, self.move_direction[1] / distance)
            self.speed = (5, 5)
            self.radius = 3
            k = random.randint(0, 240)
            self.color = (255, k, k)
        elif self.bullet_type == '炸弹':
            self.speed = (10, 10)
            self.radius = 3
            self.color = (random.randint(0, 240), random.randint(0, 240), random.randint(0, 240))

    def update_time(self):
        if self.bullet_type == '回旋镖':
            if self.time > 0:
                self.time -= 1
            elif self.time == 0:
                self.time = -1
                self.move_direction = (-self.move_direction[0], -self.move_direction[1])
                self.speed = (self.speed[0] * 2, self.speed[1] * 2)
            else:
                pass
        elif self.bullet_type == '量子':
            self.time += self.para[0]
            self.para[1] = self.radius
            self.radius = int(0.5 * self.time + 5)
            self.color = (self.radius * 11, 255 - self.radius * 10, max(self.color[0], self.color[1]))
            if self.radius in [5, 20] and self.para[1] != self.radius:
                self.para[0] = -self.para[0]
        elif self.bullet_type == '霰弹枪':
            if self.time > 0:
                self.time -= 1
            else:
                self.if_draw = False
        elif self.bullet_type == '激光':
            self.time += 2
            if self.move_direction == (0, 0):
                return None
            self.para[0] = int(self.move_direction[0] * self.speed[0] * self.time + self.pos[0])
            self.para[1] = int(self.move_direction[1] * self.speed[1] * self.time + self.pos[1])

    def move(self):
        if self.bullet_type == '激光':
            return None
        self.pos[0] += self.move_direction[0] * self.speed[0]
        self.pos[1] += self.move_direction[1] * self.speed[1]

    def judge_out_range(self):  # 判断是否出界
        if self.bullet_type == '激光':
            if 0 < self.para[0] < Mind.size[0] and 0 < self.para[1] < Mind.size[1]:
                return False
            else:
                return True
        if not self.if_draw:
            return True
        if 0 < self.pos[0] < Mind.size[0] and 0 < self.pos[1] < Mind.size[1]:
            return False
        else:
            return True

    def judge_hurt(self, player_pos, player_radius):  # 判断对玩家造成多少伤害. 参数为玩家位置和玩家半径
        if not self.if_draw:
            return 0
        x = self.pos[0] - player_pos[0]
        y = self.pos[1] - player_pos[1]
        if self.bullet_type == '激光' and self.move_direction != (0, 0):
            x = self.para[0] - player_pos[0]
            y = self.para[1] - player_pos[1]
        distance = x**2 + y**2
        abs_distance = distance - (self.radius + player_radius)**2
        if abs_distance > 0:
            return 0
        else:
            return - self.hurt

    def draw(self, screen: pygame.Surface):
        self.update_time()
        if not self.if_draw:
            return None
        self.move()
        if self.bullet_type in ['手枪', '冲锋枪', '回旋镖', '狙击', '量子', '霰弹枪']:
            pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)
        elif self.bullet_type == '激光':
            # pygame.draw.circle(screen, self.color, self.para, self.radius)
            pygame.draw.line(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.para, self.radius)


class Room:
    boss_id = 0  # 主机id
    boss_ip = 0  # 主机ip
    all_info_dict = {}
    address = ()

    def __init__(self, ip, room_id, player_id=1):
        self.ip = ip
        self.room_id = int(room_id)
        Room.address = (self.ip, self.room_id)  # 地址信息
        self.player_id = player_id
        self.rect = (500, 100, 600, 300)
        self.people_number = player_id  # 当前人数，仅有房主
        self.img = [pygame.image.load("图片素材/成员图{}.png".format(i + 1)).convert_alpha() for i in range(3)]
        self.label = [Label('P{}'.format(i + 1), '已准备',
                            (self.rect[0] + 60, self.rect[1] + 20 + i * 50)) for i in range(3)]
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        local_add = (ip, int(room_id))
        self.udp.bind(local_add)
        Room.all_info_dict = {(ip, self.room_id): PlayerInfo(player_id)}  # 所有玩家的ip与端口号
        _thread.start_new_thread(self.get_info, ())

    def update_all_player_score_img(self):  # 更新自己所有玩家的分数显示
        for key, player in self.all_info_dict.items():
            player.update_score()

    def judge_dead(self):  # 客户端判断自己是否死亡，修改自身信息
        me = self.all_info_dict[self.address]
        if me.hp <= 0:
            me.dead()
            if self.player_id == 1:
                self.set_score(self.address, me.hp)
                for key, player in self.all_info_dict.items():
                    if key != self.address:
                        self.send_info('011' + str(me.hp), key[0], key[1])
            else:
                self.send_info('010' + str(me.hp), self.boss_ip, self.boss_id)  # 向主机发送自己死亡的信息

    def set_boss_score(self, boss_hp):  # 客户端收到了主机的死亡信息并修改
        self.all_info_dict[(self.boss_ip, self.boss_id)].boss_update_dead(boss_hp)

    def set_score(self, player_address, player_hp):  # 主机修改所有玩家分数并同步
        for key, player in self.all_info_dict.items():
            if key != player_address:
                player.score += 1
                player.update_score()
            else:
                player.boss_update_dead(player_hp)

    def deal_control(self, order):  # 处理控制指令
        self.all_info_dict[(self.ip, self.room_id)].deal_control(order)

    def all_info_dict_same_ture(self):  # 客户端同步自己的所有玩家血量等信息
        for key, value in self.all_info_dict.items():
            value.init_data()

    def get_info(self):
        while True:
            get_date = self.udp.recvfrom(60000)
            player_id = (get_date[1][0], int(get_date[1][1]))
            if get_date[0] == b'000':  # 用于询问所加入房间的人数
                content = '001' + str(self.people_number)
                self.udp.sendto(bytes(content, encoding='utf-8'), player_id)
                self.people_number += 1
                self.all_info_dict[player_id] = PlayerInfo(self.people_number)
            elif get_date[0][0:3] == b'001':  # 用于接收加入房间的人数
                self.people_number = int(get_date[0][3:].decode('utf-8')) + 1
                self.player_id = self.people_number
                self.all_info_dict[player_id] = PlayerInfo(1)
                self.all_info_dict[(self.ip, int(self.room_id))] = PlayerInfo(self.player_id)
                k = 2
                for other_id, info in self.all_info_dict.items():
                    if player_id != other_id and (self.ip, self.room_id) != other_id:
                        while k == self.player_id:
                            k += 1
                        self.all_info_dict[(self.ip, self.room_id)] = PlayerInfo(k)
                        k += 1
                self.udp.sendto(b'004', player_id)  # 告诉服务器你已经加入房间完成，服务器收到后同步信息
            elif get_date[0] == b'004':  # 玩家加入游戏，服务器可以同步信息了
                self.same_all_player()
                self.all_info_dict_same_ture()
            elif get_date[0] == b'002':  # 用于通知其他玩家进入游戏
                Mind.level_now = 4
            elif get_date[0][0:3] == b'003':  # 用于同步全局信息
                info = get_date[0][3:].decode('utf-8')
                info_list = info.split('@')
                for ids, players in self.all_info_dict.items():
                    index = info_list.index(str(ids[1]))
                    self.all_info_dict[ids].same_word(info_list[index + 1])
                self.all_info_dict_same_ture()
            elif get_date[0][0:3] == b'005':  # 游戏中客户端同步来自主机的信息
                info = get_date[0][3:].decode('utf-8')
                info_list = info.split('@')
                for ids, players in self.all_info_dict.items():
                    index = info_list.index(str(ids[1]))
                    if ids == self.address:
                        self.all_info_dict[ids].same_word(info_list[index + 1], which_name='score')
                        continue
                    self.all_info_dict[ids].same_word(info_list[index + 1])
            elif get_date[0][0:3] == b'006':  # 客户端向主机发送自己的信息
                info = get_date[0][3:].decode('utf-8')
                self.all_info_dict[player_id].same_word(info)
            elif get_date[0][0:3] == b'007':  # 主机收到了客户端的子弹信息
                info = get_date[0][3:].decode('utf-8')
                if info == 'None':
                    PlayerInfo.all_bullet_dict[(player_id[0], str(player_id[1])).__str__()] = []
                else:
                    info = get_list_form_bullet(info)
                    PlayerInfo.all_bullet_dict[(player_id[0], str(player_id[1])).__str__()] = info
                other_bullet = []  # 敌人子弹
                self_id = str((self.ip, str(self.room_id)))
                for info_id, bullet_list in PlayerInfo.all_bullet_dict.items():
                    if info_id != self_id:
                        for pos_x, pos_y, bullet_type, bullet_time in bullet_list:
                            bullet_new = Bullet((pos_x, pos_y), bullet_type=bullet_type, time=bullet_time)
                            if bullet_type == '激光':
                                bullet_new.para = self.all_info_dict[player_id].pos
                            other_bullet.append(bullet_new)
                self.all_info_dict[(self.ip, self.room_id)].bullet_dict['other'] = other_bullet
                self.all_info_dict[(self.ip, self.room_id)].judge_get_hurt()
            elif get_date[0][0:3] == b'008':  # 客户端收到了来自主机的子弹信息
                info = get_date[0][3:].decode('utf-8')
                info = info.split('@')
                other_bullet = []  # 敌人子弹
                for info_id, bullet_list in list(self.all_info_dict.items())[1:]:
                    info_id = (info_id[0], str(info_id[1])).__str__()
                    bullet = info[info.index(info_id) + 1]
                    if bullet == 'None':
                        bullet = []
                    else:
                        bullet = bullet.split('|')
                    new_list = []
                    for pos in bullet:
                        pos = pos.replace(' ', '')
                        m = pos.split(',')
                        bullet_info = int(m[0]), int(m[1]), m[2], int(m[3])
                        bullet_pos = bullet_info[0:2]
                        new_list.append(bullet_info)
                        bullet_new = Bullet(bullet_pos, bullet_type=bullet_info[2], time=bullet_info[3])
                        if bullet_new.bullet_type == '激光':
                            bullet_new.para = self.all_info_dict[player_id].pos
                        other_bullet.append(bullet_new)
                    PlayerInfo.all_bullet_dict[info_id] = new_list
                self.all_info_dict[(self.ip, self.room_id)].bullet_dict['other'] = other_bullet
                self.all_info_dict[(self.ip, self.room_id)].judge_get_hurt()
            elif get_date[0][0:3] == b'010':  # 这是主机收到的消息， 主机收到来自某个客户的自身死亡信息
                hp = int(get_date[0][3:].decode('utf-8'))
                self.set_score(player_id, hp)
                self.all_info_dict[self.address].gun_type = random.choice(Bullet.bullet_name_ready)
            elif get_date[0][0:3] == b'011':  # 这是客户端收到的消息， 客户端同步主机消息
                hp = int(get_date[0][3:].decode('utf-8'))
                self.set_boss_score(hp)
                self.all_info_dict[self.address].gun_type = random.choice(Bullet.bullet_name_ready)

    def send_info(self, info, ip, room_id):
        self.udp.sendto(bytes(info, encoding='utf-8'), (ip, int(room_id)))

    def same_all_player(self):  # 同步所有玩家
        if self.player_id == 1:
            if len(self.all_info_dict) == 1:
                return None
            content = '003'
            for key, player_info in self.all_info_dict.items():
                info = str(key[1]) + '@' + player_info.__str__() + '@'
                content += info
            content = content[:-1]
            for key, player_info in list(self.all_info_dict.items())[1:]:
                self.send_info(content, key[0], key[1])

    def same_all_except_self(self):  # 游戏中同步玩家信息
        self.judge_dead()
        self.update_all_player_score_img()
        if self.player_id == 1:
            if len(self.all_info_dict) == 1:
                return None
            content = '005'
            for key, player_info in self.all_info_dict.items():
                info = str(key[1]) + '@' + player_info.__str__() + '@'
                content += info
            content = content[:-1]
            for key, player_info in list(self.all_info_dict.items())[1:]:
                self.send_info(content, key[0], key[1])
            content_bullet = '008'  # 向所有客户端同步子弹信息
            self.all_info_dict[(self.ip, self.room_id)].boss_send_bullet()
            for player_id, word in PlayerInfo.all_bullet_dict.items():
                info_bullet = ''
                for i in word:
                    for j in i:
                        try:
                            j = int(j)
                        except ValueError:
                            pass
                        info_bullet += str(j) + ','
                    info_bullet = info_bullet[:-1]
                    info_bullet += '|'
                if len(info_bullet) == 0:
                    info_bullet = 'None'
                else:
                    info_bullet = info_bullet[:-1]
                info_bullet = player_id + '@' + info_bullet + '@'
                content_bullet += info_bullet
            content_bullet = content_bullet[:-1]
            for key, player_info in list(self.all_info_dict.items())[1:]:
                self.send_info(content_bullet, key[0], key[1])
        else:
            content = '006' + self.all_info_dict[(self.ip, self.room_id)].__str__()
            self.send_info(content, Room.boss_ip, Room.boss_id)
            content_bullet = '007' + self.all_info_dict[(self.ip, self.room_id)].send_bullet()  # 向主机发送子弹信息
            self.send_info(content_bullet, Room.boss_ip, Room.boss_id)

    def player_draw(self, screen: pygame.Surface):
        self.same_all_except_self()
        for key, player_info in self.all_info_dict.items():
            player_info.draw(screen)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 1)
        for i in range(self.people_number):
            screen.blit(self.img[i], (self.rect[0] + 10, self.rect[1] + 10 + i * 50))
            self.label[i].draw(screen)


class PlayerInfo:  # 保存玩家信息，包括坐标，攻击子弹等
    hurt_speed = 10  # 攻击速度
    all_bullet_dict = {}  # 主机记录所有玩家对应的子弹列表
    hp_height = 20  # 血条显示高度
    interval_limit = 5  # 人物信息与边框的距离
    # 人物信息位置
    player_pos_list = ((interval_limit, interval_limit),
                       (Mind.size[0] - interval_limit, interval_limit),
                       (interval_limit, Mind.size[1] - interval_limit - hp_height),
                       (Mind.size[0] - interval_limit, Mind.size[1] - interval_limit - hp_height))
    hp_color = (255, 0, 0)  # 血条颜色

    def __init__(self, player_id: int):  # 玩家编号，1,2,3,4
        self.id = player_id
        self.radius = random.randint(20, 40)
        self.hp = 40 + self.radius * 3  # hp当前值
        self.pos = [random.randint(100, Mind.size[0]), random.randint(100, Mind.size[1])]
        self.color = (random.randint(0, 200), random.randint(0, 200), random.randint(0, 200))
        self.img_dict = {'攻击图标': pygame.image.load("图片素材/攻击图标.png"),
                         '攻速图标': pygame.image.load("图片素材/攻速图标.png"),
                         '得分图标': pygame.image.load("图片素材/得分图标.png")}
        self.speed = 3
        self.hurt_time_now = 0  # 为0时可攻击
        self.bullet_dict = {'self': [], 'other': []}  # 子弹队列,包括自己的和敌人的
        self.control_list = []  # 控制队列
        self.hp_pos = PlayerInfo.player_pos_list[player_id - 1]  # 血条绘制位置
        self.hp_rect = (self.hp_pos[0], self.hp_pos[1], self.hp + 2, PlayerInfo.hp_height)  # 血条绘制rect
        self.hurt_img_pos = self.hp_pos[0], self.hp_pos[1] + PlayerInfo.hp_height + 5  # 伤害图标位置
        self.hurt_speed_pos = self.hp_pos[0] + 50, self.hp_pos[1] + PlayerInfo.hp_height + 5  # 攻速图标位置
        self.score_img_pos = self.hp_pos[0] + 100, self.hp_pos[1] + PlayerInfo.hp_height + 5  # 得分图标位置
        self.gun_type_img_pos = self.hp_pos[0] + 50, self.hp_pos[1] + PlayerInfo.hp_height + 35  # 枪图标位置
        self.gun_type = random.choice(Bullet.bullet_name_ready)  # 枪械类型
        self.hurt_speed = Bullet.bullet_info_dict[self.gun_type]['fire_speed']  # 获取攻击速度
        self.score = 0  # 玩家得分，一位玩家死亡，其他所有玩家得1分
        self.label_pos_dict = {}
        self.hurt_label = None
        self.hurt_speed_label = None
        self.score_img_label = None
        self.init_data()

    def init_data(self):
        self.hurt_speed = Bullet.bullet_info_dict[self.gun_type]['fire_speed']  # 获取攻击速度
        pos = PlayerInfo.player_pos_list[self.id - 1]
        self.hp_pos = pos[0] - 1, pos[1] - 1
        if self.id == 2 or self.id == 4:
            self.hp_pos = self.hp_pos[0] - self.hp, self.hp_pos[1]
        if self.id == 3 or self.id == 4:
            self.hp_pos = self.hp_pos[0], self.hp_pos[1] - 30
        self.hp_rect = (self.hp_pos[0], self.hp_pos[1], self.hp + 2, PlayerInfo.hp_height + 2)
        self.hurt_img_pos = self.hp_pos[0], self.hp_pos[1] + PlayerInfo.hp_height + 5  # 伤害图标位置
        self.hurt_speed_pos = self.hp_pos[0] + 50, self.hp_pos[1] + PlayerInfo.hp_height + 5  # 攻速图标位置
        self.score_img_pos = self.hp_pos[0], self.hp_pos[1] + PlayerInfo.hp_height + 35  # 得分图标位置
        self.gun_type_img_pos = self.hp_pos[0] + 50, self.hp_pos[1] + PlayerInfo.hp_height + 35  # 枪图标位置
        self.label_pos_dict = {'hurt': (self.hurt_img_pos[0] + 25, self.hurt_img_pos[1]),
                               'hurt_speed': (self.hurt_speed_pos[0] + 25, self.hurt_speed_pos[1]),
                               'score': (self.score_img_pos[0] + 25, self.score_img_pos[1])}
        self.hurt_label = Label('hurt',
                                Bullet.bullet_info_dict[self.gun_type]['hurt'].__str__(), self.label_pos_dict['hurt'],
                                font_size=30)
        self.hurt_speed_label = Label('hurt_speed',
                                      '{:.1f}'.format(Mind.fps / self.hurt_speed),
                                      self.label_pos_dict['hurt_speed'],
                                      font_size=30)
        self.score_img_label = Label('score',
                                     self.score.__str__(),
                                     self.label_pos_dict['score'],
                                     font_size=30)

    def update_score(self):  # 更新玩家分数
        self.score_img_label = Label('score',
                                     self.score.__str__(),
                                     self.label_pos_dict['score'],
                                     font_size=30)

    def dead(self):  # 死亡后刷新属性
        self.radius = random.randint(10, 40)
        self.hp = 70 + self.radius * 3  # hp当前值
        self.pos = [random.randint(100, Mind.size[0]), random.randint(100, Mind.size[1])]
        self.color = (random.randint(0, 200), random.randint(0, 200), random.randint(0, 200))
        self.gun_type = random.choice(Bullet.bullet_name_ready)
        self.hurt_time_now = 0  # 为0时可攻击
        self.init_data()

    def boss_update_dead(self, player_hp):  # 主机刷新死亡玩家的信息
        self.hp = player_hp  # hp当前值
        self.init_data()

    def __str__(self):
        word = "radius={};hp={};pos={};" \
               "color={};speed={};score={};" \
               "hurt_speed={}".format(self.radius, self.hp,
                                      ','.join(str(i) for i in self.pos),
                                      ','.join(str(i) for i in self.color),
                                      self.speed, self.score, self.hurt_speed)
        return word

    def update_time_other_bullet(self):  # 更新其他玩家的时间隔相关子弹信息
        for bullet in self.bullet_dict['other']:
            bullet.update_time()

    def judge_get_hurt(self):  # 自己受到了敌方的子弹，扣除血量并本地删除子弹
        self.update_time_other_bullet()
        remove_bullet = []
        for bullet in self.bullet_dict['other']:
            hurt = bullet.judge_hurt(self.pos, self.radius)
            self.hp += hurt
            if hurt != 0:
                remove_bullet.append(bullet)
        for remove_bullets in remove_bullet:
            self.bullet_dict['other'].remove(remove_bullets)

    def judge_make_hurt(self):  # 造成伤害，并删除自己的子弹
        # 参数为一个玩家信息列表，每个元素为一个二元组，分别是玩家pos和玩家radius
        player_info_list = []
        for key, player in Room.all_info_dict.items():
            if key != Room.address:
                player_info_list.append((player.pos, player.radius))
        remove_bullet_self = []
        for pos, radius in player_info_list:
            for bullet in self.bullet_dict['self']:
                hurt = bullet.judge_hurt(pos, radius)
                if hurt != 0 and bullet not in remove_bullet_self:
                    remove_bullet_self.append(bullet)
        for remove_bullets in remove_bullet_self:
            self.bullet_dict['self'].remove(remove_bullets)

    def boss_send_bullet(self):  # 主机讲自己的子弹列表同步到总子弹列表中
        bullet_list = []
        for i in self.bullet_dict['self']:
            if i.bullet_type == '激光':
                info = tuple(list(i.para) + [i.bullet_type, i.time])
            else:
                info = tuple(list(i.pos) + [i.bullet_type, i.time])
            bullet_list.append(info)
        PlayerInfo.all_bullet_dict[(Room.boss_ip, str(Room.boss_id)).__str__()] = bullet_list
        self.judge_make_hurt()

    def send_bullet(self):  # 向主机发送自己的子弹列表
        self_bullet_list_word = '|'.join(
            str((i.pos[0].__int__() if i.bullet_type != '激光' else i.para[0].__int__(),
                 i.pos[1].__int__() if i.bullet_type != '激光' else i.para[1].__int__(),
                 i.bullet_type, i.time))[1:-1].replace(' ', '').replace("'", '')
            for i in self.bullet_dict['self'])
        if len(self_bullet_list_word) == 0:
            self_bullet_list_word = 'None'
        self.judge_make_hurt()
        return self_bullet_list_word

    def bullet_range_judge(self):  # 子弹越界检测
        remove_list = []
        for bullet in self.bullet_dict['self']:
            out = bullet.judge_out_range()
            if out:
                remove_list.append(bullet)
        for bullet_out in remove_list:
            self.bullet_dict['self'].remove(bullet_out)

    def update_g(self):  # 更新攻击计时
        if self.hurt_time_now != 0:
            self.hurt_time_now -= 1

    def same_word(self, word: str, which_name="all_name"):  # 用于字符串转为对象数据, which_name代表定向选择某个属性改变
        word_list = word.split(';')
        for name in word_list:
            m = name.split('=')
            if which_name != 'all_name':
                if m[0] == which_name:
                    if m[0] == 'radius':
                        self.radius = int(m[1])
                    elif m[0] == 'hp':
                        self.hp = int(m[1])
                    elif m[0] == 'pos':
                        pos = m[1].split(',')
                        self.pos = list(int(i) for i in pos)
                    elif m[0] == 'color':
                        color = m[1].split(',')
                        self.color = tuple(int(i) for i in color)
                    elif m[0] == 'speed':
                        self.speed = int(m[1])
                    elif m[0] == 'score':
                        self.score = int(m[1])
                    elif m[0] == 'hurt_speed':
                        self.hurt_speed = int(m[1])
                    break
                else:
                    continue
            if m[0] == 'radius':
                self.radius = int(m[1])
            elif m[0] == 'hp':
                self.hp = int(m[1])
            elif m[0] == 'pos':
                pos = m[1].split(',')
                self.pos = list(int(i) for i in pos)
            elif m[0] == 'color':
                color = m[1].split(',')
                self.color = tuple(int(i) for i in color)
            elif m[0] == 'speed':
                self.speed = int(m[1])
            elif m[0] == 'score':
                self.score = int(m[1])
            elif m[0] == 'hurt_speed':
                self.hurt_speed = int(m[1])

    def deal_control(self, order):  # 处理控制指令
        if order in ('W', 'S', 'A', 'D', 'G') and order not in self.control_list:  # G为攻击，WASD为移动
            self.control_list.append(order)
        elif order in ('W_U', 'S_U', 'A_U', 'D_U', 'G_U'):  # G为攻击取消，WASD为移动取消
            try:
                self.control_list.remove(order[:-2])
            except ValueError:
                return None

    def control_player_from_list(self):  # 处理控制队列的控制任务
        for order in self.control_list:
            if order == 'W':
                self.pos[1] -= self.speed
            elif order == 'S':
                self.pos[1] += self.speed
            elif order == 'A':
                self.pos[0] -= self.speed
            elif order == 'D':
                self.pos[0] += self.speed
            elif order == 'G' and self.hurt_time_now == 0:
                self.hurt_time_now = PlayerInfo.hurt_speed
                x, y = pygame.mouse.get_pos()
                abs_x = x - self.pos[0]
                abs_y = y - self.pos[1]
                distance = (abs_x**2 + abs_y**2)**0.5
                direction = (abs_x/distance, abs_y/distance)
                if self.gun_type == '霰弹枪':
                    for i in range(20):
                        bullet = Bullet(self.pos, direction, self.gun_type)
                        self.bullet_dict['self'].append(bullet)
                else:
                    bullet = Bullet(self.pos, direction, self.gun_type)
                    self.bullet_dict['self'].append(bullet)

    def draw_info(self, screen: pygame.Surface):  # 绘制玩家信息，参数为玩家编号1,2,3,4
        pygame.draw.rect(screen, (0, 0, 0), self.hp_rect, 1)
        pygame.draw.rect(screen, self.color,
                         (self.hp_rect[0] + 1, self.hp_rect[1] + 1, self.hp, PlayerInfo.hp_height))
        screen.blit(self.img_dict['攻击图标'], self.hurt_img_pos)
        screen.blit(self.img_dict['攻速图标'], self.hurt_speed_pos)
        screen.blit(self.img_dict['得分图标'], self.score_img_pos)
        screen.blit(Bullet.bullet_info_dict[self.gun_type]['img'], self.gun_type_img_pos)
        self.hurt_label.draw(screen)
        self.hurt_speed_label.draw(screen)
        self.score_img_label.draw(screen)

    def draw(self, screen: pygame.Surface):
        self.control_player_from_list()
        self.bullet_range_judge()
        self.update_g()  # 更新攻击计时
        self.draw_info(screen)
        pygame.draw.circle(screen, self.color, self.pos, self.radius)
        for key, bullet_list in self.bullet_dict.items():
            try:
                for bullet in bullet_list:
                    bullet.draw(screen)
            except ValueError:
                continue


def get_list_form_bullet(word):
    word = word.split('|')
    bullet_list = []
    for pos in word:
        pos = pos.replace(' ', '')
        pos_x, pos_y, bullet_type, bullet_time = tuple(pos.split(','))
        bullet_list.append((int(pos_x), int(pos_y), bullet_type, int(bullet_time)))
    return bullet_list


def run():
    pygame.init()
    pygame.display.set_caption("小球躲闪")
    mind = Mind()
    while True:
        mind.screen.fill((255, 255, 255))
        mind.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                # buttons
                mind.mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # button  左1 右3 向下5 向上4
                if event.button == 1:
                    mind.deal_event('MOUSE_LEFT_DOWN')
                elif event.button == 3:
                    mind.deal_event('MOUSE_RIGHT_DOWN')
                elif event.button == 4:
                    pass
            elif event.type == pygame.MOUSEBUTTONUP:
                # button
                if event.button == 1:
                    mind.deal_event('MOUSE_LEFT_UP')
            elif event.type == pygame.KEYDOWN:
                # print(event.key)
                if 256 <= event.key <= 265:
                    mind.deal_event(event.key - 256)  # 纯数字输入
                elif 48 <= event.key <= 57:
                    mind.deal_event(event.key - 48)   # 纯数字输入
                elif event.key == 47 or event.key == 266:
                    mind.deal_event('.')  # 小数点
                elif event.key == 8:
                    mind.deal_event('退格键')
                elif event.key == 119:  # W
                    mind.deal_event('W')
                elif event.key == 115:  # S
                    mind.deal_event('S')
                elif event.key == 97:  # A
                    mind.deal_event('A')
                elif event.key == 100:  # D
                    mind.deal_event('D')
                elif event.key == 32:  # 空格32
                    mind.deal_event('KEY_SPACE')
                elif event.key == 13:  # 回车
                    mind.deal_event('KEY_ENTER')
                elif event.key == 9:  # 换行键
                    mind.deal_event('换行')
            elif event.type == pygame.KEYUP:
                # print(event.key)
                if event.key == 119:  # W
                    mind.deal_event('W_U')
                elif event.key == 115:  # S
                    mind.deal_event('S_U')
                elif event.key == 97:  # A
                    mind.deal_event('A_U')
                elif event.key == 100:  # D
                    mind.deal_event('D_U')

        mind.clock.tick(mind.fps)
        pygame.display.update()


if __name__ == '__main__':
    run()
