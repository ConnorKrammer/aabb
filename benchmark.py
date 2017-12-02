import random
import time
from proximal import get_closest

def rand_point(max=1):
    return random.uniform(0, max), random.uniform(0, max)

def rand_line(max=1):
    return (*rand_point(max), *rand_point(max))

def benchmark(num_lines=30000, canvas_min=100, canvas_max=1000, step_size=100):
    print(f'{num_lines} lines per iteration:')
    for canvas_size in range(canvas_min, canvas_max + step_size, step_size):
        rect_min = (canvas_size - canvas_min) / 2
        rect_max = rect_min + canvas_min
        rect = (rect_min, rect_min, rect_max, rect_max)
        lines = [rand_line(canvas_size) for i in range(0, num_lines)]

        # Benchmark
        t = time.time()
        for l in lines:
            get_closest(*l, *rect)
        dt = time.time() - t

        # Results
        per_sec = round(num_lines / dt / 1000) * 1000
        print(f'  {canvas_size}x{canvas_size}: {dt:.3f}s ({per_sec:,} per sec.)')

if __name__ == '__main__':
    benchmark()
