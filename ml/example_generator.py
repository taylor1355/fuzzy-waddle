import sys, os, uuid, random
import cv2 as cv

def main():
    if len(sys.argv) != 6 and len(sys.argv) != 8:
        print("Positive Example Usage: python {} <screenshot(s) path> <destination path> <samples / img> <row> <column> <width> <height>".format(sys.argv[0]))
        print("Negative Example Usage: python {} <screenshot(s) path> <destination path> <samples / img> <width> <height>".format(sys.argv[0]))
        return

    path = sys.argv[1]
    files = []
    if os.path.isdir(path):
        for file_name in os.listdir(path):
            file = os.path.join(path, file_name)
            if is_img_file(file):
                files.append(file)
    else:
        files.append(path)

    if len(sys.argv) == 6:
        generate_negative_examples(files)
    else:
        generate_positive_examples(files)

def generate_positive_examples(files):
    destination_dir = sys.argv[2]
    num_samples = int(sys.argv[3])
    row = int(sys.argv[4])
    col = int(sys.argv[5])
    width = int(sys.argv[6])
    height = int(sys.argv[7])

    for file in files:
        img = cv.imread(file)

        for i in range(num_samples):
            radius = 0.2
            shifted_row = row + int(radius * random.random() * height) * random.choice([-1, 1])
            shifted_col = col + int(radius * random.random() * width) * random.choice([-1, 1])
            write_example(img, destination_dir, shifted_row, shifted_col, width, height)

def generate_negative_examples(files):
    destination_dir = sys.argv[2]
    num_samples = int(sys.argv[3])
    width = int(sys.argv[4])
    height = int(sys.argv[5])

    for file in files:
        img = cv.imread(file)
        img_width = img.shape[1]
        img_height = img.shape[0]

        for i in range(num_samples):
            row = random.randrange(img_height - height)
            col = random.randrange(img_width - width)
            write_example(img, destination_dir, row, col, width, height)

def write_example(img, destination_dir, row, col, width, height):
    if in_bounds(img, row + height, col + width):
        subsection = img[row : row+height, col : col+width, :]
        file_name = str(uuid.uuid4()) + ".jpg"
        cv.imwrite(os.path.join(destination_dir, file_name), subsection)

def is_img_file(file):
    extensions = ["bmp", "jpeg", "jpg", "png"]
    return not os.path.isdir(file) and file.split(".")[-1] in extensions

def in_bounds(img, row, col):
    return row < img.shape[0] and col < img.shape[1]

if __name__ == "__main__":
    main()
