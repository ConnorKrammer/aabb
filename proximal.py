# Zone code bitmasks
INSIDE = 0b0000;
LEFT   = 0b0001;
RIGHT  = 0b0010;
BOTTOM = 0b0100;
TOP    = 0b1000;

def get_zonecode(x, y, xmin, ymin, xmax, ymax):
    """
    Return a bit code indicating point's position relative to rect.

    """
    if x < xmin:
        code = LEFT
    elif x > xmax:
        code = RIGHT
    else:
        code = INSIDE

    if y < ymin:
        code |= BOTTOM
    elif y > ymax:
        code |= TOP

    return code

def clamp(x, xmin, xmax):
    """
    Return x clamped to (xmin, xmax).

    """
    if x < xmin: return xmin
    if x > xmax: return xmax
    return x

def clamp_axis(x0, x1, xmin, xmax):
    """
    Return (x0, x1) clamped to (xmin, xmax).

    """
    return clamp(x0, xmin, xmax), clamp(x1, xmin, xmax)

def get_closest(x0, y0, x1, y1, xmin, ymin, xmax, ymax):
    """
    Return the point or line segment within the min/max bounds that is closest
    to the line segment between (x0, y0) and (x1, y1).

    """
    # Line segment is horizontal or vertical
    # Beware floating point precision here
    if x0 == x1 or y0 == y1:
        x0, x1 = clamp_axis(x0, x1, xmin, xmax)
        y0, y1 = clamp_axis(y0, y1, ymin, ymax)
        return x0, y0, x1, y1

    p0_code = get_zonecode(x0, y0, xmin, ymin, xmax, ymax)
    p1_code = get_zonecode(x1, y1, xmin, ymin, xmax, ymax)

    while (True):
        # Line segment is entirely within rect
        if p0_code == p1_code == INSIDE:
            return x0, y0, x1, y1

        # Equals zero if endpoints don't share a side
        code = p0_code & p1_code

        # Line segment is on just one side of rect
        if code:
            if code & LEFT:
                x = xmin
                y = y0 if x0 > x1 else y1
                y = clamp(y, ymin, ymax)
            elif code & RIGHT:
                x = xmax
                y = y0 if x0 < x1 else y1
                y = clamp(y, ymin, ymax)
            elif code & BOTTOM:
                y = ymin
                x = x0 if y0 > y1 else x1
                x = clamp(x, xmin, xmax)
            elif code & TOP:
                y = ymax
                x = x0 if y0 < y1 else x1
                x = clamp(x, xmin, xmax)

            return x, y

        # Pick the first non-interior endpoint
        code = p0_code or p1_code

        # Ambiguous case; clip line segement and recheck on next iteration
        if code & LEFT:
            x = xmin
            y = y0 + (y1 - y0) * (xmin - x0) / (x1 - x0);
        elif code & RIGHT:
            x = xmax
            y = y0 + (y1 - y0) * (xmax - x0) / (x1 - x0);
        elif code & BOTTOM:
            y = ymin
            x = x0 + (x1 - x0) * (ymin - y0) / (y1 - y0)
        elif code & TOP:
            y = ymax
            x = x0 + (x1 - x0) * (ymax - y0) / (y1 - y0)

        # Update clipped endpoint
        if code == p0_code:
            x0, y0 = x, y
            p0_code = get_zonecode(x0, y0, xmin, ymin, xmax, ymax)
        else:
            x1, y1 = x, y
            p1_code = get_zonecode(x1, y1, xmin, ymin, xmax, ymax)

if __name__ == '__main__':
    import tkinter

    CANVAS_SIZE = 900
    RL = CANVAS_SIZE / 3 / 2 # distance from center to rect corners
    OL = CANVAS_SIZE * 10 # gridline length (extends past visible area)
    SHIFT_KEYCODE = 16

    rect = (-RL, -RL, RL, RL)
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

        closest = get_closest(x0, y0, x1, y1, *rect)

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
    canvas.create_rectangle(*rect, outline='#000000', width=4)

    # Start GUI loop
    root.mainloop()
