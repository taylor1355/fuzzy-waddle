from sklearn.externals import joblib
import numpy as np
import cv2 as cv

import ml_utils

class Model:
    def __init__(self, estimator, box_size, small_box_size):
        self.estimator = estimator
        self.box_size = box_size
        self.small_box_size = small_box_size

    def predict(self, img):
        if img.shape[0] < self.box_size[0] or img.shape[1] < self.box_size[1]:
            print("Invalid image size for prediction")
            return None

        downscaled = ml_utils.downscale(img)

        img_height, img_width = downscaled.shape[:2]
        box_height, box_width = self.small_box_size[:2]
        scale_factor = 1/4

        overlap = 0.25
        horizontal_windows = self.get_windows(box_width, img_width, overlap)
        vertical_windows = self.get_windows(box_height, img_height, overlap)
        predictions = []
        for i in range(len(vertical_windows)):
            for j in range(len(horizontal_windows)):
                x, y = int(horizontal_windows[j]), int(vertical_windows[i])
                region = downscaled[y : y + box_height, x : x + box_width]
                if self.estimator.predict(region.reshape(1,-1)) == 1:
                    predictions.append(np.array([x, y]) / scale_factor)

        if len(predictions) > 1:
            return True, np.mean(predictions, axis=0).astype(int)
        return False, None


    def get_windows(self, window_length, img_length, overlap):
        offset = overlap * window_length
        num_windows = int((img_length - window_length) / offset)
        windows = list(np.arange(0, img_length - window_length, offset))
        windows.append(img_length - window_length)
        return windows

    def save(self, path):
        joblib.dump(self, path)

    def load(path):
        return joblib.load(path)
