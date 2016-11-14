#!/usr/bin/env python

import psutil

if __name__ == "__main__":
    free_cpus = 0
    usage = psutil.cpu_percent(interval=5, percpu=True)
    for i in usage:
        if i < 1:
            free_cpus += 1
    print (free_cpus)
