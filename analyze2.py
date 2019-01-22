#!/usr/bin/env python
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import json
from scipy import stats
import random

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def getEV(n, d, c):
    edge = d*c
    pot_w = .9*n
    base_rate = 1/float(n)
    w_freq = base_rate + d
    l_freq = 1 - w_freq
    ev = w_freq * pot_w - l_freq
    return ev

def prob(hand):
    # given string hand, return probability of hand class
    cards = hand.split(' ')
    s1 = cards[0][-1]
    v1 = cards[0].replace(s1, '')
    s2 = cards[1][-1]
    v2 = cards[1].replace(s2, '')
    if v1 == v2:
        return 1/13.0 * 3/51.0
    elif s1 == s2:
        return 1/13.0 * 1/51.0 * 2
    else:
        return 1/13.0 * 3/51.0 * 2

def simulateHand(p_w, p_l, p_no_play, gain, loss):
    r = random.random()
    if r < p_no_play:
        return 0
    elif r < p_no_play + p_l:
        return loss
    else:
        return gain

filename = 'n-400_trials-50__2018-07-07_07-57-57.txt'

'''
This script prints a table of hand values.

--- N PLAYERS
Hand: p_hand p_win +- EV_given_hand EV_cumulative
'''


l = 1
b = 2*l
rake_rem = 0.9
T_pot = 4*b # your contribution to the pot



hand_to_prob = {}
top_hands = {}
## OLD CODE TO GET SORTED HAND RANKINGS

with open('all_hands.txt') as all_hands:
    hands_json = json.load(all_hands)
    with open(filename) as json_file:
        data = json.load(json_file)
        hand_evs = {}
        for h in hands_json['hands']:
            s = h + '\n'
            n_to_prob = {}
            for n_p in range(2,9):
                s += ' -- ' + str(n_p) + ':  '
                key = str(n_p)
                avg = data[h][key][0]
                s += str(round(avg,2))
                s += '   '
                std = data[h][key][1]
                low = avg - 2*std
                high = avg + 2*std
                breakeven = 1/float(n_p)
                win_delta = avg - breakeven
                if abs(std) < 10**-6:
                    std = 10**-6
                std_to_even = abs(win_delta / std)
                confidence = stats.norm.cdf(std_to_even) * 100
                if win_delta > 0:
                    s += bcolors.OKGREEN + bcolors.BOLD + '+' + str(round(win_delta,2)) + bcolors.ENDC + bcolors.ENDC
                elif win_delta <= 0:
                    s += bcolors.FAIL + str(round(win_delta,2)) + bcolors.ENDC
                s += '   ' + str(int(confidence)) + '%\n'
                ev = getEV(n_p, win_delta, confidence)
                if n_p not in hand_evs.keys():
                    hand_evs[n_p] = {}
                if ev not in hand_evs[n_p].keys():
                    hand_evs[n_p][ev] = []
                hand_evs[n_p][ev].append(h)
                #strategic
                n_to_prob[n_p] = avg
            hand_to_prob[h] = n_to_prob
            #print s
        for n in range(2, 9):
            top_hands[n] = []
            cutoff_counter = 0
            # print str(n) + ' Players'
            evs_sorted = sorted(hand_evs[n].keys(), reverse=True)
            for ev in evs_sorted:
                for h in hand_evs[n][ev]:
                    top_hands[n].append(h)
                    # print '  ' + h + ' '*(9-len(h)) + ' ' + str(round(ev, 2))

print '\n\nAssuming  blinds: $' + str(l) + '/' + str(b) + '  players give to pot: $' + str(T_pot) + '  rake remainder: ' + str(rake_rem) + '\n'

n_hands_played = {}
last_hands_played = {}
max_p_win = {}
max_p_play = {}
max_p_lose = {}

for n in range(2,9):
    hands_played = 0
    last_hand_played = ''
    print '--- ' + str(n) + ' PLAYERS' + '\n'
    p_play_cum = 0
    ev_play_hand_cum = 0
    last_ev_cum = 0
    max_p_win_cum = 0
    max_p_play_cum = 0
    max_p_lose_cum = 0
    for h in top_hands[n]:
        p_h = prob(h)
        p_w = hand_to_prob[h][n]
        line = ' '
        line += str(h) + ' '*(10-len(str(h)))
        hand_prob = str(round(p_h, 3))
        line += hand_prob + ' ' * (10-len(hand_prob))
        win_prob = str(round(p_w, 3))
        line +=  win_prob + ' ' * (10-len(win_prob))
        d = p_w - 1/float(n)
        if d > 0:
            add = bcolors.OKGREEN + '+' + str(round(d,3)) + bcolors.ENDC
            line += add + ' '*(21-len(add))
        elif d <= 0:
            add = bcolors.FAIL + str(round(d,3)) + bcolors.ENDC
            line += add + ' '*(21-len(add))
        w_pot = T_pot * n * rake_rem - T_pot
        l_pot = T_pot
        no_play_pot = (l + b)/float(n)
        ev_given_hand = p_w * w_pot - (1-p_w) * l_pot
        ev_hand = p_h * ev_given_hand - (1-p_h) * no_play_pot
        ev_play_hand_cum += p_h * ev_given_hand
        p_play_cum += p_h
        ev_cum = ev_play_hand_cum - (1-p_play_cum) * no_play_pot
        str_ev_hand = str(round(ev_given_hand, 3))
        line += str_ev_hand + ' '*(10-len(str_ev_hand))
        str_ev_h_tot = str(round(ev_hand, 3))
        line += str_ev_h_tot + ' '*(10-len(str_ev_h_tot))
        str_ev_cum = ''
        if ev_cum > last_ev_cum or last_ev_cum == 0:
            str_ev_cum = str(round(ev_cum, 3))
            hands_played += 1
            last_hand_played = h
            max_p_win_cum += p_h * p_w
            max_p_lose_cum += p_h * (1-p_w)
            max_p_play_cum = p_play_cum
        elif ev_cum <= last_ev_cum:
            str_ev_cum = bcolors.FAIL + str(round(ev_cum, 3)) + bcolors.ENDC
        line += str(str_ev_cum) + ' '*(10-len(str_ev_cum))
        last_ev_cum = ev_cum
        print line
    n_hands_played[n] = hands_played
    last_hands_played[n] = last_hand_played
    max_p_win[n] = max_p_win_cum
    max_p_lose[n] = max_p_lose_cum
    max_p_play[n] = max_p_play_cum
    print '\n\n'



''' ROLL OUT MANY HANDS AND SAMPLE
given a strategy, use p_win_tot, p_lose_tot, p_no_play_tot
simulate game and see where ending up
'''

trials = 10
rounds_to_depletion = 33
max_rounds = rounds_to_depletion * 100
chips = 500
quit_chips = chips * 0.01
cash_out = chips * 3
graph = True

print '\n\nAssuming  blinds: $' + str(l) + '/' + str(b) + '  players give to pot: $' + str(T_pot) + '  rake remainder: ' + str(rake_rem) + '\n'
print 'Starting with $' + str(chips) + '\n\n'

for n in range(5, 9):
    print '--- ' + str(n) + ' PLAYERS \n'
    gain = T_pot * n * rake_rem - T_pot
    loss = -1 * T_pot
    p_w = max_p_win[n]
    p_l = max_p_lose[n]
    p_no_play = 1 - max_p_play[n]
    for i in range(trials):
        chips = (l+b) * rounds_to_depletion
        hand_count = 0
        rd = 0
        x = [0]
        y = [chips]
        y_goal = [cash_out]
        y_bad = [quit_chips]
        while rd < max_rounds:
            for turn in range(n):
                if turn == 0:
                    chips -= l
                if turn == 1:
                    chips -= b
                chips += simulateHand(p_w, p_l, p_no_play, gain, loss)
                hand_count += 1
                y.append(chips)
                x.append(hand_count)
                y_goal.append(cash_out)
                y_bad.append(quit_chips)
            rd += 1
        if graph:
            plt.plot(x, y, color = 'b')
            plt.plot(x, y_goal, color = 'g')
            plt.plot(x, y_bad, color = 'r')
            plt.xlabel('hand count')
            plt.ylabel('chips remaining')
            plt.title('Simulated Game ' + str(n) + ' Players')
            plt.grid(True)
            plt.show()






'''

trials = 10
samples = 30
strat_ev = 0.35
rounds_to_depletion = 33
max_rounds = rounds_to_depletion * 20
quit_chips = chips * 0.0
cash_out = chips * 5

print '\n\nAssuming  blinds: $' + str(l) + '/' + str(b) + '  players give to pot: $' + str(T_pot) + '  rake remainder: ' + str(rake_rem) + '\n'
print 'Starting with $' + str(chips) + '\n\n'

for n in range(2, 9):
    print '--- ' + str(n) + ' PLAYERS \n'
    gain = T_pot * n * rake_rem - T_pot
    loss = -1 * T_pot
    p_w = max_p_win[n]
    p_l = max_p_lose[n]
    p_no_play = 1 - max_p_play[n]

    end_chips_trial = []
    for t in range(trials):
        end_chips_sample = []
        for s in range(samples):
            chips = (l+b) * rounds_to_depletion
            hand_count = 0
            rd = 0
            while rd < max_rounds:
                for turn in range(n):
                    if turn == 0:
                        chips -= l
                    if turn == 1:
                        chips -= b
                    chips += simulateHand(p_w, p_l, p_no_play, gain, loss)
                    hand_count += 1
                rd += 1
            end_chips_sample.append(chips)
        end_chips_trial.append(end_chips_sample)
'''
