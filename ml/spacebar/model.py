from sklearn.externals import joblib
import cv2 as cv

class Model:
    def __init__(self, estimator, box_size, num_downscales):
        self.estimator = estimator
        self.box_size = box_size
        self.num_downscales = num_downscales

    def predict(self, img):
        if img.shape[0] != box_size[0] or img_shape[1] != box_shape[1]:
            print("Invalid box size for prediction")
            return None
        downscaled = img
        for level in range(self.num_downscales):
            downscaled = cv.pyrDown(downscaled)

        return self.estimator.predict(downscaled)

    def save(self, path):
        joblib.dump(self, path)

    def load(path):
        return joblib.load(path)
