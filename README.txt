# README

This repository contains the code and resources for a game that utilizes Haply for haptic feedback. Here's an overview of the content:

## Files

- `PA3.py`: The main Python file containing the game's logic and the Haply's control. To run and start the game, execute this file.

- `box.py`: Contains the definition of the "Box" class.

- `pendulum.py`: Contains the definition of the "Pendulum" class, simulating the dynamics of the pendulum.

- `gripper.py`: Contains the definition of the "Gripper" class.

- `plot_scores.py`: Contains functions used to plot the results for individual participants.

- `plot_learning_curve.py`: Contains functions used to plot learning curves for groups of participants with and without haptic feedback, as well as box plots.

## Folders

- `logdata`: Contains the recorded data of each completed game. Each experiment is saved in a JSON file with the score logged at each timestamp.

## Dependencies

- `pyshape.py`, `pyhapi.py`, and `pantograph.py`: Modules required by `PA3.py` to run the Haply device.

## Resources

- Images: `grip_closed.png`, `grip_open.png`, `handle.png`, `robot.png` are used for the game's visualization.

## Running the Game

To run the game, make sure you have Python installed on your system and execute the `PA3.py` file:

```bash
python PA3.py
