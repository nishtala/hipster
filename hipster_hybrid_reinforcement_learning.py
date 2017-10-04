#!/usr/bin/env python
'''
 Authors:   Rajiv Nishtala <rajiv.nishtala@bsc.es>

 Copyright (c) 2017 Barcelona Supercomputing Center

 This file is part of *Hipster*

 Please cite our paper: *Hipster: Hybrid Task Manager for
         Latency-Critical Cloud Workloads* In the Proceedings
         of High Performance Computer Architecture 2017

 Paper link:
 <https://nishtalaraj.files.wordpress.com/2016/10/hipster-hpca-camera-ready.pdf>

 Hipster is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Hipster is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Hipster.  If not, see <http://www.gnu.org/licenses/>.

 This copyright notice must be reproduced on each copy, or partial
 copy, of this software.
'''

import psutil
from time import time
from os import system
import signal
import string
from operator import itemgetter
from bisect import bisect_left
import random

class Hipster(object):

    def __init__(self, iPID, bPID,  BIG_CORES, SMALL_CORES, BIG_FREQ, \
            SMALL_FREQ, static_order, MAX_THROUGHPUT, TDP, target, idx=0, BEGINX=0,\
            ENDX=38000, STEPX=24, UPPER_THRESHOLD = 80.0, LOWER_THRESHOLD=20.0, \
            learning_time=300, load = 0, latency = 0, power = 0, throughput = 0):

        self.iPID = iPID
        self.bPID = bPID
        self.BIG_CORES = sorted(BIG_CORES)
        self.SMALL_CORES = sorted(SMALL_CORES)
        self.BIG_FREQ = sorted(BIG_FREQ)
        self.SMALL_FREQ = sorted(SMALL_FREQ)
        self.static_order = static_order
        self.ALL_CORES = self.BIG_CORES + self.SMALL_CORES
        self.CORE_CONFIGS = list()
        self.FREQ_CONFIGS_BIG = list()
        self.FREQ_CONFIGS_SMALL = list()
        self.target = target
        self.IDX = idx
        self.BEGINX = BEGINX
        self.LOAD_DICT = dict()
        self.ENDX = ENDX
        self.STEPX = STEPX
        self.UPPER_THRESHOLD = UPPER_THRESHOLD/100.0
        self.LOWER_THRESHOLD = LOWER_THRESHOLD/100.0
        self.QOS_ALERT = target*UPPER_THRESHOLD
        self.QOS_SAFE = target*LOWER_THRESHOLD
        self.learning_time = learning_time
        self.prev_load = load
        self.prev_latency = latency
        self.prev_power = TDP
        self.prev_thru = throughput
        self.max_thru = MAX_THROUGHPUT
        self.max_power = TDP

    def start(self):
        """
        Setting up the inital parameters
        """

        helper_functions().governor_change(self.ALL_CORES, "userspace")

        self.change_static_order()
        for i in range(self.BEGINX, self.ENDX, self.STEPX):
            self.LOAD_DICT[i] = {}
            for j in self.static_order:
                self.LOAD_DICT[i][j] = 0
        helper_functions().mapper(self.iPID, self.CORE_CONFIGS[self.IDX])
        helper_functions().change_freq(self.BIG_CORES, self.FREQ_CONFIGS_BIG[self.IDX])
        helper_functions().change_freq(self.SMALL_CORES, self.FREQ_CONFIGS_SMALL[self.IDX])

    def change_static_order(self):
        """
        Changing from NBMS-BIG_DVFS-SMALL_DVFS to [core IDS] - BIG_FREQ - SMALL_FREQ
        """
        for so in self.static_order:
            so_split = so.split("-")
            num_big = int(so_split[0][0])
            num_small = int(so_split[0][2])
            self.FREQ_CONFIGS_BIG.append(so_split[1])
            self.FREQ_CONFIGS_SMALL.append(so_split[2])
            self.CORE_CONFIGS.append(self.BIG_CORES[:num_big] + self.SMALL_CORES[:num_small])

    def hipster(self, load, latency, power, throughput):
        """
        Setting up the exploration and exploitation algorithm
        """

        summary_prev = self.static_order[self.IDX]

        exploitation_phase().update_bucket(self, summary_prev)
        if (latency >= self.QOS_ALERT):
            ALERT_OR_SAFE = True
        else:
            ALERT_OR_SAFE = False
        if time() < self.learning_time:
            learning_phase().hipster_heuristic(self)
        else:
            exploitation_phase().reinforcement_learning(self)

        self.prev_load = load
        self.prev_latency = latency
        self.prev_power = power
        self.prev_thru = throughput

        helper_functions().change_freq(self.BIG_CORES, self.FREQ_CONFIGS_BIG[self.IDX])
        helper_functions().change_freq(self.SMALL_CORES, self.FREQ_CONFIGS_SMALL[self.IDX])
        helper_functions().mapper(self.iPID, self.CORE_CONFIGS[self.IDX])

        if len(self.bPID) == 0: mapping_batch = []
        mapping = self.CORE_CONFIGS[self.IDX]
        mapping_freq_big = self.FREQ_CONFIGS_BIG[self.IDX]
        mapping_freq_small = self.FREQ_CONFIGS_SMALL[self.IDX]
        if len(self.bPID) != 0:
            mapping_batch = self.ALL_CORES - self.CORE_CONFIGS[self.IDX]
            zipped = zip(self.bPID, mapping_batch)
            for j in zipped:
                p = psutil.Process(j[0])
                p.resume()
            if len(zipped) < len(self.bPID):
                for sus in range(len(zipped), len(self.bPID),1):
                    p = psutil.Process(self.bPID[sus])
                    p.suspend()
        return mapping, mapping_batch, mapping_freq_big, mapping_freq_small, self.IDX

    def end(self):
        """
        Changing to ondemand governor
        """
        helper_functions().governor_change(self.ALL_CORES, "ondemand")

    def help(self):
        print "Assumption: This API assumes Hipster is run on a big.LITTLE architecture with a socket level DVFS\n",\
        "Input\n",\
        "*iPID -- PID of the interactive workload*\n",\
        "*bPID -- PID of the batch workload*\n",\
        "*BIG_CORES -- big cores in a list*\n",\
        "*SMALL_CORES -- small cores in a list*\n",\
        "*BIG_FREQ -- big cores DVFS in a list*\n",\
        "*SMALL_FREQ -- small cores DVFS in a list*\n",\
        "*static_order -- static ordering of cores in the increasing order of power efficiency.\n",\
        "* \t \t The format of submission is 0B1S-115000-65000, 2B2S-115000-65000 as a list*\n",\
        "*MAX_THROUGHPUT -- max throughput of the system*\n",\
        "*target -- target of the interactive workload*\n",\
        "*idx -- which configuration should it start with index number*\n",\
        "*BEGINX -- The minimum load*\n",\
        "*ENDX -- The maximum load*\n",\
        "*STEPX --  The number of buckets to quantise*\n",\
        "*UPPER_THRESHOLD -- The upper threshold*\n",\
        "*LOWER_THRESHOLD -- The lower threshold*\n",\
        "*learning_time -- How long is the exploration phase*\n"\
        "*Quality of Service (latency) -- latency of the interactive workload*\n",\
        "*Load (in requests per second, etc) -- load of the interactive workload*\n",\
        "*throughput -- throughput of the batch workloads*\n",\
        "*power -- system power consumption*\n",\
        "*returns mapping --> core_mapping_interactive, core_mapping_batch, each cores P-State*"

        print "\n \n\n"

        print "First run Hipster, start, hipster, and then end\n"

class helper_functions(object):
    def __init__(self):
        pass

    def mapper(self, lc_threads, mapping):
        """
        mapping threads to cores
        """
        mapping_m = ','.join(str(x) for x in mapping)
        system('taskset -apc ' + str(mapping_m) + ' ' + str(lc_threads) + ' >/dev/null')

    def change_freq(self, cpu, val):
        """
        changing frequency at a socket level
        """
        freq = "sudo cpufreq-set -r -c 0 --freq " + str(val)
        system(freq)

    def governor_change(self, ALL_CORES, governor):
        """
        changing the acpi governor
        """
        for i in range(len(ALL_CORES)):
            gov = "sudo cpufreq-set -r -c " + str(ALL_CORES[i]) + " --governor " + governor
            system(gov)

class learning_phase(object):
    def __init__(self):
        pass
    def hipster_heuristic(self, h_self):
        """
        Implementing Hipster's heuristic
        """
        if (h_self.ALERT_OR_SAFE):
            if h_self.IDX < len(h_self.static_order) -1:
                h_self.IDX = h_self.IDX + 1
            else:
                h_self.IDX = len(h_self.static_order) -1
        else:
            if h_self.IDX == 0:
                h_self.IDX = 0
            else:
                h_self.IDX = h_self.IDX - 1

class exploitation_phase(object):
    def __init__(self):
        pass

    def takeClosest(self, myList, myNumber):
        """
        Quantised buckets and selecting the bucket
        """
        pos = bisect_left(myList, myNumber)
        if pos == 0:
            return myList[0]
        if pos == len(myList):
            return myList[-1]
        before = myList[pos - 1]
        after = myList[pos]
        if after - myNumber < myNumber - before:
           return after
        else:
           return before

    def bucket_me(self, load, BEGINX, ENDX, STEPX):
        """
        checking which bucket the load falls under
        """
        possible_buckets = list(xrange(BEGINX, ENDX, STEPX))
        cload = exploitation_phase().takeClosest(possible_buckets, load)
        return cload

    def update_bucket(self, e_self, config):
        """
        Updating the bucket for a config and load
        """
        LEARNING_FACTOR = 0.9
        DISCOUNT_FACTOR = 0.2
        bucketit = exploitation_phase().bucket_me(e_self.prev_load, e_self.BEGINX, e_self.ENDX, e_self.STEPX)
        MAX_CONFIG  = max(e_self.LOAD_DICT[bucketit].iteritems(), key=itemgetter(1))[0]
        MAX_CONFIG_VALUE = e_self.LOAD_DICT[bucketit][MAX_CONFIG]
        LATENCY_REWARD = float(e_self.prev_latency)/float(e_self.target)
        if (e_self.prev_latency >= e_self.QOS_ALERT) and (e_self.prev_latency < e_self.target):
            LATENCY_REWARD = LATENCY_REWARD - random.uniform(0, 1)
        if len(e_self.bPID) == 0:
            POWER_REWARD = float(e_self.max_power)/float(e_self.prev_power)
            if e_self.prev_latency < e_self.target:
                reward = 1  + LATENCY_REWARD + POWER_REWARD
            if e_self.prev_latency >= e_self.target:
                reward = -1 - LATENCY_REWARD + POWER_REWARD
        else:
            THROUGHPUT_REWARD = e_self.prev_thru/e_self.max_thru
            if e_self.prev_latency < e_self.target:
                reward = 1  + LATENCY_REWARD  + THROUGHPUT_REWARD
            if e_self.prev_latency >= e_self.target:
                reward = -1 - LATENCY_REWARD + THROUGHPUT_REWARD

        e_self.LOAD_DICT[bucketit][config] = e_self.LOAD_DICT[bucketit][config] + (LEARNING_FACTOR * (reward + \
                                    (DISCOUNT_FACTOR * MAX_CONFIG_VALUE) - e_self.LOAD_DICT[bucketit][config]))

    def reinforcement_learning(self, e_self):
        """
        Exploration and exploitation phase
        """
        EPSILON = 0.995
        if EPSILON > random.random():
            mapping = random.choice(e_self.CORE_CONFIGS)
            mapping_freq_big   = e_self.FREQ_CONFIGS_BIG[int(e_self.CORE_CONFIGS.index(mapping))]
            mapping_freq_small = e_self.FREQ_CONFIGS_SMALL[int(e_self.CORE_CONFIGS.index(mapping))]

        else:
            bucketit = bucket_me(e_self.load, e_self.BEGINX, e_self.ENDX, e_self.STEPX)
            sorted_x = sorted(e_self.LOAD_DICT[bucketit].items(), key=itemgetter(1))[::-1]
            configs = sorted_x[0]
            IDX = e_self.static_order.index(configs)
