import os, random
import numpy as np
import cv2 as cv

from sklearn import svm

import model

def main():
    X, y, train_X, train_y, test_X, test_y = ml_utils.load_data()

    estimator = svm.SVC(kernel="linear")
    estimator.fit(X, y)
    box_size = (65, 150)
    num_downscales = 2

    

if __name__ == "__main__":
    main()
