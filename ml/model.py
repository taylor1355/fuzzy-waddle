from sklearn.externals import joblib
import numpy as np
import cv2 as cv

import ml.ml_utils

class Model:
    def __init__(self, estimator, task_dir):
        self.estimator = estimator
        settings = ml_utils.load_settings(task_dir)
        box_width, box_height = settings["box_width"], settings["box_height"]
        self.scale_factor = settings["downscale"]
        self.box_size = (box_height, box_width)
        self.small_box_size = (int(box_height * self.scale_factor), int(box_width * self.scale_factor))

    def predict(self, img):
        if img.shape[0] != self.box_size[0] or img.shape[1] != self.box_size[1]:
            print("Invalid image size for prediction")
            return None

        downscaled = ml_utils.downscale(img, self.scale_factor)
        return int(self.estimator.predict(downscaled.reshape(1,-1)))

    def binary_predict(self, img):
        if img.shape[0] < self.box_size[0] or img.shape[1] < self.box_size[1]:
            print("Invalid image size for prediction")
            return None

        downscaled = ml_utils.downscale(img, self.scale_factor)
        img_height, img_width = downscaled.shape[:2]
        box_height, box_width = self.small_box_size[:2]

        overlap = 0.25
        horizontal_windows = self.get_windows(box_width, img_width, overlap)
        vertical_windows = self.get_windows(box_height, img_height, overlap)
        predictions = []
        for i in range(len(vertical_windows)):
            for j in range(len(horizontal_windows)):
                x, y = int(horizontal_windows[j]), int(vertical_windows[i])
                region = downscaled[y : y + box_height, x : x + box_width]
                if self.estimator.predict(region.reshape(1,-1)) == 1:
                    predictions.append(np.array([x, y]) / self.scale_factor)

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
