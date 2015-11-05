#!/usr/bin/env python3

# Python 3.5
# Brennan Kuo
# Brian Mitchell
# Linnea Sahlberg

import requests
import json
from urllib.parse import urlencode
import random
import time
from random import randint
from classes import Navigation
from classes import DFS
from classes import PapersoccerAISimple
from classes import PapersoccerAINotAsSimple
from classes import Soccerfield

BASE_URL = 'http://localhost:3000/api/'


def environment_connect(name):
    params = {'name': name}
    r = requests.get(BASE_URL + 'environment/connect?' + urlencode(params))
    print(r.status_code)
    res = json.loads(r.text)
    print(res['agentToken'])
    return res['agentToken']


# Do the stuff here to get the token
# TOKEN = sys.argv[1]
TOKEN = environment_connect('Brian Mitchell' + str(randint(0, 100000)))
TOKEN_HEADER = {'agentToken': TOKEN}
CURRENT_LOC = ''
MAP = {}
NAVIGATION_WEIGHT = []
NAVIGATION_PLAYS = 0
NAVIGATION_LOCATIONS = ['noerrebrogade', 'dis', 'bryggen', 'langelinie']
PAPERSOCCER_LOCATIONS = ['dis', 'jaegersborggade']  # parken not included


def call_api(endpoint):
    url = BASE_URL + endpoint
    s = requests.get(url, headers=TOKEN_HEADER)
    green = "\x1B[92m" + str(s.status_code) + "\x1B[0m"
    red = "\x1B[91m" + str(s.status_code) + "\x1B[0m"
    print(url, green) if s.status_code == 200 else print(url, red)
    # print(s.text)
    res = json.loads(s.text)
    # print(json.dumps(res, sort_keys=True, indent=4))
    return res

"""
Environment
"""


def environment_leave():
    call_api('environment/leave')


"""
Map
"""


def map_enter():
    global CURRENT_LOC, MAP
    res = call_api('map/enter')
    MAP = res
    CURRENT_LOC = res['state']['agents'][TOKEN]['locationId']
    # print('Current locationId:', CURRENT_LOC)


def map_bike(location_id):
    global CURRENT_LOC
    call_api('map/bike?locationId=' + location_id)
    CURRENT_LOC = location_id
    # print('Current locationId:', CURRENT_LOC)


def map_metro(direction):
    global CURRENT_LOC
    call_api('map/metro?direction=' + direction)
    CURRENT_LOC = next(iter(MAP['state']['map']['metro'][CURRENT_LOC][direction]))
    # print('Current locationId:', CURRENT_LOC)


def map_leave():
    global CURRENT_LOC
    call_api('map/leave')
    CURRENT_LOC = ''


def go_to_location(location_id, callback):  # where we are trying to go
    # print(CURRENT_LOC)
    cw_cost = 0
    ccw_cost = 0
    metro = MAP['state']['map']['metro']
    # print(metro)
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
        # print('Taking the metro cw to {0} costing {1}'.format(location_id, cw_cost))
    elif ccw_cost < cw_cost and ccw_cost < 15:
        metro_to_location(location_id, 'ccw')
        # print('Taking the metro ccw to {0} costing {1}'.format(location_id, ccw_cost))
    else:
        map_bike(location_id)
        # print('Biking to {0} costing 15'.format(location_id))
    callback()


def metro_to_location(location_id, direction):
    # print(location_id, direction)
    if direction == 'cw':
        while location_id != CURRENT_LOC:
            map_metro('cw')
    elif direction == 'ccw':
        while location_id != CURRENT_LOC:
            map_metro('ccw')
    else:
        print('Metro error')


def find_seed_map():
    loc = ''
    game = ''
    mode = ''
    seed = -10000
    navigation_seed = 0
    papersoccer_seed = 0  # start these with some higher values to add a weight towards a type of game?
    for i in range(len(NAVIGATION_LOCATIONS)):
        navigation_seed = \
            MAP['state']['map']['locations'][NAVIGATION_LOCATIONS[i]]['activities']['navigation']['config']['seed']
        cheapest = cheapest_path(NAVIGATION_LOCATIONS[i])
        cost = cheapest[0] * 1.0
        if navigation_seed/cost > seed/cost:
            seed = navigation_seed
            loc = NAVIGATION_LOCATIONS[i]
            game = 'navigation'
            mode = cheapest[1]
            # print('nav', navigation_seed, loc, mode, game)
    for j in range(len(PAPERSOCCER_LOCATIONS)):
        papersoccer_seed = \
            MAP['state']['map']['locations'][PAPERSOCCER_LOCATIONS[j]]['activities']['papersoccer']['config']['seed']
        cheapest = cheapest_path(PAPERSOCCER_LOCATIONS[j])
        cost = cheapest[0] * 1.0
        if (papersoccer_seed + 4)/cost > seed/cost:  # change this number to tweak game preference
            seed = papersoccer_seed
            loc = PAPERSOCCER_LOCATIONS[j]
            game = 'papersoccer'
            mode = cheapest[1]
            # print('papersoccer', papersoccer_seed, loc, mode, game)
    # print('nav seed', navigation_seed)
    # print('pap seed', papersoccer_seed)
    # print('Seed is: ' + str(seed))
    # print('loc is: ' + loc)
    # time.sleep(2)
    return loc, mode, game


def cheapest_path(location_id):
    # print(CURRENT_LOC)
    cw_cost = 0
    ccw_cost = 0
    metro = MAP['state']['map']['metro']
    # print(metro)
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
    if cw_cost <= ccw_cost and cw_cost < 15:
        # print('Taking the metro cw to {0} costing {1}'.format(location_id, cw_cost))
        return cw_cost, 'cw'
    elif ccw_cost < cw_cost and ccw_cost < 15:
        # print('Taking the metro ccw to {0} costing {1}'.format(location_id, ccw_cost))
        return ccw_cost, 'ccw'
    else:
        # print('Biking to {0} costing 15'.format(location_id))
        return 15, 'bike'


def go_to_best_location(loc_game_tuple):
    # print(loc_game_tuple)
    loc = loc_game_tuple[0]
    mode = loc_game_tuple[1]
    game = loc_game_tuple[2]
    if mode == 'bike':
        map_bike(loc)
    else:
        metro_to_location(loc, mode)
    return game


"""
Papersoccer
"""


def papersoccer_enter():
    res = call_api('papersoccer/enter')
    return res['state']['papersoccer'][TOKEN]


def papersoccer_leave():
    global MAP
    res = call_api('papersoccer/leave')
    MAP = res
    return res


def papersoccer_play(direction):
    res = call_api('papersoccer/play?direction=' + direction)
    return res


def papersoccer_compete():
    nav = papersoccer_enter()
    field = Soccerfield(nav)
    if field.get_k() < 2:
        print("\x1B[91mSimple AI\x1B[0m")
        ai = PapersoccerAISimple()
    else:
        print("\x1B[91mComplex AI\x1B[0m")
        ai = PapersoccerAINotAsSimple()
    while not field.terminal_test():
        move = ai.get_direction(field)
        res = papersoccer_play(move)
        # print(json.dumps(res, sort_keys=True, indent=2))
        field.process_response(res, move)
        # time.sleep(0.25)
    papersoccer_leave()


def go_to_papersoccer_location(callback):
    locations = ['dis', 'jaegersborggade']  # 'parken'
    go_to_location(random.choice(locations), callback)

"""
Navigation
"""


def navigation_enter():
    res = call_api('navigation/enter')
    return res['state']['navigation']


def navigation_leave():
    global MAP
    res = call_api('navigation/leave')
    MAP = res
    return res


def navigation_lane(direction):
    res = call_api('navigation/lane?direction=' + direction)
    return res


def dfs_play():
    nav = navigation_enter()
    board = DFS(nav, TOKEN)
    path = board.pseudo_main()
    # print(path)
    for i in range(len(path) - 1):
        navigation_lane(path[i])
        # time.sleep(0.5)
    navigation_leave()


def navigation_play():
    global NAVIGATION_WEIGHT
    global NAVIGATION_PLAYS
    nav = navigation_enter()
    board = Navigation(nav, TOKEN)
    board.pretty_print()

    path = board.get_best_first_path()
    # print(path)
    for i in range(len(path) - 1):
        # print(i)
        navigation_lane(path[i])
        # time.sleep(0.5)
    current_weight = board.final_count()
    NAVIGATION_WEIGHT.append(current_weight)
    NAVIGATION_PLAYS += NAVIGATION_PLAYS
    navigation_leave()


def average_navigation_credits():
    weight = 0
    for i in NAVIGATION_WEIGHT:
        weight = weight + i
    return weight / NAVIGATION_PLAYS


def go_to_nav_location(callback):
    locations = ['bryggen', 'noerrebrogade', 'langelinie', 'dis']
    go_to_location(random.choice(locations), callback)


def main():
    map_enter()
    while True:
        game = go_to_best_location(find_seed_map())
        # print(game)
        # time.sleep(1)
        if game == 'papersoccer':
            # print(CURRENT_LOC)
            papersoccer_compete()
            # time.sleep(2)
        elif game == 'navigation':
            # print(CURRENT_LOC)
            dfs_play()
            # time.sleep(2)
        # go_to_papersoccer_location(papersoccer_compete)
        # go_to_papersoccer_location(papersoccer_compete)
        # go_to_nav_location(dfs_play)
    map_leave()
    environment_leave()

main()
