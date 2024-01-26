# Developed By Nalin Ahuja, nalinahuja

import os
import yaml

from util import cli

# End Imports-------------------------------------------------------------------------------------------------------------------------------------------------------------

# AnnexFS Source Directory
__ANNEXFS_SRC = os.path.dirname(__file__)

# AnnexFS Configuration File
__ANNEXFS_CONFIG = os.path.join(__ANNEXFS_SRC, "../config.yml")

# End Constants-----------------------------------------------------------------------------------------------------------------------------------------------------------

# Declare Data Dictionary
data = None

# Load Data From AnnexFS Configuration File
with open(__ANNEXFS_CONFIG, "r") as file:
    # Load YAML Configuration File
    data = yaml.safe_load(file)

    # Verify Data Dictionary Integrity
    if (not(isinstance(data, dict))):
        # Raise Error
        raise ValueError(f"configuration file {cli.U}{config}{cli.N} is malformed")

# End Configuration Loader------------------------------------------------------------------------------------------------------------------------------------------------
