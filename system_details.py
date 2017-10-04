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


import argparse
import os
import subprocess
import itertools

def remove_duplicate_related_cpus(RELATED):
    RELATED.sort()
    return list(RELATED for RELATED,_ in itertools.groupby(RELATED))

def call_process(task):
        process  = subprocess.Popen(task, shell=True, \
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        return out, err

def cpu_details():
    CPU      = "cpufreq-info | grep 'analyzing CPU' | awk '{print $3 }'"
    out, err = call_process(CPU)
    ALL_CPUS = out.split("\n")[:-1]
    ALL_CPUS = [int(ALL_CPUS[i].split(":")[0]) for i in range(len(ALL_CPUS))]
    return ALL_CPUS

def related_cpus(ALL_CPUS):
    RELATED_CPUS = list()
    for CPU in ALL_CPUS:
        related  = "cpufreq-info --related-cpus -c " + str(CPU)
        out, err = call_process(related)
        RELATED  = map(int, out.split("\n")[:-1])
        RELATED_CPUS.append(RELATED)
    return remove_duplicate_related_cpus(RELATED_CPUS)

def DVFS_related_cpus(RELATED_CPUS):
    DVFS_CPUS = []
    CPUS = zip(*RELATED_CPUS)[0]
    for CPU in CPUS:
        DVFS     = 'cat /sys/devices/system/cpu/cpu'+ str(CPU) + '/CPUfreq/scaling_available_frequencies'
        out, err = call_process(DVFS)
        out      =  map(int, out.split("\n")[:-1][0].split(" "))
        DVFS_CPUS.append(out)
    return DVFS_CPUS

def combinations_cpu_freq(ALL_CPUS, RELATED_CPUS, DVFS_CPUS):
    #The related_cpus
    pass

def main(args):
    #ALL_CPUS     = cpu_details()
    #RELATED_CPUS = related_cpus(ALL_CPUS)
    #DVFS_CPUS    = DVFS_related_cpus(RELATED_CPUS)
    #BIG, SMALL   = args.BIG, args.SMALL
    print args

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--BIG',   '--arg', nargs='+', type=int)
    parser.add_argument('--SMALL', '--arg', nargs='+', type=int)
    args = parser.parse_args()
    main(args)
