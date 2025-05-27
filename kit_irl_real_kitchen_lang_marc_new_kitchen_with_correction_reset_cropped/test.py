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
import pandas as pd

tf.config.set_visible_devices([], "GPU")
data_path = "/home/nikolaus/my_data/new_kitchen_data"
csv_crop_path = "/home/nikolaus/my_data/new_kitchen_data/episodes_crop.csv"
crop_episodes = pd.read_csv(csv_crop_path)

print(crop_episodes)
import pdb
pdb.set_trace()