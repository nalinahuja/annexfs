# Developed By Nalin Ahuja, nalinahuja

import os
import yaml

# End Imports-------------------------------------------------------------------------------------------------------------------------------------------------------------

# AnnexFS Source Directory
__ANNEXFS_SRC = os.path.dirname(__file__)

# AnnexFS Configuration File
__ANNEXFS_CONFIG = os.path.join(__ANNEXFS_SRC, "config.yml")

# End Constants-----------------------------------------------------------------------------------------------------------------------------------------------------------

# Declare Metadata Dictionary
mdata = None

# Get Metadata From AnnexFS Configuration File
with open(__ANNEXFS_CONFIG, "r") as file:
    # Load YAML Configuration File
    mdata = yaml.safe_load(file)

# Verify Metadata Dictionary
if (mdata is None):
    # Raise Error
    raise ValueError(f"annexfs could not load configuration file {__ANNEXFS_CONFIG}")

# End Configuration Loader------------------------------------------------------------------------------------------------------------------------------------------------
