import random
import time

from app.core.algorithms import binary_search, insertion_sort, linear_search


if __name__ == "__main__":
    for size in [10, 500, 3000]:
        priorities = ["low", "medium", "high"]
        data = [
            {
                "id": i,
                "title": f"Task {i:04d}",
                "priority": random.choice(priorities),
            }
            for i in range(1, size + 1)
        ]
        random.shuffle(data)

        start = time.perf_counter()
        insertion_sort(list(data), key="id")
        insertion_time = time.perf_counter() - start

        sorted_data = sorted(data, key=lambda x: x["id"])
        target = sorted_data[size // 2]["id"]

        start = time.perf_counter()
        binary_search(sorted_data, target, key="id")
        binary_time = time.perf_counter() - start

        start = time.perf_counter()
        linear_search(sorted_data, target, key="id")
        linear_time = time.perf_counter() - start

        print(f"size={size} insertion_sort={insertion_time:.6f}s binary_search={binary_time:.6f}s linear_search={linear_time:.6f}s")
