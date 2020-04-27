from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
import cv2 as cv
import os, sys, csv, uuid
# import os, sys

img_width, img_height = 320, 80
min_x, max_x, min_y, max_y = -5, 29, -2, 29 # 0, 0, 0, 0
dev_x, dev_y = max_x - min_x, max_y - min_y
frame_x1, frame_y1, frame_x2, frame_y2 = 449+6, 371, 817+9, 428+2+7
frame_w, frame_h = frame_x2 - frame_x1, frame_y2 - frame_y1
pad = 5
kx1, ky1, kdi = 463-6, 380-6, 37
kw, kh = 34, 50

key_to_index = {'W': 0, 'A': 1, 'S': 2, 'D': 3}

class Classifier():

    def __init__(self, my_dir='./'):
        self.key_model = joblib.load(my_dir +'key_model.pkl')
        self.loc_model = joblib.load(my_dir + 'loc_model.pkl')

    def evaluate(self, img):
        # localization code
        img_cropped = img[frame_y1+min_y-pad:frame_y2+max_y+pad,frame_x1+min_x-pad:frame_x2+max_x+pad]
        img_small = cv.resize(img_cropped, (img_width, img_height))
        location = self.loc_model.predict([img_small.flatten()])[0]
        pixel_x, pixel_y = int(location[0]), int(location[1])

        # key detection code
        key_seq = []
        for i in range(10):
            base_y = ky1 + pixel_y
            base_x = kx1 + pixel_x + kdi*i
            key_img = img[base_y:base_y+kh,base_x:base_x+kw]
            guess = self.key_model.predict([key_img.flatten()])[0]
            if guess == 'E':
                return key_seq
            key_seq.append(key_to_index[guess])

    def evaluate_and_save(self, img, save_dir='./raw'):
        # localization code
        img_cropped = img[frame_y1+min_y-pad:frame_y2+max_y+pad,frame_x1+min_x-pad:frame_x2+max_x+pad]
        img_small = cv.resize(img_cropped, (img_width, img_height))
        location = self.loc_model.predict([img_small.flatten()])[0]
        pixel_x, pixel_y = int(location[0]), int(location[1])

        # key detection code
        key_seq = []
        for i in range(10):
            base_y = ky1 + pixel_y
            base_x = kx1 + pixel_x + kdi*i
            key_img = img[base_y:base_y+kh,base_x:base_x+kw]
            guess = self.key_model.predict([key_img.flatten()])[0]
            if guess == 'E':
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                out_dir = save_dir + '/' + str(uuid.uuid4())
                print("saving to " + out_dir)
                os.makedirs(out_dir)
                cv.imwrite(os.path.join(out_dir, "frame0.jpg"), img)
                with open(out_dir + "/" + "info.csv", mode="w") as csv_file:
                    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    csv_writer.writerow([pixel_x, pixel_y, key_seq])
                return key_seq
            key_seq.append(key_to_index[guess])