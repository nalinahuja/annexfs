# Developed by Nalin Ahuja, nalinahuja

import sys
import argparse

# End Imports-------------------------------------------------------------------------------------------------------------------------------------------------------------

# Interface Characters
RA, DA = "→", "↳"

# Cursor Escape Characters
NL, CR, TB = "\n", "\r", "\t"

# Cursor Control Sequences
UP, CL = "\033[A", CR + "\033[2K"

# Text Format Sequences
N, B, U = "\033[0m", "\033[1m", "\033[4m"

# End Constants-----------------------------------------------------------------------------------------------------------------------------------------------------------

def nl(ln = 1):
    # Return New Line Sequence
    return ((NL) * ln)

def cl(ln = 1):
    # Write Clear Line Sequence
    write((UP + CL) * ln, end = "", file = sys.stdout)

def write(*args, **kwargs):
    # Write To Command Line
    print(*args, **kwargs, flush = True)

def Parser(*args, **kwargs):
    # Return Argument Parser Object
    return (argparse.ArgumentParser(*args, **kwargs))

# End Interface Functions-------------------------------------------------------------------------------------------------------------------------------------------------
