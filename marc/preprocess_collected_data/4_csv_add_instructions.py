import pandas as pd

# Path to the CSV file and dataset directory
config_csv = "crop_data/output_g.csv"
dataset_dir = "/DATA/nikolaus/marc_datasets_modified_gripper"


# Read the CSV file
df = pd.read_csv(config_csv)


# Ensure the columns exist
if 'task' in df.columns and 'subtask' in df.columns:
    unique_combinations = df[['task', 'subtask']].drop_duplicates()
    print(unique_combinations.to_string(index=False))
else:
    raise ValueError("The CSV must contain 'task' and 'subtask' columns.")
    
#                            task                                          subtask
# banana_from_sink_to_right_stove                                     default_task
# banana_from_sink_to_right_stove                                     grasp_banana
# banana_from_sink_to_right_stove           position_with_banana_above_right_stove
# banana_from_sink_to_right_stove                                 let_go_of_banana
# banana_from_tray_to_right_stove                                     default_task
# banana_from_tray_to_right_stove                                     grasp_banana
# banana_from_tray_to_right_stove                              move_up_with_banana
# banana_from_tray_to_right_stove position_with_banana_above_right_stove_from_tray
# banana_from_tray_to_right_stove                       let_go_of_banana_from_tray
# bottle_from_right_stove_to_sink                                     default_task
#    pot_from_right_to_left_stove                                     default_task
#    pot_from_right_to_left_stove                         let_go_of_pot_from_stove
#    pot_from_right_to_left_stove                    move_to_left_stove_from_stove
#    pot_from_sink_to_right_stove                align_above_right_stove_from_sink
#    pot_from_sink_to_right_stove             grasp_pot_from_top_left_edge_in_sink
#    pot_from_sink_to_right_stove                         go_up_with_pot_from_sink
#    pot_from_sink_to_right_stove               let_go_of_pot_from_stove_from_sink
#    pot_from_sink_to_right_stove             grasp_pot_from_bot_left_edge_in_sink
#    pot_from_sink_to_right_stove            grasp_pot_from_top_right_edge_in_sink
#    pot_from_sink_to_right_stove            grasp_pot_from_bot_right_edge_in_sink
#    pot_from_sink_to_right_stove                                     default_task

instruction_dict = {
    # === From Sink ===
    ("banana_from_sink_to_right_stove", "default_task"): {
        "instruction_1": "Move the banana from sink to right stove.",
        "instruction_2": "Transfer the banana from sink to the right stove.",
        "instruction_3": "Relocate the banana from sink to the right stove."
    }, #
    ("banana_from_sink_to_right_stove", "grasp_banana"): {
        "instruction_1": "Reach into the sink and grasp the banana.",
        "instruction_2": "Close the gripper around the banana in the sink basin.",
        "instruction_3": "Firmly pick up the banana from the sink."
    }, #
    ("banana_from_sink_to_right_stove", "position_with_banana_above_right_stove"): {
        "instruction_1": "With the banana grasped from sink, lift and move it above the right stove.",
        "instruction_2": "Holding the banana in the gripper from sink, align it over the right stove burner.",
        "instruction_3": "Holding the banana from sink, position the banana above the stovetop surface."
    }, # 
    ("banana_from_sink_to_right_stove", "let_go_of_banana"): {
        "instruction_1": "Release the banana onto the right stove.",
        "instruction_2": "Let go of the banana above the right stove.",
        "instruction_3": "Open the gripper to drop the banana onto the right stove."
    }, #

    # === From Tray ===
    ("banana_from_tray_to_right_stove", "default_task"): {
        "instruction_1": "Move the banana from tray to right stove.",
        "instruction_2": "Transfer the banana from tray to the right stove.",
        "instruction_3": "Relocate the banana from tray to the right stove."
    }, # 
    ("banana_from_tray_to_right_stove", "grasp_banana"): {
        "instruction_1": "Grasp the banana from the tray.",
        "instruction_2": "Gently grasp the banana from the tray.",
        "instruction_3": "Grip the banana on the tray firmly."
    }, #
    ("banana_from_tray_to_right_stove", "move_up_with_banana"): {
        "instruction_1": "With the banana already grasped, lift it straight up off the tray.",
        "instruction_2": "Holding the banana in the gripper, raise it vertically from the tray.",
        "instruction_3": "Elevate the grasped banana upward from the tray."
    }, # 
    ("banana_from_tray_to_right_stove", "position_with_banana_above_right_stove_from_tray"): {
        "instruction_1": "While holding the banana from tray, move it above the right stove burner.",
        "instruction_2": "With the gripped banana from tray, align it over the right stove.",
        "instruction_3": "Keep a firm hold on the banana from tray and position the banana above the right stove."
    }, # 
    ("banana_from_tray_to_right_stove", "let_go_of_banana_from_tray"): {
        "instruction_1": "Release the banana onto the right stove.",
        "instruction_2": "Let go of the banana above the right stove.",
        "instruction_3": "Open the gripper to drop the banana onto the right stove."
    }, # 

    # === Bottle ===
    ("bottle_from_right_stove_to_sink", "default_task"): {
        "instruction_1": "Move the bottle from stove to sink.",
        "instruction_2": "Transfer the bottle to the sink.",
        "instruction_3": "Send the bottle to the sink."
    }, #

    # === Pot: Right → Left Stove ===
    ("pot_from_right_to_left_stove", "default_task"): {
        "instruction_1": "Move the pot from right to left stove.",
        "instruction_2": "Transfer the pot to the left stove.",
        "instruction_3": "Send the pot to the left stove."
    }, # 
    ("pot_from_right_to_left_stove", "move_to_left_stove_from_stove"): {
        "instruction_1": "Carry the pot across from the right stove to the left stove.",
        "instruction_2": "With the pot in your gripper, move it from the right burner to the left burner.",
        "instruction_3": "Transport the pot from the right stove to the left stove."
    }, # 
    ("pot_from_right_to_left_stove", "let_go_of_pot_from_stove"): {
        "instruction_1": "Release the pot onto the left stove burner.",
        "instruction_2": "Open the gripper to set the pot down on the left stove.",
        "instruction_3": "Let go of the pot gently so it rests securely on the left burner."
    }, # 

    # === Pot: Sink → Right Stove ===
    ("pot_from_sink_to_right_stove", "default_task"): {
        "instruction_1": "Move the pot from sink to right stove.",
        "instruction_2": "Transfer the pot to the right stove from sink.",
        "instruction_3": "Relocate the pot from the sink to the right stove."
    }, # 
    ("pot_from_sink_to_right_stove", "grasp_pot_from_top_left_edge_in_sink"): {
        "instruction_1": "Grasp the pot from the top-left corner in the sink",
        "instruction_2": "Securely grip the pot at the top-left corner within the sink.",
        "instruction_3": "Close the gripper around the pot from the top-left corner in the sink."
    }, #
    ("pot_from_sink_to_right_stove", "go_up_with_pot_from_sink"): {
        "instruction_1": "With the pot already grasped, lift it up out of the sink.",
        "instruction_2": "Holding the pot in the gripper, raise it vertically from the sink basin.",
        "instruction_3": "Elevate the pot upward while maintaining your grip."
    }, # 
    ("pot_from_sink_to_right_stove", "align_above_right_stove_from_sink"): {
        "instruction_1": "While holding the pot, move it above the right stove burner.",
        "instruction_2": "With the gripped pot, align it directly over the right stove.",
        "instruction_3": "Keep a firm hold and position the pot above the right stovetop."
    }, # 
    ("pot_from_sink_to_right_stove", "let_go_of_pot_from_stove_from_sink"): {
        "instruction_1": "Release the pot onto the stove burner.",
        "instruction_2": "Let go of the pot over the right stove.",
        "instruction_3": "Gently drop the pot onto the burner."
    }, # 
    ("pot_from_sink_to_right_stove", "grasp_pot_from_bot_left_edge_in_sink"): {
        "instruction_1": "Grasp the pot from the bottom-left corner in the sink",
        "instruction_2": "Securely grip the pot at the bottom-left corner within the sink.",
        "instruction_3": "Close the gripper around the pot from the bottom-left corner in the sink."
    }, # 
    ("pot_from_sink_to_right_stove", "grasp_pot_from_top_right_edge_in_sink"): {
        "instruction_1": "Grasp the pot from the top-right corner in the sink",
        "instruction_2": "Securely grip the pot at the top-right corner within the sink.",
        "instruction_3": "Close the gripper around the pot from the top-right corner in the sink."
    }, # 
    ("pot_from_sink_to_right_stove", "grasp_pot_from_bot_right_edge_in_sink"): {
        "instruction_1": "Grasp the pot from the bottom-right corner in the sink",
        "instruction_2": "Securely grip the pot at the bottom-right corner within the sink.",
        "instruction_3": "Close the gripper around the pot from the bottom-right corner in the sink."
    }, # 
}


for row in unique_combinations.itertuples(index=False):
    task = row.task
    subtask = row.subtask
    instructions = instruction_dict.get((task, subtask), None)
    print(f"instructions: {instructions}")
    
    if instructions:
        df.loc[(df['task'] == task) & (df['subtask'] == subtask), 'instructions_1'] = instructions['instruction_1']
        df.loc[(df['task'] == task) & (df['subtask'] == subtask), 'instructions_2'] = instructions['instruction_2']
        df.loc[(df['task'] == task) & (df['subtask'] == subtask), 'instructions_3'] = instructions['instruction_3']
    else:
        raise ValueError(f"No instructions found for Task: {task}, Subtask: {subtask}")
    
df.to_csv("crop_data/output_gi.csv", index=False)