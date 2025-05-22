import cv2

import numpy as np
import os

dataset_dir = "/home/nikolaus/my_data/new_kitchen_data"


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

for root, dirs, files in os.walk(dataset_dir):
    for dir_name in dirs:
        if dir_name == "top_cam_orig" or dir_name == "side_cam_orig":
            print(f"Processing directory: {os.path.join(root, dir_name)}")
            orig_dir = os.path.join(root, dir_name)
            crop_dir = os.path.join(root, dir_name.replace("orig", "crop"))

            if os.path.exists(crop_dir):
                print(f"Directory already exists, skipping: {crop_dir}")
                continue
            
            os.makedirs(crop_dir, exist_ok=True)

            for img_file in os.listdir(orig_dir):
                if not img_file.endswith(".png"):
                    continue

                img_path = os.path.join(orig_dir, img_file)
                image = cv2.imread(img_path)

                if image is None:
                    print(f"Could not read image: {img_path}")
                    continue
                
                if "top_cam_orig" in dir_name:
                    position = "top_center_new_lab"
                    processed_image = resize_and_crop(image, position, image_size[0], image_size[1])
                elif "side_cam_orig" in dir_name:
                    position = "front_center_new_lab"
                    processed_image = resize_and_crop(image, position, image_size[0], image_size[1])

                output_path = os.path.join(crop_dir, img_file.replace(".png", ".jpeg"))
                cv2.imwrite(output_path, processed_image)

print("Image processing and saving completed.")