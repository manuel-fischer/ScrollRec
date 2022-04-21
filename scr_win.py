import sys
import os
import subprocess
from subprocess import Popen, PIPE
from PIL import Image


AV_LOG_QUIET   = "quiet"
AV_LOG_PANIC   = "panic"
AV_LOG_FATAL   = "fatal"
AV_LOG_ERROR   = "error"
AV_LOG_WARNING = "warning"
AV_LOG_INFO    = "info"
AV_LOG_VERBOSE = "verbose"
AV_LOG_DEBUG   = "debug"

ffmpeg_loglevel = AV_LOG_ERROR


IS_WIN32 = 'win32' in str(sys.platform).lower()
SUBPROCESS_ARGS = {}
if IS_WIN32:
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    SUBPROCESS_ARGS['startupinfo'] = startupinfo


def screen_size():
    return 1920, 1080

def take_screenshot(x=0,y=0,w=None,h=None):
    fn = "output.png"
    
    rect = []
    if x: rect += ["-offset_x", f"{x}"]
    if y: rect += ["-offset_y", f"{y}"]
    if w: rect += ["-video_size", f"{w}x{h}"]
    else: w, h = screen_size()
    
    cmd = [
        'ffmpeg',
        '-f', 'gdigrab',
        '-draw_mouse', '0',
        *rect,
        '-i', 'desktop',
        '-frames:v', '1',
        '-vf', 'format=rgba',
        '-f', 'rawvideo',
        '-',
        
        # logging
        '-loglevel', ffmpeg_loglevel,
        '-hide_banner',
    ]


    process = Popen(cmd, stdout=PIPE, stderr=PIPE, **SUBPROCESS_ARGS)
    stdout, stderr = process.communicate()
    print(stderr.decode(), end='', file=sys.stderr)
    img = Image.frombytes('RGBA', (w, h), stdout, 'raw')
    
    return img

def grab_screenshot(rect_points):
    x0, y0, x1, y1 = rect_points
    return take_screenshot(x0, y0, x1-x0, y1-y0)

if __name__ == "__main__":
    img = take_screenshot(100, 100, 200, 300)
    img.show()
