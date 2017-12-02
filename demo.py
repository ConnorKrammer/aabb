import tkinter
from proximal import get_closest

# Constants
CANVAS_SIZE = 900
RL = CANVAS_SIZE / 3 / 2 # distance from center to rect corners
OL = CANVAS_SIZE * 10 # gridline length (extends past visible area)
RECT = (-RL, -RL, RL, RL)
SHIFT_KEYCODE = 16

# GUI state
current_line = None
closest_line = None
snap_to_axis = False

def enable_snap_to_axis(event):
    global snap_to_axis
    if event.keycode == SHIFT_KEYCODE:
        snap_to_axis = True
        update_lines(event)

def disable_snap_to_axis(event):
    global snap_to_axis
    if event.keycode == SHIFT_KEYCODE:
        snap_to_axis = False
        update_lines(event)

def place_endpoint(event):
    global current_line
    global closest_line

    if not current_line:
        x0, y0 = canvas.canvasx(event.x), canvas.canvasy(event.y)
        current_line = canvas.create_line(x0, y0, x0, y0, fill='#000000', width=4, capstyle='round')
        closest_line = canvas.create_line(x0, y0, x0, y0, fill='#f30f30', capstyle='round')
        update_lines(event)
    else:
        current_line = None
        canvas.itemconfig(closest_line, fill='#a30a30')

def cancel_line(event):
    global current_line
    global closest_line

    if current_line:
        canvas.delete(current_line)
        canvas.delete(closest_line)
        current_line = None
        closest_line = None

def update_lines(event):
    if not current_line:
        return

    x0, y0 = tuple(canvas.coords(current_line)[0:2])
    x1, y1 = canvas.canvasx(event.x), canvas.canvasy(event.y)

    if snap_to_axis:
        if abs(x0 - x1) < abs(y0 - y1):
            x1 = x0
        else:
            y1 = y0

    closest = get_closest(x0, y0, x1, y1, *RECT)

    if len(closest) == 2:
        closest *= 2

    if closest[0:2] == closest[2:4]:
        canvas.itemconfig(closest_line, width=15)
    else:
        canvas.itemconfig(closest_line, width=5)

    canvas.coords(closest_line, *closest)
    canvas.coords(current_line, x0, y0, x1, y1)

def resize_canvas(event):
    w, h = event.width, event.height
    canvas.config(scrollregion=(-w/2, -h/2, w/2, h/2))
    canvas.xview_moveto(0)
    canvas.yview_moveto(0)

# Initialize GUI
root = tkinter.Tk()
canvas = tkinter.Canvas(root, width=CANVAS_SIZE, height=CANVAS_SIZE, background='#ffffff', confine=False)
canvas.pack(fill='both', expand=1)

# Event bindings for interactivity
root.bind('<KeyPress>', enable_snap_to_axis)
root.bind('<KeyRelease>', disable_snap_to_axis)
root.bind('<Escape>', cancel_line)
canvas.bind('<Configure>', resize_canvas)
canvas.bind('<1>', place_endpoint)
canvas.bind('<Motion>', update_lines)

# Background grid
canvas.create_line(-RL, -OL, -RL,  OL, fill='#eeeeee', width=4)
canvas.create_line( RL, -OL,  RL,  OL, fill='#eeeeee', width=4)
canvas.create_line(-OL, -RL,  OL, -RL, fill='#eeeeee', width=4)
canvas.create_line(-OL,  RL,  OL,  RL, fill='#eeeeee', width=4)

# Main rectangle
canvas.create_rectangle(*RECT, outline='#000000', width=4)

# Start GUI loop
root.mainloop()
