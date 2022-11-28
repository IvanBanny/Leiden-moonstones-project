import numpy as np
import random
from tkinter import *
import tkinter.simpledialog as tkdialog
import tkinter.font as font
import tkinter.messagebox as tkmesage
import itertools
import time


def solve_moon(canvas, mode, moon_size, stone_num, moon):
    def generate_path(canvas, opt_path):
        # A function to draw the path and print the path to the menu
        def draw_move(canvas, moon_size, cell1, cell2):
            # A function to draw an arrow from cell1 to cell2
            cell_size = 480 // moon_size
            canvas.create_line(9 + cell_size // 2 + cell1[0] * cell_size, 9 + cell_size // 2 + cell1[1] * cell_size,
                               9 + cell_size // 2 + cell2[0] * cell_size, 9 + cell_size // 2 + cell2[1] * cell_size,
                               fill="red", width=5, arrow=LAST)

        # An array with all the stones and the starting position
        stones = [[0, 0]]
        for row in range(moon_size):
            for col in range(moon_size):
                if moon[row][col] and (row != 0 or col != 0):
                    stones.append([row, col])

        ans, row, col = "[0, 0]", 0, 0  # Answer string with the path and the current coordinate iterators
        for i in range(len(opt_path)):
            # Make horizontal coordinates equal
            while col != stones[opt_path[i]][0]:
                temp_col = col
                col += (stones[opt_path[i]][0] - col) // abs(stones[opt_path[i]][0] - col)
                ans += f", {[row, col]}"
                draw_move(canvas, moon_size, [row, temp_col], [row, col])
            # Make vertical coordinates equal
            while row != stones[opt_path[i]][1]:
                temp_row = row
                row += (stones[opt_path[i]][1] - row) // abs(stones[opt_path[i]][1] - row)
                ans += f", {[row, col]}"
                draw_move(canvas, moon_size, [temp_row, col], [row, col])
        return ans

    # Erase the old menu, draw the moon again and print "SOLVING..." to the menu
    canvas.create_rectangle(500, 0, 1000, 500, fill="black")
    draw_new_moon(canvas, moon, moon_size)
    canvas.create_text(515, 160, width=470, anchor=NW,
                       text="SOLVING...", fill="white", font=font.Font(size=12, weight='bold'))

    # Starting time measurement
    start_time = time.time()

    if stone_num == 2 and moon[0][0]:
        # A special case
        row1, col1 = 0, 0
        for row1 in range(moon_size):
            for col1 in range(moon_size):
                if moon[row1][col1] and (row1 != 0 or col1 != 0):
                    break
        opt, opt_path = abs(row1) + abs(col1), [0, 1]
    else:
        # Solve as regular
        opt, opt_path = held_karp_sol(moon_size, moon) if mode == 0 else comb_sol(moon_size, stone_num, moon)

    # End time measurement
    sol_time = time.time() - start_time

    # round the time
    i = 5
    while round(sol_time, i) == 0 and i <= 10:
        i += 1
    sol_time = round(sol_time, i)

    # Erase old menu and draw the solution info
    canvas.create_rectangle(500, 0, 1000, 500, fill="black")
    canvas.create_text(515, 160, width=470, anchor=NW,
                       text=f"Solving using the {'Held-Karp' if mode == 0 else 'all permutations'} method took {sol_time}s",
                       fill="white", font=font.Font(size=12, weight='bold'))
    canvas.create_text(515, 180, width=470, anchor=NW,
                       text=f"The path length is {opt}",
                       fill="white", font=font.Font(size=12, weight='bold'))

    canvas.create_text(515, 200, width=470, anchor=NW,
                       text=f"Path: {generate_path(canvas, opt_path)}",
                       fill="white", font=font.Font(size=12, weight='bold'))


def comb_sol(moon_size, stone_num, moon):
    # The going through all the possible paths solution
    def path_len(stones, path):
        # A function to get a paths length
        path_len = 0
        for i in range(len(path) - 1):
            # add the horizontal and vertical differences between the 2 stones that are adjacent in path
            path_len += abs(stones[path[i + 1]][0] - stones[path[i]][0]) \
                        + abs(stones[path[i + 1]][1] - stones[path[i]][1])
        return path_len

    # An array with all the stones and the starting position
    stones = [[0, 0]]
    for row in range(moon_size):
        for col in range(moon_size):
            if moon[row][col] and (row != 0 or col != 0):
                stones.append([row, col])

    max_path, max_path_len = tuple(range(1, stone_num + (1 if moon[0][0] != 1 else 0))), \
                             path_len(stones, range(stone_num + (1 if moon[0][0] != 1 else 0)))
    # Going through all the path permutations and picking the shortest one
    for path in itertools.permutations(range(1, stone_num + (1 if moon[0][0] != 1 else 0))):
        tmp = path_len(stones, (0, ) + path)
        if max_path_len > tmp:
            max_path = path
            max_path_len = tmp

    # Return the cost of the path and the path of indexes in stones list
    return path_len(stones, (0, ) + max_path), list((0, ) + max_path)


def held_karp_sol(moon_size, moon):
    # The Held-Carp algorithm solution
    # The following algorithm implementation has been borrowed from https://github.com/CarlEkerot/held-karp (MIT license)
    # and edited to find paths and not loops

    def dists(stones, a, b):
        return abs(stones[b][0] - stones[a][0]) + abs(stones[b][1] - stones[a][1])

    # An array with all the stones and the starting position
    stones = [[0, 0]]
    for row in range(moon_size):
        for col in range(moon_size):
            if moon[row][col] and (row != 0 or col != 0):
                stones.append([row, col])

    n = len(stones)

    # Maps each subset of the nodes to the cost to reach that subset, as well
    # as what node it passed before reaching this subset.
    # Node subsets are represented as set bits.
    C = {}

    # Set transition cost from initial state
    for k in range(1, n):
        C[(1 << k, k)] = (dists(stones, 0, k), 0)

    # Iterate subsets of increasing length and store intermediate results
    # in classic dynamic programming manner
    for subset_size in range(2, n):
        for subset in itertools.combinations(range(1, n), subset_size):
            # Set bits for all nodes in this subset
            bits = 0
            for bit in subset:
                bits |= 1 << bit

            # Find the lowest cost to get to this subset
            for k in subset:
                prev = bits & ~(1 << k)

                res = []
                for m in subset:
                    if m == 0 or m == k:
                        continue
                    res.append((C[(prev, m)][0] + dists(stones, m, k), m))
                C[(bits, k)] = min(res)

    # We're interested in all bits but the least significant (the start state)
    bits = (2 ** n - 1) - 1

    # Calculate optimal cost
    res = []
    for k in range(1, n):
        res.append((C[(bits, k)][0], k))
    opt, parent = min(res)

    # Backtrack to find full path
    path = []
    for i in range(n - 1):
        path.append(parent)
        new_bits = bits & ~(1 << parent)
        _, parent = C[(bits, parent)]
        bits = new_bits

    # Add implicit start state
    path.append(0)

    # Return the cost of the path and the path of indexes in stones list
    return opt, list(reversed(path))


def draw_new_moon(canvas, moon, moon_size):
    # Erase everything
    canvas.create_rectangle(0, 0, 1000, 500, fill="black")

    # Draw the moon
    cell_size = 480 // moon_size
    for row in range(moon_size):
        for col in range(moon_size):
            canvas.create_rectangle(10 + col * cell_size, 10 + row * cell_size, 7 + cell_size + col * cell_size,
                                    7 + cell_size + row * cell_size, fill=("green" if moon[row][col] else "white"))


def get_draw_new_moon(canvas):
    # global is for retrieving the values moon_size, stone_num, moon from lambda: get_draw_new_moon(canvas),
    # that is triggered when the "New moon" button is pressed
    global moon_size, stone_num, moon

    # Get the new values
    moon_size, stone_num, moon = get_moon()

    # Draw the new values
    draw_new_moon(canvas, moon, moon_size)


def get_moon():
    moon_size = tkdialog.askstring("Moon size", "On what moon size do you want your robot to search (5, 6, 7 or 8)?")
    try:
        moon_size = int(moon_size)
        if moon_size in [5, 6, 7, 8]:
            moon = np.zeros((moon_size, moon_size))

            stone_num = int(tkdialog.askstring("Stone count", "How many stones would you like to have?"))
            if 2 <= stone_num <= moon_size ** 2:
                while (moon == 1).sum() < stone_num:
                    moon[random.randint(0, moon_size-1), random.randint(0, moon_size-1)] = 1

                return moon_size, stone_num, moon
            else:
                tkmesage.showinfo("", "Your input is invalid!")
                return get_moon()
        else:
            tkmesage.showinfo("", "Your input is invalid!")
            return get_moon()
    except:
        tkmesage.showinfo("", "Your input is invalid!")
        return get_moon()


def main():
    print("A Tkinter window has opened.")

    # Global is for retrieving the values moon_size, stone_num, moon from lambda: get_draw_new_moon(canvas),
    # that is triggered when the "New moon" button is pressed
    global moon_size, stone_num, moon

    # Open a window
    top = Tk()
    top.geometry("1000x500")
    canvas = Canvas(top, bg="black", height=500, width=1000)

    # Get the new values for the moon and draw it
    get_draw_new_moon(canvas)

    # Creating menu buttons
    b_new = Button(top, text="New moon", width=20,
                   command=lambda: get_draw_new_moon(canvas),
                   font=font.Font(size=12, weight='bold'))
    b_new.place(x=510, y=20)

    b_sol = Button(top, text="Solve Held-Karp", width=20,
                   command=lambda: solve_moon(canvas, 0, moon_size, stone_num, moon),
                   font=font.Font(size=12, weight='bold'))
    b_sol.place(x=510, y=60)

    b_sol = Button(top, text="Solve All permutations", width=20,
                   command=lambda: solve_moon(canvas, 1, moon_size, stone_num, moon),
                   font=font.Font(size=12, weight='bold'))
    b_sol.place(x=510, y=100)

    # Some code for the window to run properly
    canvas.pack()
    top.mainloop()


global moon_size, stone_num, moon
# This makes sure that the program starts running with the main() function
if __name__ == "__main__":
    main()
