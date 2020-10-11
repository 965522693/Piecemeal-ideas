from pygame import time
from pygame import display
from pygame import Surface
from pygame import init
from pygame import event as events
from pygame import MOUSEMOTION
from pygame import MOUSEBUTTONDOWN
from pygame import MOUSEBUTTONUP
from pygame import KEYDOWN
from pygame import KEYUP
from pygame import QUIT
from pygame import image
from numpy import array
from sys import exit
import socket
from _thread import start_new_thread
import random
from 我斗地主贼六.ui import Button
from 我斗地主贼六.ui import Label
from 我斗地主贼六.ui import EditBox
from 我斗地主贼六.ui import Ui


class Mind:
    level_now = '初始房间'  # 当前层次
    size = 800, 600  # 尺寸
    fps = 60
    time_now = 0  # 当前时间

    def __init__(self):
        self.clock = time.Clock()
        self.screen = display.set_mode(Mind.size)
        self.time_max = Mind.fps
        self.if_run = True  # 时间开关
        self.button_dict = {}
        self.exit_box_dict = {}
        self.label_dict = {}
        self.exit_box_now = None  # 当前正在编辑的输入框
        self.room = None  # 房间
        self.init_data()

    def init_data(self):
        self.button_dict = {
            '初始房间_创建房间': Button('创建房间', '创建房间', (350, 200)),
            '初始房间_加入房间': Button('加入房间', '加入房间', (350, 250)),
            '创建房间_确认': Button('确认', '确认', (350, 250)),
            '加入房间_确认': Button('确认', '确认', (350, 350)),
            '等待中_开始游戏': Button('开始游戏', '开始游戏', (350, 350)),
            '叫地主=叫地主': Button('叫地主', '叫地主', (250, 300), if_draw=False),
            '叫地主=不叫': Button('不叫', '不叫', (400, 300), if_draw=False),
            '出牌=出牌': Button('出牌', '出牌', (250, 300), if_draw=False),
            '出牌=过': Button('过', '过', (400, 300), if_draw=False),
            '等待=等待': Button('等待', '等待其他玩家', (300, 300), if_draw=False, if_wait=True),
            '撤销=撤销': Button('撤销', '撤销', (300, 300), if_draw=False)

        }
        self.exit_box_dict = {
            '创建房间_房间号': EditBox('房间号', '房间号：', (350, 200)),
            '加入房间_房间号': EditBox('房间号', '房间号：', (350, 200)),
            '加入房间_ip号': EditBox('ip号', 'ip号：', (350, 250)),
            '加入房间_id号': EditBox('id号', '我的id：', (350, 300))
        }
        self.exit_box_dict['创建房间_房间号'].input_content('8888')
        self.exit_box_dict['加入房间_房间号'].input_content('8888')
        self.update_level_ui(self.level_now)

    def update_level_ui(self, level_new):  # 更新当前层次的显示UI
        self.level_now = level_new
        for key, button in self.button_dict.items():
            try:
                level, name = key.split('_')
            except ValueError:
                continue
            if level == self.level_now:
                button.if_draw = True
            else:
                button.if_draw = False
        for key_box, exit_box in self.exit_box_dict.items():
            level, name = key_box.split('_')
            if level == self.level_now:
                exit_box.if_draw = True
            else:
                exit_box.if_draw = False
        if Room.my_address == Room.boss_address and self.level_now == '等待中':
            self.button_dict['等待中_开始游戏'].if_draw = True
        else:
            self.button_dict['等待中_开始游戏'].if_draw = False

    def draw_ui(self):
        for key, button in self.button_dict.items():
            button.draw(self.screen)
        for key_box, exit_box in self.exit_box_dict.items():
            exit_box.draw(self.screen)

    def update_time(self):
        if self.if_run:
            self.time_now = (self.time_now + 1) % self.time_max

    def draw_room(self):
        if self.room is not None:
            self.room.draw(self.screen)

    def game_running(self):  # 游戏中持续监测room状态更新ui
        if self.level_now != '游戏中':
            return None
        for key, button in self.button_dict.items():
            try:
                level, name = key.split('=')
            except ValueError:
                continue
            if level == Room.my_state:
                button.if_draw = True
            else:
                button.if_draw = False
        if len(Room.last_card_list) == 0:
            self.button_dict['出牌=过'].if_draw = False

    def draw(self):
        self.game_running()
        self.update_time()
        self.draw_room()
        self.draw_ui()

    def found_room(self):  # 用于主机创建房间
        ip = socket.gethostbyname(socket.gethostname())
        room_id = int(self.exit_box_dict['创建房间_房间号'].content)
        self.room = Room(ip, room_id)
        self.update_level_ui('等待中')

    def join_room(self):  # 用于玩家加入房间
        ip = self.exit_box_dict['加入房间_ip号'].content
        room_id = int(self.exit_box_dict['加入房间_房间号'].content)
        my_ip = socket.gethostbyname(socket.gethostname())
        my_id = int(self.exit_box_dict['加入房间_id号'].content)
        self.room = Room(my_ip, my_id, False, ip, room_id)
        self.update_level_ui('游戏中')

    def get_first_hand_player(self):  # 抢地主
        k = random.randint(0, 2)
        self.room.first_player_go(k)  # 要求主机通知先手玩家抢地主
        self.update_level_ui('游戏中')  # Mind 脱离控制权

    def deal_event(self, event_type):
        if event_type == 'MOUSE_LEFT_DOWN':
            for key, button in self.button_dict.items():
                down = button.judge_rect()
                if down:
                    if key == '初始房间_创建房间':
                        self.update_level_ui('创建房间')
                    elif key == '初始房间_加入房间':
                        self.update_level_ui('加入房间')
                    elif key == '创建房间_确认':
                        self.found_room()
                    elif key == '加入房间_确认':
                        self.join_room()
                    elif key == '等待中_开始游戏':
                        self.room.start_game()
                        self.get_first_hand_player()
                    elif key == '叫地主=叫地主':
                        self.room.get_boss()
                    elif key == '叫地主=不叫':
                        self.room.do_not_get_boss()
                    elif key == '出牌=出牌':
                        self.room.out_card()
                    elif key == '出牌=过':
                        self.room.pass_card()
                    elif key == '撤销=撤销':
                        self.room.drawback_card()
            for key, exit_box in self.exit_box_dict.items():
                down = exit_box.judge_rect()
                if down:
                    self.exit_box_now = exit_box
            if self.level_now == '游戏中':
                self.room.judge_card_choice()
        elif event_type == 'MOUSE_RIGHT_DOWN':
            if self.level_now == '游戏中':
                self.room.judge_card_choice(True)
        elif (type(event_type) is int and 0 <= event_type <= 9) or event_type == '.':
            if self.exit_box_now is not None and self.exit_box_now.if_draw:
                self.exit_box_now.input_content(str(event_type))
        elif event_type == '退格键':
            if self.exit_box_now is not None and self.exit_box_now.if_draw:
                self.exit_box_now.del_content()


class Room:
    boss_id = 0  # 主机id
    boss_ip = 0  # 主机ip
    boss_address = (boss_ip, boss_id)
    all_address_list = []  # 主机第一个，玩家按顺序排列
    my_id = 0  # 自己id
    my_ip = 0  # 自己ip
    my_address = (my_ip, my_id)
    ui_pos = ((50, 50), (50, 500), (600, 50))  # 分别是左边玩家ui坐标，自己ui坐标，右边玩家ui坐标
    img_dict = {}  # 卡牌图片字典
    card_order = [str(i + 3) for i in range(8)] + ['J', 'Q', 'K', 'A', '2', '小王', '大王']  # 卡牌次序从小到大
    card_color = ['梅花', '黑桃', '方片', '红心']
    img_dir = "扑克素材/扑克_游戏使用/"
    my_state = ''  # 我的当前状态 ：叫地主，出牌, 等待
    last_card_list = []  # 最后一次出牌的顺序
    end_score = 1000  # 基础分
    end_score_now = 1000  # 底分  炸一次成2

    def __init__(self, my_ip, my_id, if_boss=True, boss_ip=0, boss_id=0):
        self.if_boss = if_boss
        Room.my_ip = my_ip
        Room.my_id = int(my_id)
        Room.boss_ip = boss_ip
        Room.boss_id = boss_id
        self.my_index = 0  # 我在信息列表中的索引
        Room.my_address = (my_ip, int(my_id))  # 地址信息
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.bind(self.my_address)
        start_new_thread(self.get_info, ())
        self.ui_list = []  # 分别是左中右玩家ui,  自己在ui_list中的索引永远是1
        self.card_list = []  # 自己的卡牌列表
        self.button_dict = {}  # 游戏中的按钮ui
        self.player_now_index = 0  # 当前出牌的玩家，该变量由主机控制
        self.get_boss_number = 0  # 记录没有叫地主玩家的个数
        self.boss_player_index = 0  # 地主玩家编号
        self.end_card = []  # 底牌
        self.last_card_player_index = 0  # 最后出牌的玩家
        self.drawback_card_list = []  # 我上次出的牌
        self.init_date()

    def init_date(self):
        if self.if_boss:
            Room.boss_id = self.my_id
            Room.boss_ip = self.my_ip
            Room.boss_address = (self.my_ip, self.my_id)
            Room.all_address_list.append(self.boss_address)
            self.get_ui_list()
        else:
            Room.boss_address = (self.boss_ip, self.boss_id)
            self.ask_boss_all_player()

        self.img_dict = {'小王': image.load(self.img_dir + "小王.png"),
                         '大王': image.load(self.img_dir + "大王.png"),
                         '扑克背景': image.load(self.img_dir + "扑克背景.png")}
        for k in self.card_order[:-2]:
            for m in self.card_color:
                name = m + k
                cord_dir = self.img_dir + name + '.png'
                self.img_dict[name] = image.load(cord_dir)

    def start_game(self):  # 主机开始发牌并通知各个玩家
        hand_card = random.sample(range(54), 3)  # 抽取3张不同的牌 0是大王，1是小王，往后依次按照card_color的顺序排列
        hand_card_str = []
        for i in hand_card:
            if i == 0:
                hand_card_str.append('大王')
            elif i == 1:
                hand_card_str.append('小王')
            else:
                k = (i - 2) // 4
                m = (i - 2) % 4
                card_name = self.card_color[m] + self.card_order[k]
                hand_card_str.append(card_name)
        self.end_card = hand_card_str
        all_card_list = list(range(54))
        all_card_list_str = []
        for i in all_card_list:
            if i == 0:
                all_card_list_str.append('大王')
            elif i == 1:
                all_card_list_str.append('小王')
            else:
                k = (i - 2) // 4
                m = (i - 2) % 4
                card_name = self.card_color[m] + self.card_order[k]
                all_card_list_str.append(card_name)
        for i in hand_card_str:
            all_card_list_str.remove(i)
        random.shuffle(all_card_list_str)
        boss_card_list = all_card_list_str[:17]
        next_card_list = all_card_list_str[17:34]
        last_card_list = all_card_list_str[34:]
        self.order_card_from_str(boss_card_list, True)
        next_card_list_order = self.order_card_from_str(next_card_list)
        last_card_list_order = self.order_card_from_str(last_card_list)
        next_card_info = '你的卡牌是!' + '|'.join(next_card_list_order)
        last_card_info = '你的卡牌是!' + '|'.join(last_card_list_order)
        self.send_info(next_card_info, self.all_address_list[1])
        self.send_info(last_card_info, self.all_address_list[2])

    def first_player_go(self, address_index):  # 先手玩家出牌，address为该玩家的地址
        address = Room.all_address_list[address_index]
        self.player_now_index = (address_index + 1) % 3
        self.send_info('你要叫地主吗!', address)
        self.get_boss_number = 1

    def order_card_from_str(self, card_list, if_self=False):
        if len(card_list) == 0 or (len(card_list) == 1 and card_list[0] == ''):
            return []
        order_card_list = []
        for card in card_list:
            if card == '大王' or card == '小王':
                name = card
            else:
                name = card[2:]
            number = self.card_order.index(name)
            order_card_list.append((number, card))
        order_card_list.sort(key=lambda x: x[0], reverse=True)
        if if_self:
            self.card_list = list(array(order_card_list)[:, 1])
            self.ui_list[1].join_card_list(self.card_list)
        else:
            return list(array(order_card_list)[:, 1])

    def ask_boss_all_player(self):  # 向主机询问当前房间内所有玩家地址
        self.send_info('询问所有玩家地址! ', self.boss_address)

    def tell_player_all_address(self):  # 告诉所询问人数的客户所有玩家地址
        info = '|'.join(str(i).replace(' ', '').replace('(', '').replace(')', '').replace("'", '')
                        for i in self.all_address_list)
        return '所有玩家地址如下!' + info

    def same_address_from_boss(self, info):  # 客户同步主机发来的玩家地址信息
        info_list = info.split('|')
        self.all_address_list = []
        i = 0
        for address in info_list:
            m = address.split(',')
            m_ip = m[0]
            m_id = int(m[1])
            address_now = (m_ip, m_id)
            if address_now == self.my_address:
                self.my_index = i
            i += 1
            self.all_address_list.append(address_now)
        self.get_ui_list()

    def get_ui_list(self):  # 获取UI列表
        self.ui_list = []
        try:
            left_address = self.all_address_list[(self.my_index + 2) % 3]
            self.ui_list.append(Ui(self.ui_pos[0], left_address))
        except IndexError:
            pass
        mid_address = self.all_address_list[self.my_index]
        self.ui_list.append(Ui(self.ui_pos[1], mid_address))
        try:
            right_address = self.all_address_list[(self.my_index + 1) % 3]
            self.ui_list.append(Ui(self.ui_pos[2], right_address))
        except IndexError:
            pass

    def get_info(self):
        # 消息中感叹号之前代表命令
        while True:
            get_date = self.udp.recvfrom(6000)
            player_address = get_date[1]
            info_list = get_date[0].decode('utf-8').split('!')
            order = info_list[0]
            info = info_list[1]
            if order == '询问所有玩家地址':  # 主机收到来自客户端的消息  要求主机向客户端发送所有玩家信息
                self.all_address_list.append(player_address)
                massage = self.tell_player_all_address()
                self.get_ui_list()
                for address in self.all_address_list[1:]:
                    self.send_info(massage, address)
            elif order == '所有玩家地址如下':  # 客户端收到来自主机的消息  收到主机发来的所有玩家的地址信息并同步
                self.same_address_from_boss(info)
            elif order == '你的卡牌是':
                self.same_card(info)  # 同步卡牌信息
                Room.end_score_now = Room.end_score  # 底分归为初始化
            elif order == '你要叫地主吗':  # 客户端收到来自主机的消息 询问自己是否要叫地主
                Room.my_state = '叫地主'
            elif order == '我叫地主':  # 主机收到来自客户端的消息  客户要叫地主
                self.rob_boss(info)
            elif order == '我不叫地主':  # 主机收到来自客户端的消息  客户不叫地主
                self.second_get_boss()
            elif order == '该玩家是地主':  # 所有玩家收到了地主的消息
                self.player_now_index = int(info)
                self.boss_player_index = int(info)
            elif order == '出牌':  # 玩家收到了出牌指令
                Room.my_state = '出牌'
            elif order == '你是地主':  # 玩家收到了你是地主出牌指令
                self.same_card(info, True)
            elif order == '玩家出牌':  # 玩家受到了其他玩家出的牌
                self.last_card_player_index = info[0]
                if info[1] == str(self.my_index):
                    Room.my_state = '出牌'
                else:
                    Room.my_state = '等待'
                if info[0] == str(self.my_index):
                    Room.last_card_list = []
                else:
                    Room.last_card_list = self.order_card_from_str(info[2:].split('|'))
                    self.ui_list[1].join_mid_card_list(Room.last_card_list)
            elif order == '撤销出牌':
                Room.my_state = '等待'
                Room.last_card_list = self.order_card_from_str(info.split('|'))
                self.ui_list[1].join_mid_card_list(Room.last_card_list)
            elif order == '我出完了':  # 有玩家出完了，所有玩家增加对应玩家的分数
                win_player_list = info.split('|')
                if len(win_player_list) == 1:  # 地主赢了
                    k = 1
                else:
                    k = -1
                if self.my_index == self.boss_player_index:
                    boss_index = 1
                elif (self.my_index + 1) % 3 == self.boss_player_index:
                    boss_index = 2
                else:
                    boss_index = 0
                i = 0
                for player_ui in self.ui_list:
                    if i == boss_index:
                        player_ui.update_score(k * Room.end_score_now * 2)
                    else:
                        player_ui.update_score(- k * Room.end_score_now)
                    i += 1

    def drawback_card(self):  # 撤销刚出的牌
        Room.my_state = '出牌'
        self.same_card('|'.join(Room.last_card_list), True)
        Room.last_card_list = self.drawback_card_list
        info = '撤销出牌!' + '|'.join(Room.last_card_list)
        print(info)
        self.ui_list[1].join_mid_card_list(Room.last_card_list)
        for i in range(3):
            if i == self.my_index:
                continue
            else:
                self.send_info(info, self.all_address_list[i])

    def remove_choice_list(self, card_list):  # 从我自己的卡牌列表中移除已经出过的牌
        while len(card_list) != 0:
            self.card_list.remove(card_list[0])
            card_list.pop(0)

    def out_card(self):  # 出牌:谁出的牌，下一个需要压的玩家，需要压的牌  竖线划分不同的牌
        info = self.ui_list[1].out_card_ui(self.last_card_list, self.my_index, (self.my_index + 1) % 3)
        if info == '出牌错误':
            return None
        else:
            if_win = info[0]
            info = info[1:]
            self.drawback_card_list = Room.last_card_list.copy()  # 保存之前需要压的牌
            card_list = info.split('!')[1][2:].split('|')
            Room.last_card_list = self.order_card_from_str(card_list)
            self.remove_choice_list(card_list)
            self.ui_list[1].join_mid_card_list(Room.last_card_list)
            for i in range(3):
                if i == self.my_index:
                    continue
                else:
                    self.send_info(info, self.all_address_list[i])
            Room.my_state = '撤销'
            if if_win == '是':  # 我出完了
                info = '我出完了!' + str(self.my_index)  # 告诉其他玩家我出完了，其他玩家增加自己的信息  如果是地主则只给自己加分
                if self.boss_player_index != self.my_index:
                    k = [0, 1, 2]
                    k.remove(self.my_index)
                    print(self.boss_player_index)
                    k.remove(self.boss_player_index)
                    info = info + '|' + str(k[0])
                for i in range(3):
                    self.send_info(info, self.all_address_list[i])

    def pass_card(self):  # 过牌
        info = '玩家出牌!' + str(self.last_card_player_index) + str((self.my_index + 1) % 3) +\
               '|'.join(Room.last_card_list)
        self.ui_list[1].join_mid_card_list(Room.last_card_list)
        for i in range(3):
            if i == self.my_index:
                continue
            else:
                self.send_info(info, self.all_address_list[i])
        Room.my_state = '等待'

    def get_boss(self):  # 我叫地主, 并告诉主机
        Room.my_state = '等待'
        self.send_info('我叫地主!' + str(self.my_index), Room.boss_address)

    def do_not_get_boss(self):  # 我不叫地主， 并告诉主机
        Room.my_state = '等待'
        self.send_info('我不叫地主!', Room.boss_address)

    def rob_boss(self, boss_player_index):  # 确定该玩家为地主
        info = '该玩家是地主!' + str(int(boss_player_index))
        for address in self.all_address_list:  # 向所有玩家发送地主玩家索引，有玩家抢到了地主
            self.send_info(info, address)
        self.send_info('出牌!', self.all_address_list[int(boss_player_index)])
        self.send_info('你是地主!' + '|'.join(self.end_card), self.all_address_list[int(boss_player_index)])

    def second_get_boss(self):  # 玩家不叫地主，问下一个玩家要叫地主吗
        self.get_boss_number += 1
        if self.get_boss_number == 4:
            self.start_game()
            k = random.randint(0, 2)
            self.first_player_go(k)  # 没有玩家叫地主，开始从新洗牌
        else:
            address = Room.all_address_list[self.player_now_index]
            self.player_now_index = (self.player_now_index + 1) % 3
            self.send_info('你要叫地主吗!', address)

    def same_card(self, info, if_join=False):  # 同步来自主机发来的卡牌信息
        card_list = info.split('|')
        if if_join:
            self.card_list = self.card_list + card_list
            self.order_card_from_str(self.card_list, True)
        else:
            self.card_list = card_list
        self.ui_list[1].join_card_list(self.card_list)

    def send_info(self, info, address):
        self.udp.sendto(bytes(info, encoding='utf-8'), address)

    def draw_ui(self, screen: Surface):  # 绘制房间ui
        screen.blit(self.img_dict['扑克背景'], (int(Mind.size[0] / 2 - 100), int(Mind.size[1] / 2 - 150)))
        for player_ui in self.ui_list:
            player_ui.draw(screen)

    def judge_card_choice(self, if_see=False):
        try:
            self.ui_list[1].judge_choice_card(if_see)
        except IndexError:
            pass

    def draw(self, screen: Surface):
        self.draw_ui(screen)


def run():
    init()
    display.set_caption("我斗地主贼六")
    mind = Mind()
    while True:
        mind.screen.fill((255, 255, 255))
        mind.draw()
        for event in events.get():
            if event.type == QUIT:
                exit()
            elif event.type == MOUSEMOTION:
                # buttons
                mind.mouse_pos = event.pos
            elif event.type == MOUSEBUTTONDOWN:
                # button  左1 右3 向下5 向上4
                if event.button == 1:
                    mind.deal_event('MOUSE_LEFT_DOWN')
                elif event.button == 3:
                    mind.deal_event('MOUSE_RIGHT_DOWN')
                elif event.button == 4:
                    pass
            elif event.type == MOUSEBUTTONUP:
                # button
                if event.button == 1:
                    mind.deal_event('MOUSE_LEFT_UP')
            elif event.type == KEYDOWN:
                if 256 <= event.key <= 265:
                    mind.deal_event(event.key - 256)  # 纯数字输入
                elif 48 <= event.key <= 57:
                    mind.deal_event(event.key - 48)  # 纯数字输入
                elif event.key == 47 or event.key == 266:
                    mind.deal_event('.')  # 小数点
                elif event.key == 8:
                    mind.deal_event('退格键')
            elif event.type == KEYUP:
                # print(event.key)
                pass
        mind.clock.tick(mind.fps)
        display.update()


if __name__ == '__main__':
    run()
