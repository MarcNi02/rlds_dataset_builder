import pandas as pd
import os
import torch

from collections import Counter

# Path to the CSV file and dataset directory
config_csv = "output_g.csv"
dataset_dir = "/DATA/nikolaus/marc_datasets_modified_gripper"

consistent_gripper_tasks = [
    ("banana_from_tray_to_right_stove", "position_with_banana_above_right_stove_from_tray"),
    ("banana_from_tray_to_right_stove", "move_up_with_banana"),
    ("banana_from_sink_to_right_stove", "position_with_banana_above_right_stove"),
    ("pot_from_right_to_left_stove", "move_to_left_stove_from_stove"),
    ("pot_from_sink_to_right_stove", "go_up_with_pot_from_sink"),
    ("pot_from_sink_to_right_stove", "align_above_right_stove_from_sink"),
]

# Read the CSV file
df = pd.read_csv(config_csv)

count_inconsistent = 0
count_modified_inconsistent = 0

count_consistent = 0
count_modified_consistent = 0

# Loop through each row in the DataFrame
for idx, row in df.iterrows():
    task_path = os.path.join(dataset_dir, row['path'])

    # Load gripper state (PyTorch tensor)
    gripper_path = os.path.join(task_path, "Gello leader", "gripper_state.pt")
    assert os.path.exists(gripper_path), f"Gripper state file not found for: {gripper_path}"

    gripper_state = torch.load(gripper_path)

    # Load cropped image sequence
    start = int(row["cropped_traj_start"])
    end = int(row["cropped_traj_end"])
    same_gripper_state = bool(row["same_gripper_state"])
    
    # Check if the task is in the consistent_gripper_tasks list
    task_name = (row['task'], row['subtask'])
    
    print(70 * "#")
    print(f"Task: {task_name}, Episode: {row['episode']}")
    
    if task_name in consistent_gripper_tasks:
        print("     Consistent gripper state expected.")
        count_consistent += 1
        
        if not same_gripper_state:
            count_modified_consistent += 1
            
            # If the task is in the list, we expect the gripper state to be constant
            cropped_gripper = gripper_state[start:end + 1].int()
            value_counts = Counter(cropped_gripper.tolist())
            most_common_value = max(value_counts, key=value_counts.get)
            print(f"     Most Common Gripper State: {most_common_value}, Proportion: {value_counts[most_common_value]} / {len(cropped_gripper)}")
            
            # ask user 
            user_input = input("     Replace gripper state with majority value? [y/n]: ").strip().lower()
            if user_input == 'y':
                print("     Modifying gripper state...")
                gripper_state[start:end + 1] = float(most_common_value)
                output_path = os.path.join(task_path, "Gello leader", f"gripper_state-{row['subtask']}.pt")
                torch.save(gripper_state.double(), output_path)
                print(f"     Saved modified gripper state to: {output_path}")
            else:
                print("     No modification performed.")
    else:
        print("     Inconsistent gripper state expected.")
        count_inconsistent += 1
        # If the task is not in the list, we check if the gripper state is consistent
        if same_gripper_state:
            count_modified_inconsistent += 1
            print(f"      Expected inconsistent gripper state for {task_name} but found consistent.")
             # If the task is in the list, we expect the gripper state to be constant
            cropped_gripper = gripper_state[start:end + 1].int()
            value_counts = Counter(cropped_gripper.tolist())
            most_common_value = max(value_counts, key=value_counts.get)
            print(f"     Most Common Gripper State: {most_common_value}, Proportion: {value_counts[most_common_value]} / {len(cropped_gripper)}")
            
            # ask user 
            user_input = input("     Replace first gripper state with different value? [y/n]: ").strip().lower()
            if user_input == 'y':
                print("     Modifying gripper state...")
                gripper_state[start] = float(-most_common_value)
                output_path = os.path.join(task_path, "Gello leader", f"gripper_state-{row['subtask']}.pt")
                torch.save(gripper_state.double(), output_path)
                print(f"     Modified gripper state: {gripper_state[start: end + 1]}")
                print(f"     Saved modified gripper state to: {output_path}")
            else:
                print("     No modification performed.")
        
print(70 * "#")
print(f"Total inconsistent tasks: {count_inconsistent}")
print(f"Total modified tasks: {count_modified_inconsistent}")
print(70 * "#")
print(f"Total consistent tasks: {count_consistent}")
print(f"Total modified tasks: {count_modified_consistent}")

# ######################################################################
# Total inconsistent tasks: 234
# Total modified tasks: 22
# ######################################################################
# Total consistent tasks: 122
# Total modified tasks: 24