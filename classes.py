# Python 3.5
# Brennan Kuo
# Brian Mitchell
# Linnea Sahlberg
import random
import json
import itertools


class Navigation:
    move_list = []
    weight_count = 0
    board = []
    current_location = {}
    initial_return = {}
    token = ''

    def __init__(self, nav, token):
        self.move_list = []
        self.weight_count = 0
        self.initial_return = nav
        self.token = token
        self.board = [[0]*nav[token]['config']['size']['columns'] for i in range(nav[token]['config']['size']['rows'])]
        for i in nav[token]['graph']['vertices']:
            self.board[nav[token]['graph']['vertices'][i]['row']][nav[token]['graph']['vertices'][i]['column']] \
                = nav[token]['graph']['vertices'][i]['weight']
        self.current_location = nav[token]['config']['initial']

    def final_count(self):
        weight = self.weight_count / len(self.move_list)
        return weight

    def set_current_location(self, string):
        string = string[1:-1]
        string = string.split(',')
        self.current_location['row'] = string[0]
        self.current_location['column'] = string[1]

    def get_weight(self, string):
        string = string[1:-1]
        string = string.split(',')
        row = int(string[0])
        col = int(string[1])
        return self.weight(row, col)

    def pretty_print(self):
        print('Current location:', self.current_location)
        for i in self.board:
            print(i)

    def weight(self, row, col):
        return -10000 if row < 0 and col < 0 else self.board[row][col]

    def direction(self, direction):
        try:
            edge = self.initial_return[self.token]['graph']['edges']['[' + str(self.current_location['row']) + ',' +
                                                                     str(self.current_location['column']) + ']']
            return edge[direction]
        except Exception as e:
            print(e)
            return '[-1,-1]'

    def which_direction(self):
        left = self.direction('left')
        right = self.direction('right')
        stay = self.direction('stay')
        if self.get_weight(left) > self.get_weight(right) and self.get_weight(left) > self.get_weight(stay):
            self.move_list.append('left')
            chosen_direction = left
        elif self.get_weight(right) > self.get_weight(left) and self.get_weight(right) > self.get_weight(stay):
            self.move_list.append('right')
            chosen_direction = right
        else:
            self.move_list.append('stay')
            chosen_direction = stay
        for i in self.initial_return[self.token]['graph']['vertices']:
            if i == chosen_direction:
                self.weight_count = self.weight_count \
                                    + self.initial_return[self.token]['graph']['vertices'][i]['weight']
        self.set_current_location(chosen_direction)

    def is_complete(self):
        return True if self.current_location['column'] \
                       == self.initial_return[self.token]['config']['size']['columns'] - 1 else False

    def is_dead_end(self):
        left = self.direction('left')
        right = self.direction('right')
        stay = self.direction('stay')
        return True if \
            self.get_weight(left) < -100 and self.get_weight(right) < -100 and self.get_weight(stay) < -100 else False

    def get_best_first_path(self):
        while not self.is_complete() and not self.is_dead_end():
            self.which_direction()
        return self.move_list



class DFS:

    def __init__(self, nav, token):
        self.current_position = nav[token]['position']
        self.move_list = []
        self.size = nav[token]['config']['size']
        self.board = [[0]*nav[token]['config']['size']['columns'] for i in range(nav[token]['config']['size']['rows'])]
        for i in nav[token]['graph']['vertices']:
            self.board[nav[token]['graph']['vertices'][i]['row']][nav[token]['graph']['vertices'][i]['column']] \
                = nav[token]['graph']['vertices'][i]['weight']

    def go_left(self, position):  # position is an object
        row = position['row'] - 1
        col = position['column'] + 1
        return {'row':row, 'column': col}

    def go_stay(self, position):
        row = position['row']
        col = position['column'] + 1
        return {'row':row, 'column':col}

    def go_right(self, position):
        row = position['row'] + 1
        col = position['column'] + 1
        return {'row':row, 'column':col}

    def get_weight(self, position):
        return self.board[position['row']][position['column']]

    def max_weight(self, stay, left, right):
        dir_list = ['stay', 'left', 'right']
        lst = []
        lst.append(stay)
        lst.append(left)
        lst.append(right)
        max_value = max(lst)
        max_index = lst.index(max_value)
        return max_value, dir_list[max_index]


    def search(self, root, level):
        #print('LEVEL ' + str(level))
        current_pos = root
        response = self.search_recursive(current_pos, level - 1)
        return  response[0], response[1]

    def search_recursive(self, current_pos, level):
        #print(current_pos)
        if level == 0:
            return self.get_weight(current_pos), 'E'
        else:
            mv_lst = []
            weight = None
            if current_pos['row'] > 0 and current_pos['row'] < self.size['rows'] - 1:
                #print('MIDDLE ROWS')
                left_node = self.go_left(current_pos)
                left_response = self.search_recursive(left_node, level - 1)
                stay_node = self.go_stay(current_pos)
                stay_response = self.search_recursive(stay_node, level - 1)
                right_node = self.go_right(current_pos)
                right_response = self.search_recursive(right_node, level - 1)

                left_weight = self.get_weight(left_node)
                stay_weight = self.get_weight(stay_node)
                right_weight = self.get_weight(right_node)

                highest = self.max_weight(stay_weight, left_weight, right_weight)
                if highest[1] == 'left':
                    #print('LEFT')
                    weight = left_response[0]
                    mv_lst = list(left_response[1])
                elif highest[1] == 'stay':
                    #print('STAY')
                    weight = stay_response[0]
                    mv_lst = list(stay_response[1])
                elif highest[1] == 'right':
                    #print('RIGHT')
                    weight = right_response[0]
                    mv_lst = list(right_response[1])
                weight = weight + highest[0]
                mv_lst.insert(0, highest[1])

                return weight, mv_lst


            elif current_pos['row'] <= 0:
                #print('LEFT ROW LEFT EDGE')
                stay_node = self.go_stay(current_pos)
                stay_response = self.search_recursive(stay_node, level - 1)
                right_node = self.go_right(current_pos)
                right_response = self.search_recursive(right_node, level - 1)

                stay_weight = self.get_weight(stay_node)
                right_weight = self.get_weight(right_node)

                highest = self.max_weight(stay_weight, -90000, right_weight)
                if highest[1] == 'left':
                    print('WHAT THE FUCKING HELL ARE YOU DOING GOING LEFT')
                elif highest[1] == 'stay':
                    #print('STAY')
                    weight = stay_response[0]
                    mv_lst = list(stay_response[1])
                elif highest[1] == 'right':
                    #print('RIGHT')
                    weight = right_response[0]
                    mv_lst = list(right_response[1])
                weight = weight + highest[0]
                mv_lst.insert(0, highest[1])

                return weight, mv_lst

            elif current_pos['row'] >= self.size['rows'] - 1:
                #print('RIGHT ROW')
                left_node = self.go_left(current_pos)
                left_response = self.search_recursive(left_node, level - 1)
                stay_node = self.go_stay(current_pos)
                stay_response = self.search_recursive(stay_node, level - 1)

                left_weight = self.get_weight(left_node)
                stay_weight = self.get_weight(stay_node)

                highest = self.max_weight(stay_weight, left_weight, -90000)
                if highest[1] == 'left':
                    #print('LEFT')
                    weight = left_response[0]
                    mv_lst = list(left_response[1])
                elif highest[1] == 'stay':
                    #print('STAY')
                    weight = stay_response[0]
                    mv_lst = list(stay_response[1])
                elif highest[1] == 'right':
                    print('WHAT THE FUCKING HELL ARE YOU DOING GOING RIGHT')
                weight = weight + highest[0]
                mv_lst.insert(0, highest[1])

                return weight, mv_lst

    def move_current_loc(self, lst, current_pos):
        lst = lst
        current_pos = current_pos
        for i in lst:
            if i == 'left':
                current_pos = self.go_left(current_pos)
            if i == 'stay':
                current_pos = self.go_stay(current_pos)
            if i == 'right':
                current_pos = self.go_right(current_pos)
            if i == 'E':
                pass
        return current_pos

    def pseudo_main(self):
        remaining_levels = self.size['columns']
        while remaining_levels != 0:
            if remaining_levels >= 5:
                response = self.search(self.current_position, 5)
                remaining_levels = remaining_levels - 4
                local_move_list = response[1]
                local_move_list = local_move_list[:-1]
                self.move_list.append(local_move_list)
                self.current_position = self.move_current_loc(response[1], self.current_position)
            else:
                response = self.search(self.current_position, remaining_levels)
                remaining_levels = 0
                local_move_list = response[1]
                local_move_list = local_move_list[:-1]
                self.move_list.append(local_move_list)
                self.current_position = self.move_current_loc(response[1], self.current_position)
        chain = itertools.chain.from_iterable(self.move_list)
        return list(chain)


class Papersoccer:
    directions = {'nw': [-1, -1],
                  'n': [-1, 0],
                  'ne': [-1, 1],
                  'e': [0, 1],
                  'se': [1, 1],
                  's': [1, 0],
                  'sw': [1, -1],
                  'w': [0, -1]
                  }
    opposite_direction = {'nw': 'se',
                          'n': 's',
                          'ne': 'sw',
                          'e': 'w',
                          'se': 'nw',
                          's': 'n',
                          'sw': 'ne',
                          'w': 'e'}
    initial_return = {}
    ball_location = {}
    vertices = {}
    edges = {}
    game_ended = False

    def __init__(self, nav):
        self.initial_return = nav
        self.ball_location = nav['currentVertex']
        self.vertices = nav['soccerfield']['vertices']
        self.edges = nav['soccerfield']['edges']
        self.game_ended = False

    def pretty_print(self):
        print('Ball location:', self.ball_location)
        # print(self.vertices)

    def str_loc(self):
        return '[' + str(self.ball_location['row']) + ',' + str(self.ball_location['column']) + ']'

    def game_complete(self):
        return self.game_ended

    def turn(self):  # TODO implement AI
        return random.choice(list(self.opposite_direction.keys()))

    def move(self, player, move):
        print(player + ' move: ' + move)
        self.vertices[self.str_loc()][move] = player
        self.ball_location['row'] += self.directions[move][0]
        self.ball_location['column'] += self.directions[move][1]
        self.vertices[self.str_loc()][self.opposite_direction[move]] = player
        self.vertices[self.str_loc()]['visited'] = True

    def process_response(self, res, turn):
        print(json.dumps(res, sort_keys=True, indent=4))
        if any(x in res['action']['message'] for x in ['win', 'lost', 'tie', 'over']):
            self.game_ended = True
        elif res['action']['applicable']:
            self.move('agent', turn)
            for i in range(len(res['action']['percepts'])):
                self.move('opponent', res['action']['percepts'][i])
