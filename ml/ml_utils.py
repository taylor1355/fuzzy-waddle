import os, random
from sklearn.model_selection import train_test_split
import numpy as np
import cv2 as cv

def load_data(data_dir, test_fraction):
    positive_dir = os.path.join(data_dir, "positive")
    negative_dir = os.path.join(data_dir, "negative")

    positive_examples = load_examples(positive_dir)
    negative_examples = load_examples(negative_dir)

    num_features = positive_examples[0].size
    num_examples = len(positive_examples) + len(negative_examples)

    data = []
    data.extend([(example, 1) for example in positive_examples])
    data.extend([(example, 0) for example in negative_examples])
    random.shuffle(data)

    X = np.empty((num_examples, num_features))
    y = np.empty((num_examples,))
    for row in range(len(data)):
        X[row] = data[row][0]
        y[row] = data[row][1]

    train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=test_fraction)
    return X, y, train_X, train_y, test_X, test_y

def load_examples(dir):
    examples = []
    for file_name in os.listdir(dir):
        file = os.path.join(dir, file_name)
        img = cv.pyrDown(cv.pyrDown(cv.imread(file)))
        examples.append(img.ravel())
    return examples
