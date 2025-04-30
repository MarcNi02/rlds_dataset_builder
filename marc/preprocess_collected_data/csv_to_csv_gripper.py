import pandas as pd
import os
import torch
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image

# Path to the CSV file and dataset directory
config_csv = "output.csv"
output_csv = "output_g.csv"
dataset_dir = "/home/hk-project-sustainebot/ob0961/ws_data/hkfswork/ob0961-data/data/marc_collected_data/marc_datasets"

# Read the CSV file
df = pd.read_csv(config_csv)

# List to store True/False results for each row
gripper_state_consistency = []

# Loop through each row in the DataFrame
for idx, row in df.iterrows():
    task_path = os.path.join(dataset_dir, row['path'])

    # Load gripper state (PyTorch tensor)
    gripper_path = os.path.join(task_path, "Gello leader", "gripper_state.pt")
    if not os.path.exists(gripper_path):
        print(f"Gripper state file not found for: {gripper_path}")
        gripper_state_consistency.append(False)
        continue

    gripper_state = torch.load(gripper_path)

    # Load cropped image sequence
    start = int(row["cropped_traj_start"])
    end = int(row["cropped_traj_end"])

    # Check gripper state consistency in the cropped range
    cropped_gripper = gripper_state[start:end + 1]
    is_constant = torch.all(cropped_gripper.eq(cropped_gripper[0])).item()
    gripper_state_consistency.append(bool(is_constant))


# Add the results to the DataFrame and save
df["same_gripper_state"] = gripper_state_consistency
df.to_csv(output_csv, index=False)
print(f"Updated DataFrame saved to {output_csv}")
