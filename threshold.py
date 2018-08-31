import cv2 as cv
import sys
import os

def main():
    if len(sys.argv) <= 1:
        print("Pass image path as argument")
        return
    elif not os.path.exists(sys.argv[1]):
        print("Image path doesn't exist")
        return
    img_file_name = sys.argv[1].split(".")

    img = cv.imread(sys.argv[1])
    img = cv.medianBlur(img, 3)
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    thresh = None
    while True:
        _, thresh = cv.threshold(img_gray, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)

        cv.imshow("Image", img)
        cv.imshow("Thresholded Image", thresh)

        key = cv.waitKey(0)
        if key == ord("q"):
            return
        elif key == ord(" "):
            break

    img_file_name = sys.argv[1].split(".")
    threshold_file_name = "." + img_file_name[-2] + "_mask.jpg"
    print(threshold_file_name)
    cv.imwrite(threshold_file_name, thresh)

if __name__ == "__main__":
    main()
