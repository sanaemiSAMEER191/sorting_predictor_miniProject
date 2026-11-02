import joblib
import pandas as pd
import time
from sorting_algorithms import (
    bubble_sort,
    selection_sort,
    insertion_sort,
    merge_sort,
    heap_sort,
    quick_sort
)
# -----------------------------
# Load Model
# -----------------------------
model = joblib.load("sorting_model.pkl")

#ACTUAL
algorithms_functions = {
    "Bubble": bubble_sort,
    "Selection": selection_sort,
    "Insertion": insertion_sort,
    "Merge": merge_sort,
    "Heap": heap_sort,
    "Quick": quick_sort
}
def benchmark(sort_function, arr):
    start = time.perf_counter()
    sort_function(arr)
    end = time.perf_counter()

    return end - start

def calculate_sortedness(arr):
    if len(arr) <= 1:
        return 100.0

    count = 0

    for i in range(len(arr) - 1):
        if arr[i] <= arr[i + 1]:
            count += 1

    return (count / (len(arr) - 1)) * 100
# -----------------------------
# User Input
# -----------------------------
arr = list(map(int, input("Enter array elements separated by spaces:\n").split()))

# -----------------------------
# Feature Extraction
# -----------------------------
size = len(arr)
minimum = min(arr)
maximum = max(arr)
value_range = maximum - minimum
duplicate_percentage = (1 - len(set(arr)) / len(arr)) * 100
sortedness = calculate_sortedness(arr)

# -----------------------------
# Algorithms
# -----------------------------
algorithms = [
    "Bubble",
    "Selection",
    "Insertion",
    "Merge",
    "Heap",
    "Quick"
]

predictions = {}

# -----------------------------
# Predict
# -----------------------------
for algo in algorithms:

    test = pd.DataFrame([{
        "size": size,
        "minimum": minimum,
        "maximum": maximum,
        "range": value_range,
        "duplicate_percentage": duplicate_percentage,
        "algorithm": algo,
        "sortedness": sortedness,
    }])

    predicted_time = model.predict(test)[0]

    predictions[algo] = predicted_time


# -----------------------------
# Actual Benchmark
# -----------------------------
print("\nActual Execution Times\n")

actual_times = {}

for algo, func in algorithms_functions.items():

    actual = benchmark(func, arr)

    actual_times[algo] = actual

    print(f"{algo:<12} : {actual:.8f} sec")

# -----------------------------
# Best Algorithms
# -----------------------------
best_predicted = min(predictions, key=predictions.get)
sorted_predictions = sorted(predictions.items(), key=lambda x: x[1])

best_time = sorted_predictions[0][1]
second_best_time = sorted_predictions[1][1]

confidence = (
    (second_best_time - best_time)
    / second_best_time
) * 100
best_actual = min(actual_times, key=actual_times.get)

print("\nML Recommendation :", best_predicted)
print(f"Confidence         : {confidence:.2f}%")
print("Actual Fastest    :", best_actual)
sorted_array = algorithms_functions[best_actual](arr)
print("\nSorted Array")

print(sorted_array)
#[-399, -12, 2, 7, 11, 13, 15, 123] : one of those working cases in viva