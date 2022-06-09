import pandas as pd
import matplotlib.pyplot as mp
import sys
import warnings
warnings.filterwarnings("ignore")

def extract_vals(url='Next_Generation_Simulation__NGSIM__Vehicle_Trajectories_and_Supporting_Data.csv', location=None):
  print("Reading CSV with filename:", url)
  df = pd.read_csv(url)
  df = df.loc[df.Location == location]

  # Split data-frame into data for each vehicle
  # If a value for a vehicle was once 0 and becomes a number on the next frame, increment the inflow of that intersection (keep a new data-frame that maps frame to total number of cars that have entered the intersection until that frame (should have 1 row per frame, with one column for each intersection)
  # Can compute inflows for each over time by subtracting the current number from the one 10 frames before for per_second inflow rate
  
  df.Vehicle_ID = pd.to_numeric(df.Vehicle_ID)
  df = df.sort_values(['Vehicle_ID', 'Frame_ID'])
  UniqueVehicles = df.Vehicle_ID.unique()
  num_unique_ints = df.Int_ID.nunique()

  print("Splitting dataframe for " + location + " to a dataframe for each vehicle.")
  VehicleToDataFrameDict = {vehicle : pd.DataFrame() for vehicle in UniqueVehicles}
  for key in VehicleToDataFrameDict.keys():
    VehicleToDataFrameDict[key] = df[:][df.Vehicle_ID == key]

  num_to_dir = {1: 'EB', 2: 'NB', 3: 'WB', 4: 'SB'} # East, North, West, South Bound
  num_to_movement = {1: 'TH', 2: 'LT', 3: 'RT'} # Through, left turn, right turn

  # Create empty dataframe for flow data
  UniqueFrames = df.Frame_ID.unique()
  flow_df = pd.DataFrame(UniqueFrames, columns=['Frame_ID'])
  flow_df = flow_df.sort_values('Frame_ID')

  # Initialize dataframe with zeros
  print("Initializing empty flow dataframe")
  for int_id in range(1, num_unique_ints):
    column_name = 'Int_' + str(int_id) + '_Flow'
    flow_df[column_name] = 0
    column_name = 'Int_' + str(int_id) + '_Inflow_Vel_Sum'
    flow_df[column_name] = 0
    for dir in range(1, 5):
      column_name = 'Int_' + str(int_id) + '_' + num_to_dir[dir] + '_Flow'
      flow_df[column_name] = 0
      column_name = 'Int_' + str(int_id) + '_' + num_to_dir[dir] + '_Inflow_Vel_Sum'
      flow_df[column_name] = 0
      for movement in range(1, 4):
        column_name = 'Int_' + str(int_id) + '_' + num_to_dir[dir] + '_' + num_to_movement[movement] + '_Flow'
        flow_df[column_name] = 0
        column_name = 'Int_' + str(int_id) + '_' + num_to_dir[dir] + '_' + num_to_movement[movement] + '_Inflow_Vel_Sum'
        flow_df[column_name] = 0

  # We have dictionary mapping vehicle to all frames for that vehicle, along with empty flow data frame for each frame
  print("Computing Inflow")
  for vehicle_id, curr_df in VehicleToDataFrameDict.items():
    # For each row in the vehicle's df, if current row 
    frame_int_df = curr_df[['Frame_ID', 'Int_ID', 'Direction', 'Movement', 'v_Vel']]
    # make list of frame ids that are not 0
    # Loop through each of these frames and 
    frame_int_df['Int_ID_Changes'] = frame_int_df['Int_ID'].diff()
    
    # If a frame has a positive number for int_id_changes, increment flow_df value at ['frame_id'][intersection number flow]
    change_rows_df = frame_int_df.loc[frame_int_df['Int_ID_Changes'] > 0]
    
    for ind in change_rows_df.index:
      frame = change_rows_df['Frame_ID'][ind]
      intersection_entered = change_rows_df['Int_ID_Changes'][ind]
      direction = int(change_rows_df['Direction'][ind])
      movement = int(change_rows_df['Movement'][ind])
      vel = change_rows_df['v_Vel'][ind]
      
      # Increment Flow for specified intersection
      column_name = 'Int_' + str(int(intersection_entered)) + '_Flow'
      flow_df[column_name].loc[flow_df['Frame_ID'] == frame] += 1
      
      # Increment sum of velocities of all entering vehicles based on intersection
      column_name = 'Int_' + str(int(intersection_entered)) + '_Inflow_Vel_Sum'
      flow_df[column_name].loc[flow_df['Frame_ID'] == frame] += vel
      
      # Increment flow for specified intersection AND approach direction
      column_name = 'Int_' + str(int(intersection_entered)) + "_" + num_to_dir[direction] + "_Flow" 
      flow_df[column_name].loc[flow_df['Frame_ID'] == frame] += 1
      
      # Increment sum of velocities of all entering vehicles based on intersection AND approach direction
      column_name = 'Int_' + str(int(intersection_entered)) + "_" + num_to_dir[direction] + '_Inflow_Vel_Sum'
      flow_df[column_name].loc[flow_df['Frame_ID'] == frame] += vel
      
      # Increment flow for specified intersection, approach direction AND movement
      column_name = 'Int_' + str(int(intersection_entered)) + "_" + num_to_dir[direction] + "_" + num_to_movement[movement] + "_Flow" 
      flow_df[column_name].loc[flow_df['Frame_ID'] == frame] += 1
      
      # Increment sum of velocities of all entering vehicles based on intersection, approach direction AND movement
      column_name = 'Int_' + str(int(intersection_entered)) + "_" + num_to_dir[direction] + "_" + num_to_movement[movement] + '_Inflow_Vel_Sum'
      flow_df[column_name].loc[flow_df['Frame_ID'] == frame] += vel
      
  # Add all flows to get total number of vehicles that pass through an intersection until a given frame
  print("Computing Cumulative Inflow and Velocity Sums per frame (looking at last minute of data)")
  for column in flow_df:
    if column == 'Frame_ID': continue
    if column[-4:] == 'Flow':
      cumulative_column_name = column[:-4] + 'Cumulative_Flow'
      flow_df[cumulative_column_name] = flow_df[column].cumsum()
    if column[-14:] == 'Inflow_Vel_Sum':
      cumulative_column_name = column[:-14] + 'Cumulative_Vel_Sum' # Sum of velocities of all vehicles that entered by the current frame number
      flow_df[cumulative_column_name] = flow_df[column].cumsum()

  # Subtracting each element from the element 600 before gives us the number of cars that entered the intersection in the past minute (vehicles per minute approximately)
  for column in flow_df:
    if column[-15:] == 'Cumulative_Flow':
      inflow_rate_col_name = column[:-15] + 'Inflow_Rate'
      flow_df[inflow_rate_col_name] = flow_df[column].diff(600)
      
    if column[-18:] == 'Cumulative_Vel_Sum':
      col_name = column[:-18] + 'Vel_Sum_Past_Minute' # Sum of all velocities of vehicles that entered in the past minute
      flow_df[col_name] = flow_df[column].diff(600)

  # Plot Cumulative Flows against Flow Rates for a specific approach
  flow_df.plot(x="Frame_ID", y=["Int_1_NB_Cumulative_Flow", 'Int_1_NB_Inflow_Rate'])
  flow_df.plot(x="Frame_ID", y=["Int_2_NB_Cumulative_Flow", 'Int_2_NB_Inflow_Rate'])
  flow_df.plot(x="Frame_ID", y=["Int_3_NB_Cumulative_Flow", 'Int_3_NB_Inflow_Rate'])
  flow_df.plot(x="Frame_ID", y=["Int_4_NB_Cumulative_Flow", 'Int_4_NB_Inflow_Rate'])

  # Plot Cumulative Flows against Flow Rates for a specific approach and turn movement
  flow_df.plot(x="Frame_ID", y=["Int_1_NB_RT_Cumulative_Flow", 'Int_1_NB_RT_Inflow_Rate'])
  flow_df.plot(x="Frame_ID", y=["Int_2_NB_RT_Cumulative_Flow", 'Int_2_NB_RT_Inflow_Rate'])
  flow_df.plot(x="Frame_ID", y=["Int_3_NB_RT_Cumulative_Flow", 'Int_3_NB_RT_Inflow_Rate'])
  flow_df.plot(x="Frame_ID", y=["Int_4_NB_RT_Cumulative_Flow", 'Int_4_NB_RT_Inflow_Rate'])
  
  # Compute average speeds by dividing inflow rate by sum of velocities of entering vehicles
  print("Computing Average Speed for each combination of variables")
  for column in flow_df:
    if column[-15:] == 'Cumulative_Flow':
      inflow_rate_col_name = column[:-15] + 'Inflow_Rate'
      vel_sum_past_min_col_name = column[:-15] + 'Vel_Sum_Past_Minute'
      new_col = column[:-15] + 'Avg_Speed'
      flow_df[new_col] = flow_df[vel_sum_past_min_col_name] / flow_df[inflow_rate_col_name]
    

  # Plot Average Speeds of all four intersections
  flow_df.plot(x="Frame_ID", y=["Int_1_Avg_Speed"])
  flow_df.plot(x="Frame_ID", y=["Int_2_Avg_Speed"])
  flow_df.plot(x="Frame_ID", y=["Int_3_Avg_Speed"])
  flow_df.plot(x="Frame_ID", y=["Int_4_Avg_Speed"])
  mp.show()
  
  # export CSV with data that we want
  cols_to_keep = []
  for column in flow_df:
    if column[-11:] == 'Inflow_Rate' or column[-9:] == 'Avg_Speed':
      cols_to_keep.append(column)

  exp_csv = flow_df.loc[:, cols_to_keep].to_csv('./exports/' + location + '_flow_data.csv')
  
  return exp_csv

n = len(sys.argv)
if n == 1:
  print("Location not specified")
elif n == 2:
  extract_vals(location=sys.argv[1])
else:
  extract_vals(location=sys.argv[2], url=sys.argv[1])