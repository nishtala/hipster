* I . Overview

Hipster is a user-level scheduler for Linux OS, designed to implement a hybrid
reinforcement learning algorithm to schedule latency-critical and batch workloads to
improve resource utilisation of a cloud system.  This scheduler was built at the Barcelona
Supercomputing Center and Universitat Politècnica de Catalunya, Spain.  The scheduler
algorithm should be invoked at the sampling interval of the latency-critical workload.
Hipster should be provided with the number of big and small cores, DVFS states of big and small
cores, and the static order of the power efficient configurations of the system. 

Very important! Please read (at the very least browse through) the following paper before
using Hipster.
https://nishtalaraj.files.wordpress.com/2016/10/hipster-hpca-camera-ready.pdf 
The paper will explain the purpose of our scheduler and briefly how it works.

* II. How to install

1. Here is how to install packages necessary for Hipster:

 sudo pip install psutil

2. How to get initial input parameters
 
 To give the basic input details for hipster. Please identify the following:
 - The big cores and small cores and their respective DVFS states.  
 - static_order: Using the stress microbenchmark provided (stress_cpu.c), run it at all
   possible combination and gather performance (IPS) and power statistics. Only the
   power-efficiency order (IPS/W) of the combinations for the heuristic mapper.  
 - MAX_THROUGHPUT, TDP: Run the microbenchmark on all cores at the highest DVFS states and
   gather performance and power statistics.
 - target: target of the latency-critical workload

In case you will have additional questions (especially about internal code of the
scheduler), please don't hesitate to email me directly at: <rajiv.nishtala@bsc.es> or
<nishtala.raj@gmail.com>


* III. Getting help

Got a question? Found a bug? Please contact the me directly.  

Please do the following to get a useful response and save time for both of us:

1) Please briefly describe what do you want to use Hipster for? What is the purpose of
your experiments? Without understanding what you want to see, it is hard to recommend the
best use of Hipster for your task. Also, please elaborate a little bit on the workload you
are using in your tests (what apps, what is their CPU usage, etc.).

2) Please indicate what Hipster version you're using, and send the output file from
Hipster.

Cheers!
-Rajiv
