import numpy as np
import cv2 as cv
import os, csv

csv_name = 'info.csv'

frame_x1, frame_y1, frame_x2, frame_y2 = 449, 371, 817, 428
cut_pad = 50
scale_ratio = 4
kx, ky, kdx, kdy, kdi = 463, 380, 30, 30, 35

base = '../../../ref_images/'
key_colors = [cv.imread(base+'w_key_color.tiff', 1), cv.imread(base+'a_key_color.tiff', 1), cv.imread(base+'s_key_color.tiff', 1), cv.imread(base+'d_key_color.tiff', 1)]
h, w, _ = key_colors[0].shape

folders = []
folders_raw = os.listdir('.')
for folder in folders_raw:
	if os.path.isdir(folder):
		folders.append(folder)

class image_show:
	folder_index = 0
	def reset():
		image_show.key_index = 0
		image_show.edit_key = False
		image_show.has_saved = True
		image_show.key_seq = []
		folder = folders[image_show.folder_index]
		with open(os.path.join(folder, csv_name), 'r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
			for row in csv_reader:
				x, y, keys = row
				image_show.x_off = int(x)
				image_show.y_off = int(y)
				i = 1
				while (i < len(keys) and keys[i] != ']'):
					image_show.key_seq.append(int(keys[i]))
					i += 3
				image_show.has_key = True
				break

	def reload():
		folder = folders[image_show.folder_index]
		x, y = image_show.x_off, image_show.y_off
		# print('{} - x: {}, y: {}, keys: {}'.format(folder, x, y, keys))
		img = cv.imread(os.path.join(folder, 'frame0.jpg'), 1)
		cv.rectangle(img, (frame_x1+x, frame_y1+y), (frame_x2+x, frame_y2+y), (255, 0, 0))
		for i in range(len(image_show.key_seq)):
			key = key_colors[image_show.key_seq[i]]
			mask = key[:,:,2] > 150
			snipped = img[ky+y:ky+y+h,kx+x+i*kdi:kx+x+w+i*kdi]
			snipped[mask] = (0, 255, 0)
		if image_show.edit_key:
			cv.rectangle(img, (kx+x+image_show.key_index*kdi, ky+y), (kx+x+w+image_show.key_index*kdi, ky+y+h), (0, 0, 255))

		img_small = img[frame_y1+y-cut_pad:frame_y2+y+cut_pad,frame_x1+x-cut_pad:frame_x2+x+cut_pad]
		cv.putText(img_small, (folder + ("" if image_show.has_saved else " *")), (0, img_small.shape[0]-5), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))

		img_scaled = cv.resize(img_small, (img_small.shape[1]*scale_ratio, img_small.shape[0]*scale_ratio))
		cv.imshow('img', img_scaled)

	def save():
		folder = folders[image_show.folder_index]
		with open(os.path.join(folder, csv_name), mode="w") as csv_file:
			csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			csv_writer.writerow([image_show.x_off, image_show.y_off, image_show.key_seq])
		image_show.has_saved = True

def inc_image(amnt):
	fi = image_show.folder_index + amnt
	if (fi < 0):
		fi += len(folders)
	elif (fi >= len(folders)):
		fi -= len(folders)
	image_show.folder_index = fi
	image_show.reset()
	image_show.reload()

def move_offset(x, y):
	image_show.x_off += x
	image_show.y_off += y
	image_show.has_saved = False
	image_show.reload()

def inc_key_index():
	if image_show.key_index < len(image_show.key_seq):
		image_show.key_index += 1
		image_show.reload()
	else:
		print('index out of range')

def edit_key(key):
	if key == -1:
		if image_show.key_index == len(image_show.key_seq) - 1:
			del image_show.key_seq[-1]
			image_show.has_saved = False
		else:
			print('can not delete key that is not at the end')
	else:
		if image_show.key_index == len(image_show.key_seq):
			image_show.key_seq.append(key)
		else:
			image_show.key_seq[image_show.key_index] = key
		image_show.has_saved = False
		inc_key_index()
	image_show.reload()

image_show.reset()
image_show.reload()
while 1:
	changed = True
	key = cv.waitKey() & 0xEFFFFF
	if not image_show.edit_key:
		if (key == 119): # w key
			move_offset(0, -1)
		elif (key == 97): # a key
			move_offset(-1, 0)
		elif (key == 115): # s key
			move_offset(0, 1)
		elif (key == 100): # d key
			move_offset(1, 0)
		elif (key == 101): # e key
			image_show.edit_key = True
			image_show.reload()
		elif (key == 122): # z key
			if image_show.has_saved:
				inc_image(-1)
			else:
				print('can not leave staged changes')
		elif (key == 99): # c key
			if image_show.has_saved:
				inc_image(1)
			else:
				print('can not leave staged changes')
		elif (key == 27): # ESC key
			break
		elif (key == 9): # Tab key
			image_show.save()
			image_show.reload()
		elif (key == 116): # t key
			image_show.reset()
			image_show.reload()
		else:
			changed = False
	else: # editing
		if (key == 119): # w key
			edit_key(0)
		elif (key == 97): # a key
			edit_key(1)
		elif (key == 115): # s key
			edit_key(2)
		elif (key == 100): # d key
			edit_key(3)
		elif (key == 113): # q key
			image_show.edit_key = False
			image_show.reload()
		elif (key == 120): # x key
			edit_key(-1)
		elif (key == 122): # z key
			if image_show.key_index > 0:
				image_show.key_index -= 1
				image_show.reload()
			else:
				print('index out of range')
		elif (key == 99): # c key
			inc_key_index()
		elif (key == 9): # Tab key
			image_show.save()
			image_show.edit_key = False
			image_show.reload()
		elif (key == 116): # t key
			image_show.reset()
			image_show.reload()
		elif (key == 27): # ESC key
			break
		else:
			changed = False
cv.destroyAllWindows()
