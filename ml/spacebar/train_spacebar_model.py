import sys, os, random
import numpy as np
import cv2 as cv
from sklearn import svm

sys.path.append('../')
import ml_utils
import model

def main():
    X, y, train_X, train_y, test_X, test_y = ml_utils.load_data("data/", 0)
    estimator = svm.SVC(kernel="linear", C=100)
    estimator.fit(X, y)

    box_size = (65, 150)
    num_downscales = 3

    spacebar_model = model.Model(estimator, box_size, num_downscales)
    spacebar_model.save("spacebar_model.pkl")

if __name__ == "__main__":
    main()
