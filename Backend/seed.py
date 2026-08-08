import random
import time

from app.core.algorithms import binary_search, insertion_sort, linear_search


if __name__ == "__main__":
    for size in [10, 500, 3000]:
        data = list(range(size, 0, -1))
        random.shuffle(data)

        start = time.perf_counter()
        insertion_sort(list(data))
        insertion_time = time.perf_counter() - start

        sorted_data = sorted(data)
        target = sorted_data[size // 2]

        start = time.perf_counter()
        binary_search(sorted_data, target)
        binary_time = time.perf_counter() - start

        start = time.perf_counter()
        linear_search(sorted_data, target)
        linear_time = time.perf_counter() - start

        print(f"size={size} insertion_sort={insertion_time:.6f}s binary_search={binary_time:.6f}s linear_search={linear_time:.6f}s")
