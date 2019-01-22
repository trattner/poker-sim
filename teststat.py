import numpy
import random
import math

trials = 100
n = 4

results = []

for i in range(trials):
    rolls = []
    for x in range(n):
        rolls.append(random.randint(1,6))
    results.append(rolls)

avg_list = []
std_list = []

for i in range(trials):
    avg = numpy.average(results[i])
    std = numpy.std(results[i])
    avg_list.append(avg)
    std_list.append(std)

cum_avg = numpy.average(avg_list)
max_std = max(std_list)
min_std = min(std_list)

std_avg_list = numpy.std(avg_list)
avg_std = numpy.average(std_list)

print cum_avg
print max_std
print min_std
print std_avg_list
print avg_std / math.sqrt(n)
print avg_std / math.sqrt(trials)

# CONCLUDE: std goes down with sqrt(n)
