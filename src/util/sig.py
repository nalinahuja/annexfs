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
        # Ignore Signal
        self.sigmask = signal(self.sigtype, SIG_IGN)

    def __exit__(self, *args):
        # Acknowledge Signal
        signal(self.sigtype, self.sigmask)

# End Signal Classes------------------------------------------------------------------------------------------------------------------------------------------------------
