from pygame import font
from pygame import Surface
from pygame import mouse
from pygame import draw
from pygame import image


class Label:
    def __init__(self, name, label, pos, font_size=30):
        self.name = name
        self.label = label
        self.pos = pos
        self.font = font.SysFont('SimHei', font_size)
        self.label = self.font.render(self.label, True, (0, 0, 0))

    def draw(self, screen: Surface):
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
        self.line_end_pos = (self.line_begin_pos[0] + 200, self.line_begin_pos[1])
        self.content = ''  # 所记录的内容
        self.content_pos = (self.line_begin_pos[0] + 2, self.rect[1] + 2)
        self.content_label = Label(name, self.content, self.content_pos)
        self.judge_rect_x = (self.rect[0], self.line_end_pos[0])
        self.judge_rect_y = (self.rect[1], self.line_end_pos[1])
        self.if_draw = True  # 是否显示

    def del_content(self):
        if not self.if_draw:
            return None
        self.content = self.content[:-1]
        self.content_label = Label(self.name, self.content, self.content_pos)

    def input_content(self, word):
        if not self.if_draw:
            return None
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
        if not self.if_draw:
            return False
        x, y = mouse.get_pos()
        if self.judge_rect_x[0] <= x <= self.judge_rect_x[1] and self.judge_rect_y[0] <= y <= self.judge_rect_y[1]:
            self.if_inputting = True
            return True
        self.if_inputting = False
        return False

    def draw(self, screen: Surface):
        if not self.if_draw:
            return None
        self.label.draw(screen)
        draw.rect(screen, EditBox.Inputting_color if self.if_inputting else EditBox.Free_color, self.rect, 1)
        draw.line(screen, EditBox.Inputting_color if self.if_inputting else EditBox.Free_color,
                  self.line_begin_pos, self.line_end_pos)
        self.content_label.draw(screen)


class Button:
    word_color = (0, 0, 0)
    rect_color = (0, 0, 0)

    def __init__(self, name, show_name, pos, img=None, if_draw=True, if_wait=False):
        self.name = name
        self.show_name = show_name
        self.pos = pos
        self.img = img
        self.font = font.SysFont('SimHei', 30)
        self.label = self.font.render(self.name, True, Button.word_color)
        self.word_rect_width = 10
        self.word_pos = (pos[0] + self.word_rect_width, pos[1] + self.word_rect_width)
        self.rect = (pos[0], pos[1], len(self.show_name) * 30 + self.word_rect_width * 2,
                     30 + self.word_rect_width * 2)
        self.if_draw = if_draw  # 是否显示
        self.if_wait = if_wait  # 是否为等待按钮

    def judge_rect(self):
        if not self.if_draw:
            return False
        x, y = mouse.get_pos()
        if 0 < x - self.pos[0] < self.rect[2] and 0 < y - self.pos[1] < self.rect[3]:
            return True
        else:
            return False

    def draw(self, screen: Surface):
        if not self.if_draw:
            return None
        if self.img is not None:
            screen.blit(self.img, self.pos)
            return None
        screen.blit(self.label, self.word_pos)
        if self.if_wait:
            return None
        draw.rect(screen, Button.rect_color, self.rect, 1)


class Ui:
    # 单个玩家的UI游戏中UI显示
    ui_width = 100
    ui_height = 200
    card_order = [str(i + 3) for i in range(8)] + ['J', 'Q', 'K', 'A', '2', '小王', '大王']  # 卡牌次序从小到大
    card_color = ['梅花', '黑桃', '方片', '红心']
    img_dir = "扑克素材/扑克_游戏使用/"
    img_dict = {'小王': image.load(img_dir + "小王.png"),
                '大王': image.load(img_dir + "大王.png"),
                '扑克背景': image.load(img_dir + "扑克背景.png")}
    for k in card_order[:-2]:
        for m in card_color:
            name = m + k
            cord_dir = img_dir + name + '.png'
            img_dict[name] = image.load(cord_dir)
    card_pos_base = (380, 400)
    card_show_width = 35
    card_choice_height = 40  # 被选中后向上移动的距离
    card_mid_pos_base = 380, 200

    def __init__(self, pos, address, if_boss=False):  # if_boss为是否为地主
        self.pos = pos
        self.rect = (pos[0], pos[1], self.ui_width, self.ui_height)
        self.my_ip = address[0]
        self.my_id = int(address[1])
        self.id_label = Label('ID', 'ID:' + str(address[1]), self.pos, font_size=20)
        self.ip_label = Label('IP', 'IP:' + self.my_ip, (self.pos[0], self.pos[1] + 21), font_size=20)
        self.card_list = []  # 卡牌对象
        self.choice_card_list = []  # 选中的卡牌名称
        self.bigger_card_list = []  # 更大的卡牌列表
        self.boom_list = []  # 炸弹列表,用竖线划分
        self.see_card_now = None  # 当前正在看的卡牌
        self.score = 0  # 自己的分数
        self.mid_card_list = []  # 在中间现实的卡牌
        self.score_label = Label('豆子', '豆子:' + str(self.score), (self.pos[0], self.pos[1] + 42), font_size=20)
        self.if_boss = if_boss  # 是否为地主
        self.boss_pos_ui = 0, 0  # 地主ui显示位置

    def update_score(self, abs_score):  # 更新自己的分数与现实
        self.score += abs_score
        self.score_label = Label('豆子', '豆子:' + str(self.score), (self.pos[0], self.pos[1] + 42), font_size=20)

    def out_card_ui(self, other_card_list, who_out, next_out):  # 出牌:谁出的牌，下一个需要压的玩家，需要压的牌  竖线划分不同的牌
        if len(self.choice_card_list) == 0:
            return '出牌错误'
        """if not self.check_card_order(other_card_list):  # 不做合法性检测
            return '出牌错误'"""
        info = '玩家出牌!' + str(who_out) + str(next_out) + '|'.join(self.choice_card_list)
        self.remove_choice_list()
        if len(self.card_list) == 0:
            info = '是' + info
        else:
            info = '否' + info  # 第一个字表示自己是否出完
        return info

    def remove_choice_list(self):
        if self.see_card_now is not None:
            self.see_card_now.see_the_card(False)
            self.see_card_now = None
        while len(self.choice_card_list) != 0:
            for card in self.card_list:
                if card.name in self.choice_card_list:
                    self.choice_card_list.remove(card.name)
                    self.card_list.remove(card)
                    break
        self.choice_card_list = []
        card_first_pos = self.card_pos_base[0] - self.card_show_width * len(self.card_list) // 2, self.card_pos_base[1]
        i = 0
        for card in self.card_list:
            pos = card_first_pos[0] + i * self.card_show_width, card_first_pos[1]
            card.update_show_pos(pos)
            i += 1

    def check_card_order(self, other_card_list):  # 检查出牌合法性
        self.get_bigger_card_list(other_card_list)
        if len(self.bigger_card_list) == 0:
            return False
        if self.bigger_card_list[0] == 'all':
            return self.just_check_right()
        else:
            pass

    def just_check_right(self):  # 仅做合法性检测
        if len(self.choice_card_list) == 1:
            return True
        elif len(self.choice_card_list) == 2:
            if self.choice_card_list[0][2:] == self.choice_card_list[1][2:]:
                return True
        elif len(self.choice_card_list) == 3:
            if self.choice_card_list[0][2:] == self.choice_card_list[1][2:] == self.choice_card_list[2][2:]:
                return True
        elif len(self.choice_card_list) == 4:
            if self.choice_card_list[0][2:] == self.choice_card_list[1][2:] \
                    == self.choice_card_list[2][2:] == self.choice_card_list[3][2:]:
                return True
            else:
                card_list = [card[2:] for card in self.choice_card_list]
                number_1 = card_list.count(card_list[0])
                number_2 = card_list.count(card_list[1])
                if number_1 == 3 or number_2 == 3:
                    return True
        elif len(self.choice_card_list) == 5:
            if self.judge_order_card_list(5, self.choice_card_list):
                return True
            else:
                card_list = [card[2:] for card in self.choice_card_list]
                number_list = []
                for i in range(5):
                    number_list.append(card_list.count(card_list[i]))
                while 3 in number_list:
                    number_list.remove(3)
                while 2 in number_list:
                    number_list.remove(2)
                if len(number_list) == 0:
                    return True
        else:
            if self.judge_airport():
                return True
            elif self.judge_boom_with_both():
                return True
            elif self.judge_order_card_list(len(self.choice_card_list), self.choice_card_list):
                return True
            elif self.judge_if_both_list():
                # 判断是否为连队
                return True
        return False

    def judge_if_both_list(self):  # 判断是否为连对
        card_list = list(set(i[2:] for i in self.choice_card_list))
        if '' in card_list or '2' in card_list:
            return False
        else:
            order_card_list = ['黑桃' + i for i in card_list]
            return self.judge_order_card_list(len(order_card_list), order_card_list)

    def judge_boom_with_both(self):  # 判断是不是炸弹带两对或两单
        number = len(self.choice_card_list)
        card_list = [card[2:] for card in self.choice_card_list]
        if '' in card_list:
            return False
        number_list = []
        for i in range(number):
            number_list.append(card_list.count(card_list[i]))
        if max(number_list) != 4:
            return False
        boom_number = number_list.count(4) // 4
        boom_list = []
        for i in range(number):
            if number_list[i] == 4:
                boom_list.append(self.card_order.index(self.choice_card_list[i][2:]))
        if self.card_order.index('2') in boom_list:
            return False
        boom_list = list(set(boom_list))
        boom_list.sort()
        for k in range(len(boom_list) - 1):
            if boom_list[k] + 1 == boom_list[k + 1]:
                continue
            else:
                break
        else:
            if len(self.choice_card_list) == boom_number * 4 + boom_number * 2:
                return True
            elif len(self.choice_card_list) == boom_number * 4 + boom_number * 4:
                while 4 in number_list:
                    number_list.remove(4)
                while 2 in number_list:
                    number_list.remove(2)
                if len(number_list) == 0:
                    return True
        return False

    def judge_airport(self):  # 判断是不是飞机, 若参数为真则判断是否为飞机
        number = len(self.choice_card_list)
        if number % 2 == 1:
            return False
        card_list = [card[2:] for card in self.choice_card_list]
        if '' in card_list:
            return False
        number_list = [card_list.count(i) for i in card_list]
        airport_list = []
        k = 0
        for i in number_list:
            if i == 3:
                airport_list.append(self.card_order.index(card_list[k]))
            k += 1
        airport_list = list(set(airport_list))
        airport_list.sort()
        for m in range(len(airport_list) - 1):
            if airport_list[m] + 1 == airport_list[m + 1]:
                continue
            else:
                break
        else:
            p = len(airport_list)
            if len(card_list) == p * 3 + p:
                return True
            elif len(card_list) == p * 3 + p * 2:
                while 3 in number_list:
                    number_list.remove(3)
                for i in number_list:
                    if i % 2 == 0:
                        continue
                    else:
                        return False
                else:
                    return True
            else:
                return False
        return False

    def judge_order_card_list(self, number, judge_card_list):  # 判断是不是顺子
        card_list = []
        for card in judge_card_list:
            if card[2:] == '' or card[2:] == '2':
                continue
            else:
                card_list.append(self.card_order.index(card[2:]))
        card_list.sort()
        if len(card_list) != number:
            return False
        for i in range(number - 1):
            if card_list[i] + 1 == card_list[i + 1]:
                continue
            else:
                break
        else:
            return True
        return False

    def get_bigger_card_list(self, card_list):  # 从自己的卡牌列表中搜索所有大于当前需要压过的卡牌
        self.bigger_card_list = []
        if len(card_list) == 0:
            self.bigger_card_list = ['all']  # 代表所有卡牌都可以
            return None
        self.get_boom_list()  # 获取所有炸弹
        get_biggest_boom = False
        if '大王|小王' in self.boom_list:
            self.bigger_card_list.append('大王|小王')
            get_biggest_boom = True
        if len(card_list) == 1 or (len(card_list) == 2 and '大王' not in card_list)\
                or len(card_list) == 3 or len(card_list) > 4:
            self.bigger_card_list += self.boom_list
        if len(card_list) == 1:
            for card in self.card_list:
                if card.if_bigger(card_list[0]):
                    self.bigger_card_list.append(card.name[2:])
            return None
        elif len(card_list) == 2:
            if '大王' in card_list and '小王' in card_list:
                self.bigger_card_list = []
                return None
            else:
                both_card_list = self.get_bigger_same_card(card_list[0])
                self.bigger_card_list += both_card_list
        elif len(card_list) == 3:
            same_card_list = self.get_bigger_same_card(card_list[0], 3)
            self.bigger_card_list += same_card_list
        elif len(card_list) == 4:
            if card_list[0][2:] == card_list[1][2:] == card_list[2][2:] == card_list[3][2:]:
                if get_biggest_boom:
                    boom_list = self.boom_list[1:]
                else:
                    boom_list = self.boom_list
                for boom in boom_list:
                    self_boom_number = self.card_order.index(boom.split('|')[0])
                    other_boom_number = self.card_order.index(card_list[0][2:])
                    if self_boom_number > other_boom_number:
                        self.bigger_card_list.append(boom)
            else:
                same_card_list = self.get_bigger_same_card(card_list[0], 3)
                self.bigger_card_list += same_card_list
        elif len(card_list) == 5:
            if card_list[0][2:] == card_list[1][2:] == card_list[2][2:]:  # 3带一对
                same_card_list = self.get_bigger_same_card(card_list[0], 3)
                self.bigger_card_list += same_card_list
            else:
                order_card_list = self.get_order_card_list(card_list[0], 5)  # 5连
                self.bigger_card_list += order_card_list
        else:
            order_card_list = self.get_order_card_list(card_list[0], len(card_list))
            self.bigger_card_list += order_card_list

    def get_order_card_list(self, other_first_name, number=5):  # 获取大于other_first_name的连子列表
        if len(self.card_list) < number:
            return []
        card_list = []
        card_name_list = []
        for card in self.card_list:
            if card.name[2:] == '' or card.name[2:] == '2':
                continue
            else:
                card_list.append(self.card_order.index(card.name[2:]))
                card_name_list.append(card.name[2:])
        k = number - 1
        order_card_list = []
        for card in card_list[number - 1:]:
            for i in range(number - 1):
                if card - 1 - i == card_list[k - 1 - i]:
                    continue
                else:
                    break
            else:
                if card - number + 1 > self.card_order.index(other_first_name[2:]):
                    order_card_list.append('|'.join(card_name_list[k - number + 1:k + 1]))
            k += 1
        return order_card_list

    def get_bigger_same_card(self, other_name, number=2):  # 返回所有比other_name大的相同卡牌列表
        same_card_list = []
        if len(self.card_list) < number:
            return []
        k = number - 1
        for card in self.card_list[number - 1:]:
            for i in range(number - 1):
                if card == self.card_list[k - 1 - i]:
                    continue
                else:
                    break
            else:
                if card.if_bigger(other_name):
                    same_card_list.append('|'.join(m.name[2:] for m in self.card_list[k + 1 - number:k + 1]))
                k += number
                continue
            k += 1
        return same_card_list

    def get_boom_list(self):  # 获取炸弹列表
        get_biggest_boom = False  # 是否拥有王炸
        self.boom_list = []
        try:
            if self.card_list[0] == '大王' and self.card_list[1] == '小王':
                self.boom_list.append('大王|小王')
                get_biggest_boom = True
        except IndexError:
            pass
        if get_biggest_boom:
            card_list = self.card_list[2:]
        else:
            card_list = self.card_list
        if len(card_list) < 4:
            return None
        k = 3
        for card in card_list[3:]:
            if card == card_list[k - 1] and card == card_list[k - 2] and card == card_list[k - 3]:
                self.boom_list.append('|'.join(i.name[2:] for i in card_list[k - 3:k + 1]))
                k += 4
            else:
                k += 1

    def join_mid_card_list(self, card_list):  # 添加需要在中间现实的卡牌
        self.mid_card_list = []
        base_pos = self.card_mid_pos_base[0] - self.card_show_width * len(card_list) // 2, self.card_mid_pos_base[1]
        i = 0
        for name in card_list:
            pos = base_pos[0] + i * self.card_show_width, base_pos[1]
            self.mid_card_list.append(Card(name, pos, self.img_dict[name]))
            i += 1

    def join_card_list(self, card_list):
        self.card_list = []
        self.choice_card_list = []
        card_first_pos = self.card_pos_base[0] - self.card_show_width * len(card_list) // 2, self.card_pos_base[1]
        i = 0
        for name in card_list:
            pos = card_first_pos[0] + i * self.card_show_width, card_first_pos[1]
            self.card_list.append(Card(name, pos, self.img_dict[name]))
            i += 1

    def judge_choice_card(self, if_see=True):  # 返回被选中的卡牌对象, 参数为是否观看卡牌，如果为真则将卡牌向下移动
        i = 1
        for card in self.card_list:
            if i == len(self.card_list):
                k = True
            else:
                k = False
            i += 1
            if card.judge_choice(k):
                if if_see:
                    if card.name in self.choice_card_list:
                        return None
                    if self.see_card_now is None:
                        card.see_the_card(True)
                        self.see_card_now = card
                    else:
                        if self.see_card_now.name == card.name:
                            card.see_the_card(False)
                            self.see_card_now = None
                        else:
                            card.see_the_card(True)
                            self.see_card_now.see_the_card(False)
                            self.see_card_now = card
                    return None
                if self.see_card_now is not None and card.name == self.see_card_now.name:
                    return None
                if card.name in self.choice_card_list:
                    self.choice_card_list.remove(card.name)
                    card.change_state()
                else:
                    self.choice_card_list.append(card.name)
                    card.change_state()
                return None

    def draw_mid_card(self, screen: Surface):
        if len(self.mid_card_list) == 0:
            return None
        for card in self.mid_card_list:
            card.draw(screen)

    def draw_card(self, screen: Surface):
        if len(self.card_list) == 0:
            return None
        for card in self.card_list:
            card.draw(screen)

    def draw_boss_ui(self, screen: Surface):  # 绘制地主UI
        if self.if_boss:
            pass


    def draw(self, screen: Surface):
        self.id_label.draw(screen)
        self.ip_label.draw(screen)
        self.score_label.draw(screen)
        self.draw_mid_card(screen)
        self.draw_card(screen)


class Card:
    # 处理单张卡牌信息
    card_order = [str(i + 3) for i in range(8)] + ['J', 'Q', 'K', 'A', '2', '小王', '大王']  # 卡牌次序从小到大

    def __init__(self, name, pos, img):
        self.name = name
        self.pos = pos
        self.show_pos = pos
        self.img = img
        self.if_choice = False

    def update_show_pos(self, pos):
        self.pos = pos
        self.show_pos = pos

    def if_bigger(self, other):  # 以字符串形式比较
        if self.name == '大王' or self.name == '小王':
            self_key = self.name
        else:
            self_key = self.name[2:]
        if other == '大王' or other == '小王':
            other_key = other
        else:
            other_key = other[2:]
        self_number = self.card_order.index(self_key)
        other_number = self.card_order.index(other_key)
        return self_number > other_number

    def __eq__(self, other):  # 判断两张卡牌对象是否相等
        if len(self.name) == 2 or len(other.name) == 2:
            return False
        return self.name[2:] == other.name[2:]

    def judge_choice(self, if_all_judge):  # 判断是否选中卡牌, 参数为是否完全判断
        x, y = mouse.get_pos()
        abs_x = x - self.show_pos[0]
        abs_y = y - self.show_pos[1]
        img_rect = self.img.get_rect()
        width = img_rect[2] if if_all_judge else Ui.card_show_width
        height = img_rect[3]
        if 0 < abs_x < width and 0 < abs_y < height:
            return True
        else:
            return False

    def change_state(self):  # 根据选中与否切换状态
        self.if_choice = not self.if_choice
        if self.if_choice:
            self.show_pos = self.pos[0], self.pos[1] - Ui.card_choice_height
        else:
            self.show_pos = self.pos

    def see_the_card(self, if_see):  # 看这张卡牌
        if if_see:
            self.show_pos = self.pos[0], self.pos[1] + Ui.card_choice_height
        else:
            self.show_pos = self.pos

    def draw(self, screen: Surface):
        screen.blit(self.img, self.show_pos)


if __name__ == '__main__':
    pass
