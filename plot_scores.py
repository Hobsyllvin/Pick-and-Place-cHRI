import json
import os
from scipy.interpolate import UnivariateSpline
import numpy as np
import matplotlib.pyplot as plt

'''
Creating individual plots for the data obtained in the game and stored in the json files
'''


# Plotting scores for each player
def plot_score(timestamps, scores, plot_number):
    # Ensure timestamps and scores are numpy arrays for compatibility with UnivariateSpline
    timestamps_np = np.array(timestamps)
    scores_np = np.array(scores)
    # The 's' parameter controls the amount of smoothing. A small value of 's' means more smoothing.
    # If 's' is None, s=len(x) which is the default and uses a residual-based estimation.
    spline = UnivariateSpline(timestamps_np, scores_np, s=50)

    # Generate a dense range of timestamps for a smooth curve
    dense_timestamps = np.linspace(min(timestamps_np), max(timestamps_np), 1000)
    smooth_scores = spline(dense_timestamps)  # Evaluate the spline at the dense timestamps

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(dense_timestamps, smooth_scores, label='Smooth Curve')
    plt.title('Score vs Timestamp')
    plt.xlabel('Timestamp, s')
    plt.ylabel('Score')
    plt.grid(True)
    plt.legend()
    plt.savefig(f'plots/{plot_number}_score_vs_timestamp.png')  # Saving the plot to a file in the specified path
    plt.close()


# Normalizing the data to get rid of after-game time
def normalize_data(data):
    new_max = 120000
    filtered_data = [data for data in data if data['timestamp'] <= new_max]
    return filtered_data


# Plotting the derivative of picking up boxes for each player
def plot_derivative(timestamps, scores, plot_number):
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
            score_derivative[i] = score_derivative[i - 1]

    # Since the derivative is calculated between points, we'll use the midpoints of timestamps for plotting
    timestamps_midpoints = (timestamps_np[:-1] + timestamps_np[1:]) / 2

    # Plotting the derivative of score with respect to time vs time
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps_midpoints, score_derivative, 'r-', label='Smooth Curve')
    plt.title('Derivative of Score with Respect to Time vs Time')
    plt.xlabel('Time')
    plt.ylabel('Derivative of Score')
    plt.grid(True)
    plt.savefig(f'plots/{plot_number}_derivative_vs_timestamp.png')  # Saving the plot to a file in the specified path
    plt.close()


# Defining the directory of files
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

plot_number = 0

# Iterating over the entire dataset, plotting all of them
for data in all_data:
    plot_number += 1
    # Create arrays for forces, timestamps and scores
    filtered_data = normalize_data(data)
    timestamps = [item['timestamp'] for item in filtered_data]
    scores = [item['score'] for item in filtered_data]
    forces = [item['forces'] for item in filtered_data]

    plot_score(timestamps, scores, plot_number)
    plot_derivative(timestamps, scores, plot_number)
