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

    settings = ml_utils.load_settings(task_dir)
    width, height = settings["box_width"], settings["box_height"]
    classes, negative_class = settings["classes"], settings["negative_class"]

    num_examples = int(sys.argv[2])
    row, col = int(sys.argv[3]), int(sys.argv[4])

    for class_name, class_label in classes.items():
        img_files = grab_img_files(os.path.join(screenshot_dir, class_name))
        num_samples = max(1, int(num_examples / (len(classes) * len(img_files))))
        print("CN: {}, CL: {}, NC: {}, #C: {}, #E: {}, #F: {}, #S: {}".format(class_name, class_label, negative_class, len(classes), num_examples, len(img_files), num_samples))
        if class_label == negative_class:
            generate_negative_examples(img_files, data_dir, class_name, num_samples, width, height)
        else:
            generate_positive_examples(img_files, data_dir, class_name, num_samples, row, col, width, height)

def generate_positive_examples(files, data_dir, class_name, num_samples, row, col, width, height):
    destination_dir = os.path.join(data_dir, class_name)
    for file in files:
        img = cv.imread(file)
        for i in range(num_samples):
            radius = 0.1
            shifted_row = row + int(radius * random.random() * height) * random.choice([-1, 1])
            shifted_col = col + int(radius * random.random() * width) * random.choice([-1, 1])
            write_example(img, destination_dir, shifted_row, shifted_col, width, height)

def generate_negative_examples(files, data_dir, class_name, num_samples, width, height):
    destination_dir = os.path.join(data_dir, class_name)
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
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
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
    return row >= 0 and col >= 0 and row < img.shape[0] and col < img.shape[1]

if __name__ == "__main__":
    main()
