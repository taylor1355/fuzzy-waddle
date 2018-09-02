import sys, os, random
import numpy as np
import cv2 as cv
from sklearn import svm
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier

my_dir = os.path.dirname(sys.argv[0])
sys.path.append(os.path.join(my_dir, '../'))
import ml_utils
import model

def main():
    X, y, train_X, train_y, test_X, test_y = ml_utils.load_data(os.path.join(my_dir, "data/"), 0)
    estimator = RandomForestClassifier(n_estimators=60 , max_depth=3)
    estimator.fit(X, y)

    box_size = (65, 150)
    small_box_size = (16, 37)

    spacebar_model = model.Model(estimator, box_size, small_box_size)
    spacebar_model.save(os.path.join(my_dir, "spacebar_model.pkl"))

if __name__ == "__main__":
    main()
