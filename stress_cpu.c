/*
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
*/


#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <signal.h>

#define GIGABYTE 1073741824

void sig_end(int);
void stress_cpu(void);


void stress_cpu(void){
  unsigned int iseed = (unsigned int)time(NULL);
  float rando;
  srand (iseed);
  time_t start;
  time(&start);
    
  while(time(0) - start < 10000000000000){
    rando = rand();
    rando *= 1.9987823;
    rando /= .977288;
    float result = cosh( sqrt(rando) * cos(rando) * sin(rando) * acos(rando) * asin(rando) * atan(rando) * atan2(rando, rando) ) ;
    result = result * rando;
    result = result / pow(rando, 2.999999998);
    result = ((int)result << 17) * 1.0000000001;
    srand ((long int)result);
  }
}

int main (int argc, char **argv){
  stress_cpu();
  return 0;
}
