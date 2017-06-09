#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

'''
#   Takes all the records in the db0 consisting of   dataset:date_format -> entry
#   then put inside db1 the record                  ip                  -> (timestamp -> list(entry))
#
#   Second part process this added data to deduce the device frequency with an acceptation window
#
'''

import sys
import argparse
import redis
import struct, socket
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import csv
import ast
import pprint
from statistics import mean, median, pstdev, pvariance




# CONFIG #
dataset = "blackhole1"
ONE_DAY = 60*60*24 #1 day
ACCEPTATION_WINDOW = ONE_DAY*1 #1 day

#annotate curve
def autolabel2(ax):
    print('labeling')
    """tot_number_of_session
    Attach a text label above each bar displaying its height
    """
    to_label = [1,2,3,7,10,11,20]
    xy = ax.lines[0].get_xydata()
    for i, tab in enumerate(xy):
        x, y = tab
        if y <= 0:
            continue
        if x not in to_label: 
            continue
        to_label.remove(x)
        ax.text(x, y-0.03, 
                "{:.2f}".format(y),
                ha='center', va='bottom')

def plot():
    #plot

    with open('make_stats_telnet_cdf_ip_login.output', 'r') as f:
        temp = f.read()

    baseList = ast.literal_eval(temp)
    X = baseList[0]
    Y = baseList[1]
    dico_stat = baseList[2]
    
    txt = ""
    for stat, val in dico_stat.items():
        txt += stat + ": " + "{0:.2f}".format(val) + "\n"
    
    #plot
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    ax.plot(X, Y)
    ax.set_title("CDF of the mean(login attempt IP.src) within the acceptation window ("+str(int(ACCEPTATION_WINDOW/ONE_DAY))+" day) per unique ip")
    ax.set_xlabel("# of login attempt")
    ax.set_ylabel("CDF")
    ax.set_xscale('log')
    ax.xaxis.grid(True, which='both')
    ax.yaxis.grid(True, which='both')
    fig.text(.65, .4, txt, bbox={'facecolor':'yellow', 'alpha':0.5, 'pad':10})

    ax.set_xticks([1.0, 10.0, 100.0, 400.0] + [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 20.0])
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

    autolabel2(ax)

    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Makes stats about the frequency of IP within a acceptation window')
    parser.add_argument('-r', '--refresh', required=False, default=False, help='Refresh the data in redis')
    args = parser.parse_args()
    
    plot()

