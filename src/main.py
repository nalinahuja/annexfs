# Developed By Nalin Ahuja, nalinahuja

import sys
import traceback

from util import cli

# End Imports-------------------------------------------------------------------------------------------------------------------------------------------------------------

if (__name__ == "__main__"):
    # Initialize Argument Parser
    parser = cli.Parser(prog = "annexfs")

    # Initialize Action Arguments Group
    action_arguments = parser.add_mutually_exclusive_group(required = True)

    # Add Linkage Arguments
    action_arguments.add_argument("--create", help = "create annexfs entry", type = str)
    action_arguments.add_argument("--delete", help = "delete annexfs entry", type = str)

    # Add Transfer Arguments
    action_arguments.add_argument("--transfer-from", help = "transfer files from main to annexfs", type = str)
    action_arguments.add_argument("--transfer-to", help = "transfer files to main from annexfs", type = str)

    # Parse Arguments
    args = parser.parse_args()

    # Declare Error Return
    err = None

    try:
        # Import AnnexFS Module
        import axfs

        # Complete Specified Action
        if (args.create):
            # Create AnnexFS Entry
            err = axfs.create(args.create)
        elif (args.delete):
            # Delete AnnexFS Entry
            err = axfs.delete(args.delete)
        elif (args.transfer_from):
            # Transfer Files To AnnexFS
            err = axfs.transfer_from(args.transfer_from)
        elif (args.transfer_to):
            # Transfer Files From AnnexFS
            err = axfs.transfer_to(args.transfer_to)
    except KeyboardInterrupt:
        # Print Interrupt Status
        cli.write(cli.nl(2) + f"annexfs: Program interrupted by user", file = sys.stderr)
    except Exception:
        # Get Error Information
        err_type, err_msg, err_tb = sys.exc_info()

        # Print Error Status
        cli.write(cli.nl(2) + f"annexfs: A fatal error has occurred", file = sys.stderr)

        # Print Error Information
        cli.write(f"{cli.DA} {err_type.__name__} - {err_msg}", file = sys.stderr)

        # Print Error Traceback
        traceback.print_tb(err_tb)

    # Check Error Status Value
    if (not(err is None)):
        # Print Error Status
        cli.write(cli.nl(2) + f"annexfs: A non-fatal error has occurred", file = sys.stderr)

        # Print Error Information
        cli.write(f"{cli.DA} {type(err).__name__} - {err}", file = sys.stderr)

# End Main Function-------------------------------------------------------------------------------------------------------------------------------------------------------
