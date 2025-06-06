import os
import cv2
from typing import Iterator, Tuple, Any
from scipy.spatial.transform import Rotation

import glob
import numpy as np
import natsort
import tensorflow as tf
import tensorflow_datasets as tfds
import tensorflow_hub as hub
from tqdm import tqdm
import torch
from pathlib import Path

tf.config.set_visible_devices([], "GPU")
data_path = "/home/nikolaus/my_data/new_kitchen_data"


exclude_episodes = set([
                    '2025_05_19-14_58_56', '2025_05_19-15_01_31', '2025_05_19-15_03_33', '2025_05_19-15_04_16', '2025_05_19-15_06_16',
                    '2025_05_19-15_19_42', '2025_05_19-15_23_18', '2025_05_19-15_23_54', '2025_05_19-15_24_37', '2025_05_19-15_25_16',
                    '2025_05_19-15_26_22', '2025_05_19-15_54_27', '2025_05_19-15_55_02', '2025_05_19-15_56_10', '2025_05_19-15_56_45',
                    '2025_05_19-15_57_21', '2025_05_19-15_58_01', '2025_05_19-15_59_11', '2025_05_19-15_59_43', '2025_05_19-16_00_21',
                    '2025_05_19-16_01_35', '2025_05_19-16_03_02', '2025_05_19-16_04_15', '2025_05_19-16_05_21', '2025_05_19-16_06_46', # banana fro sink to right stove
                    '2025_05_20-18_10_34', '2025_05_20-18_11_38', '2025_05_20-18_13_19', '2025_05_20-18_14_30', '2025_05_20-18_15_45',
                    '2025_05_20-18_16_24', '2025_05_20-18_17_44', '2025_05_20-18_18_26', '2025_05_20-18_19_45', '2025_05_20-18_21_46', # pot from right to left stove
                    '2025_05_19-14_16_27', '2025_05_19-14_17_44', '2025_05_19-14_19_39', '2025_05_19-14_24_53', '2025_05_19-14_25_30',
                    '2025_05_19-14_27_32', '2025_05_19-14_28_11', '2025_05_19-14_30_16', '2025_05_19-14_30_57', '2025_05_19-14_34_30',
                    '2025_05_19-14_35_07', '2025_05_19-14_35_44', '2025_05_19-14_36_23', '2025_05_19-14_38_15', '2025_05_19-14_38_53',
                    '2025_05_19-14_43_01', '2025_05_19-14_44_28', '2025_05_19-14_45_11', '2025_05_19-14_46_35', '2025_05_19-14_48_23',
                    '2025_05_19-14_48_58', '2025_05_19-14_50_51', '2025_05_19-14_51_29' # pot from sink to right stove
                    ]) 



instruction_set = {'pot_from_sink_to_right_stove': ['Put the pot from the sink to the right stove.', 
                                                    'Move the pot from the sink to the right stove.', 
                                                    'Take the pot from the sink to the right stove.'],
                   'pot_from_sink_to_right_stove_with_tray': ['Put the pot from the sink to the right stove.',
                                                    'Move the pot from the sink to the right stove.',
                                                    'Take the pot from the sink to the right stove.'],
                    'banana_from_sink_to_right_stove': ['Put the banana from the sink to the right stove.',
                                                        'Move the banana from the sink to the right stove.',
                                                        'Take the banana from the sink to the right stove.'],
                    'banana_sink_with_tray_open': ['Put the banana from the sink to the right stove.',
                                                        'Move the banana from the sink to the right stove.',
                                                        'Take the banana from the sink to the right stove.'],
                    'banana_from_tray_to_right_stove': ['Put the banana from the tray to the right stove.',
                                                        'Move the banana from the tray to the right stove.',
                                                        'Take the banana from the tray to the right stove.'],   
                    'pot_from_right_to_left_stove_with_tray': ['Place the flower near the fire gently, its fine.',
                                                                'Keep the flower fine and away from the fire.',
                                                                'Move the flower before the fire ruins its fine look.'],
                    'pot_from_right_to_left_stove': ['Place the flower near the fire gently, its fine.',
                                                    'Keep the flower fine and away from the fire.',
                                                    'Move the flower before the fire ruins its fine look.'],
                    'above_sink_banana': ['Position above the banana in the sink.',
                                        'Move above the banana in the sink.',
                                        'Go above the banana in the sink.'],
                    'infront_stove_banana_tray': ['Position in front of the stove.',
                                                'Move in front of the stove.',
                                                'Go in front of the stove.'],
                    'above_right_stove': ['Position above the right stove.',
                                        'Move above the right stove.',
                                        'Go above the right stove.'],
                    'above_sink_pot': ['Position above the pot in the sink.',
                                        'Move above the pot in the sink.',
                                        'Go above the pot in the sink.'],
                    'left_rim_pot_sink': ['Put the pot on its left rim from the sink to the right stove.',
                                        'Move the pot on its left rim from the sink to the right stove.',
                                        'Take the pot on its left rim from the sink to the right stove.'],
                    'right_rim_pot_sink': ['Put the pot on its right rim from the sink to the right stove.',
                                        'Move the pot on its right rim from the sink to the right stove.',
                                        'Take the pot on its right rim from the sink to the right stove.'],
                   }

class KitIrlRealKitchenLangMarcNewKitchenWithCorrectionImposter(tfds.core.GeneratorBasedBuilder):
    """DatasetBuilder for example dataset."""

    VERSION = tfds.core.Version('1.0.0')
    RELEASE_NOTES = {
      '1.0.0': 'Initial release.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self._embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/5")

    def _info(self) -> tfds.core.DatasetInfo:
        """Dataset metadata (homepage, citation,...)."""
        return self.dataset_info_from_configs(
            features=tfds.features.FeaturesDict({
                'steps': tfds.features.Dataset({
                    'observation': tfds.features.FeaturesDict({
                        'image_top': tfds.features.Image(
                            shape=(224, 224, 3),
                            dtype=np.uint8,
                            encoding_format='jpeg',
                            doc='Main Top camera RGB observation.',
                        ),
                        'image_side': tfds.features.Image(
                            shape=(224, 224, 3),
                            dtype=np.uint8,
                            encoding_format='jpeg',
                            doc='Side camera RGB observation.',
                        ),
                        'joint_state': tfds.features.Tensor(
                            shape=(7,),
                            dtype=np.float64,
                            doc='Robot joint state. Consists of [7x joint states]',
                        ),
                        'joint_state_velocity': tfds.features.Tensor(
                            shape=(7,),
                            dtype=np.float64,
                            doc='Robot joint velocities. Consists of [7x joint velocities]',
                        ),
                        'end_effector_pos': tfds.features.Tensor(
                            shape=(3,),
                            dtype=np.float64,
                            doc='Current End Effector position in Cartesian space',
                        ),
                        'end_effector_ori': tfds.features.Tensor(
                            shape=(3,),
                            dtype=np.float64,
                            doc='Current End Effector orientation in Cartesian space as Euler (xyz)',
                        ),
                        'end_effector_ori_quat': tfds.features.Tensor(
                            shape=(4,),
                            dtype=np.float64,
                            doc='Current End Effector orientation in Cartesian space as Quaternion',
                        )
                    }),
                    'action': tfds.features.Tensor(
                        shape=(7,),
                        dtype=np.float64,
                        doc='Delta robot action, consists of [3x delta_end_effector_pos, '
                            '3x delta_end_effector_ori (euler: roll, pitch, yaw), 1x des_gripper_width].',
                    ),
                    'action_abs': tfds.features.Tensor(
                        shape=(7,),
                        dtype=np.float64,
                        doc='Absolute robot action, consists of [3x end_effector_pos, '
                            '3x end_effector_ori (euler: roll, pitch, yaw), 1x des_gripper_width].',
                    ),
                    'action_joint_state': tfds.features.Tensor(
                        shape=(7,),
                        dtype=np.float64,
                        doc='Robot action in joint space, consists of [7x joint states]',
                    ),
                    'action_joint_vel': tfds.features.Tensor(
                        shape=(7,),
                        dtype=np.float64,
                        doc='Robot action in joint space, consists of [7x joint velocities]',
                    ),
                    'delta_des_joint_state': tfds.features.Tensor(
                        shape=(7,),
                        dtype=np.float64,
                        doc='Delta robot action in joint space, consists of [7x joint states]',
                    ),
                    'action_gripper_width': tfds.features.Scalar(
                        dtype=np.float64,
                        doc='Desired gripper width, consists of [1x gripper width] in range [0, 1]',
                    ),
                    'discount': tfds.features.Scalar(
                        dtype=np.float64,
                        doc='Discount if provided, default to 1.'
                    ),
                    'reward': tfds.features.Scalar(
                        dtype=np.float64,
                        doc='Reward if provided, 1 on final step for demos.'
                    ),
                    'is_first': tfds.features.Scalar(
                        dtype=np.bool_,
                        doc='True on first step of the episode.'
                    ),
                    'is_last': tfds.features.Scalar(
                        dtype=np.bool_,
                        doc='True on last step of the episode.'
                    ),
                    'is_terminal': tfds.features.Scalar(
                        dtype=np.bool_,
                        doc='True on last step of the episode if it is a terminal step, True for demos.'
                    ),
                    'language_instruction': tfds.features.Text(
                        doc='Language Instruction.'
                    ),
                    'language_instruction_2': tfds.features.Text(
                        doc='Language Instruction.'
                    ),
                    'language_instruction_3': tfds.features.Text(
                        doc='Language Instruction.'
                    ),
                }),
                'episode_metadata': tfds.features.FeaturesDict({
                    'file_path': tfds.features.Text(
                        doc='Path to the original data file.',
                    ),
                    'traj_length': tfds.features.Scalar(
                        dtype=np.float64,
                        doc='Number of samples in trajectorie'
                    )
                }),
            }))

    def _split_generators(self, dl_manager: tfds.download.DownloadManager):
        """Define data splits."""
        return {
            'train': self._generate_examples(path=data_path),
            # 'val': self._generate_examples(path='data/val/episode_*.npy'),
        }

    def _generate_examples(self, path) -> Iterator[Tuple[str, Any]]:
        """Generator of examples for each split."""

        # create list of all examples
        raw_dirs = []
        get_trajectorie_paths_recursive(data_path, raw_dirs)
        filtered_dirs = [
            path for path in raw_dirs
            if not any(ep in path for ep in exclude_episodes)
        ]
        print("# of trajectories:", len(filtered_dirs))

        for sample in filtered_dirs:
            yield _parse_example(sample)


def _parse_example(episode_path, embed=None):
    print(f"Parsing {episode_path}")

    data = {}
    leader_path = os.path.join(episode_path, 'Gello leader/*.pt')
    follower_path = os.path.join(episode_path, 'Panda 102 follower/*.pt')

    # 'gripper_state.pt' 'ee_vel.pt' 'joint_vel.pt' 'ee_pos.pt' 'joint_pos.pt' (franka panda robot)
    for file in glob.glob(follower_path):
        name = Path(file).stem
        data.update({name : torch.load(file)})
    # 'gripper_state.pt' 'joint_pos.pt' (gello)
    for file in glob.glob(leader_path):
        name = 'des_' + Path(file).stem
        data.update({name : torch.load(file)})
    # all data entry should have the same traj length (primary length of tensor)
    trajectory_length = data[list(data.keys())[0]].size()[0]


    top_cam_path = os.path.join(episode_path, 'images/top_cam_crop')
    side_cam_path = os.path.join(episode_path, 'images/side_cam_crop')
    top_cam_vector = create_img_vector(top_cam_path, trajectory_length)
    side_cam_vector = create_img_vector(side_cam_path, trajectory_length)

    data.update({
                'image_top': top_cam_vector, 
                'image_side': side_cam_vector
                })

    episode = []

    delta_ee_pos = np.zeros((data["ee_pos"].size()[0], 7))
    delta_des_joint_state = torch.zeros_like(data["des_joint_pos"])

    for i in range(trajectory_length):

        # compute deltas: delta_ee_pos (pos and ori) & delta_des_joint_state
        if i == 0:
            delta_ee_pos[i] = 0
            delta_des_joint_state[i] = 0
        else:
            delta_ee_pos[i][0:3] = data["ee_pos"][i][0:3] - data["ee_pos"][i-1][0:3]

            rot_quat = Rotation.from_quat(data["ee_pos"][i][3:7])
            rot_quat_prev = Rotation.from_quat(data["ee_pos"][i-1][3:7])
            delta_rot = rot_quat * rot_quat_prev.inv()
            delta_ee_pos[i][3:6] = delta_rot.as_euler("xyz")

            delta_des_joint_state[i] = data["des_joint_pos"][i] - data["des_joint_pos"][i-1]


        # compute action 
        action_pos_ori = delta_ee_pos[i][0:6]
        action_gripper = data['des_gripper_state'][i]
        action = np.append(action_pos_ori, action_gripper)
        # compute action_abs
        action_abs_pos = data["ee_pos"][i][0:3]
        action_abs_ori = Rotation.from_quat(data["ee_pos"][i][3:7]).as_euler("xyz")
        action_abs_gripper = data['des_gripper_state'][i]
        action_abs = np.concatenate([action_abs_pos, action_abs_ori, [action_abs_gripper]])

        # compute eef orientation
        end_effector_ori = Rotation.from_quat(data["ee_pos"][i][3:7]).as_euler("xyz")

        episode.append({
            'observation': {
                'image_top': data['image_top'][i],
                'image_side': data['image_side'][i],
                'joint_state': data['joint_pos'][i],
                'joint_state_velocity': data['joint_vel'][i],
                'end_effector_pos': data['ee_pos'][i][0:3],
                'end_effector_ori_quat': data['ee_pos'][i][3:7], 
                'end_effector_ori': end_effector_ori,
            },
            'action': action,
            'action_abs': action_abs,
            'action_joint_state': data['des_joint_pos'][i],
            'action_joint_vel': data['joint_vel'][i], # 'action_joint_vel': data['des_joint_vel'][i],
            'action_gripper_width': data['des_gripper_state'][i],
            'delta_des_joint_state': delta_des_joint_state[i],
            'discount': 1.0,
            'reward': float(i == (trajectory_length - 1)),
            'is_first': i == 0,
            'is_last': i == (trajectory_length - 1),
            'is_terminal': i == (trajectory_length - 1),
            'language_instruction': instruction_set[episode_path.split('/')[-2]][0],
            'language_instruction_2': instruction_set[episode_path.split('/')[-2]][1],
            'language_instruction_3': instruction_set[episode_path.split('/')[-2]][2],
        })

    # create output data sample
    sample = {
        'steps': episode,
        'episode_metadata': {
            'file_path': episode_path,
            'traj_length': trajectory_length,
        }
    }

    # if you want to skip an example for whatever reason, simply return None
    return episode_path, sample

def create_img_vector(img_folder_path, trajectory_length):
    cam_list = []
    img_paths = glob.glob(os.path.join(img_folder_path, '*.jpeg'))
    img_paths = natsort.natsorted(img_paths)
    assert len(img_paths)==trajectory_length, "Number of images does not equal trajectory length!"

    for img_path in img_paths:
        img_array = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_RGB2BGR)
        cam_list.append(img_array)
    return cam_list

def get_trajectorie_paths_recursive(directory, sub_dir_list):
    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        if os.path.isdir(full_path):
            sub_dir_list.append(directory) if entry == "images" else get_trajectorie_paths_recursive(full_path, sub_dir_list)

if __name__ == "__main__":
    # create list of all examples
    raw_dirs = []
    get_trajectorie_paths_recursive(data_path, raw_dirs)
    # filter out any paths that include an excluded episode id
    filtered_dirs = [
        path for path in raw_dirs
        if not any(ep in path for ep in exclude_episodes)
    ]
    for trajectorie_path in tqdm(filtered_dirs):
        _, sample = _parse_example(trajectorie_path)
        # print(f"sample: {sample}")