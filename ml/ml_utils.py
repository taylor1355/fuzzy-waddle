import os, random
from sklearn.model_selection import train_test_split
import numpy as np
import cv2 as cv

def load_data(data_dir, test_fraction, flatten=True):
    positive_dir = os.path.join(data_dir, "positive")
    negative_dir = os.path.join(data_dir, "negative")

    positive_examples = load_examples(positive_dir, flatten)
    negative_examples = load_examples(negative_dir, flatten)

    num_features = positive_examples[0].size
    num_examples = len(positive_examples) + len(negative_examples)

    data = []
    data.extend([(example, 1) for example in positive_examples])
    data.extend([(example, 0) for example in negative_examples])
    random.shuffle(data)

    X = np.empty((num_examples,) + positive_examples[0].shape)
    y = np.empty((num_examples,))
    for row in range(len(data)):
        X[row] = data[row][0]
        y[row] = data[row][1]

    train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=test_fraction)
    return X, y, train_X, train_y, test_X, test_y

#def load_data(task_dir, test_fraction, flatten=True):
    # get class: label map

    # load examples from data directories, put into data
    # shuffle data

    # get num examples

    # put data into X, y

    # return

def load_examples(dir, flatten):
    examples = []
    for file_name in os.listdir(dir):
        file = os.path.join(dir, file_name)
        img = downscale(cv.imread(file))
        if flatten:
            img = img.ravel()
        examples.append(img)
    return examples

def downscale(img):
    height, width = img.shape[:2]
    small_height, small_width = int(height / 4), int(width / 4)
    return cv.resize(img, (small_width, small_height), interpolation=cv.INTER_AREA)
