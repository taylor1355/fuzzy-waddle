import os
import cv2 as cv
import numpy as np


class Colors():
    GOLD = 1
    BLUE = 2
    GREEN = 3
    OTHER = 4

class ColorGrabber():

    item_x, item_y, dx = 11, 61, 54
    back_colors = (
        (Colors.GOLD, (115, 69, 47)),
        (Colors.BLUE, (99.5, 124.5, 151.5)),
        (Colors.GREEN, (140, 105.5, 117)),
    )

    def __init__(self):
        self.comp_img = cv.imread('../resources/item_box.jpg', 0)
        self.color_mask = cv.imread('../resources/item_color_mask3.tiff', 0)
        self.relic_img = cv.imread('../resources/relic_shard.jpg', 1) * 1.0

    def evaluate(self, frame, discardBlue, discardGreen, keepUnknowns):
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        result = cv.matchTemplate(self.comp_img, frame_gray, cv.TM_SQDIFF)
        mn, _, mnLoc, _ = cv.minMaxLoc(result)
        x, y = mnLoc

        img = frame[y:y+self.comp_img.shape[0], x:x+self.comp_img.shape[1]]

        img_colors = []
        diffs = []
        shouldPass = True
        for i in range(4):
            color = [0,0,0]
            diffs.append(np.sum(np.square(self.relic_img - img[61:61+45,11+i*self.dx:11+i*self.dx+45])))
            for c in range(3):
                color[c] = np.sum(self.color_mask * img[61:61+45,11+i*self.dx:11+i*self.dx+45,c]) / 176
            print(color)
            for index, back_color in self.back_colors:
                for c in range(3):
                    if abs(back_color[c] - color[c]) > 10:
                        break
                else:
                    if index == Colors.GOLD:
                        print('gold')
                        return True
                    elif index == Colors.BLUE:
                        print('blue')
                        if discardBlue:
                            shouldPass = False
                        else:
                            return True
                    elif index == Colors.GREEN:
                        print('green')
                        if discardGreen:
                            shouldPass = False
                        else:
                            return True
                    break
        # check to see if it is relic
        if min(diffs) < 1000000:
            print('relic')
            return True
        return shouldPass and keepUnknowns


base_dir = '../ml/new_ui_keys/catches/'

cg = ColorGrabber()

for filename in os.listdir(base_dir):
    img = cv.imread(base_dir + filename)
    cg.evaluate(img, False, True, True)
    cv.imshow('img', img)
    cv.waitKey()
cv.destroyAllWindows()