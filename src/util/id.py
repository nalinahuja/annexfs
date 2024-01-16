# Developed By Nalin Ahuja, nalinahuja

import uuid

# End Imports-------------------------------------------------------------------------------------------------------------------------------------------------------------

def generate(s):
    # Encode String As UTF-8
    s = s.encode("utf-8")

    # Create UUID From String
    u = uuid.uuid4()

    # Decode UUID As Hex
    h = u.hex

    # Return Hex String
    return (h)

# End Identifier Functions------------------------------------------------------------------------------------------------------------------------------------------------
