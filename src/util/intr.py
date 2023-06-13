# Developed By Nalin Ahuja, nalinahuja

import signal

# End Imports-------------------------------------------------------------------------------------------------------------------------------------------------------------

class InterruptProtector:
    def __init__(self, intr_type):
        # Initialize Interrupt Type
        self.inttype = intr_type

        # Declare Interrupt Mask
        self.intmask = None

    def __enter__(self):
        # Disable Interrupt Type
        self.intmask = signal.signal(self.inttype, signal.SIG_IGN)

    def __exit__(self, *args):
        # Restore Interrupt Type
        signal.signal(self.inttype, self.intmask)

# End Interrupt Classes---------------------------------------------------------------------------------------------------------------------------------------------------
