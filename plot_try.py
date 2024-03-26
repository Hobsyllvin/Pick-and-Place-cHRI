import matplotlib.pyplot as plt
import numpy as np
import json
import os
from scipy.optimize import curve_fit


def normalize_data(data):
    new_max = 120000
    filtered_data = [data for data in data if data['timestamp'] <= new_max]
    return filtered_data


def load_and_process_data(weight_timestamps, weight_score):
    """
    Load data from a JSON file and process it to calculate completion times.

    Parameters:
    - file_path: Path to the JSON file.

    Returns:
    - A list of tuples, where each tuple contains (score, completion time).
    """

    # Variables to keep track of the last score and timestamp

    completion_times = []

    for i in range(len(weight_timestamps)):
        last_score = 0
        last_timestamp = 0
        for j in range(len(weight_timestamps[i])):
            current_score = weight_score[i][j]
            current_timestamp = weight_timestamps[i][j]

            # Check if the score has increased
            if current_score > last_score:
                # Calculate the completion time and update the list
                completion_time = (current_timestamp - last_timestamp) / 1000.0
                completion_times.append((current_score, completion_time))

                # Update last score and timestamp for the next iteration
                last_score = current_score
                last_timestamp = current_timestamp

    return completion_times


def plot_with_trendline(completion_times_without, completion_times_with):
    """
    Creates a scatter plot with the completion times and fits a trendline.

    Parameters:
    - completion_times: A list of tuples containing (score, completion time).
    """
    # Unpack the completion times into separate lists
    scores_without, times_without = zip(*completion_times_without)
    scores_with, times_with = zip(*completion_times_with)

    # Create a scatter plot
    plt.scatter(scores_with, times_with, label='Completion Time With Weight', color='red', s=10)
    plt.scatter(scores_without, times_without, label='Completion Time Without Weight', color='blue', s=10)

    # Logarithmic function to fit
    def log_func(x, a, b):
        return a + b * np.log(x)

    # Fit the logarithmic model
    params_without, covariance_without = curve_fit(log_func, scores_without, times_without)
    params_with, covariance_with = curve_fit(log_func, scores_with, times_with)

    # Plot the fitted curve
    plt.plot(np.unique(scores_without), log_func(np.unique(scores_without), *params_without), label='Log curve without weight',
             color='blue')
    plt.plot(np.unique(scores_with), log_func(np.unique(scores_with), *params_with), label='Log curve with weight',
             color='red')

    '''
    # Fit a trendline
    z = np.polyfit(scores, times, 5)
    z_weight = np.polyfit(scores, times, 5)
    p = np.poly1d(z)
    p_weight = np.poly1d(z_weight)
    plt.plot(np.unique(scores), p(np.unique(scores)), "b--", label='Trendline Without Weight')
    plt.plot(np.unique(scores_with), p_weight(np.unique(scores_with)), "r--", label='Trendline With Weight')
    '''

    # Labeling the plot
    plt.title('Score vs. Completion Time')
    plt.xlabel('Score')
    plt.ylabel('Completion Time (s)')
    plt.legend()
    plt.grid(True)

    # Show the plot
    plt.show()

    # Box plots
    # Creating the box plot
    plt.figure(figsize=(8, 6))
    plt.boxplot([times_without, times_with], labels=['Without Weight', 'With Weight'])

    plt.title('Completion Times Box Plot')
    plt.ylabel('Completion Time (s)')
    plt.grid(True)
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

with_weight_timestamps = []
with_weight_scores = []
without_weight_timestamps = []
without_weight_scores = []

for data in all_data:
    # Create arrays for forces, timestamps and scores
    filtered_data = normalize_data(data)
    timestamps = [item['timestamp'] for item in filtered_data]
    scores = [item['score'] for item in filtered_data]
    forces = [item['forces'] for item in filtered_data]
    with_weight_perception_values = [item['with_weight_perception'] for item in filtered_data]

    if with_weight_perception_values[0]:
        with_weight_timestamps.append(timestamps)
        with_weight_scores.append(scores)

    else:
        without_weight_timestamps.append(timestamps)
        without_weight_scores.append(scores)

completion_times_without = load_and_process_data(without_weight_timestamps, without_weight_scores)
completion_times_with = load_and_process_data(with_weight_timestamps, with_weight_scores)

plot_with_trendline(completion_times_without, completion_times_with)
