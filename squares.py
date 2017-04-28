import pandas as pd
import numpy as np
from skimage.transform import radon # Currently unused, but will make some life easier when actually implemented

from PIL import Image

# Comments about cardinal directions when using an array as opposed to cartesian coordinates!

# So normally (+1,+1) is Up and to the right, or "UR" (UDLR, etc)
# But in this case (+1,+1) is DR (At least with traditional representation and image creation)

# Now we care about the 8 directions, U, UR, R, DR, D, DL, l, UL.
# I want to iterate through those directions at every step, and in order to do that, I need to number these

# Since (+1, +1) is DR though, I think we need to assign that to 0
# Even if a more "familiar" orientation there would be 0 is up. This is just to make my life nicer

# A Reference Diagram then
#  4  5  6
#   \ | /
#  3-   -7
#   / | \
#  2  1  0

# These comments will apply to everything after this when numerical coordinates are used

def create_board(w,l):
    board = np.zeros((l,w))
    return board


def dvec_coords(board, coord_x, coord_y, direction, seg_distance):
    segd_mod = seg_distance
    if direction == 1:
        start_y, end_y = coord_y, coord_y+segd_mod
        start_x, end_x = coord_x, coord_x
    elif direction == 5:
        #start_y, end_y = coord_y-segd_mod, coord_y+1
        start_y, end_y = coord_y,  coord_y-(segd_mod)
        start_x, end_x = coord_x, coord_x           
    elif direction == 3:
        start_y, end_y = coord_y, coord_y
        start_x, end_x = coord_x, coord_x-(segd_mod)
    elif direction == 7:
        start_y, end_y = coord_y, coord_y
        start_x, end_x = coord_x, coord_x+segd_mod
    else:
        raise Exception("Something went wrong")
    return start_x,end_x,start_y,end_y


# OH SHIT DOE! This is actually just the radon transform in a particular direction!
# I TOTALLY FORGOT ABOUT THAT SHIT! So just do the radon transform on the subimage, that's more fun
# anyway though.
def neighbors(board, coord_x, coord_y, direction, seg_distance):
    # So this is really easy in UP and Down, and Left and right directions
    # this is really annoying in diagnols though cause depending on how you do it, you get very different images
    # I'm going to have fun fucking around with this though, so once I get the rest of it working I can come back
    # and mess with how this works:
    
    init_val = board[coord_y, coord_x]
    
    # TODO: REMOVE THIS!!! THIS IS BULLSHIT FOR THE ABOVE
    if direction % 2 == 0:
        #So we'll try every direction, we just won't do shit in a diagnol
        return 1
    else:
        start_x, end_x, start_y, end_y = dvec_coords(board,coord_x,coord_y,direction,seg_distance)
        if start_x == end_x:
            results = np.sum(board[min(start_y,end_y):max(start_y,end_y)+1,start_x]) - init_val
            #results = np.sum(board[start_y:end_y,start_x]) - init_val
        elif start_y == end_y:
            results = np.sum(board[start_y,min(start_x,end_x):max(start_x,end_x)+1]) - init_val
            #results = np.sum(board[start_y,start_x:end_x]) - init_val
    return results


def travel(board_start, start_x, start_y, seg_distance=2, seg_value=1):
    
    # ------------------
    # Housekeeping stuff
    # ------------------

    # Pad the board so that we don't have to worry about going outside of the boundaries
    # (Since the boundaries are always 1 we don't have to worry about going there)
    board = np.pad(board_start, seg_distance, mode='constant', constant_values=1)
    
    if seg_distance < 2:
        raise Exception("Segment distance must be between 2 and min(board.x,board.y)")
    elif (seg_distance > len(board_start)) or (seg_distance > len(board_start[0])):
        # TODO: Max distance is actually significantly smaller than board size it's
        # more like some significantly smaller fraction of board size otherwise nothing
        # makes sense because like wtf is travelling 1/3 of the distance going to do?
        raise Exception("Segment distance must be between 2 and min(board.x,board.y)")
    
    if board_start[start_x, start_y] == 0:
        x, y = start_x+seg_distance, start_y+seg_distance
    else:
        #raise Exception("starting coordinate is not 0")
        board = board[seg_distance:-(seg_distance),seg_distance:-(seg_distance)]
        return board, 0
    
    # ------------------
    # The Actual work!
    # ------------------

    #from IPython.core.debugger import Tracer
    #Tracer()() #this one triggers the debugger
    
    iterations = 0
    while True:
        
        board[y,x] = seg_value
        direction = np.random.randint(0,8)  # Half open
        halt = False
        iterations+=1
        
        for attempt in range(0,8):
            direction = (direction + attempt) % 8
            
            has_neighbors = bool(neighbors(board,x,y,direction,seg_distance))
            
            if not has_neighbors:
                start_x, end_x, start_y, end_y = dvec_coords(board, x, y, direction, seg_distance)
                
                if start_x == end_x:
                    board[min(start_y,end_y):max(start_y,end_y), start_x] = seg_value
                    x, y = start_x, end_y

                elif start_y == end_y:
                    board[start_y, min(start_x,end_x):max(start_x,end_x)] = seg_value
                    x, y = end_x, start_y

                break
            
            elif attempt == 7:
                halt = True
                continue
            
            else:
                continue
        
        if halt:
            break
    
    # Since we padded in the beginning make sure we remember to "unpad"
    board = board[seg_distance:-(seg_distance),seg_distance:-(seg_distance)]
    
    return board, iterations


def generate_image(width, step_size, attempts):
    board = create_board(width, width)
    grid_size = width / step_size

    for x in range(1, attempts):
        start_x = np.random.randint(1,grid_size) * step_size
        start_y = np.random.randint(1,grid_size) * step_size
        board, _ = travel(board, start_x, start_y, step_size, seg_value=1)

    img = Image.fromarray((board * 255).astype(np.uint8))
    return img

if __name__ == '__main__':
    res_img = generate_image(500,5,1000)
    res_img.show()