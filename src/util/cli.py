# Developed by Nalin Ahuja, nalinahuja

import os
import sys
import argparse

# End Imports-------------------------------------------------------------------------------------------------------------------------------------------------------------

# Response Characters
YES, NO = "y", "n"

# Interface Characters
HR, RA, DA = "─", "→", "↳"

# Cursor Escape Characters
NL, CR, TB = "\n", "\r", "\t"

# Cursor Control Sequences
UP, CL = "\033[A", CR + "\033[2K"

# Text Format Sequences
N, B, U = "\033[0m", "\033[1m", "\033[4m"

# End Constants-----------------------------------------------------------------------------------------------------------------------------------------------------------

def size():
    # Return Command Line Size
    return (os.get_terminal_size())

def prompt(msg):
    # Return Prompt Response
    return (input(msg).strip().lower())

def write(*args, **kwargs):
    # Write To Command Line
    print(*args, **kwargs, flush = True)

def Parser(*args, **kwargs):
    # Return Argument Parser Object
    return (argparse.ArgumentParser(*args, **kwargs))

def hr():
    # Get Command Line Width
    width, _ = os.get_terminal_size()

    # Write Horizontal Line
    write((HR) * width, file = sys.stdout)

def nl(ln = 1):
    # Return New Line Sequence
    return ((NL) * ln)

def cl(ln = 1):
    # Write Clear Line Sequence
    write((UP + CL) * ln, end = "", file = sys.stdout)

# End Interface Functions-------------------------------------------------------------------------------------------------------------------------------------------------
