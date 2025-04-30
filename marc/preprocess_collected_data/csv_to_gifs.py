import pandas as pd
import os
import torch
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image

# Path to the CSV file and dataset directory
config_csv = "output.csv"
dataset_dir = "/home/hk-project-sustainebot/ob0961/ws_data/hkfswork/ob0961-data/data/marc_collected_data/marc_datasets"

# Read the CSV file
df = pd.read_csv(config_csv)

# Loop through each row in the DataFrame
for idx, row in df.iterrows():
    task_path = os.path.join(dataset_dir, row['path'])
    
    # Set output file path
    gif_out_path = os.path.join(task_path, f"cropped_video_{idx}.gif")

    # Skip if gif already exists
    if os.path.exists(gif_out_path):
        print(f"Skipping {row['path']} - GIF already exists.")
        continue

    # Load gripper state (PyTorch tensor)
    gripper_path = os.path.join(task_path, "Gello leader", "gripper_state.pt")
    if not os.path.exists(gripper_path):
        print(f"Gripper state file not found for: {gripper_path}")
        continue

    gripper_state = torch.load(gripper_path)

    # Load cropped image sequence
    start = int(row["cropped_traj_start"])
    end = int(row["cropped_traj_end"])
    frame_dir = os.path.join(task_path, "images", "top_cam_orig")

    fig, ax = plt.subplots()
    ims = []

    for i in range(start, end + 1):
        img_path = os.path.join(frame_dir, f"{i}.png")
        if not os.path.exists(img_path):
            print(f"Image not found: {img_path}")
            continue

        img = Image.open(img_path)
        im = ax.imshow(img, animated=True)
        ax.set_axis_off()  # hide axes

        grip_info = gripper_state[i].tolist() if i < len(gripper_state) else 'N/A'
        text = ax.text(10, 20, f"Frame {i} - Gripper: {grip_info}", color='white', fontsize=10, backgroundcolor='black')
        ims.append([im, text])

    if not ims:
        print(f"No valid frames for {row['path']}")
        plt.close(fig)
        continue

    # Create and save animation as GIF
    ani = animation.ArtistAnimation(fig, ims, interval=100, blit=True, repeat_delay=1000)
    ani.save(gif_out_path, writer='pillow', fps=10)
    print(f"Saved GIF to: {gif_out_path}")

    plt.close(fig)
