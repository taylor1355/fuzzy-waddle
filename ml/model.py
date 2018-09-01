from sklearn.externals import joblib
import cv2 as cv

class Model:
    def __init__(self, estimator, box_size, num_downscales):
        self.estimator = estimator
        self.box_size = box_size
        self.num_downscales = num_downscales

    def predict(self, img):
        if img.shape[0] != self.box_size[0] or img.shape[1] != self.box_size[1]:
            print("Invalid box size for prediction")
            return None
        downscaled = img
        for level in range(self.num_downscales):
            print(downscaled.shape)
            downscaled = cv.pyrDown(downscaled)
        print(downscaled.shape)
        return self.estimator.predict(downscaled.reshape(1,-1)) == 1

    def save(self, path):
        joblib.dump(self, path)

    def load(path):
        print(path)
        return joblib.load(path)
