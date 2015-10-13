# Python 3.5
# Brennan Kuo
# Brian Mitchell
# Linnea Sahlberg


class Navigation:
    move_list = []
    weight_count = 0
    board = []
    current_location = {}
    initial_return = {}
    token = ''
    keep_going = True

    def __init__(self, nav, token):
        self.initial_return = nav
        self.token = token
        self.board = [[0]*nav[token]['config']['size']['columns'] for i in range(nav[token]['config']['size']['rows'])]
        for i in nav[token]['graph']['vertices']:
            self.board[nav[token]['graph']['vertices'][i]['row']][nav[token]['graph']['vertices'][i]['column']] \
                = nav[token]['graph']['vertices'][i]['weight']
        self.current_location = nav[token]['config']['initial']

    def iterate(self):
        return self.keep_going

    def final_list(self):
        return self.move_list

    def final_count(self):
        return self.weight_count

    def set_current_location(self, string):
        string = string[1:-1]
        string = string.split(',')
        self.current_location['row'] = string[0]
        self.current_location['column'] = string[1]

    def pretty_print(self):
        print('Current location:', self.current_location)
        for i in self.board:
            print(i)

    def weight(self, row, col):
        return self.board[row][col]

    def left(self, row, col):
        try:
            edge = self.initial_return[self.token]['graph']['edges']['[' + str(row) + ',' + str(col) + ']']
            left = edge['left']
        except Exception as e:
            print(e)
            return '-10000'
        return left

    def right(self, row, col):
        try:
            edge = self.initial_return[self.token]['graph']['edges']['[' + str(row) + ',' + str(col) + ']']
            right = edge['right']
        except Exception as e:
            print(e)
            return '-10000'
        return right

    def stay(self, row, col):
        try:
            edge = self.initial_return[self.token]['graph']['edges']['[' + str(row) + ',' + str(col) + ']']
            stay = edge['stay']
        except Exception as e:
            print(e)
            return '-10000'
        return stay

    def which_direction(self, row, col):
        chosen_direction = ''
        left = self.left(row, col)
        right = self.right(row, col)
        stay = self.stay(row, col)
        if left > right and left > stay:
            self.move_list.append('left')
            chosen_direction = left
        elif right > left and right > stay:
            self.move_list.append('right')
            chosen_direction = right
        else:
            self.move_list.append('stay')
            chosen_direction = stay
        if stay == '-10000' and left == '-10000' and right == '-10000':
            self.keep_going = False
        else:
            for i in self.initial_return[self.token]['graph']['vertices']:
                if i == chosen_direction:
                    self.weight_count = self.weight_count \
                                        + self.initial_return[self.token]['graph']['vertices'][i]['weight']
            self.set_current_location(chosen_direction)
