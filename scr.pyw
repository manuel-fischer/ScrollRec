#!/usr/bin/python3

 #  #
######
 #  #    Scroll Record  --  by Manuel Fischer
######
 #  #

import sys
import tkinter as tk
from tkinter import ttk
import string

# LINUX: xclip should be installed!

from PIL import Image
from PIL import ImageTk # sudo apt-get install python3-pil python3-pil.imagetk


#try:
#from PIL import ImageGrab
#grab_screenshot = ImageGrab.grab

IS_WIN = 'win32' in str(sys.platform).lower()

if IS_WIN:
    from scr_win import grab_screenshot, clipboard_set_image
else:
    from scr_linux import grab_screenshot, clipboard_set_image

#ImageGrab.grab([rect]).show()
import os

REC_INTERVAL = 1

SCALE = 1

BSZ = 5 # bordersize
BTN_W = int(150*SCALE) # button bar width
BTN_H = int(24*SCALE) # button bar height
BTN_S = int(32*SCALE) # button size, (width of single button)
BTN_ICON_SIZE = int(16*SCALE)

CRN = 18 # cornersize
CRB = CRN-BSZ # cornersize minus bordersize

x = 200
y = 100
w = 500
h = 300

of_x = of_y = 0

btn_w = w+2*BTN_W

BORDER_COLOR = "#ffff00"
IDLE_COLOR = "#000060"
REC_COLORS = ["#a00000", "#ff2010"]

rec_color = 0



def check_smaller(val, boundary, length, on_none = False):
    if boundary is None: return on_none
    if boundary < 0: boundary += length
    return val < boundary

def check_greater(val, boundary, length):
    return not check_smaller(val, boundary, length, True)

def apply_drag(win, drag_regions):
    last_x, last_y = 0, 0 # screen x / y
    cur_region = 0
    dragging = False
    current_cursor = None

    def update_region(x, y):
        nonlocal cur_region, current_cursor
        if dragging:
            if current_cursor:
                win["cursor"] = current_cursor[1]
            return
        win_w, win_h = win.winfo_width(), win.winfo_height()

        cur_region = None
        # find region
        for i, (rect, drag_fn, cursor) in enumerate(drag_regions):
            l, t, r, b = rect

            if check_smaller(x, l, win_w): continue
            if check_greater(x, r, win_w): continue

            if check_smaller(y, t, win_h): continue
            if check_greater(y, b, win_h): continue

            cur_region = i
            break

        current_cursor = None
        if cur_region is None:
            win["cursor"] = "arrow"
        else:
            rect, drag_fn, cursor = drag_regions[cur_region]
            if isinstance(cursor, list):
                current_cursor = cursor
                cursor = cursor[0]
            win["cursor"] = cursor

    def motion(event):
        update_region(event.x, event.y)

    def enter(event):
        update_region(event.x, event.y)
    
    def start_drag(event):
        nonlocal last_x, last_y, cur_region, dragging
        global of_x, of_y

        update_region(event.x, event.y)
        
        if cur_region is None: return
        if event.num != 1: return

        if dragging: return

        dragging = True
        update_region(event.x, event.y)
        
        wx, wy = win.winfo_x(), win.winfo_y()
        last_x, last_y = event.x+wx, event.y+wy

        of_x = of_y = 0

        liftall()

    def drag_motion(event):
        nonlocal last_x, last_y
        
        if cur_region is None: return
        
        wx, wy = win.winfo_x(), win.winfo_y()
        cur_x, cur_y = event.x+wx, event.y+wy

        dx = cur_x - last_x
        dy = cur_y - last_y
        
        last_x, last_y = cur_x, cur_y

        rect, drag_fn, cursor = drag_regions[cur_region]
        drag_fn(dx, dy)

        assert w >= 1
        assert h >= 1
        
        #last_x, last_y = event.x-dx, event.y-dy
        update_windows()

    def stop_drag(event):
        nonlocal dragging
        if event.num != 1: return
        dragging = False
        update_region(event.x, event.y)
        
    win.bind('<ButtonPress>', start_drag)
    win.bind('<ButtonRelease>', stop_drag)
    win.bind('<Enter>', enter)
    win.bind('<Motion>', motion)
    win.bind('<B1-Motion>', drag_motion)

def make_border(master, fmt, drag_regions):
    win = tk.Toplevel(master)
    win.geometry(fmt())
    win.attributes('-topmost', True)
    if IS_WIN:
        win.attributes('-toolwindow', True)
        win.attributes('-alpha', '0.6')
    else:
        win.wm_attributes('-alpha', '0.6')

    win.overrideredirect(1)
    win["bg"] = BORDER_COLOR


    apply_drag(win, drag_regions)

    return (win, fmt)




def drag_move(dx, dy):
    global x, y, w, h, of_x, of_y
    if not recording: x += dx
    y += dy

def drag_top(dx, dy):
    global x, y, w, h, of_x, of_y
    #y += dy
    #h -= dy
    y += dy + of_y
    h -= dy + of_y
    if h < 1: of_y = -h+1; h += of_y; y -= of_y
    else:     of_y = 0
    
def drag_bot(dx, dy):
    global x, y, w, h, of_x, of_y
    #h += dy
    h += dy - of_y
    if h < 1: of_y = -h+1; h += of_y
    else:     of_y = 0

def drag_lft(dx, dy):
    global x, y, w, h, of_x, of_y
    if recording: return
    #x += dx
    #w -= dx
    x += dx + of_x
    w -= dx + of_x
    if w < 1: of_x = -w+1; w += of_x; x -= of_x
    else:     of_x = 0

def drag_rgt(dx, dy):
    global x, y, w, h, of_x, of_y
    if recording: return
    #w += dx
    w += dx - of_x
    if w < 1: of_x = -w+1; w += of_x
    else:     of_x = 0

def drag_both(a, b):
    def drag(dx, dy):
        a(dx, dy)
        b(dx, dy)

    return drag

winBtn = tk.Tk()

def winBtnFmt():
    global btn_w
    
    xx = x-BSZ
    ww = w+2*BSZ
    if xx < 0:
        ww += xx
        xx = 0
    ww = max(ww, BTN_W)
    btn_w = ww
    
    yy = y-BSZ-BTN_H
    if yy < 0: yy = y+h+BSZ
    
    return f"{ww}x{BTN_H}+{xx}+{yy}"


# https://www.tcl.tk/man/tcl8.4/TkCmd/cursors.html
if IS_WIN:
    CUR_MOVE = "size"
    CUR_MOVING = "size"

    # Corners
    CUR_SIZE_NW = "size_nw_se"
    CUR_SIZE_SE = "size_nw_se"
    CUR_SIZE_NE = "size_ne_sw"
    CUR_SIZE_SW = "size_ne_sw"

    # Borders
    CUR_SIZE_S = "size_ns"
    CUR_SIZE_S = "size_ns"
    CUR_SIZE_W = "size_we"
    CUR_SIZE_E = "size_we"
else:
    CUR_MOVE = "hand1" # DOWN: "fleur"
    CUR_MOVING = "fleur"

    # Corners
    CUR_SIZE_NW = "top_left_corner"
    CUR_SIZE_SE = "bottom_right_corner"
    CUR_SIZE_NE = "top_right_corner"
    CUR_SIZE_SW = "bottom_left_corner"

    #CUR_SIZE_NW, CUR_SIZE_SE = CUR_SIZE_SE, CUR_SIZE_NW # fix offset
    #CUR_SIZE_NE, CUR_SIZE_SW = CUR_SIZE_SW, CUR_SIZE_NE # fix offset

    CUR_SIZE_N = "top_side"
    CUR_SIZE_S = "bottom_side"
    CUR_SIZE_W = "left_side"
    CUR_SIZE_E = "right_side"



winBtn.geometry(winBtnFmt())
winBtn.attributes('-topmost', True)
if IS_WIN:
    winBtn.attributes('-toolwindow', True)
    winBtn.attributes('-alpha', '0.9')
else:
    winBtn.wm_attributes('-alpha', '0.9')

winBtn.overrideredirect(1)
winBtn["bg"] = IDLE_COLOR
apply_drag(winBtn, [([2*BTN_S, None, -BTN_H, None], drag_move, [CUR_MOVE, CUR_MOVING])])

style = ttk.Style()
style.theme_use("default")

def darken_color(hexstr, i = 1):
    darken_x = lambda c: string.hexdigits[max(0, int(c, 16)-i)] if c.lower() in string.hexdigits else c
    return "".join(map(darken_x, hexstr))

def lighten_color(hexstr, i = 1):
    darken_x = lambda c: string.hexdigits[min(15, int(c, 16)+i)] if c.lower() in string.hexdigits else c
    return "".join(map(darken_x, hexstr))

def set_highlight_color(color):
    winBtn["bg"] = color
    style.configure("Window.TButton",
                    foreground="#ffffff",
                    background=color,
                    relief="flat",
                    borderwidth=0
    )

    style.map("Window.TButton",
        foreground=[('pressed', "#ffffff"), ('active', "#ffffff")],
        background=[('pressed', darken_color(color, 4)), ('active', lighten_color(color, 3))],
    )



img_storage = []

def load_icon(name):
    img = Image.open(f"icons/{name}.png").convert("RGBA")
    img = img.resize((img.width*BTN_ICON_SIZE//img.height, BTN_ICON_SIZE))
    pimg = ImageTk.PhotoImage(img)
    #pimg = tk.PhotoImage(file=fn)
    img_storage.append(pimg)
    return pimg



set_highlight_color(IDLE_COLOR)

def do_prt():
    img = grab_screenshot([x, y, x+w, y+h])

    clipboard_set_image(img)


btnPrt = ttk.Button(winBtn, image=load_icon("prt"), command=do_prt, style="Window.TButton")
btnPrt.place(x=0, y=0, h=BTN_H, w=BTN_S)

recording = False
rec_img = None
def keep_recording():
    if recording:
        winBtn.after(REC_INTERVAL, do_record_frame)

def calc_pix_loss(a, b):
    ar, ag, ab = a
    br, bg, bb = b
    dr = ar-br
    dg = ag-bg
    db = ab-bb
    return dr*dr + dg*dg + db*db

def do_record_frame():
    if not recording: return
    global rec_img, rec_color
    #print("record frame")
    

    rec_color ^= 1
    color = REC_COLORS[rec_color]
    set_highlight_color(color)

    iw, ih = rec_img.size if rec_img else (w, 0)

    curframe = grab_screenshot([x, y, x+w, y+h]).convert('RGB')

    SW = 1#8
    xx = 0
    MAX_DY = h//2
    MAX_LOSS = 1

    # find out stitching position
    if rec_img:
        r_img = rec_img.resize((SW, ih), Image.ANTIALIAS)
        c_img = curframe.resize((SW, h), Image.ANTIALIAS)

        r_dat = r_img.load()
        c_dat = c_img.load()

        low_pos  = ih
        low_loss = float('inf')
        for iy in range(ih-h-MAX_DY, ih-h+MAX_DY):
            cur_loss = 0
            dy = min(ih-iy, h)
            dy = max(dy, 1)
            
            max_loss = MAX_LOSS*dy
            for yy in range(0+10, dy-10):
                #for xx in range(SW):
                cur_loss += calc_pix_loss(r_dat[xx, iy+yy], c_dat[xx, yy])
                if cur_loss > max_loss: break
                
            else:
                cur_loss /= dy
                if cur_loss < low_loss:
                    low_pos  = iy
                    low_loss = cur_loss

        print(f"{low_loss=} {low_pos=} dy={ih-low_pos-h}")
        
        paste_y = low_pos
    else:
        paste_y = 0


    # create new image
    ih = paste_y+h
    n_img = Image.new('RGB', (iw, ih))

    if rec_img:
        n_img.paste(rec_img, (0, 0))

    n_img.paste(curframe, (0, paste_y))

    rec_img = n_img

    keep_recording()

def do_toggle_rec():
    global recording, rec_img
    recording = not recording
    rec_color = 0
    color = REC_COLORS[0] if recording else IDLE_COLOR
    set_highlight_color(color)

    if not recording:
        # copy to clipboard
        clipboard_set_image(rec_img)

    rec_img = None
    keep_recording()
    
btnRec = ttk.Button(winBtn, image=load_icon("rec"), command=do_toggle_rec, style="Window.TButton")
btnRec.place(x=BTN_S, y=0, h=BTN_H, w=BTN_S)



rect_shown = True
def do_toggle_rect():
    global rect_shown
    rect_shown = not rect_shown
    for win, *_ in rect_windows:
        if rect_shown:
            win.deiconify()
        else:
            win.withdraw()




btnTRect = ttk.Button(winBtn, image=load_icon("min"), command=do_toggle_rect, style="Window.TButton") # also closes border
btnClose = ttk.Button(winBtn, image=load_icon("x"), command=winBtn.destroy, style="Window.TButton") # also closes border




def update_layout():
    btnTRect.place(x=btn_w-2*BTN_H, y=0, h=BTN_H, w=BTN_H)
    btnClose.place(x=btn_w-1*BTN_H, y=0, h=BTN_H, w=BTN_H)

update_layout()

winTop = make_border(winBtn, lambda: f"{2*BSZ+w}x{BSZ}+{x-BSZ}+{y-BSZ}", [
    ([None, None,  CRN, None], drag_both(drag_lft, drag_top), CUR_SIZE_NW),
    ([-CRN, None, None, None], drag_both(drag_rgt, drag_top), CUR_SIZE_NE),
    ([None, None, None, None], drag_top, CUR_SIZE_N)
])
winBot = make_border(winBtn, lambda: f"{2*BSZ+w}x{BSZ}+{x-BSZ}+{y+h}", [
    ([-CRN, None, None, None], drag_both(drag_rgt, drag_bot), CUR_SIZE_SE),
    ([None, None,  CRN, None], drag_both(drag_lft, drag_bot), CUR_SIZE_SW),
    ([None, None, None, None], drag_bot, CUR_SIZE_S)
])
winLft = make_border(winBtn, lambda: f"{BSZ}x{h}+{x-BSZ}+{y}", [
    ([None, None, None,  CRB], drag_both(drag_lft, drag_top), CUR_SIZE_NW),
    ([None, -CRB, None, None], drag_both(drag_lft, drag_bot), CUR_SIZE_SW),
    ([None, None, None, None], drag_lft, CUR_SIZE_W)
])
winRgt = make_border(winBtn, lambda: f"{BSZ}x{h}+{x+w}+{y}", [
    ([None, -CRB, None, None], drag_both(drag_rgt, drag_bot), CUR_SIZE_SE),
    ([None, None, None,  CRB], drag_both(drag_rgt, drag_top), CUR_SIZE_NE),
    ([None, None, None, None], drag_rgt, CUR_SIZE_E)
])

rect_windows = [
    winTop,
    winBot,
    winLft,
    winRgt,
]

windows = [
    (winBtn, winBtnFmt),
    *rect_windows,
]
    

def update_windows():
    global x, y, w, h
    #if w < 1: w = 1
    #if h < 1: h = 1
    assert w >= 1
    assert h >= 1
    
    for win, fmt in windows:
        win.geometry(fmt())
        
    update_layout()
    
    for win, fmt in windows:
        win.update()

    if not IS_WIN:
        winBtn.attributes('-alpha', '0.9')
        for win, fmt in rect_windows:
            win.wm_attributes('-alpha', '0.6')

def liftall():
    for win, fmt, in windows:
        win.lift()

liftall()

if not IS_WIN:
    winBtn.wait_visibility()
    update_windows()

winBtn.mainloop()


