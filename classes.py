# Python 3.5
# Brennan Kuo
# Brian Mitchell
# Linnea Sahlberg
import random
import json


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
