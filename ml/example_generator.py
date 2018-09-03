import sys, os, uuid, random
import cv2 as cv

import ml_utils

def main():
    if len(sys.argv) != 5:
        print("Usage: python {} <task path> <num examples> <row> <column>".format(sys.argv[0]))
        return

    task_dir = sys.argv[1]
    screenshot_dir = os.path.join(task_dir, "screenshots")
    data_dir = os.path.join(task_dir, "data")
    positive_img_files = grab_img_files(os.path.join(screenshot_dir, "positive"))
    negative_img_files = grab_img_files(os.path.join(screenshot_dir, "negative"))

    num_examples = int((int(sys.argv[2]) + 1) / 2)
    row, col = int(sys.argv[3]), int(sys.argv[4])

    settings = ml_utils.load_settings(task_dir)
    width, height = settings["box_width"], settings["box_height"]

    generate_positive_examples(positive_img_files, data_dir, num_examples, row, col, width, height)
    generate_negative_examples(negative_img_files, data_dir, num_examples, width, height)

def generate_positive_examples(files, screenshot_dir, num_examples, row, col, width, height):
    destination_dir = os.path.join(screenshot_dir, "positive")
    num_samples = max(1, int(num_examples / len(files)))

    for file in files:
        img = cv.imread(file)

        for i in range(num_samples):
            radius = 0.125
            shifted_row = row + int(radius * random.random() * height) * random.choice([-1, 1])
            shifted_col = col + int(radius * random.random() * width) * random.choice([-1, 1])
            write_example(img, destination_dir, shifted_row, shifted_col, width, height)

def generate_negative_examples(files, screenshot_dir, num_examples, width, height):
    destination_dir = os.path.join(screenshot_dir, "negative")
    num_samples = max(1, int(num_examples / len(files)))

    for file in files:
        img = cv.imread(file)
        img_width = img.shape[1]
        img_height = img.shape[0]

        for i in range(num_samples):
            if img_width == width and img_height == height:
                row, col = 0, 0
            else:
                row = random.randrange(img_height - height)
                col = random.randrange(img_width - width)
            write_example(img, destination_dir, row, col, width, height)

def write_example(img, destination_dir, row, col, width, height):
    if in_bounds(img, row + height - 1, col + width - 1):
        subsection = img[row : row+height, col : col+width, :]
        file_name = str(uuid.uuid4()) + ".jpg"
        cv.imwrite(os.path.join(destination_dir, file_name), subsection)

def grab_img_files(dir):
    files = []
    for file_name in os.listdir(dir):
        file = os.path.join(dir, file_name)
        if is_img_file(file):
            files.append(file)
    return files

def is_img_file(file):
    extensions = ["bmp", "jpeg", "jpg", "png"]
    return not os.path.isdir(file) and file.split(".")[-1] in extensions

def in_bounds(img, row, col):
    return row < img.shape[0] and col < img.shape[1]

if __name__ == "__main__":
    main()
