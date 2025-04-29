import csv
import re


tasks = ["[banana_from_sink_to_right_stove]", 
         "[banana_from_tray_to_right_stove]",
         "[bottle_from_right_stove_to_sink]",
         "[pot_from_right_to_left_stove]",
         "[pot_from_sink_to_right_stove]"]

subtasks = ["[default_task]",
            "[let_go_of_pot_from_stove]", 
            "[move_to_left_stove_from_stove]", 
            "[align_above_right_stove_from_sink]"]

special_subtask = "[border_of_sink(4x_different_pos)]"

def build_range_pattern(n):
    if n < 1:
        raise ValueError("Must have at least one range")

    # Base pattern for a single "a - b"
    range_pattern = r'(?:\d{1,3}\s*-\s*\d{1,3}|invalid)'

    # First range (no comma before it)
    full_pattern = f'^{range_pattern}'

    # Add n-1 more ranges, each prefixed with a comma
    for _ in range(n - 1):
        full_pattern += r'\s*,\s*' + range_pattern

    # End of string
    full_pattern += '$'
    return full_pattern

def build_range_pattern_find(n):
    if n < 1:
        raise ValueError("Must have at least one range")

    patterns = [r'(?:(\d{1,3})\s*-\s*(\d{1,3})|invalid)']
    for _ in range(n - 1):
        patterns.append(r'\s*,\s*(?:(\d{1,3})\s*-\s*(\d{1,3})|invalid)')
    return '^' + ''.join(patterns) + '$'


def parse_txt_to_csv(input_path, output_path):
    with open(input_path, 'r') as file:
        lines = file.readlines()

    current_task = None
    current_subtasks = []
    current_episode = None
    current_pattern = None
    trajs = []
    path = [None, None]
    special_active = False
    output_rows = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        if not stripped:
            continue
        
        print("##########  Current line (stripped):", stripped)
        if stripped in tasks:
            current_task = stripped[1:-1]
            current_subtasks = []
            path[0] = stripped[1:-1]
            special_active = False
            continue
        
        if stripped in subtasks:
            current_subtasks = [stripped[1:-1]]
            path[1] = stripped[1:-1]
            # Create regex pattern for "a - b, c - d" format where a, b, c, d are numbers between 0-999
            current_pattern = build_range_pattern(2)
            special_active = False
            continue
        
        if stripped.startswith(special_subtask):
            current_subtasks = stripped.split(special_subtask + " ")[1].strip().split(',')
            current_subtasks = [s.strip() for s in current_subtasks]
            path[1] = special_subtask[1:-1]
            # Create regex pattern for "a - b, c - d" format where a, b, c, d are numbers between 0-999
            current_pattern = build_range_pattern(len(current_subtasks) + 1)
            special_active = True
            print("         special_active", special_active)
            continue
        
        if stripped.startswith('[others]'):
            current_subtasks = stripped.split("[others] ")[1].strip().split(',')
            current_subtasks = [s.strip() for s in current_subtasks]
            path[1] = "others"
            # Create regex pattern for "a - b, c - d" format where a, b, c, d are numbers between 0-999
            current_pattern = build_range_pattern(len(current_subtasks) + 1)
            continue
        
        if re.match(r'^\[\d{4}_\d{2}_\d{2}-\d{2}_\d{2}_\d{2}\].*$', stripped):
            current_episode = re.findall(r'^\[(\d{4}_\d{2}_\d{2}-\d{2}_\d{2}_\d{2})\].*$', stripped)
            assert len(current_episode) == 1, f"invalid format at line {i+1}: {stripped}"
            current_episode = current_episode[0]
            if special_active:
                after_episode_str = re.findall(r'^\[\d{4}_\d{2}_\d{2}-\d{2}_\d{2}_\d{2}\](.*)$', stripped)
                assert len(after_episode_str) == 1, f"invalid format at line {i+1}: {stripped}"
                after_episode_str = after_episode_str[0].strip()
            continue
        
        if stripped.startswith('[images]'):
            traj = stripped.split("[images] ")[1].strip()
            # Check if the trajectory matches the pattern
            # print("         traj curent pattern", current_pattern)
            if re.match(current_pattern, traj):     
                amount_ranges = len(current_subtasks) + 1                          
                find_regex = build_range_pattern_find(amount_ranges)
                pairs = re.findall(find_regex, traj)
                assert len(pairs) == 1, f"More than 1 possible regex solution found for line {stripped}"
                
                pairs = pairs[0]
                # print("         traj pattern length", amount_ranges)
                # print("         traj pairs length", 2 * amount_ranges)
                # print("         traj current subtasks", current_subtasks)
                # print("         traj find_regex", find_regex)
                # print("         traj traj", traj)         
                # print("         traj pairs", pairs)  
                trajs = []
                for j in range(0, 2 * amount_ranges, 2):
                    if pairs[j] != '':
                        trajs.append((int(pairs[j]), int(pairs[j + 1])))  
                    else:
                        trajs.append((None, None))    
                # print("         traj trajs", trajs) 
            else:
                raise ValueError(f"Invalid trajectory format at line {i+1}: {line.strip()}")
            
            for j in range(len(current_subtasks)):
                print("Appending to output rows")
                print("     j", j)
                # Append the task, subtask, episode, and trajectory to the output rows
                print("     current_task", current_task)
                if special_active and "xxx" in current_subtasks[j]:
                    print("     current_subtasks[j]", current_subtasks[j].replace("xxx", after_episode_str))
                else:
                    print("     current_subtasks[j]", current_subtasks[j])
                print("     current_episode", current_episode)
                print("     trajs", trajs[0][0], trajs[0][1], trajs[j+1][0], trajs[j+1][1])
                print("     path main task", path[0])
                print("     path subtask", path[1])
                print("     full path", "/".join([path[0], path[1], current_episode]))
                # print(current_task, current_subtasks[j], current_episode, trajs[0][0], trajs[0][1], trajs[j+1][0], trajs[j+1][1], "/".join([path[0], path[1], current_episode]))
                if trajs[j+1][0] != None and trajs[j+1][1] != None:
                    if special_active and "xxx" in current_subtasks[j]:
                        output_rows.append([current_task, current_subtasks[j].replace("xxx", after_episode_str), current_episode, trajs[0][0], trajs[0][1], trajs[j+1][0], trajs[j+1][1], "/".join([path[0], path[1], current_episode])])
                    else:
                        output_rows.append([current_task, current_subtasks[j], current_episode, trajs[0][0], trajs[0][1], trajs[j+1][0], trajs[j+1][1], "/".join([path[0], path[1], current_episode])])
            
            # Write output to CSV
            with open(output_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['task', 'subtask', 'episode', 'original_start', 'original_end', 'cropped_traj_start', 'cropped_traj_end', 'path'])
                writer.writerows(output_rows)
            continue

        raise ValueError(f"Unknown format found at line {i+1}: {stripped}")

# Run the parser
parse_txt_to_csv('crop_traj.txt', 'output.csv')
