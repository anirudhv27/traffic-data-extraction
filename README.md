# Traffic Data Extraction

This script was used to extract the inflow rates and average speed of vehicles entering each intersection in a specified location. The inflow rates computed are also calculated for specific subsets of the dataset, sorted as follows:
- Intersection Number: 1-4 for Lankershim Boulevard, 1-5 for Peachtree Street
- Incoming Approach: Assumed north-bound, south-bound, east-bound, and west-bound approaches based on the dataset
- Turning movement: Left Turn, Right Turn, and Through (no turning)

Inflows are calculated on each intersection by first computing a cumulative property that counts the number of cars that enter the intersection by a certain frame, then computing a similar property that sums the velocity of all cars that enter an intersection by a certain frame. These properties are computed for intersection number only, intersection AND incoming approach, and for intersection AND incoming approach AND turning movement.

Since the NGSIM footage is 10 frames per second, the inflow rate at a certain point in time (in vehicles per minute) is estimated by subtracting the cumulative sum's value 600 frames prior from the cumulative sum's value at the time needed. 

Average speed is computed by finding the sum of all velocities in the last 600 frames using a similar approach to the inflow rate, then dividing the sum of velocities by the number of vehicles that enter an intersection (and satisfy the specified properties) within the past minute, which is the inflow rate.

## Data Format

The script can be used to extract the inflow rate and average speed from any CSV dataset structured with the following properties:
- `location`: Categorical variable that specifies the location where the data was collected (eg. Lankershim, Peachtree, etc.)
- `Vehicle_ID`: Numerical variable that identifies a single vehicle to track from frame to frame.
- `Frame_ID`: Numerical variable that identifies a single frame with several vehicles.
- `Int_ID`: Categorical variable that is set to `0` if the specified vehicle is not in an intersection at specified frame, set to the intersection's ID otherwise
- `Direction`: Categorical variable that represents the direction of the vehicle's velocity (1: 'EB', 2: 'NB', 3: 'WB', 4: 'SB')
- `Movement`: Categorical variable that represents the movement of a vehicle through specified intersection (1: 'TH', 2: 'LT', 3: 'RT')

The output is a CSV that stores both the computed inflow rate and average speed at the specified frame. 

Each column is labeled as `Int_(int_number)_(dir)_(movement)_Inflow_Rate` or `Int_(int_number)_(dir)_(movement)_Avg_Speed`. For example, the column labeled `Int_1_NB_RT_Inflow_Rate` represents the inflow rate of vehicles that take a right turn approaching intersection 1 northbound, and `Int_3_Avg_Speed` represents the average speed of all vehicles that enter intersection 3.

This format is informed by the Next Generation Simulation (NGSIM) Vehicle Trajectories and Supporting Data dataset from the US Department of Transportation (Source: https://data.transportation.gov/Automobiles/Next-Generation-Simulation-NGSIM-Vehicle-Trajector/8ect-6jqj)

## Using This Script
`python ngsim_data_analysis.py [file path to dataset] [location category in dataset]`

This script's dependencies are `pandas` and `matplotlib`.
