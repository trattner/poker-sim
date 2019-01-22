import datetime
import time
import random
import numpy
import json


### helper functions - everything in strings
def cardValConvert(input_string):
    '''
    take a given string AKQJ10 etc convert to numeric value or vice-versa
    outputs string
    '''
    lookup = {}
    lookup['a'] = '14'
    lookup['k'] = '13'
    lookup['q'] = '12'
    lookup['j'] = '11'
    lookup['14'] = 'A'
    lookup['13'] = 'K'
    lookup['12'] = 'Q'
    lookup['11'] = 'J'
    output_string = str(input_string)
    search = str(input_string).lower()
    if search in lookup.keys():
        output_string = lookup[search]
    return output_string

def cardSuitConvert(input_string):
    '''
    take a given string convert to numeric value or vice-versa
    outputs string
    '''
    lookup = {}
    lookup['c'] = '0'
    lookup['d'] = '1'
    lookup['h'] = '2'
    lookup['s'] = '3'
    lookup['0'] = 'c'
    lookup['1'] = 'd'
    lookup['2'] = 'h'
    lookup['3'] = 's'
    output_string = str(input_string)
    search = str(input_string).lower()
    if search in lookup.keys():
        output_string = lookup[search]
    return output_string

def generateAllHands():
    card_vals = 'A K Q J 10 9 8 7 6 5 4 3 2'
    match = ['u', 's']
    val_list = []
    for s in card_vals.split():
        val_list.append(s)
    all_hands = []
    for i1 in range(13):
        for i2 in range(i1,13):
            for s in match:
                v1 = val_list[i1]
                v2 = val_list[i2]
                if v1==v2 and s=='s':
                    continue
                trial = v1 + ' ' + v2 + ' ' + s
                hand = parseHand(trial)
                all_hands.append(hand)
    return all_hands

def stringToCard(input_string):
    suit = input_string[-1]
    value = input_string.replace(suit,'')
    return Card(value,suit)

def cardIndexConvert(input_string):
    # from input of either card ('Kd') or index (32) return corresponding card or index
    cardList = Deck().flatList()
    if isinstance(input_string, Card):
        return cardList.index(input_string)
    if input_string in range(53):
        return cardList[input_string]
    else:
        card = stringToCard(input_string)
        return cardList.index(card)

def getHighVal(value_dict, exclude_list):
    # given a dictionary of values and suits, find the high value with longest suit list
    if len(exclude_list) == 2 and len(value_dict[exclude_list[0]]) == 2 and len(value_dict[exclude_list[1]]) == 2:
        maxval = 0
        for val in value_dict.keys():
            if val > maxval and val not in exclude_list:
                maxval = val
        return maxval
    max_kind = 0
    sorted_vals = sorted(value_dict.keys(),reverse=True)
    for i in range(len(sorted_vals)):
        kind = len(value_dict[sorted_vals[i]])
        if kind > max_kind and sorted_vals[i] not in exclude_list:
            max_kind = kind
            max_kind_ind = i
    return sorted_vals[max_kind_ind]

def stringToHand(input_string):
    # takes string of space separated cards and returns hand
    hand = Hand()
    for s in input_string.split():
        hand.deal(stringToCard(s))
    return hand

def findHighFive(hand, player_index):
    # given a hand of cards (typically 7 though arbitrary is fine) find the best 5 card hand, return HighFive of said hand
    category = 0
    tiebreak_value_lists = []
    suit_dict = {}
    value_dict = {}
    for card in hand:
        v = int(card.getNumValue())
        s = int(card.getNumSuit())
        if v not in value_dict.keys():
            value_dict[v] = []
        value_dict[v].append(s)
        if s not in suit_dict.keys():
            suit_dict[s] = []
        suit_dict[s].append(v)
    for s in suit_dict.keys():
        if len(suit_dict[s]) >= 5:
            l = sorted(suit_dict[s],reverse=True)
            straight = [l[0]]
            for i in range(1,len(l)):
                if straight[-1] - 1 == l[i]:
                    straight.append(l[i])
                else:
                    straight = [l[i]]
                if len(straight) == 5:
                    break
            if straight[-1] == 2 and l[0] == 14:
                straight.append(l[0])
            if len(straight) >= 5:
                tiebreak_value_lists.append(straight[0:5])
                category = handCategoryConvert('straight flush')
                return HighFive(category, player_index, tiebreak_value_lists)
            else:
                category = handCategoryConvert('flush')
                tiebreak_value_lists.append(l[0:5])
    high_val_list = []
    kind_list = []
    while sum(kind_list) < 5:
        high_val = getHighVal(value_dict, high_val_list)
        kind = 0
        for s in value_dict[high_val]:
            kind += 1
            if (sum(kind_list) + kind) == 5:
                break
        kind_list.append(kind)
        high_val_list.append(high_val)
    if kind_list[0]==4:
        category = handCategoryConvert('four of a kind')
        tiebreak_1 = [high_val_list[0]]*4
        tiebreak_2 = [high_val_list[1]]
        return HighFive(category, player_index, [tiebreak_1, tiebreak_2])
    if kind_list[0]==3 and kind_list[1]==2:
        category = handCategoryConvert('full house')
        tiebreak_1 = [high_val_list[0]]*3
        tiebreak_2 = [high_val_list[1]]*2
        return HighFive(category, player_index, [tiebreak_1, tiebreak_2])
    if category > 6:
        return HighFive(category, player_index, tiebreak_value_lists)
    sorted_vals = sorted(value_dict.keys(),reverse=True)
    straight = [sorted_vals[0]]
    for i in range(1,len(sorted_vals)):
        if straight[-1] - 1 == sorted_vals[i]:
            straight.append(sorted_vals[i])
        else:
            straight = [sorted_vals[i]]
        if len(straight) == 5:
            break
    if straight[-1] == 2 and sorted_vals[0] == 14:
        straight.append(sorted_vals[0])
    if len(straight) >= 5:
        category = handCategoryConvert('straight')
        return HighFive(category, player_index, [straight[0:5]])
    if kind_list[0]==3:
        category = handCategoryConvert('three of a kind')
        tiebreak_1 = [high_val_list[0]]*3
        tiebreak_2 = [high_val_list[1], high_val_list[2]]
        return HighFive(category, player_index, [tiebreak_1, tiebreak_2])
    if kind_list[0]==2 and kind_list[1]==2:
        category = handCategoryConvert('two pair')
        best = high_val_list[0]
        second = high_val_list[1]
        high_val_list.remove(best)
        high_val_list.remove(second)
        tiebreak_1 = [best, best, second, second]
        tiebreak_2 = [max(high_val_list)]
        return HighFive(category, player_index, [tiebreak_1, tiebreak_2])
    if kind_list[0]==2:
        category = handCategoryConvert('pair')
        tiebreak_1 = [high_val_list[0],high_val_list[0]]
        tiebreak_2 = [high_val_list[i] for i in range(1,4)]
        return HighFive(category, player_index, [tiebreak_1, tiebreak_2])
    if kind_list[0]==1:
        category = handCategoryConvert('high card')
        tiebreak_1 = [high_val_list[0]]
        tiebreak_2 = [high_val_list[i] for i in range(1,5)]
        return HighFive(category, player_index, [tiebreak_1, tiebreak_2])
    return HighFive(0, player_index, [[],[]])

def handCategoryConvert(input_string):
    lookup = {}
    lookup['straight flush'] = 10
    lookup['four of a kind'] = 9
    lookup['full house'] = 8
    lookup['flush'] = 7
    lookup['straight'] = 6
    lookup['three of a kind'] = 5
    lookup['two pair'] = 4
    lookup['pair'] = 3
    lookup['high card'] = 2
    lookup['failed to categorize'] = 0
    for key in lookup.keys():
        lookup[lookup[key]] = key
    if input_string in lookup.keys():
        return lookup[input_string]
    else:
        return 'hand category not found'

def getTiebreakIndices(l):
    # given a list of equal category HighFives, return list of winning player indices using tiebreak lists of values sorted in descending order starting with winning category components
    if len(l) == 1:
        return [l[0].getPlayer()]
    winners = set([hf.getPlayer() for hf in l])
    for r in range(5):
        players = set(winners)
        max_val = 0
        player_to_card = {}
        for hf in l:
            current_tiebreak_val = int(cardValConvert(hf.getValues()[r]))
            player_to_card[hf.getPlayer()] = current_tiebreak_val
            if current_tiebreak_val > max_val and hf.getPlayer() in winners:
                max_val = current_tiebreak_val
        for p in players:
            if player_to_card[p] < max_val and p in winners:
                winners.remove(p)
        if len(winners) == 1:
            return list(winners)
    return list(winners)

def parseHand(input_string):
    # takes space separated values and suited or unsuited param, returns hand
    hand = Hand()
    l = input_string.split()
    s1 = 'c'
    s2 = 'd'
    if l[-1] == 's':
        s2 = s1
    hand.deal(stringToCard(str(l[0]+s1)))
    hand.deal(stringToCard(str(l[1]+s2)))
    return hand

### classes
class Deck():
    '''
    Deck initialized with 52 cards
    pops off cards at random
    can remove specific cards
    '''
    def __init__(self):
        self.deckList = []
        for numSuit in range(4):
            cardSuit = cardSuitConvert(numSuit)
            self.deckList.append([])
            for numVal in range(2,15):
                cardVal = cardValConvert(numVal)
                card = Card(cardVal,cardSuit)
                self.deckList[numSuit].append(card)
        return

    def cardsLeft(self):
        output_int = 0
        for numSuit in range(len(self.deckList)):
            for card in self.deckList[numSuit]:
                output_int += 1
        return output_int

    def flatList(self):
        output_list = []
        for l in self.deckList:
            for c in l:
                output_list.append(c)
        return output_list

    def draw(self):
        # draw a card at random and remove it from deck
        rand_i = random.randint(1,self.cardsLeft())
        card = self.flatList()[rand_i - 1]
        return self.take(card.getFaceValue(), card.getSuit())

    def take(self, value, suit):
        # remove a specific card and return it or error string
        input_card = Card(value, suit)
        intSuit = int(cardSuitConvert(suit))
        try:
            i = self.deckList[intSuit].index(input_card)
            return self.deckList[intSuit].pop(i)
        except ValueError:
            return 'card (' + str(input_card) + ') not found in deck'

    def remove(self, input_card):
        try:
            dl = self.deckList[int(input_card.getNumSuit())]
            i = dl.index(input_card)
            return dl.pop(i)
        except ValueError:
            return 'card (' + str(input_card) + ') not found in deck'

    def __str__(self):
        output_string = ' Deck: \n'
        for numSuit in range(len(self.deckList)):
            output_string += '  ' + cardSuitConvert(numSuit) + ': '
            for card in self.deckList[numSuit]:
                output_string += ' ' + card.getFaceValue() + ' '
            output_string += '\n'
        return output_string

class Card():
    '''
    Card has value (K,4,Q=12) and suit (d,c,h,s)
    '''
    def __init__(self, value, suit):
        # create a card
        self.suit = str(suit)
        self.value = int(cardValConvert(value))
        return

    def getFaceValue(self):
        return cardValConvert(self.value)

    def getNumValue(self):
        return self.value

    def getSuit(self):
        return self.suit

    def getNumSuit(self):
        return cardSuitConvert(self.suit)

    def __str__(self):
        return self.getFaceValue() + self.getSuit()

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.getSuit() == other.getSuit() and self.getFaceValue() == other.getFaceValue()
        return False

class Hand():
    '''
    Hand is a list of cards
    Update hand by dealing additional cards
    '''
    def __init__(self):
        self.cards = []
        return

    def deal(self, card):
        self.cards.append(card)
        return

    def getCards(self):
        return list(self.cards)

    def copy(self):
        copy_hand = Hand()
        for card in self.cards:
            copy_hand.deal(card)
        return copy_hand

    def __iter__(self):
        for x in self.cards:
            yield x

    def __str__(self):
        output_string = ''
        for card in self.cards:
            output_string += str(card) + ' '
        return output_string[:-1]

    def __eq__(self, other):
        if isinstance(other, Hand):
            ocards = other.getCards()
            if len(ocards)==len(self.getCards()):
                for card in self.cards:
                    if not card in ocards:
                        return False
                return True
        return False

class HighFive():
    '''
    HighFive is a class of metadata about a hand.
    - hand category (input number)
    - player index
    - tiebreak value lists
    '''
    def __init__(self, category, player_index, tiebreak_value_lists):
        self.categoryNumber = category
        self.categoryName = handCategoryConvert(category)
        self.player_index = player_index
        self.tieCategory = tiebreak_value_lists[0] #category value features
        self.tieRest = []
        if len(tiebreak_value_lists) > 1:
            self.tieRest = tiebreak_value_lists[1] #rest of cards
    def getPlayer(self):
        return self.player_index
    def getCategoryNum(self):
        return self.categoryNumber
    def getCategoryName(self):
        return self.categoryName
    def getPrimaryTiebreak(self):
        return list(self.tieCategory)
    def getSecondaryTiebreak(self):
        return list(self.tieRest)
    def getValues(self):
        t = [cardValConvert(c) for c in self.getPrimaryTiebreak()]
        t.extend([cardValConvert(c) for c in self.getSecondaryTiebreak()])
        return t
    def __eq__(self, other):
        if isinstance(other, HighFive):
            if self.categoryNumber == other.getCategoryNum and set(self.tieCategory) == set(other.getPrimaryTiebreak()) and set(self.tieRest) == set(other.getSecondaryTiebreak()):
                return True
        return False

class Game():
    '''
    Game starts with some number of players including you and a new deck
    Proceeds by subroutines (random or preset) for
    - dealing cards
    - flop
    - turn
    - river
    - winner
    '''
    def __init__(self, n):
        self.deck = Deck()
        self.table = Hand()
        self.burned = []
        self.players = []
        for player in range(n):
            self.players.append(Hand())
        self.win_lose_dict = {'winners':[],'losers':[]}
        self.player_data = {}
        return

    def giveHand(self, player_index, hand):
        for card in hand:
            self.players[player_index].deal(self.deck.remove(card))
        return

    def giveTable(self, hand):
        for card in hand:
            self.table.deal(self.deck.remove(card))
        return

    def randomDeal(self):
        n = len(self.players)
        for i in range(2*n):
            if len(self.players[i % n].getCards()) < 2:
                self.players[i % n].deal(self.deck.draw())
        return

    def flop(self):
        self.burned.append(self.deck.draw())
        for i in range(3):
            self.table.deal(self.deck.draw())
        return

    def turn(self):
        self.burned.append(self.deck.draw())
        self.table.deal(self.deck.draw())
        return

    def river(self):
        self.burned.append(self.deck.draw())
        self.table.deal(self.deck.draw())
        return

    def randomTable(self):
        self.flop()
        self.turn()
        self.river()
        return

    def getDeck(self):
        return str(self.deck)

    def getBurned(self):
        output_string = 'burned: '
        for card in self.burned:
            output_string += str(card) + ' '
        return output_string

    def simulate(self, hand):
        g.giveHand(0,hand)
        g.randomDeal()
        g.randomTable()
        g.findWinners()
        return g.getOutcome(0)

    def findWinners(self):
        # updates self with hand evaluations
        category_ranking = {}
        for i in range(len(self.players)):
            # first make full hand combining table and pocket
            combined = self.getTable()
            for card in self.getHand(i):
                combined.deal(card)
            # then find best hand and categorize
            high_five = findHighFive(combined,i)
            cat = high_five.getCategoryNum()
            if cat not in category_ranking.keys():
                category_ranking[cat] = []
            category_ranking[cat].append(i)
            self.player_data[i] = high_five
        # determine best category and break ties
        top_cat = max(category_ranking.keys())
        winning_indices = getTiebreakIndices([self.player_data[i] for i in category_ranking[top_cat]])
        losing_indices = range(len(self.players))

        for i in winning_indices:
            self.win_lose_dict['winners'].append(i)
            losing_indices.remove(i)
        for i in losing_indices:
            self.win_lose_dict['losers'].append(i)
        return

    def getWinReport(self):
        output = ''
        for i in self.win_lose_dict['winners']:
            output += ' WIN: p' + str(i) + ' ' + str(self.player_data[i].getCategoryName()) + ' ' + str(self.player_data[i].getValues()) + '\n'
        for i in self.win_lose_dict['losers']:
            output += ' LOSE: p' + str(i) + ' ' + str(self.player_data[i].getCategoryName()) + ' ' + str(self.player_data[i].getValues()) + '\n'
        return output

    def getWinIndices(self):
        return list(self.win_lose_dict['winners'])

    def getOutcome(self, player_index):
        if player_index in self.win_lose_dict['winners']:
            return 1/float(len(self.win_lose_dict['winners']))
        else:
            return 0

    def getOptimalHands(self):
        output = []
        for i in range(len(self.players)):
            output.append(self.player_data[i].getValues())
        return output

    def getHandCategories(self):
        output = []
        for i in range(len(self.players)):
            output.append(self.player_data[i].getCategoryName())
        return output

    def getHand(self, player_index):
        return self.players[player_index].copy()

    def getTable(self):
        return self.table.copy()

    def __str__(self):
        output_string = ' Table: ' + str(self.table)
        for i in range(len(self.players)):
            output_string += '\n  p' + str(i) + ': ' + str(self.players[i])
        return output_string[:-1]

'''
for i in range(10000):
    n = 3
    card1 = stringToCard('Ks')
    card2 = stringToCard('10c')
    hand = Hand()
    hand.deal(card1)
    hand.deal(card2)
    g = Game(n)
    g.giveHand(0, hand)
    g.randomDeal()
    g.randomTable()
    print '\n\n===== START GAME ' + str(i) + ' ======='
    print g
    print '------ END GAME --------\n'
    print '----- WIN REPORT -------'
    g.findWinners()
    print g.getWinReport()
    print '===== END REPORT =======\n\n'
'''

'''

hand0 = stringToHand('Ks 10c')
hand1 = stringToHand('10s 9c')
hand2 = stringToHand('8c Qh')
table = stringToHand('10h 4d Jh 8d 3h')

g = Game(3)
g.giveHand(0, hand0)
g.giveHand(1, hand1)
g.giveHand(2, hand2)
g.giveTable(table)
print g
g.findWinners()
print g.getWinReport()
'''

'''

all_hands = generateAllHands()
filename = 'all_hands.txt'
data = {'hands':[]}
for hand in all_hands:
    data['hands'].append(str(hand))
with open(filename, 'w') as outfile:
    json.dump(data, outfile)


'''

trials = 50
n = 400
all_hands = generateAllHands()
data = {}
progress = 0
complete = len(all_hands)
last_percent = 0
t_start = time.time()
for hand in all_hands:
    data[str(hand)] = {}
    for n_p in range(2, 9):
        trial_results = []
        for t in range(trials):
            sample = []
            for i in range(n):
                g = Game(n_p)
                outcome = g.simulate(hand)
                sample.append(outcome)
            trial_results.append(numpy.average(sample))
        data[str(hand)][n_p] = [numpy.average(trial_results), numpy.std(trial_results)]
    progress += 1
    percent = progress / float(complete)
    elapse = (time.time()-t_start)/float(60)
    print 'approx mins remaining: ' + str(elapse * (complete-progress))
    if percent - last_percent > 1:
        print 'percent complete: ' + str(percent)
        last_percent = percent

filename = 'n-'+str(n) + '_trials-' + str(trials) + '__' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S') + '.txt'

with open(filename, 'w') as outfile:
    json.dump(data, outfile)


# run a bunch of simulated games
'''
players = 8
t0 = 'A A u'
t1 = 'K K u'
t2 = 'mixed'
hand0 = parseHand(t0)
hand1 = parseHand(t1)
n = 5000
results_dict = {}
results_dict[t0] = []
results_dict[t1] = []
results_dict[t2] = []
for rd in range(n):
    g0 = Game(players)
    g1 = Game(players)
    g2 = Game(players)
    g0.giveHand(0, hand0)
    g1.giveHand(1, hand1)
    g2.giveHand(0, hand0)
    g2.giveHand(1, hand1)
    g0.randomDeal()
    g1.randomDeal()
    g2.randomDeal()
    g0.randomTable()
    g1.randomTable()
    g2.randomTable()
    g0.findWinners()
    g1.findWinners()
    g2.findWinners()
    g0_winners = g0.getWinIndices()
    g1_winners = g1.getWinIndices()
    g2_winners = g2.getWinIndices()
    g0_outcome = g0.getOutcome(0)
    g1_outcome = g1.getOutcome(1)
    g2_outcome_0 = g2.getOutcome(0)
    g2_outcome_1 = g2.getOutcome(1)
    results_dict[t0].append(g0_outcome)
    results_dict[t1].append(g1_outcome)
    results_dict[t2].append(g2_outcome_0)
    print g0
    print g0_winners
    print g0_outcome
    print g0.getWinReport()
    print g1
    print g1_winners
    print g1_outcome
    print g1.getWinReport()
    print g2
    print g2_winners
    print g2_outcome_0
    print g2_outcome_1
    print g2.getWinReport()
print 'PLAYERS--' + str(players)
print t0 + ' average in ' + str(n) + ' trials: ' + str(sum(results_dict[t0])/float(len(results_dict[t0])))
print t1 + ' average in ' + str(n) + ' trials: ' + str(sum(results_dict[t1])/float(len(results_dict[t1])))
print t2 + ' average in ' + str(n) + ' trials: ' + str(sum(results_dict[t2])/float(len(results_dict[t2])))
'''

'''
### START

# make log file
log_name = 'log_' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
log = open(log_name,"a")
log.write("Starting Hold-Em.py\n")

# set up hand


log.write("\n\nEnding Hold-Em.py - ")
log.close()
'''
