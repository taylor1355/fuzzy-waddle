import ctypes
from ctypes import wintypes
from collections import namedtuple
import numpy as np
import cv2 as cv
import time
import mss

user32 = ctypes.WinDLL('user32', use_last_error=True)

def check_zero(result, func, args):
    if not result:
        err = ctypes.get_last_error()
        if err:
            raise ctypes.WinError(err)
    return args

if not hasattr(wintypes, 'LPDWORD'): # PY2
    wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)

WindowInfo = namedtuple('WindowInfo', 'pid title')

WNDENUMPROC = ctypes.WINFUNCTYPE(
    wintypes.BOOL,
    wintypes.HWND,    # _In_ hWnd
    wintypes.LPARAM,) # _In_ lParam

user32.EnumWindows.errcheck = check_zero
user32.EnumWindows.argtypes = (
   WNDENUMPROC,      # _In_ lpEnumFunc
   wintypes.LPARAM,) # _In_ lParam

user32.IsWindowVisible.argtypes = (
    wintypes.HWND,) # _In_ hWnd

user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetWindowThreadProcessId.argtypes = (
  wintypes.HWND,     # _In_      hWnd
  wintypes.LPDWORD,) # _Out_opt_ lpdwProcessId

user32.GetWindowTextLengthW.errcheck = check_zero
user32.GetWindowTextLengthW.argtypes = (
   wintypes.HWND,) # _In_ hWnd

user32.GetWindowTextW.errcheck = check_zero
user32.GetWindowTextW.argtypes = (
    wintypes.HWND,   # _In_  hWnd
    wintypes.LPWSTR, # _Out_ lpString
    ctypes.c_int,)   # _In_  nMaxCount

class GameWindow():
    def __init__(self, name):
        self.name = name

        self.window_info, self.window_handle, self.rect = self.find_window()
        print("{} {} {}".format(self.window_info, self.window_handle, self.rect))
        if self.window_info == None:
            print("Could not find {} window".format(self.name))

    def move_to_foreground(self):
        user32.SetForegroundWindow(self.window_handle)
        time.sleep(0.1)

    def grab_frame(self):
        with mss.mss() as sct:
            monitor = {"top": self.rect.bottom, "left": self.rect.left, "width": self.rect.width, "height": self.rect.height}
            return np.array(sct.grab(monitor))

    def local_to_global(self, point):
        return np.array([point[0] + self.rect.left, point[1] + self.rect.bottom])

    def find_window(self):
        results = []
        @WNDENUMPROC
        def enum_proc(hWnd, lParam):
            #if user32.IsWindowVisible(hWnd):
            pid = wintypes.DWORD()
            tid = user32.GetWindowThreadProcessId(hWnd, ctypes.byref(pid))

            length = user32.GetWindowTextLengthW(hWnd) + 1
            title = ctypes.create_unicode_buffer(length)
            user32.GetWindowTextW(hWnd, title, length)

            rect = wintypes.RECT()
            user32.GetWindowRect(hWnd, ctypes.byref(rect))

            if title.value.startswith(self.name):
                results.append((WindowInfo(pid.value, title.value), hWnd, Rect(rect.left, rect.right, rect.bottom, rect.top)))
            return True
        user32.EnumWindows(enum_proc, 0)
        return None if len(results) == 0 else results[0]

class Rect():
    def __init__(self, left, right, top, bottom):
        self.left = left
        self.right = right
        self.width = right - left

        self.top = top
        self.bottom = bottom
        self.height = abs(top - bottom)

    def center(self):
        x = int(self.left + self.width / 2)
        y = int(self.bottom + self.height / 2)
        return (x, y)
