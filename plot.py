import json
import os
from scipy.interpolate import UnivariateSpline
import numpy as np
import matplotlib.pyplot as plt

def plot_score(timestamps, scores):
    # Plotting Score vs Timestamp
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, scores)
    plt.title('Score vs Timestamp')
    plt.xlabel('Timestamp, s')
    plt.ylabel('Score')
    plt.grid(True)
    plt.savefig('plots/score_vs_timestamp.png') # Saving the plot to a file in the specified path
    plt.show()

def normalize_time(timestamps):
    new_min = 0
    new_max = 120000

    # Min and max values from the original timestamps
    original_min = min(timestamps)
    original_max = max(timestamps)

    # Normalize the timestamps
    normalized_timestamps = [(x - original_min) * (new_max - new_min) / (original_max - original_min) + new_min for x in
                             timestamps]
    normalized_timestamps = [x / 1000 for x in normalized_timestamps] # in seconds
    return normalized_timestamps

def plot_derivative(timestamps, scores):
    # Convert lists to numpy arrays for easier mathematical operations
    timestamps_np = np.array(timestamps)
    scores_np = np.array(scores)

    # Calculate the differences between consecutive elements
    time_differences = np.diff(timestamps_np)
    score_differences = np.diff(scores_np)

    # Compute the derivative of score with respect to time (change in score over change in time)
    score_derivative = score_differences / time_differences

    # Eliminating zero-derivative terms
    for i in range(1, len(score_derivative)):
        if score_derivative[i] == 0:
            score_derivative[i] = score_derivative[i-1]


    # Since the derivative is calculated between points, we'll use the midpoints of timestamps for plotting
    timestamps_midpoints = (timestamps_np[:-1] + timestamps_np[1:]) / 2

    # Plotting the derivative of score with respect to time vs time
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps_midpoints, score_derivative, 'r-', label='Smooth Curve')
    plt.title('Derivative of Score with Respect to Time vs Time')
    plt.xlabel('Time')
    plt.ylabel('Derivative of Score')
    plt.grid(True)
    plt.savefig('plots/derivative_vs_timestamp.png')  # Saving the plot to a file in the specified path
    plt.show()

directory = 'logdata'
all_data = []

# Loop through each file in the specified directory
for filename in os.listdir(directory):
    # Check if the file is a JSON file
    if filename.endswith('.json'):
        # Construct the full file path
        file_path = os.path.join(directory, filename)
        # Open and read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)
            all_data.append(data)

for data in all_data:
    # Create arrays for forces, timestamps and scores
    timestamps = [item['timestamp'] for item in data]
    scores = [item['score'] for item in data]
    forces = [item['forces'] for item in data]
    with_weight_perception_values = [item['with_weight_perception'] for item in data]
    norm_time = normalize_time(timestamps) # in seconds
    plot_score(norm_time, scores)
    plot_derivative(norm_time, scores)

