import pygame,sys
import random as ra
import math
import time
class Qtable():
    def __init__(self,state_rite=0.9,learning_rite=0.9,change_rite=0.9,epoch_write=100):
        # state_rite 为行为概率
        self.state_rite = state_rite
        self.learning_rite = learning_rite
        self.change_rite = change_rite
        self.epoch_write = epoch_write
        self.action = ['U','D','L','R','N']
        self.table = {}#每一行为 状态与该状态对应上(U)、下(D)、左(L)、右(R)、不行为(N)各个得分 如：((1,1)'U'):[0,0,0,0,0]
        self.per_epoch_can_eat_food = {}#每训练epoch_write轮所能在一条命中吃到的食物数
        self.per_epoch_can_eat_food_all = {}#每训练epoch_write轮所能吃的食物总数
    def append_per_epoch_list(self,epoch,food_num):
        # 参数为轮次，该条命吃到的食物数,该条命吃第一个食物所用时间
        if epoch not in self.per_epoch_can_eat_food.keys():
            self.per_epoch_can_eat_food[epoch] = food_num
    def append_per_epoch_list_all(self,epoch,food_num):
        if epoch not in self.per_epoch_can_eat_food_all.keys():
            self.per_epoch_can_eat_food_all[epoch] = food_num
    def save_Q_table(self,filename,per_eat_food_filename,per_eat_food_all_filename):
        text = '得分\n状态\行为,向上,向下,向左,向右,不作为\n'
        for i in self.table.keys():
            y = str(i).replace(',','，')
            text+=str(y)
            text+=','
            for j in self.table[i]:
                text+=str(j)
                text+=','
            text=text[:-1]
            text+='\n'
        file = open(filename,'w')
        file.write(text)
        file.close()
        per_epoch_text = '轮次,该伦次所能吃的食物数\n'
        for x in self.per_epoch_can_eat_food.keys():
            per_epoch_text+=str(x)
            per_epoch_text+=','
            per_epoch_text+=str(self.per_epoch_can_eat_food[x])
            per_epoch_text+='\n'
        per_file = open(per_eat_food_filename,'w')
        per_file.write(per_epoch_text)
        per_file.close()
        per_epoch_all_file = open(per_eat_food_all_filename,'w')
        per_eat_all_text = '轮次,上次到现在所吃食物总数\n'
        for y in self.per_epoch_can_eat_food_all.keys():
            per_eat_all_text+=(str(y)+','+str(self.per_epoch_can_eat_food_all[y])+'\n')
        per_epoch_all_file.write(per_eat_all_text)
        per_epoch_all_file.close()
    def choice_action(self,state):
        # 从行为表中根据当先指向食物的向量选择一个行为
        self.check_if_state_in_table(state)
        if ra.random() < self.state_rite:
            return self.get_ture_action(state)
        else:
            return ra.choice(self.action)
    def get_ture_action(self,state):
        # 随机选择一个最佳动作
        action = self.table[state]
        next_action = []
        max_action = max(action)
        for i in range(len(action)):
            if action[i] == max_action:
                next_action.append(i)
        return self.action[ra.choice(next_action)]
    def learn(self,state,action,score,next_state,if_eat_food):
        self.check_if_state_in_table(next_state)
        q_pre = self.table[state][self.action.index(action)]
        q_rel = score + self.learning_rite * max(self.table[next_state])
        q = q_rel - q_pre
        if if_eat_food:
            q = 3
        if (state[1] == 'L' or state[1] == 'R') and (action == 'L' or action == 'R'):
            q = -10
        elif (state[1] == 'U' or state[1] == 'D') and (action == 'U' or action == 'D'):
            q = -10
        if state[2] == action and action != 'N':
            q = -10
        self.table[state][self.action.index(action)] += self.change_rite * q
    def check_if_state_in_table(self,state):
        # state 为指向食物向量与当前前进方向组成的索引
        if state not in self.table.keys():
            self.table[state] = [0,0,0,0,0]
            return False# 说明不在table中
        return True# 在table中
class Snake():
    def __init__(self, if_AI):
        self.time = time.time()
        self.size = width, height = 1200, 600
        self.screen = pygame.display.set_mode(self.size)
        self.Snake_move_size = Snake_width, Snake_height = 1000,600
        self.if_AI = if_AI
        if if_AI:
            self.AI_epoch = 0#AI训练轮次
            self.fps = 50
        else:
            self.fps = 10
        self.food_radius = 5
        self.food_pos = [ra.randint(0,Snake_width),ra.randint(0,Snake_height)]
        self.clock = pygame.time.Clock()  # 创建一个时间对象
        self.Snake_body_per_size_half = 10
        self.Snake_head_radius = 5
        self.move_speed = 2*self.Snake_body_per_size_half
        self.font = pygame.font.SysFont('SimHei', 15)
        self.init_Snake_body = [[int(Snake_width/2),int(Snake_height/2)],
                           [int(Snake_width / 2 - 2 * self.Snake_body_per_size_half), int(Snake_height / 2)],
                           [int(Snake_width / 2 - 4 * self.Snake_body_per_size_half), int(Snake_height / 2)],
                           [-1,-1]]
        self.Snake_body = self.init_Snake_body.copy()
        self.Snake_director = 'R'# 左 L，右 R 上U ,下 D
        self.score = 0
        self.all_score = 0
        self.last_all_score = 0#上阶段所吃总数
        self.has_cont_epoch = []#记录表已经统计过的时间
        self.has_use_time = 0#记录本次用时
    def AI_dead(self):
        self.AI_epoch += 1
    def AI_get_next_state(self,action):
        # 根据AI行为从环境中获取反馈
        now_score = self.score
        distance = self.get_point_distance(self.food_pos,self.Snake_body[0])
        dead, dead_score = self.change_AI_move_director(action)
        next_food_vector = ((self.food_pos[0] - self.Snake_body[0][0]),(self.food_pos[1] - self.Snake_body[0][1]))
        next_state_vector_x = 0
        next_state_vector_y = 0
        if next_food_vector[0] > 0:
            next_state_vector_x = 1
        elif next_food_vector[0] < 0:
            next_state_vector_x = -1
        if next_food_vector[1] > 0:
            next_state_vector_y = 1
        elif next_food_vector[1] < 0:
            next_state_vector_y = -1
        next_state_vector = (next_state_vector_x,next_state_vector_y)
        new_dis = self.get_point_distance(self.food_pos,self.Snake_body[0])
        score = distance - new_dis
        now_score = self.score - now_score
        if now_score>0:
            if_eat_food = True
        else:
            if_eat_food = False
        next_state = (next_state_vector, self.Snake_director, self.get_dead_director())
        return next_state,score,dead,dead_score,if_eat_food
    def get_AI_data(self,epoch):
        # 统计AI训练到现在的成果
        self.has_cont_epoch.append(epoch)
        return self.score,self.has_use_time
    def get_dead_director(self):
        if self.Snake_body[0][0] - self.move_speed <= 0:
            return 'L'
        elif self.Snake_body[0][0] + self.move_speed >= self.Snake_move_size[0]:
            return 'R'
        elif self.Snake_body[0][1] - self.move_speed <= 0:
            return 'U'
        elif self.Snake_body[0][1] + self.move_speed >= self.Snake_move_size[1]:
            return 'D'
        else:
            for pos in self.Snake_body[2:-1]:
                if self.get_point_distance(pos,
                                           (self.Snake_body[0][0] - self.move_speed,self.Snake_body[0][1]))\
                        < self.Snake_body_per_size_half:
                    return 'L'
                elif self.get_point_distance(pos,
                                           (self.Snake_body[0][0] + self.move_speed,self.Snake_body[0][1]))\
                        < self.Snake_body_per_size_half:
                    return 'R'
                elif self.get_point_distance(pos,
                                           (self.Snake_body[0][0],self.Snake_body[0][1] - self.move_speed))\
                        < self.Snake_body_per_size_half:
                    return 'U'
                elif self.get_point_distance(pos,
                                           (self.Snake_body[0][0],self.Snake_body[0][1] + self.move_speed))\
                        < self.Snake_body_per_size_half:
                    return 'D'
            return 'N'
    def get_state(self):
        food_vector = ((self.food_pos[0] - self.Snake_body[0][0]), (self.food_pos[1] - self.Snake_body[0][1]))
        next_state_vector_x = 0
        next_state_vector_y = 0
        if food_vector[0] > 0:
            next_state_vector_x = 1
        elif food_vector[0] < 0:
            next_state_vector_x = -1
        if food_vector[1] > 0:
            next_state_vector_y = 1
        elif food_vector[1] < 0:
            next_state_vector_y = -1
        next_state_vector = (next_state_vector_x, next_state_vector_y)
        next_state = (next_state_vector,self.Snake_director,self.get_dead_director())
        return next_state
    def get_point_distance(self,point1,point2):
        dis = math.sqrt((point1[0]-point2[0])**2+(point1[1]-point2[1])**2)
        return dis
    def eat_food(self):
        if self.get_point_distance(self.food_pos,
                                   self.Snake_body[0]) <= self.food_radius + 2*self.Snake_body_per_size_half:
            self.add_Snake_body()
            self.food_pos = [ra.randint(5, self.Snake_move_size[0]-5), ra.randint(5, self.Snake_move_size[1]-5)]
    def init_data(self):
        # 死亡后初始化数据
        self.Snake_body = self.init_Snake_body.copy()
        self.score = 0
    def draw_all(self):
        for snake_x,snake_y in self.Snake_body[0:-1]:
            pygame.draw.rect(self.screen, (255,255,255), (int(snake_x - self.Snake_body_per_size_half),
                                                        int(snake_y - self.Snake_body_per_size_half),
                                                        int(2 * self.Snake_body_per_size_half),
                                                        int(2 * self.Snake_body_per_size_half)))
        pygame.draw.circle(self.screen,(0,0,0),self.Snake_body[0],self.Snake_head_radius)
        pygame.draw.line(self.screen,(255,255,255),(self.Snake_move_size[0],0),self.Snake_move_size)
        pygame.draw.circle(self.screen,(255,255,255),self.food_pos,self.food_radius)
        text = self.font.render('当前轮次分数:{}'.format(self.score), True, (255,255,255))
        self.screen.blit(text, (self.Snake_move_size[0]+10, 20))
        text = self.font.render('总分数:{}'.format(self.all_score), True, (255, 255, 255))
        self.screen.blit(text, (self.Snake_move_size[0] + 10, 50))
        text = self.font.render('↑ ↓ ← →键控制移动', True, (255, 255, 255))
        self.screen.blit(text, (self.Snake_move_size[0] + 10, 80))
        text = self.font.render('按H键切换操作者', True, (255, 255, 255))
        self.screen.blit(text, (self.Snake_move_size[0] + 10, 110))
        text = self.font.render('当前速率:{}'.format(self.fps), True, (255, 255, 255))
        self.screen.blit(text, (self.Snake_move_size[0] + 10, 140))
        if self.if_AI:
            text = self.font.render('Q键(速率+10)(仅限AI)', True, (255, 255, 255))
            self.screen.blit(text, (self.Snake_move_size[0] + 10, 170))
            text = self.font.render('E键(速率-10)(仅限AI)', True, (255, 255, 255))
            self.screen.blit(text, (self.Snake_move_size[0] + 10, 200))
            text = self.font.render('A键(速率+500)(仅限AI)', True, (255, 255, 255))
            self.screen.blit(text, (self.Snake_move_size[0] + 10, 230))
            text = self.font.render('D键(速率设为30)(仅限AI)', True, (255, 255, 255))
            self.screen.blit(text, (self.Snake_move_size[0] + 10, 260))
            text = self.font.render('当前操作者：AI'.format(self.AI_epoch), True, (255, 255, 255))
            self.screen.blit(text, (self.Snake_move_size[0] + 10, 290))
            text = self.font.render('AI训练轮次：{}'.format(self.AI_epoch), True, (255, 255, 255))
            self.screen.blit(text, (self.Snake_move_size[0] + 10, 320))
            text = self.font.render('按Tab键保存AI所学到的数据', True, (255, 255, 255))
            self.screen.blit(text, (self.Snake_move_size[0] + 10, 350))
            text = self.font.render('当前训练时间:{:.1f}s'.format(time.time()-self.time), True, (255, 255, 255))
            self.screen.blit(text, (self.Snake_move_size[0] + 10, 380))
        else:
            text = self.font.render('当前操作者：人类'.format(self.AI_epoch), True, (255, 255, 255))
            self.screen.blit(text, (self.Snake_move_size[0] + 10, 170))
        self.eat_food()
    def change_AI_move_director(self,director):
        # 向director方向移动
        if director == 'L':
            if self.Snake_director != 'L' and self.Snake_director != 'R':
                self.Snake_director = 'L'
                self.Snake_body.insert(0,[self.Snake_body[0][0] - self.move_speed,
                                          self.Snake_body[0][1]])
                self.Snake_body.pop(-1)
        elif director == 'R':
            if self.Snake_director != 'L' and self.Snake_director != 'R':
                self.Snake_director = 'R'
                self.Snake_body.insert(0, [self.Snake_body[0][0] + self.move_speed,
                                           self.Snake_body[0][1]])
                self.Snake_body.pop(-1)
        elif director == 'U':
            if self.Snake_director != 'U' and self.Snake_director != 'D':
                self.Snake_director = 'U'
                self.Snake_body.insert(0, [self.Snake_body[0][0],
                                           self.Snake_body[0][1] - self.move_speed])
                self.Snake_body.pop(-1)
        elif director == 'D':
            if self.Snake_director != 'U' and self.Snake_director != 'D':
                self.Snake_director = 'D'
                self.Snake_body.insert(0, [self.Snake_body[0][0],
                                           self.Snake_body[0][1] + self.move_speed])
                self.Snake_body.pop(-1)
        elif director == 'N':
            if self.Snake_director == 'L':
                self.Snake_body.insert(0, [self.Snake_body[0][0] - self.move_speed,
                                           self.Snake_body[0][1]])
                self.Snake_body.pop(-1)
            elif self.Snake_director == 'R':
                self.Snake_body.insert(0, [self.Snake_body[0][0] + self.move_speed,
                                           self.Snake_body[0][1]])
                self.Snake_body.pop(-1)
            elif self.Snake_director == 'U':
                self.Snake_body.insert(0, [self.Snake_body[0][0],
                                           self.Snake_body[0][1] - self.move_speed])
                self.Snake_body.pop(-1)
            else:
                self.Snake_body.insert(0, [self.Snake_body[0][0],
                                           self.Snake_body[0][1] + self.move_speed])
                self.Snake_body.pop(-1)
        a, b = self.if_dead()
        return a, b
    def change_move_director(self,director):
        # 向director方向移动
        if director == 'L':
            if self.Snake_director != 'L' and self.Snake_director != 'R':
                self.Snake_director = 'L'
                self.Snake_body[0][0] -= self.move_speed
        elif director == 'R':
            if self.Snake_director != 'L' and self.Snake_director != 'R':
                self.Snake_director = 'R'
                self.Snake_body[0][0] += self.move_speed
        elif director == 'U':
            if self.Snake_director != 'U' and self.Snake_director != 'D':
                self.Snake_director = 'U'
                self.Snake_body[0][1] -= self.move_speed
        elif director == 'D':
            if self.Snake_director != 'U' and self.Snake_director != 'D':
                self.Snake_director = 'D'
                self.Snake_body[0][1] += self.move_speed
        a, b=self.if_dead()
        return a, b
    def if_dead(self):
        if (self.Snake_body[0][0] >= 0) \
                and (self.Snake_body[0][0] <= self.Snake_move_size[0]) \
                and (self.Snake_body[0][1] >= 0)\
                and (self.Snake_body[0][1] <= self.Snake_move_size[1]):
            for pos in self.Snake_body[2:-1]:
                if self.get_point_distance(pos,self.Snake_body[0]) < self.Snake_body_per_size_half:
                    score = self.score
                    self.init_data()
                    return True,score  # 死亡
            return False,0#没有死
        else:
            score = self.score
            self.init_data()
            return True,score#死亡
    def move_Snake(self):
        if self.Snake_director == 'U':
            self.Snake_body.insert(0,[self.Snake_body[0][0],self.Snake_body[0][1]-self.move_speed])
        elif self.Snake_director == 'D':
            self.Snake_body.insert(0, [self.Snake_body[0][0], self.Snake_body[0][1] + self.move_speed])
        elif self.Snake_director == 'L':
            self.Snake_body.insert(0, [self.Snake_body[0][0] - self.move_speed, self.Snake_body[0][1]])
        elif self.Snake_director == 'R':
            self.Snake_body.insert(0, [self.Snake_body[0][0] + self.move_speed, self.Snake_body[0][1]])
        self.Snake_body.pop(-1)
        return self.if_dead()
    def add_Snake_body(self):
        #增加1个蛇体长度和加1得分
        self.Snake_body.insert(-1,[-10,-10])
        self.score += 1
        self.all_score += 1
def main(if_AI=False,Q_Table_filename=''):
    pygame.init()
    Snakes = Snake(if_AI)
    AI = Qtable()
    while True:
        if Snakes.if_AI:
            pygame.display.set_caption("贪吃蛇(AI控制)")
            while True:
                if Snakes.AI_epoch<1500:
                    AI.state_rite = Snakes.AI_epoch/3000+0.5
                else:
                    AI.state_rite = 0.95
                state = Snakes.get_state()
                if not Snakes.if_AI:
                    Snakes.fps = 10
                    break
                while True:
                    Snakes.screen.fill((0, 0, 0))
                    Snakes.draw_all()
                    action = AI.choice_action(state)
                    next_state, score, dead,after_dead_score,if_eat_food = Snakes.AI_get_next_state(action)
                    AI.learn(state, action, score, next_state, if_eat_food)
                    state = next_state
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == 9:  # TAB键
                                AI.save_Q_table(Q_Table_filename + '\AI训练{}轮次{:.1f}小时学习数据.csv'.format(Snakes.AI_epoch,
                                                                                                      (time.time()-Snakes.time)/3600),
                                                Q_Table_filename + '\AI训练{}轮次{:.1f}小时成果数据.csv'.format(Snakes.AI_epoch,
                                                                                                      (time.time()-Snakes.time)/3600),
                                                Q_Table_filename + '\AI训练{}轮次{:.1f}小时食物阶段差数据.csv'.format(Snakes.AI_epoch,
                                                                                                         (time.time()-Snakes.time)/3600))
                            elif event.key == 113:  # Q
                                Snakes.fps += 10
                            elif event.key == 101:  # E
                                if Snakes.fps >= 20:
                                    Snakes.fps -= 10
                            elif event.key == 97:  # A
                                Snakes.fps += 500
                            elif event.key == 100:  # D
                                Snakes.fps = 30
                            elif event.key == 104:  # H键
                                Snakes.if_AI = not Snakes.if_AI
                                if not Snakes.if_AI:
                                    break
                    if dead:
                        break
                    Snakes.clock.tick(Snakes.fps)
                    pygame.display.update()
                Snakes.AI_dead()
                if Snakes.AI_epoch % AI.epoch_write == 0:
                    AI.append_per_epoch_list(Snakes.AI_epoch, after_dead_score)
                    AI.append_per_epoch_list_all(Snakes.AI_epoch, Snakes.all_score - Snakes.last_all_score)
                    Snakes.last_all_score = Snakes.all_score
        else:
            pygame.display.set_caption("贪吃蛇")
            while True:
                Snakes.screen.fill((0, 0, 0))
                Snakes.draw_all()
                if Snakes.if_AI:
                    Snakes.fps = 30
                    break
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        # 273 上，274下，276 左，275右
                        if event.key == 273:
                            Snakes.change_move_director('U')
                        elif event.key == 274:
                            Snakes.change_move_director('D')
                        elif event.key == 276:
                            Snakes.change_move_director('L')
                        elif event.key == 275:
                            Snakes.change_move_director('R')
                        elif event.key == 104:  # H键
                            Snakes.if_AI = not Snakes.if_AI
                            if Snakes.if_AI:
                                break
                Snakes.move_Snake()
                Snakes.clock.tick(Snakes.fps)
                pygame.display.update()
main(True,r'C:\Users\Meng\Desktop\贪吃蛇AI\贪吃蛇AI_Qleaning表')