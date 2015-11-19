# Python 3.5
# Brennan Kuo
# Brian Mitchell
# Linnea Sahlberg
import random
import itertools
from copy import deepcopy
import operator


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


class Soccerfield:
    def __init__(self, soccerfield):
        self.height = soccerfield['soccerfield']['height']
        self.width = soccerfield['soccerfield']['width']
        self.k = soccerfield['soccerfield']['k']
        self.plays_made = soccerfield['soccerfield']['playsMade']
        self.current_vertex = soccerfield['currentVertex']
        self.vertices = soccerfield['soccerfield']['vertices']
        self.edges = soccerfield['soccerfield']['edges']
        self.message = ''
        self.agents_turn = True
        self.directions = ['e', 'ne', 'se', 'n', 's', 'nw', 'sw', 'w']

    @staticmethod
    def str_loc(obj):
        return '[' + str(obj['row']) + ',' + str(obj['column']) + ']'

    @staticmethod
    def move_info(loc, direction):
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
        return {
            'orig': loc,
            'dest': {
                'row': loc['row'] + directions[direction][0],
                'column': loc['column'] + directions[direction][1]
            },
            'opposite_direction': opposite_direction[direction]
        }

    def get_current_vertex(self):
        return self.current_vertex

    def get_k(self):
        return self.k

    def get_agents_turn(self):
        return self.agents_turn

    def is_playable(self, orig, dest):
        if orig not in self.vertices or dest not in self.vertices:
            return False
        return dest not in self.edges[orig] and orig not in self.edges[dest]

    def is_in_goal(self, loc):
        left_goal = loc['row'] == 2 + self.k and loc['column'] == 0
        right_goal = loc['row'] == 2 + self.k and loc['column'] == self.width - 1
        return left_goal or right_goal

    def legal_moves(self, loc):
        moves = []
        for i in range(len(self.directions)):
            if self.can_move(loc, self.directions[i]):
                moves.append(self.directions[i])
        return moves

    def can_move(self, loc, direction):
        edge = self.move_info(loc, direction)
        return self.is_playable(self.str_loc(edge['orig']), self.str_loc(edge['dest']))

    def is_trapped(self, loc):
        for i in range(len(self.directions)):
            if self.can_move(loc, self.directions[i]):
                # print('can move to', self.directions[i], self.can_move(loc, self.directions[i]))
                return False
        print('\x1B[91mIT\'S A TRAP!\x1B[0m')
        return True

    def terminal_test(self):
        # TODO this is super hacky, look for alternatives
        if any(x in self.message for x in ['win', 'lost', 'tie', 'over']):
            return True
        loc = self.current_vertex
        in_goal = self.is_in_goal(loc)
        is_trapped = self.is_trapped(loc)
        return True if in_goal else is_trapped

    def move(self, direction, player):
        loc = self.current_vertex
        edge = self.move_info(loc, direction)
        orig_str = self.str_loc(edge['orig'])
        dest_str = self.str_loc(edge['dest'])
        self.vertices[orig_str][direction] = player
        self.vertices[dest_str][edge['opposite_direction']] = player
        self.vertices[orig_str]['visited'] = True
        self.vertices[dest_str]['visited'] = True
        self.edges[orig_str][dest_str] = player
        self.edges[dest_str][orig_str] = player
        self.current_vertex = edge['dest']
        self.plays_made += 1
        return self.current_vertex

    def destination(self, loc, direction):
        return self.move_info(loc, direction)['dest']

    def is_visited(self, loc, direction):
        edge = self.move_info(loc, direction)
        if self.str_loc(edge['orig']) not in self.vertices:
            return True  # Unreachable vertices have already been visited
        return 'visited' in self.vertices[self.str_loc(edge['orig'])]

    def process_response(self, res, move):
        self.message = res['action']['message']
        if res['action']['applicable']:
            self.move(move, 'agent')
            self.agents_turn = False
            for i in range(len(res['action']['percepts'])):
                self.move(res['action']['percepts'][i], 'opponent')
            self.agents_turn = True
        else:
            print('\x1B[91mNOT APPLICABLE. SOMETHING IS WRONG :\'(\x1B[0m')

    def utility(self, loc):
        trapped = self.is_trapped(loc)
        is_in_left_goal = self.is_in_goal(loc) and loc['column'] == 0
        is_in_right_goal = self.is_in_goal(loc) and loc['column'] == self.width - 1
        if is_in_left_goal or (trapped and self.agents_turn):
            return -self.plays_made
        if is_in_right_goal or (trapped and not self.agents_turn):
            return self.plays_made
        return None

    def successors(self, loc):
        return [(direction, self.destination(loc, direction)) for direction in self.legal_moves(loc)]

    def clone(self):  # TODO make sure this works with deep copy, etc.
        fields = {'soccerfield': {
            'height': self.height,
            'width': self.width,
            'k': self.k,
            'plays_made': self.plays_made,
            'vertices': deepcopy(self.vertices),
            'edges': deepcopy(self.edges),
            'currentVertex': self.current_vertex
            }
        }
        clone = Soccerfield(fields)
        return clone


class PapersoccerAISimple:
    def __init__(self):
        print('\x1B[95mSimple\x1B[0m')

    def get_direction(self, soccerfield):
        priority_list = ['e', 'ne', 'se', 'n', 's', 'sw', 'nw', 'w']
        for i in range(len(priority_list)):
            truth = soccerfield.can_move(soccerfield.get_current_vertex(), priority_list[i])
            if truth:
                return priority_list[i]
        return "no move"


class PapersoccerAINotAsSimple:
    def __init__(self):
        print('\x1B[95mBrian\'s Bad AI\x1B[0m')

    def prefer_visited(self, soccerfield, directions):
        nd = deepcopy(directions)
        loc = soccerfield.get_current_vertex()
        for direction, weight in directions.items():
            is_visited = soccerfield.is_visited(loc, direction)
            if is_visited and 'e' in direction:
                nd[direction] = weight + 1
            elif is_visited and 'w' in direction:
                nd[direction] = weight - 0.5
            elif is_visited:
                nd[direction] = weight + 0.5
        return nd

    def get_highest_value(self, obj):
        m = -100000
        for k, v in obj.items():
            if v > m:
                m = v
        ret = {}
        for k, v, in obj.items():
            if v == m:
                ret[k] = v
        return ret

    def get_direction(self, soccerfield):
        loc = soccerfield.get_current_vertex()
        directions = {'e': 3,
                      'ne': 2,
                      'se': 2,
                      'n': 1,
                      's': 1,
                      'nw': 0,
                      'sw': 0,
                      'w': 0}
        nd = deepcopy(directions)
        for k, v in directions.items():
            if not soccerfield.can_move(loc, k):
                nd.pop(k)

        options = self.prefer_visited(soccerfield, nd)
        highest_value = self.get_highest_value(options)
        if len(highest_value) > 0:
            return random.choice(list(highest_value))
        else:
            return 'no move'


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
        return {'row': row, 'column': col}

    def go_stay(self, position):
        row = position['row']
        col = position['column'] + 1
        return {'row': row, 'column': col}

    def go_right(self, position):
        row = position['row'] + 1
        col = position['column'] + 1
        return {'row': row, 'column': col}

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

    def is_dead_end(self, position):
        col_loc = position['column']
        if col_loc >= self.size['columns'] - 1:
            return True
        else:
            if position['row'] > 0 and position['row'] < self.size['rows'] - 1:
                left = self.go_left(position)
                right = self.go_right(position)
                stay = self.go_stay(position)
                return True if \
                    self.get_weight(left) < -100 and self.get_weight(right) < -100 and self.get_weight(stay) < -100 else False
            elif position['row'] <= 0:
                right = self.go_right(position)
                stay = self.go_stay(position)
                return True if \
                    self.get_weight(right) < -100 and self.get_weight(stay) < -100 else False
            elif position['row'] >= self.size['rows'] - 1:
                left = self.go_left(position)
                stay = self.go_stay(position)
                return True if \
                self.get_weight(left) < -100 and self.get_weight(stay) < -100 else False

    def search(self, root, level):
        # print('LEVEL ' + str(level))
        current_pos = root
        response = self.search_recursive(current_pos, level - 1)
        return response[0], response[1]

    def search_recursive(self, current_pos, level):
        # print(current_pos)
        if level == 0:
            return self.get_weight(current_pos), 'E'
        if self.is_dead_end(current_pos):
            return self.get_weight(current_pos), 'E'
        else:
            mv_lst = []
            weight = None
            if current_pos['row'] > 0 and current_pos['row'] < self.size['rows'] - 1:
                # print('MIDDLE ROWS')
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
                    # print('LEFT')
                    weight = left_response[0]
                    mv_lst = list(left_response[1])
                elif highest[1] == 'stay':
                    # print('STAY')
                    weight = stay_response[0]
                    mv_lst = list(stay_response[1])
                elif highest[1] == 'right':
                    # print('RIGHT')
                    weight = right_response[0]
                    mv_lst = list(right_response[1])
                weight = weight + highest[0]
                mv_lst.insert(0, highest[1])

                return weight, mv_lst

            elif current_pos['row'] <= 0:
                # print('LEFT ROW LEFT EDGE')
                stay_node = self.go_stay(current_pos)
                stay_response = self.search_recursive(stay_node, level - 1)
                right_node = self.go_right(current_pos)
                right_response = self.search_recursive(right_node, level - 1)

                stay_weight = self.get_weight(stay_node)
                right_weight = self.get_weight(right_node)

                highest = self.max_weight(stay_weight, -90000, right_weight)
                if highest[1] == 'left':
                    pass
                    # print('WHAT THE FUCKING HELL ARE YOU DOING GOING LEFT')
                elif highest[1] == 'stay':
                    # print('STAY')
                    weight = stay_response[0]
                    mv_lst = list(stay_response[1])
                elif highest[1] == 'right':
                    # print('RIGHT')
                    weight = right_response[0]
                    mv_lst = list(right_response[1])
                weight = weight + highest[0]
                mv_lst.insert(0, highest[1])

                return weight, mv_lst

            elif current_pos['row'] >= self.size['rows'] - 1:
                # print('RIGHT ROW')
                left_node = self.go_left(current_pos)
                left_response = self.search_recursive(left_node, level - 1)
                stay_node = self.go_stay(current_pos)
                stay_response = self.search_recursive(stay_node, level - 1)

                left_weight = self.get_weight(left_node)
                stay_weight = self.get_weight(stay_node)

                highest = self.max_weight(stay_weight, left_weight, -90000)
                if highest[1] == 'left':
                    # print('LEFT')
                    weight = left_response[0]
                    mv_lst = list(left_response[1])
                elif highest[1] == 'stay':
                    # print('STAY')
                    weight = stay_response[0]
                    mv_lst = list(stay_response[1])
                elif highest[1] == 'right':
                    # print('WHAT THE FUCKING HELL ARE YOU DOING GOING RIGHT')
                    pass
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
                remaining_levels -= 4
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
