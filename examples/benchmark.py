import time
import memory_profiler
from memory_profiler import profile
from pyecs_async.hibitset import HiBitset


class HibitsetPython:
    def __init__(self):
        self.bitset = 0

    def add(self, idx):
        self.bitset |= (1 << idx)

    def remove(self, idx):
        self.bitset &= ~(1 << idx)

    def contains(self, idx):
        return (self.bitset & (1 << idx)) != 0


def benchmark(hibitset_class, iterations):
    start_time = time.time()
    hibitset = hibitset_class()

    for i in range(iterations):
        hibitset.add(i)
        hibitset.contains(i)
        hibitset.remove(i)

    end_time = time.time()
    return end_time - start_time


iterations = 100000000


def main():
    #python_time = benchmark(HibitsetPython, iterations)
    cython_time = benchmark(HiBitset, iterations)

    #print(f"Python Hibitset: {python_time} seconds")
    print(f"Cython Hibitset: {cython_time} seconds")
    #print(f"Cython is {python_time / cython_time} times faster than Python")



# memory_profiler.memory_usage()

#main()


@profile
def mtest1():
    return benchmark(HiBitset, iterations)


print(f"Cython Hibitset memory: {memory_profiler.memory_usage()} MB")
mtest1()


@profile
def mtest2():
    return benchmark(HibitsetPython, iterations)


#print(f"Python Hibitset memory: {memory_profiler.memory_usage()} MB")
#mtest2()
