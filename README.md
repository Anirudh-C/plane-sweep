# Line Intersection Project
## Setup
In a working `python3` environment (preferrably virtualenv) run the setup script
```sh
$ source setup.sh
```
## Testing and Running the program
Create a text file with line segments, where each line segmnet is contained on a new line.
Look at `tests/test.in` for an example.
To run the plane sweep algorithm for line intersection run the following command
```sh
$ python3 main.py [test_file] --plane-sweep
```
To run the brute force implementation, disregard the `--plane-sweep` flag.
## Visualization
I will update these in the next revision (before the demo)
