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
