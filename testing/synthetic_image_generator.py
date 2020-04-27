import os, csv, random
import numpy as np
import cv2 as cv
from tqdm import tqdm
import uuid

csv_name = 'info.csv'
base_names = ('../ml/new_ui_keys/good/', '../ml/new_ui_keys/good_OLD/')
blank_folder = '../ml/new_ui_keys/rand_backgrounds/'

min_x, max_x, min_y, max_y = -5, 29, -2, 29 # 0, 0, 0, 0
dev_x, dev_y = max_x - min_x, max_y - min_y
frame_x1, frame_y1, frame_x2, frame_y2 = 449+6, 371, 817+9, 428+2+7
frame_w, frame_h = frame_x2 - frame_x1, frame_y2 - frame_y1
img_width, img_height = 80, 20

kx1, ky1, kx2, ky2, kdi = 463+0, 380+0, 463+22, 380+38, 37
kw, kh = kx2 - kx1, ky2 - ky1

pad = 5
rand_x1, rand_y1, rand_x2, rand_y2 = 30, 200, 1255 - frame_w - pad*2, 630 - frame_h - pad*2
rand_w, rand_h = rand_x2 - rand_x1, rand_y2 - rand_y1

ignore_y = 60
bar_min_perc = 0.2

pre_ratio = 0.4
scale_ratio = 4

frame_avg = np.zeros((frame_h, frame_w, 3), np.uint8)
frame_mask = np.zeros((frame_h, frame_w, 3), np.uint8)

imgs = []

def scale_img(img, scale):
	return cv.resize(img, (img.shape[1]*scale, img.shape[0]*scale))

def show_cut_images():
	for base_name in base_names:
		for folder in os.listdir(base_name):
			if not os.path.isdir(base_name + folder):
				continue
			with open(os.path.join(base_name + folder, csv_name), 'r') as csv_file:
				csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
				for row in csv_reader:
					x, y, keys = row
					x_off = int(x)
					y_off = int(y)
					break
				img = cv.imread(os.path.join(base_name + folder, 'frame0.jpg'), 1)
				imgs.append(img[frame_y1+y_off:frame_y2+y_off,frame_x1+x_off:frame_x2+x_off])
	print('Done loading images')
	for yi in tqdm(range(frame_h)):
		for xi in range(frame_w):
			total = (0, 0, 0)
			for img in imgs:
				total += img[yi,xi]
			avg = total / len(imgs)
			std_dev_sum = 0
			for img in imgs:
				std_dev_sum += np.square(img[yi,xi] - avg)
			std_dev = std_dev_sum / len(imgs)
			frame_avg[yi,xi] = avg
			frame_mask[yi,xi] = std_dev
	cv.imshow('avg', frame_avg)
	cv.imshow('mask', frame_mask)
	# cv.imwrite('keys_avg.tiff', frame_avg)
	cv.waitKey()

def comp_keys_to_images():
	thresh = 0.2
	keys_back = np.float32(cv.imread('keys_avg.tiff')) / 255.0
	base_name = '../ml/new_ui_keys/good/'
	totals = [ np.zeros((kh, kw), np.float32), np.zeros((kh, kw), np.float32), np.zeros((kh, kw), np.float32), np.zeros((kh, kw), np.float32) ]
	cntrs = [ 0, 0, 0, 0 ]
	for folder in os.listdir(base_name):
		key_seq = []
		if not os.path.isdir(base_name + folder):
			continue
		with open(os.path.join(base_name + folder, csv_name), 'r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
			for row in csv_reader:
				x, y, keys = row
				x_off = int(x)
				y_off = int(y)
				i = 1
				while (i < len(keys) and keys[i] != ']'):
					key_seq.append(int(keys[i]))
					i += 3
				break
			img = np.float32(cv.imread(os.path.join(base_name + folder, 'frame0.jpg'), 1)) / 255.0
			img_cut = img[frame_y1+y_off:frame_y2+y_off,frame_x1+x_off:frame_x2+x_off]
			img_diff = abs(img_cut - keys_back)
			mask = np.logical_and(img_diff[:,:,0] < thresh, np.logical_and(img_diff[:,:,1] < thresh, img_diff[:,:,2] < thresh))
			img_diff[mask] = (0, 0, 0)
			for i, key in enumerate(key_seq):
				x, y = kx1 - frame_x1 + kdi*i, ky1 - frame_y1
				totals[key] += cv.cvtColor(img_diff[y:y+kh,x:x+kw], cv.COLOR_BGR2GRAY)
				cntrs[key] += 1

			# cv.imshow('img', scale_img(img_diff, 4))
			# cv.waitKey()
	for i in range(4):
		totals[i] /= cntrs[i]
		totals[i] *= 255.0
		totals[i] = np.uint8(totals[i])
		cv.imshow('img' + str(i), scale_img(totals[i], 8))
		cv.imwrite('mask' + str(i) + '.tiff', totals[i])
	cv.waitKey()

def comp_keys_to_images_2():
	thresh = 0
	keys_back = np.float32(cv.imread('keys_avg.tiff')) / 255.0
	base_name = '../ml/new_ui_keys/good/'
	totals = [ np.zeros((kh, kw), np.float32), np.zeros((kh, kw), np.float32), np.zeros((kh, kw), np.float32), np.zeros((kh, kw), np.float32) ]
	cntrs = [ 0, 0, 0, 0 ]
	for folder in os.listdir(base_name):
		key_seq = []
		if not os.path.isdir(base_name + folder):
			continue
		with open(os.path.join(base_name + folder, csv_name), 'r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
			for row in csv_reader:
				x, y, keys = row
				x_off = int(x)
				y_off = int(y)
				i = 1
				while (i < len(keys) and keys[i] != ']'):
					key_seq.append(int(keys[i]))
					i += 3
				break
			img = np.float32(cv.imread(os.path.join(base_name + folder, 'frame0.jpg'), 1)) / 255.0
			img_cut = img[frame_y1+y_off:frame_y2+y_off,frame_x1+x_off:frame_x2+x_off]
			img_diff = img_cut - keys_back
			mask = np.logical_or(img_diff[:,:,0] > thresh, np.logical_or(img_diff[:,:,1] > thresh, img_diff[:,:,2] > thresh))
			img_diff[mask] = (0,0,0)
			img_diff = cv.cvtColor(img_diff, cv.COLOR_BGR2GRAY)
			img_diff *= 4
			img_diff = abs(img_diff)
			mask = img_diff[:,:] < 0.1
			img_diff[mask] = 0
			mask = img_diff[:,:] > 1.0
			img_diff[mask] = 1

			for i, key in enumerate(key_seq):
				x, y = kx1 - frame_x1 + kdi*i, ky1 - frame_y1
				totals[key] += img_diff[y:y+kh,x:x+kw]
				cntrs[key] += 1
			# cv.imshow('img', scale_img(img_diff, 4))
			# cv.waitKey()
	for i in range(4):
		totals[i] /= cntrs[i]
		totals[i] *= 255.0
		totals[i] = np.uint8(totals[i])
		cv.imshow('img' + str(i), scale_img(totals[i], 8))
		# cv.imwrite('dark_mask' + str(i) + '.tiff', totals[i])
	cv.waitKey()


RESIZE = False
final_img_width, final_img_height = 320, 80
output_dir = '../ml/new_ui_keys/synth_full_size'
SAVE_IMAGES = True
SHOW_IMAGES = False
CENTER_CROP = False

def gen_images(amnt):
	if not os.path.exists(output_dir):
		os.mkdir(output_dir)
		print(f'make dir: {output_dir}')
	backs_names = os.listdir(blank_folder)
	keys_back = cv.imread('keys_avg.tiff')
	key_masks = [np.float32(cv.imread('mask' + str(i) + '.tiff'))/255.0 for i in range(4)]
	key_dark_masks = [np.float32(cv.imread('dark_mask' + str(i) + '.tiff', 1))/255.0 for i in range(4)]
	for key_mask in key_masks:
		key_mask /= np.max(key_mask)
	for i in tqdm(range(amnt)):
		# print(backs_names[random.randrange(len(backs_names))])
		back_img = cv.imread(os.path.join(blank_folder, backs_names[random.randrange(len(backs_names))]))
		if CENTER_CROP:
			x, y = random.randrange(rand_x1, rand_x2), random.randrange(rand_y1, rand_y2)
		else:
			x, y = random.randrange(0, back_img.shape[1] - (frame_w+pad*2+dev_x)), random.randrange(0, back_img.shape[0] - (frame_h+pad*2+dev_y))
		img = back_img[y:y+frame_h+pad*2+dev_y,x:x+frame_w+pad*2+dev_x]
		place_x, place_y = pad + random.randrange(dev_x), pad + random.randrange(dev_y)
		img[place_y:place_y+ignore_y,place_x:place_x+frame_w] = keys_back[:ignore_y,:]
		bar_width = int(bar_min_perc*frame_w) + random.randrange(frame_w - int(bar_min_perc*frame_w))
		img[place_y+ignore_y:place_y+frame_h,place_x:place_x+bar_width] = keys_back[ignore_y:frame_h,:bar_width]
		color = (random.randrange(256), random.randrange(256), random.randrange(256))
		x, y = kx1 - frame_x1, ky1 - frame_y1
		sequence = [random.randrange(4) for i in range(random.randrange(2, 10))]
		for key in sequence:
			# print(place_y, y, key_masks[key].shape[0])
			img[place_y+y:place_y+y+key_masks[key].shape[0],place_x+x:place_x+x+key_masks[key].shape[1]] = img[place_y+y:place_y+y+key_masks[key].shape[0],place_x+x:place_x+x+key_masks[key].shape[1]] * (1-key_masks[key]) + color * key_masks[key]
			img[place_y+y:place_y+y+key_masks[key].shape[0],place_x+x:place_x+x+key_masks[key].shape[1]] = img[place_y+y:place_y+y+key_masks[key].shape[0],place_x+x:place_x+x+key_masks[key].shape[1]] * (1-key_dark_masks[key])
			x += kdi
		if RESIZE:
			scaled_img = cv.resize(img, (final_img_width, final_img_height))
		else:
			scaled_img = img
		if SHOW_IMAGES:
			print(img.shape)
			cv.imshow('large_img', scale_img(img, 3))
			cv.imshow('scaled_img', scaled_img)
			cv.waitKey()
		if SAVE_IMAGES:
			folder_path = f'{output_dir}/{str(uuid.uuid4())}'
			os.mkdir(folder_path)
			with open(f'{folder_path}/info.csv', 'w+') as f:
				f.write(f'{place_x-pad+min_x},{place_y-pad+min_y},"{sequence}"')
			cv.imwrite(f'{folder_path}/frame0.jpg', scaled_img)
	cv.destroyAllWindows()

gen_images(20000)