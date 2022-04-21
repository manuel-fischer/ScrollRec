from PIL import Image
from ffmpeg_util import popen_ffmpeg
import tempfile
import os

# Clipboard: possible better solution:
# https://stackoverflow.com/questions/3571855/pasting-image-to-clipboard-in-python-in-linux

def take_screenshot(x,y,w,h):
    fn = "output.png"
    
    args = [
        '-video_size', f'{w}x{h}',

        '-f', 'x11grab',
        '-draw_mouse', '0',

        # Rectangle
        '-i', f':0.0+{x},{y}',
        
        '-frames:v', '1',
        '-vf', 'format=rgba',
        '-f', 'rawvideo',
        '-',
    ]

    stdout, _ = popen_ffmpeg(args)
    img = Image.frombytes('RGBA', (w, h), stdout, 'raw')
    return img

def grab_screenshot(rect_points):
    x0, y0, x1, y1 = rect_points
    return take_screenshot(x0, y0, x1-x0, y1-y0)


def clipboard_set_image(img):
    with tempfile.NamedTemporaryFile(suffix=".png") as tmpfile:
        img.save(tmpfile.name, "PNG")
        #assert os.path.exists(tmpfile.name)
        cmd = f'xclip -i -selection clipboard -t image/png {tmpfile.name}'
        os.system(cmd)


if __name__ == "__main__":
    img = take_screenshot(100, 100, 200, 300)
    img.show()



# 