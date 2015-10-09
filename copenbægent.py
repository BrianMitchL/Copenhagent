#!/usr/bin/env python3

# Python 3.5
# Brennan Kuo
# Brian Mitchell
# Linnea Sahlberg

import requests
import json
from urllib.parse import urlencode
import sys
from collections import namedtuple
from random import randint


def environment_connect(name):
    params = {'name': name}
    r = requests.get('http://localhost:3000/api/environment/connect?' + urlencode(params))
    print(r.status_code)
    res = json.loads(r.text)
    print(res['agentToken'])
    return res['agentToken']


# Do the stuff here to get the token
# TOKEN = sys.argv[1]
TOKEN = environment_connect('Brian Mitchell' + str(randint(0,100000)))
TOKEN_HEADER = {'agentToken': TOKEN}
CURRENT_LOC = ''
MAP = {}


def call_api(url):
    s = requests.get(url, headers=TOKEN_HEADER)
    print(url, "\x1B[92m" + str(s.status_code) + "\x1B[0m")
    res = json.loads(s.text)
    # print(json.dumps(res, sort_keys=True, indent=4))
    return res


"""
Environment
"""


def environment_leave():
    res = call_api('http://localhost:3000/api/environment/leave')


"""
Map
"""


def map_enter():
    global CURRENT_LOC, MAP
    res = call_api('http://localhost:3000/api/map/enter')
    MAP = res
    CURRENT_LOC = res['state']['agents'][TOKEN]['locationId']
    print('Current locationId:', CURRENT_LOC)


def map_bike(location_id):
    global CURRENT_LOC
    res = call_api('http://localhost:3000/api/map/bike?locationId=' + location_id)
    CURRENT_LOC = location_id
    print('Current locationId:', CURRENT_LOC)


def map_metro(direction):
    global CURRENT_LOC
    res = call_api('http://localhost:3000/api/map/metro?direction=' + direction)
    CURRENT_LOC = next(iter(MAP['state']['map']['metro'][CURRENT_LOC][direction]))
    print('Current locationId:', CURRENT_LOC)


def map_leave():
    global CURRENT_LOC
    res = call_api('http://localhost:3000/api/map/leave')
    CURRENT_LOC = ''


def go_to_location(location_id):  # where we are trying to go
    cw_cost = 0
    ccw_cost = 0
    metro = MAP['state']['map']['metro']
    new_cw_loc = next(iter(metro[CURRENT_LOC]['cw']))
    new_ccw_loc = next(iter(metro[CURRENT_LOC]['ccw']))
    ccw_cost = ccw_cost + metro[CURRENT_LOC]['ccw'][new_ccw_loc]
    cw_cost = cw_cost + metro[CURRENT_LOC]['cw'][new_cw_loc]
    while location_id != new_cw_loc:
        newer_cw_loc = next(iter(metro[new_cw_loc]['cw']))
        cw_cost = cw_cost + metro[new_cw_loc]['cw'][newer_cw_loc]
        new_cw_loc = newer_cw_loc
    while location_id != new_ccw_loc:
        newer_ccw_loc = next(iter(metro[new_ccw_loc]['ccw']))
        ccw_cost = ccw_cost + metro[new_ccw_loc]['ccw'][newer_ccw_loc]
        new_ccw_loc = newer_ccw_loc
    # print(cw_cost, ccw_cost)
    if cw_cost <= ccw_cost and cw_cost < 15:
        metro_to_location(location_id, 'cw')
        print('Taking the metro cw to {0} costing {1}'.format(location_id, cw_cost))
    elif ccw_cost < cw_cost and ccw_cost < 15:
        metro_to_location(location_id, 'ccw')
        print('Taking the metro ccw to {0} costing {1}'.format(location_id, ccw_cost))
    else:
        map_bike(location_id)
        print('Biking to {0} costing 15'.format(location_id))


def metro_to_location(location_id, direction):
    if direction == 'cw':
        while location_id != CURRENT_LOC:
            map_metro('cw')
    elif direction == 'ccw':
        while location_id != CURRENT_LOC:
            map_metro('ccw')
    else:
        print('FUCK YOU TELL ME WHERE YOU WANT TO GO')

"""
Papersoccer
"""


def papersoccer_enter():
    res = call_api('http://localhost:3000/api/papersoccer/enter')
    return res['state']['papersoccer']


def papersoccer_leave():
    res = call_api('http://localhost:3000/api/papersoccer/leave')
    return res


def papersoccer_play(dir):
    res = call_api('http://localhost:3000/api/papersoccer/lane?direction=' + dir)
    return res


"""
Navigation
"""


def navigation_enter():
    res = call_api('http://localhost:3000/api/navigation/enter')
    return res['state']['navigation']


def navigation_leave():
    res = call_api('http://localhost:3000/api/navigation/leave')
    return res


def navigation_lane(dir):
    res = call_api('http://localhost:3000/api/navigation/lane?direction=' + dir)
    return res


def navigation_play():
    nav = navigation_enter()
    board = [[0]*nav[TOKEN]['config']['size']['columns'] for i in range(nav[TOKEN]['config']['size']['rows'])]
    # new_board = namedtuple('Struct', board.keys())(*board.values())
    # print(new_board)
    for i in nav[TOKEN]['graph']['vertices']:
        # print(nav[TOKEN]['graph']['vertices'][i])
        board[int(nav[TOKEN]['graph']['vertices'][i]['row'])][int(nav[TOKEN]['graph']['vertices'][i]['column'])] \
            = int(nav[TOKEN]['graph']['vertices'][i]['weight'])
    loc = nav[TOKEN]['config']['initial']
    board_pretty(board)

def tree_search():
    pass

def board_pretty(board):
    print(type(board))
    for i in board:
        print(i)


def main():
    map_enter()
    go_to_location('langelinie')
    # go_to_location('christianshavn')
    navigation_play()
    # map_leave()

main()
