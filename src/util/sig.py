# Developed By Nalin Ahuja, nalinahuja

from signal import *

# End Imports-------------------------------------------------------------------------------------------------------------------------------------------------------------

class SignalProtector:
    def __init__(self, sigtype):
        # Initialize Signal Type
        self.sigtype = sigtype

        # Declare Signal Mask
        self.sigmask = None

    def __enter__(self):
        # Save Signal Mask
        self.sigmask = signal(self.sigtype, SIG_IGN)

    def __exit__(self, *args):
        # Restore Signal Mask
        signal(self.sigtype, self.sigmask)

# End Signal Classes------------------------------------------------------------------------------------------------------------------------------------------------------
