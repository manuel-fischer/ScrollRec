from PIL import Image
from ffmpeg_util import popen_ffmpeg

import io
import win32clipboard as wclp

def take_screenshot(x,y,w,h):
    fn = "output.png"
    
    args = [
        '-f', 'gdigrab',
        '-draw_mouse', '0',

        # Rectangle
        '-offset_x', f'{x}',
        '-offset_y', f'{y}',
        '-video_size', f'{w}x{h}',

        '-i', 'desktop',
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





# stackoverflow.com/21319486
# stackoverflow.com/34322132
# windows only
def clipboard_set_image(img):

    output = io.BytesIO()
    img.convert('RGB').save(output, 'BMP')
    data = output.getvalue()[14:] # skip bmp file header
    output.close()
    

    wclp.OpenClipboard()
    wclp.EmptyClipboard()
    wclp.SetClipboardData(wclp.CF_DIB, data)
    wclp.CloseClipboard()



if __name__ == "__main__":
    img = take_screenshot(100, 100, 200, 300)
    img.show()
