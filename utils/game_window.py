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

        self.window_info, self.window_handle = self.find_window()
        self.rect = WindowRect(self.window_handle)

    def move_to_foreground(self):
        user32.SetForegroundWindow(self.window_handle)
        time.sleep(0.1)

    def grab_frame(self):
        with mss.mss() as sct:
            self.rect.update()
            monitor = {"top": self.rect.top, "left": self.rect.left, "width": self.rect.width, "height": self.rect.height}
            return np.array(sct.grab(monitor))[:, :, :-1]

    def local_to_global(self, point):
        return np.array([point[0] + self.rect.left, point[1] + self.rect.top])

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

            if title.value.startswith(self.name):
                results.append((WindowInfo(pid.value, title.value), hWnd))
            return True
        user32.EnumWindows(enum_proc, 0)
        return None if len(results) == 0 else results[0]

class WindowRect():
    def __init__(self, window_handle):
        self.window_handle = window_handle
        self.update()

    def update(self):
        rect = wintypes.RECT()
        user32.GetWindowRect(self.window_handle, ctypes.byref(rect))

        self.left = rect.left
        self.right = rect.right
        self.width = abs(rect.right - rect.left)

        self.top = rect.top
        self.bottom = rect.bottom
        self.height = abs(rect.bottom - rect.top)

    def center(self):
        x = int(self.left + self.width / 2)
        y = int(self.top + self.height / 2)
        print("{} {}".format(self.bottom, self.top))
        return (x, y)
