from flask import Flask, render_template, request
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

app = Flask(__name__)

# Load trained ML model
model = joblib.load("sorting_model.pkl")


# --------------------------------------------------
# Sorting algorithms
# --------------------------------------------------

algorithms_functions = {
    "Bubble": bubble_sort,
    "Selection": selection_sort,
    "Insertion": insertion_sort,
    "Merge": merge_sort,
    "Heap": heap_sort,
    "Quick": quick_sort
}

algorithms = list(algorithms_functions.keys())


# --------------------------------------------------
# Benchmarking
# --------------------------------------------------

def benchmark(sort_function, arr, runs=10):

    total = 0

    for _ in range(runs):

        start = time.perf_counter()

        sort_function(arr)

        total += time.perf_counter() - start

    return total / runs


# --------------------------------------------------
# Calculate sortedness
# --------------------------------------------------

def calculate_sortedness(arr):

    if len(arr) <= 1:
        return 100.0

    count = 0

    for i in range(len(arr) - 1):

        if arr[i] <= arr[i + 1]:
            count += 1

    return (count / (len(arr) - 1)) * 100


# --------------------------------------------------
# Home page
# --------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        # ------------------------------------------
        # Get input array
        # ------------------------------------------

        raw_input = request.form["array"]

        try:
            arr = [
                int(x)
                for x in raw_input.replace(",", " ").split()
            ]
        except ValueError:
            return render_template(
                "index.html",
                error="Please enter only whole numbers separated by spaces.",
                array=raw_input
            )

        if not arr:
            return render_template(
                "index.html",
                error="Please enter at least one number.",
                array=raw_input
            )

        # ------------------------------------------
        # Calculate input characteristics
        # ------------------------------------------

        size = len(arr)

        minimum = min(arr)

        maximum = max(arr)

        value_range = maximum - minimum

        duplicate_percentage = (
            1 - len(set(arr)) / len(arr)
        ) * 100

        sortedness = calculate_sortedness(arr)


        # ------------------------------------------
        # Features for ML model
        # ------------------------------------------

        base_features = {
            "size": size,
            "minimum": minimum,
            "maximum": maximum,
            "range": value_range,
            "duplicate_percentage": duplicate_percentage,
            "sortedness": sortedness
        }


        # ------------------------------------------
        # ML Predictions
        # ------------------------------------------

        predictions = {}

        for algo in algorithms:

            features = base_features.copy()

            features["algorithm"] = algo

            df = pd.DataFrame([features])

            predicted_time = model.predict(df)[0]

            predictions[algo] = float(predicted_time)


        # ------------------------------------------
        # Actual benchmark
        # ------------------------------------------

        actual_times = {}

        for algo, func in algorithms_functions.items():

            actual_times[algo] = benchmark(func, arr)


        # ------------------------------------------
        # Find best algorithms
        # ------------------------------------------

        best_predicted = min(
            predictions,
            key=predictions.get
        )

        best_actual = min(
            actual_times,
            key=actual_times.get
        )


        # ------------------------------------------
        # Prediction margin
        # ------------------------------------------

        sorted_predictions = sorted(
            predictions.items(),
            key=lambda x: x[1]
        )

        best_prediction = sorted_predictions[0][1]

        second_prediction = sorted_predictions[1][1]

        if second_prediction != 0:

            prediction_margin = (
                (second_prediction - best_prediction)
                / second_prediction
            ) * 100

        else:

            prediction_margin = 0


        # ------------------------------------------
        # Prepare visualization data
        # ------------------------------------------

        rows = []

        for algo in algorithms:

            rows.append({

                "algorithm": algo,

                "predicted": predictions[algo],

                "actual": actual_times[algo]

            })


        # ------------------------------------------
        # Input statistics
        # ------------------------------------------

        statistics = {

            "size": size,

            "minimum": minimum,

            "maximum": maximum,

            "range": value_range,

            "duplicates": round(
                duplicate_percentage,
                2
            ),

            "sortedness": round(
                sortedness,
                2
            )

        }


        # ------------------------------------------
        # Final result
        # ------------------------------------------

        result = {

            "best_predicted": best_predicted,

            "best_actual": best_actual,

            "prediction_margin": round(
                prediction_margin,
                2
            ),

            "sorted_array":
                algorithms_functions[
                    best_predicted
                ](arr),

            "rows": rows,

            "statistics": statistics,

            "input_array": arr

        }


        return render_template(

            "index.html",

            result=result,

            array=" ".join(
                map(str, arr)
            )

        )


    # ----------------------------------------------
    # GET request
    # ----------------------------------------------

    return render_template("index.html")


# --------------------------------------------------
# Run application
# --------------------------------------------------

if __name__ == "__main__":

    app.run(debug=True)