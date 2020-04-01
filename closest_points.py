from tkinter import *

import math
from statistics import median
import random

import time

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "({}, {})".format(self.x, self.y)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        if self.x == other.x:
            return self.y < other.y
        else:
            return self.x < other.x
        
def generate_points(npoints):
    ret = []

    x_used = set([None])
    
    for i in range(npoints):
        # Find a unique `x` value
        x = None
        while x in x_used:
            x = random.randint(1, 1000)
            
        y = random.randint(1, 1000)

        # Sanity check
        assert(x not in x_used)
        pt = Point(x, y)

        # Include the `x` as used
        x_used.add(x)
        
        ret.append(pt)

    return ret

def pt_dist(pt1, pt2):
    xdiff = pt1.x - pt2.x
    ydiff = pt1.y - pt2.y

    return math.sqrt(xdiff * xdiff + ydiff * ydiff) 

def trivial_closest_points(points):
    npoints = len(points)
    min_dist = -1
    closest_pt_pair = None
    
    for i in range(npoints):
        for j in range(i + 1, npoints):
            pt1 = points[i]
            pt2 = points[j]

            dist = pt_dist(pt1, pt2)

            if min_dist == -1 or dist < min_dist:
                min_dist = dist
                closest_pt_pair = (pt1, pt2)

    # A sanity check
    assert(closest_pt_pair != None)

    return closest_pt_pair

def closest_points(points):
    # ADDED
    # Make sure all of the `points` are unique
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            assert(points[i] != points[j])
    
    # Base case
    #
    # Since 3 points cannot be split any further into smaller
    # subgroups with at least 2 points in each
    if len(points) <= 3:
        return trivial_closest_points(points)
    
    median_x = median(map(lambda pt: pt.x, points))

    # Organize the points to those <= to the median and > the `median_x`
    points_L = list(filter(lambda pt: pt.x <= median_x, points))
    points_R = list(filter(lambda pt: pt.x > median_x, points))

    # Recurse on the left and right portions of points
    closest_pt1_L, closest_pt2_L = closest_points(points_L)

    # Render the left line
    line_L = UI_line_connect_points((closest_pt1_L, closest_pt2_L),
                                    wait_time=2)

    closest_pt1_R, closest_pt2_R = closest_points(points_R)

    # Render the right line
    line_R = UI_line_connect_points((closest_pt1_R, closest_pt2_R),
                                    wait_time=2)
    
    min_pts = None
    min_d = None
    
    min_d_L = pt_dist(closest_pt1_L, closest_pt2_L)
    min_d_R = pt_dist(closest_pt1_R, closest_pt2_R)

    # Record the minimal points    
    if min_d_L < min_d_R:
        min_d = min_d_L
        min_pts = (closest_pt1_L, closest_pt2_L)
    else:
        min_d = min_d_R
        min_pts = (closest_pt1_R, closest_pt2_R)
        
    # Extract all of the points that are within `min_d` of the `median_x`
    middle_points = \
        list(filter(lambda pt: median_x - min_d <= pt.x <= median_x + min_d,
                    points))
    
    # Sort by the y coordinate of the `middle_points`
    middle_points.sort(key=lambda pt: pt.y)

    # Check if the `min_d` should be updated based on the `middle_points`
    for i in range(1, len(middle_points)):
        j = i - 1

        # Sanity check
        assert(j >= 0)

        # Sanity check the sorted order
        assert(middle_points[i].y >= middle_points[j].y)

        # TODO: In the slide, `min_d` is a `d`
        while j >= 0 and middle_points[i].y - middle_points[j].y < min_d:
            # Update the minimum distance between points
            dist = pt_dist(middle_points[i], middle_points[j])
            if dist < min_d:
                min_d = dist

                # Make sure that the same point is not pushed twice
                assert(middle_points[i] != middle_points[j])
                min_pts = (middle_points[i], middle_points[j])

            # Check over the next point
            j -= 1

    # Remove the two lines rendered above to let a higher level render
    UI_line_remove(line_L)
    UI_line_remove(line_R)
    
    return min_pts

#
# UI Functionality
#

PYTHON_GREEN = "#476042"
PYTHON_RED = "#ff0000"

root = None
canvas = None

points = []
x_used = set([None])

def UI_click_callback(event):
    global canvas, points, x_used

    # All of the x-cords must be unique
    if event.x in x_used:
        print("X-coordinates of points must be unique")
        return

    points.append(Point(event.x, event.y))
    x_used.add(event.x)

    # Draw an oval that is visible as the point
    x1, y1 = (event.x - 1), (event.y - 1)
    x2, y2 = (event.x + 1), (event.y + 1)
    
    canvas.create_oval(x1, y1, x2, y2, fill=PYTHON_GREEN)

def UI_calculate_closest_pair():
    global canvas, points

    # Sanity check that we have enough points
    if len(points) < 2:
        print("Not enough points to form closest pair")
        return
    
    triv_closest_pair = trivial_closest_points(points)
    closest_pair = closest_points(points)

    print("Trivial: {}\nAdvanced: {}".format(triv_closest_pair,
                                             closest_pair))

    # Check the correctness of the closest points pair found 
    if sorted(triv_closest_pair) == sorted(closest_pair):
        print("SUCCESS")

        # Visualize the closest points pair in RED
        UI_line_connect_points(closest_pair, PYTHON_RED)
    else:
        print("FAIL")

def UI_line_connect_points(pts, fill_color=PYTHON_GREEN,
                           wait_time=None):
    global root, canvas

    # First check that we are using a graphical mode
    if root == None:
        return
    
    # Visualize the closest points pair in RED
    line = canvas.create_line(pts[0].x, pts[0].y,
                              pts[1].x, pts[1].y,
                              fill=fill_color)

    canvas.update_idletasks()

    if wait_time is not None:
        time.sleep(wait_time)
    
    return line

def UI_line_remove(line):
    global root, canvas

    # First check that we are using a graphical mode
    if root == None:
        return

    canvas.delete(line)
    
def UI_init():
    global canvas, root

    root = Tk()

    canvas = Canvas(root, width=500, height=500)
    canvas.bind("<Button-1>", UI_click_callback)

    button = Button(root, text="Find Closest Points Pair",
                    command=UI_calculate_closest_pair)
    
    button.pack()
    canvas.pack()

    root.mainloop()

#
# UI Functionality
#

if __name__ == '__main__':
    UI_init()
