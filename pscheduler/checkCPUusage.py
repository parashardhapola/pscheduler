#!/usr/bin/env python

import psutil


def get_usage():
    free_cpus = 0
    usage = psutil.cpu_percent(interval=5, percpu=True)
    for i in usage:
        if i < 1:
            free_cpus += 1
    return free_cpus


if __name__ == "__main__":
    print (min(get_usage(), get_usage()))
