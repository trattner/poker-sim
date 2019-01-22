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

def calcEV(Pt_w, p_play, n, l, b, T_pot, rake_rem, r = False):
    if r:
        sample = random.uniform(0,1)
        upper_win = Pt_w * p_play
        lower_no_play = 1 - p_play
        if  sample < upper_win:
            return T_pot * rake_rem - (l+b)/float(n)
        elif sample > lower_no_play:
            return -(l + b)/float(n)
        else:
            return -(T_pot + l + b)/float(n)
    else:
        return (Pt_w * T_pot * rake_rem - (1-Pt_w)*T_pot/float(n)) - (l+b)/float(n)


filename = 'n-400_trials-50__2018-07-07_07-57-57.txt'

hand_to_prob = {}
top_hands = {}
top_cutoffs = {}
cutoff = 0.33

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
            print s
        for n in range(2, 9):
            top_hands[n] = []
            cutoff_counter = 0
            print str(n) + ' Players'
            evs_sorted = sorted(hand_evs[n].keys(), reverse=True)
            for ev in evs_sorted:
                for h in hand_evs[n][ev]:
                    top_hands[n].append(h)
                    print '  ' + h + ' '*(9-len(h)) + ' ' + str(round(ev, 2))
                    cutoff_counter += 1
                    if ev <= cutoff and n not in top_cutoffs.keys():
                        top_cutoffs[n] = cutoff_counter
print '\n ---- STRATEGIC CONSIDERATIONS ---- \n'

l = 1
b = 2*l
rake_rem = 0.9
T_pot = 4*b
n_play_range = range(1, 166, 5)
graphs = True

Pt_w = {}
EV_total = {}

for n_played in n_play_range:
    for n in range(2,9):
        prob_win_n = 0
        n_h_tot = len(top_hands[n])
        for i in range(n_h_tot):
            if i < n_played:
                h = top_hands[n][i]
                prob_win_n += prob(h) * hand_to_prob[h][n]
        key = (n, n_played)
        Pt_w[key] = prob_win_n
        EV_total[key] = calcEV(prob_win_n, n, l, b, T_pot, rake_rem)

if graphs:
    for n in range(2, 9):
        x = list(n_play_range)
        y = []
        colors = []
        for n_played in n_play_range:
            key = (n, n_played)
            e = EV_total[key]
            y.append(e)
            if e > 0:
                colors.append('g')
            else:
                colors.append('r')
        plt.scatter(x, y, c=colors, alpha=0.5)
        plt.xlabel('Top x Hands played')
        plt.ylabel('Expected Value of random single hand')
        plt.title('EV of Top Only Strategies with ' + str(n) + ' Players')
        plt.grid(True)
        plt.show()
