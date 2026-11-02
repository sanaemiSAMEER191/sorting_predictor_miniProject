import random
import time
import pandas as pd

from sorting_algorithms import (
    bubble_sort,
    selection_sort,
    insertion_sort,
    merge_sort,
    heap_sort,
    quick_sort
)

# -----------------------------
# Configuration
# -----------------------------
NUM_ARRAYS = 1000
NUM_BENCHMARK_RUNS = 10

# -----------------------------
# Generate Random Array
# -----------------------------
def generate_random_array():

    n = random.randint(5, 500)

    array_type = random.choice([
        "random",
        "nearly_sorted",
        "reverse_sorted",
        "duplicates"
    ])

    # Completely Random
    if array_type == "random":
        arr = [random.randint(0, 1000) for _ in range(n)]

    # Nearly Sorted
    elif array_type == "nearly_sorted":

        arr = sorted(random.randint(0, 1000) for _ in range(n))

        swaps = max(1, n // 10)      # disturb about 10%

        for _ in range(swaps):
            i = random.randint(0, n - 1)
            j = random.randint(0, n - 1)
            arr[i], arr[j] = arr[j], arr[i]

    # Reverse Sorted
    elif array_type == "reverse_sorted":

        arr = sorted(
            [random.randint(0, 1000) for _ in range(n)],
            reverse=True
        )

    # Duplicate Heavy
    else:

        unique = max(2, n // 10)

        values = [random.randint(0, 1000) for _ in range(unique)]

        arr = [random.choice(values) for _ in range(n)]

    return arr


# -----------------------------
# Benchmark Function
# -----------------------------
def benchmark(sort_function, arr, runs=NUM_BENCHMARK_RUNS):

    total_time = 0

    for _ in range(runs):
        start = time.perf_counter()
        sort_function(arr)
        end = time.perf_counter()

        total_time += (end - start)

    return total_time / runs


# -----------------------------
# Sorting Algorithms Dictionary
# -----------------------------
algorithms = {
    "Bubble": bubble_sort,
    "Selection": selection_sort,
    "Insertion": insertion_sort,
    "Merge": merge_sort,
    "Heap": heap_sort,
    "Quick": quick_sort
}


# -----------------------------
# Calculate Sortedness
# -----------------------------
def calculate_sortedness(arr):

    if len(arr) <= 1:
        return 100.0

    count = 0

    for i in range(len(arr) - 1):
        if arr[i] <= arr[i + 1]:
            count += 1

    return (count / (len(arr) - 1)) * 100


# -----------------------------
# Feature Extraction
# -----------------------------
def extract_features(arr):

    size = len(arr)
    minimum = min(arr)
    maximum = max(arr)
    value_range = maximum - minimum

    duplicate_percentage = (
        1 - len(set(arr)) / len(arr)
    ) * 100

    sortedness = calculate_sortedness(arr)

    return {
        "size": size,
        "minimum": minimum,
        "maximum": maximum,
        "range": value_range,
        "duplicate_percentage": duplicate_percentage,
        "sortedness": sortedness
    }


# -----------------------------
# Dataset Generation
# -----------------------------
dataset = []

for _ in range(NUM_ARRAYS):

    arr = generate_random_array()

    features = extract_features(arr)

    for name, func in algorithms.items():

        row = features.copy()

        row["algorithm"] = name
        row["execution_time"] = benchmark(func, arr)

        dataset.append(row)


# -----------------------------
# Save Dataset
# -----------------------------
df = pd.DataFrame(dataset)

df.to_csv("sorting_dataset.csv", index=False)

print(df.head())

print("\nTotal Rows :", len(df))

print("\nAlgorithms Distribution:")
print(df["algorithm"].value_counts())