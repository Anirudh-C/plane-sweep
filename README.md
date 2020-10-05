# Line Intersection Project
## Setup
In a working `python3` environment (preferably virtualenv) run the setup script
```sh
$ source setup.sh
```
## Testing and Running the program
Create a text file with line segments, where each line segment is contained on a new line.
Look at `tests/test.txt` for an example.
To run the plane sweep algorithm for line intersection run the following command
```sh
$ python3 main.py [test_file] --plane-sweep
```
To run the brute force implementation, disregard the `--plane-sweep` flag.
## Visualisation
`main.py` itself opens the visualisation interface. Alternatively, running the following also
works
```sh
$ python3 main.py --plane-sweep
```
The interface works as follows:
### Inserting Line Segments
1. Click on the "+" button at the bottom right. 
2. Click at any location to insert a point. Move the mouse cursor to the other end point and click to add the 
   line segment. Repeat the clicking and moving to add more line segments. Press `<ESC>` at any stage to cancel 
   the insertion.
3. Undoing and redoing line segment insertions: `C-z` and `C-r` undo and redo the insertion of line segments,
   respectively. (`C-` denotes pressing the control key as a modifier)
4. Pressing `C-s` saves the line segments into the `tests/` folder. This file can be loaded via the same program
   again using the `[test_file]` argument as described above.
### Running the Algorithm
1. Once the line segments are added, click `<ENTER>` to run the corresponding algorithm.
2. If the algorithm has already been run, then clicking `<ENTER>` highlights the intersection points red.
3. Clicking `<BACKSPACE>` clears the screen and resets to just the line segments
### Visualising the steps
1. Alternatively, click the left and right buttons present at the bottom left of the screen to move backwards and
   forwards in execution
2. Pressing `<ESC>` at any stage resets the progress in the algorithm and hence going back to the start
### Quitting the visualisation interface
Press `q` to quit the visualisation interface.
