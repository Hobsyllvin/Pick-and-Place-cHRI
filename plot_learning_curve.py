import matplotlib.pyplot as plt
import numpy as np
import json
import os
from scipy.optimize import curve_fit
from scipy.stats import ttest_ind

'''
This code plots the combined scores from all participants, 
draws the learning curves for with and without haptic feedback groups and plots box plots for both of them
'''


# Normalizing the data to get rid of after-game time
def normalize_data(data):
    new_max = 120000
    filtered_data = [data for data in data if data['timestamp'] <= new_max]
    return filtered_data


# Processing json files
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
    Creates a scatter plot with the completion times and fits a logarithmic trendline.

    Parameters:
    - completion_times: A list of tuples containing (score, completion time).
    """
    # Unpack the completion times into separate lists
    scores_without, times_without = zip(*completion_times_without)
    scores_with, times_with = zip(*completion_times_with)

    t_stat, p_value = ttest_ind([time for scores_without, time in completion_times_without], [time for scores_with, time in completion_times_with])

    print(f"T-statistic: {t_stat}, P-value: {p_value}")

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
    plt.plot(np.unique(scores_without), log_func(np.unique(scores_without), *params_without),
             label='Log curve without weight',
             color='blue')
    plt.plot(np.unique(scores_with), log_func(np.unique(scores_with), *params_with), label='Log curve with weight',
             color='red')

    # Labeling the plot
    plt.title('Score vs. Completion Time')
    plt.xlabel('Score')
    plt.ylabel('Completion Time (s)')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'plots/learning_curve.png')  # Saving the plot to a file in the specified path
    plt.show()  # Show the plot

    # Box plots for both groups
    # Creating the box plot
    plt.figure(figsize=(8, 6))
    plt.boxplot([times_without, times_with], labels=['Without Weight', 'With Weight'])

    plt.title('Completion Times Box Plot')
    plt.ylabel('Completion Time (s)')
    plt.grid(True)
    plt.savefig(f'plots/box_plot.png')  # Saving the plot to a file in the specified path
    plt.show()


# Defining the directory of the json files
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

# Defining lists of timestamps and corresponding scores
with_weight_timestamps = []
with_weight_scores = []
without_weight_timestamps = []
without_weight_scores = []

# Iterating through data
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

# Calculating completion times
completion_times_without = load_and_process_data(without_weight_timestamps, without_weight_scores)
completion_times_with = load_and_process_data(with_weight_timestamps, with_weight_scores)

# Plotting the learning curve and the boxplots
plot_with_trendline(completion_times_without, completion_times_with)
