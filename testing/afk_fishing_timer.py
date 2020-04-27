import os, sys, time
import cv2 as cv
import pyautogui

my_dir = os.path.dirname(sys.argv[0])
sys.path.append(os.path.join(my_dir, '../'))
from utils.game_window import GameWindow


start_target_x = 588
start_target_y = 197
target_thresh = 5


comp_path = "../resources/fishing_space_bar.jpg"
comp_img = cv.imread(comp_path, 0)

window = GameWindow("BLACK DESERT")
window.move_to_foreground()

point = window.rect.center()
pyautogui.moveTo(point[0], point[1], duration=2)

seen_thresh = 100
enter_time = time.time()
last_seen = time.time()
finish_time = time.time()
frames_since_seen = seen_thresh+1
while True:
    img = window.grab_frame()
    stream_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    method = cv.TM_SQDIFF
    result = cv.matchTemplate(comp_img, stream_gray, method)
    mn, _, mnLoc, _ = cv.minMaxLoc(result)
    MPx, MPy = mnLoc
    if (MPx > start_target_x - target_thresh and MPx < start_target_x + target_thresh and MPy > start_target_y - target_thresh and MPy < start_target_y + target_thresh):
        print('Yes')
        if frames_since_seen > seen_thresh:
            bite_time = time.time() - finish_time
            print(f'Entered afk, bite time: {bite_time}')
            with open('bite_times.txt', 'a+') as f:
                f.write(f'{bite_time}\n')
            enter_time = time.time()
        last_seen = time.time()
        frames_since_seen = 0
    else:
        print('No')
        frames_since_seen += 1
        if frames_since_seen == seen_thresh:
            finish_time = last_seen
            afk_time = last_seen - enter_time
            print(afk_time)
            time.sleep(1)
            with open('afk_fishing_times.txt', 'a+') as f:
                f.write(f'{afk_time}\n')

    time.sleep(0.1)
