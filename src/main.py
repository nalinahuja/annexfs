# Developed By Nalin Ahuja, nalinahuja

import afs
import sys
import traceback

from util import cli

if (__name__ == "__main__"):
    # Initialize Argument Parser
    parser = cli.Parser(prog = "annexfs")

    # Initialize Action Arguments Group
    action_arguments = parser.add_mutually_exclusive_group(required = True)

    # Add Linkage Arguments
    action_arguments.add_argument("--create", help = "create annexfs entry", type = str)
    action_arguments.add_argument("--delete", help = "delete annexfs entry", type = str)

    # Add Transfer Arguments
    action_arguments.add_argument("--transfer-to", help = "restore files and delete annexfs entry", type = str)
    action_arguments.add_argument("--transfer-from", help = "create annexfs entry and save files", type = str)

    # Parse Arguments
    args = parser.parse_args()

    # Define Error
    err = None

    try:
        # Process Mutually Exclusive Arguments
        if (args.create):
            # Create AnnexFS Entry
            err = afs.create(args.create)
        elif (args.delete):
            # Delete AnnexFS Entry
            err = afs.delete(args.delete)

        if (args.transfer_to):
            # Restore Files From AnnexFS
            err = afs.transfer_to(args.transfer_to)
        elif (args.transfer_from):
            # Save Files To AnnexFS
            err = afs.transfer_from(args.transfer_from)
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
