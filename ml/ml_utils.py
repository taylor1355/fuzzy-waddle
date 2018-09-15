import os, random
from sklearn.model_selection import train_test_split
import numpy as np
import cv2 as cv
import csv

def load_settings(task_dir):
    settings = load_csv_dict(os.path.join(task_dir, "settings.csv"))
    settings["box_width"] = int(settings["box_width"])
    settings["box_height"] = int(settings["box_height"])
    settings["downscale"] = float(settings["downscale"])
    settings["negative_class"] = int(settings["negative_class"])
    return settings

def load_data(task_dir, test_fraction, flatten=True):
    downscale_factor = load_settings(task_dir)["downscale"]
    classes = load_csv_dict(os.path.join(task_dir, "class_info.csv"))

    data = []
    for class_name in classes:
        dir = os.path.join(task_dir, "data/", class_name)
        data.extend((example, int(classes[class_name])) for example in load_examples(dir, flatten, downscale_factor))
    random.shuffle(data)

    X = np.empty((len(data),) + data[0][0].shape)
    y = np.empty((len(data),))
    for row in range(len(data)):
        X[row] = data[row][0]
        y[row] = data[row][1]

    train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=test_fraction)
    return X, y, train_X, train_y, test_X, test_y

def load_csv_dict(path):
    dict = {}
    with open(path) as file:
        reader = csv.reader(file, delimiter = ",")
        next(reader) # skip header line
        for row in reader:
            dict[row[0].strip()] = row[1].strip()
    return dict

def load_examples(dir, flatten, downscale_factor):
    examples = []
    for file_name in os.listdir(dir):
        file = os.path.join(dir, file_name)
        img = downscale(cv.imread(file), downscale_factor)
        if flatten:
            img = img.ravel()
        examples.append(img)
    return examples

def downscale(img, scale_factor):
    height, width = img.shape[:2]
    small_height, small_width = int(height * scale_factor), int(width * scale_factor)
    return cv.resize(img, (small_width, small_height), interpolation=cv.INTER_AREA)
