# Developed By Nalin Ahuja, nalinahuja

import hashlib

# End Imports-------------------------------------------------------------------------------------------------------------------------------------------------------------

def md5(s):
    # Encode String As UTF-8
    s = s.encode("utf-8")

    # Create MD5 Hash Of String
    m = hashlib.md5(s)

    # Decode Hash As Hex
    h = m.hexdigest()

    # Return Hex String
    return (h)

# End Hash Functions------------------------------------------------------------------------------------------------------------------------------------------------------
