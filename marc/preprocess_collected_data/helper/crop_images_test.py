import cv2

import numpy as np
import os

dataset_dir = "/DATA/nikolaus/marc_datasets_modified_gripper"


def resize_and_crop(
        cam_img_array, position, des_width: int = 224, des_height: int = 224
    ):
    """
    Resizes and crops an image to a square shape, centered or aligned to the left or right side.

    Arguments:
    - image_array: a NumPy array representing the image to be resized and cropped.
    - position: a string specifying the position of the crop within the image.
                Valid values are 'left', 'right', 'center', and 'center_right'.
    - size: a tuple specifying the desired size of the output image after resizing. The default value is (500, 500).

    Returns:
    - image_resized: a NumPy array representing the resized and cropped image.

    The method first calculates the size of the largest square that fits inside the original image,
    then crops the image to a square centered or aligned to the specified position.
    Finally, the cropped image is resized to the specified output size using the OpenCV library.

    Note that this method modifies the input image array in-place,
    so make a copy of the original image if you need to keep it intact.
    """

    size = (des_width, des_height)
    # O Get the height and width of the image
    height, width, _ = cam_img_array.shape
    # Calculate the size of the square
    square_size = min(width, height)
    # Calculate the left, top, right, and bottom coordinates of the square
    if position == "left":
        # Crop the left side of the image
        left = 0
        top = 0
        right = square_size
        bottom = square_size
    elif position == "right":
        # Crop the right side of the image
        left = width - square_size
        top = 0
        right = width
        bottom = square_size
    elif position == "center":
        left = (width - square_size) // 2
        top = (height - square_size) // 2
        right = left + square_size 
        bottom = top + square_size 
    elif position == "top_center_new_lab":
        left = 550
        top = 0
        right = 1700
        bottom = top + square_size 
    elif position == "front_center_new_lab":
        left = 0
        top = 0
        right = 1700
        bottom = top + square_size
    elif position == "front_center_new_lab_2":
        left = 360
        right = 1760
        top = 0
        bottom = 1080
    elif position == "center_left":
        left = (width - square_size) // 2 - 30
        top = (height - square_size) // 2
        right = left + square_size
        bottom = top + square_size
    elif position == "center_far_left":
        left = (width - square_size) // 2 - 100
        top = (height - square_size) // 2
        right = left + square_size
        bottom = top + square_size
    elif position == "center_right":
        left = (width - square_size) // 2 + 100
        top = (height - square_size) // 2
        right = left + square_size
        bottom = top + square_size
    else:
        raise ValueError("Invalid position. Use correct position values")

    # Crop the image to create a square
    image_cropped = cam_img_array[top:bottom, left:right]
    image_resized = cv2.resize(image_cropped, size)

    return image_resized


# florence images dims
image_size = (224, 224)

input_path = "/home/nikolaus/my_data/marc_datasets_modified_gripper/banana_from_tray_to_right_stove/default_task/2025_04_14-14_59_11/images/side_cam_orig/42.png"
output_path = "/home/nikolaus/my_data/marc_datasets_modified_gripper/banana_from_tray_to_right_stove/default_task/2025_04_14-14_59_11/images/side_cam_crop/42_test.png"


image = cv2.imread(input_path)

if not image is None and "side_cam_orig" in input_path:
    position = "front_center_new_lab_2"
    processed_image = resize_and_crop(image, position, image_size[0], image_size[1])


cv2.imwrite(output_path, processed_image)

print("Image processing and saving completed.")