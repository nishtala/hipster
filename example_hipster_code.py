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


import hipster_hybrid_reinforcement_learning as hybrid

iPID = 2000
bPID = ''
BIG_CORES = [0,1]
SMALL_CORES = [2,3,4,5]
BIG_DVFS = [100, 200, 300]
SMALL_DVFS= [400, 500, 600]
static_order = ['0B3S-100-400','1B2S-200-400']
MAX_THRU_IPS = 2000.0 #given in instructions per second.
MAX_POWER = 100.0
TARGET = 10.0

hipster = hybrid.Hipster(iPID, bPID, BIG_CORES, SMALL_CORES, BIG_DVFS, SMALL_DVFS, static_order, MAX_THRU_IPS, MAX_POWER, TARGET)

hipster.start()

current_load_iPID = 36000 #requests per second, for example
current_latency_iPID = 500 # 500 ms current tail latency
current_power = 40 # 40w, was the power consumption at the time when the above readings were taken.
current_thruput_bPID = 0 # no batch workload iis running.

hipster.hipster(current_load_iPID, current_latency_iPID, current_power, current_thruput_bPID)

hipster.end()


