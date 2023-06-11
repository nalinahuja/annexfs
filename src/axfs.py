# Developed By Nalin Ahuja, nalinahuja

import os
import conf
import shutil

from util import cli
from util import hash

# End Imports------------------------------------------------------------------------------------------------------------------------------------------------------------

# Define AnnexFS Root Path
__ANNEXFS_ROOT = conf.mdata["ANNEXFS_ROOT"]

# End Constants----------------------------------------------------------------------------------------------------------------------------------------------------------

def sanity_checks(func):
    # Verify AnnexFS Root Path Is Set
    if (__ANNEXFS_ROOT is None):
        # Raise Error
        raise ValueError("annexfs root is None")

    # Verify AnnexFS Root Exists
    elif (not(os.path.exists(__ANNEXFS_ROOT))):
        # Raise Error
        raise FileNotFoundError(f"annexfs root {cli.U}{__ANNEXFS_ROOT}{cli.N} does not exist")

    # Verify AnnexFS Root Is A Directory
    elif (not(os.path.isdir(__ANNEXFS_ROOT))):
        # Raise Error
        raise NotADirectoryError(f"annexfs root {cli.U}{__ANNEXFS_ROOT}{cli.N} is not a directory")

    # Return Function Reference
    return (func)

# End Decorator Functions------------------------------------------------------------------------------------------------------------------------------------------------

@sanity_checks
def create(ent_path):
    # Preprocess Entry Path
    ent_path = os.path.abspath(os.path.expanduser(ent_path))

    # Verify Entry Path Does Not Exist
    if (os.path.exists(ent_path)):
        # Return Error
        return (FileExistsError(f"entry path {cli.U}{ent_path}{cli.N} exists"))

    # Form Path To Enclosing Directory
    enc_path = os.path.join(__ANNEXFS_ROOT, hash.md5(ent_path))

    # Verify Path To Enclosing Directory Does Not Exist
    if (os.path.exists(enc_path)):
        # Return Error
        return (FileExistsError(f"annexfs has stored {cli.U}{ent_path}{cli.N}"))

    # Get Basename From Entry Path
    ent_bname = os.path.basename(ent_path)

    # Form Path To Destination Directory
    dst_path = os.path.join(enc_path, ent_bname)

    try:
        # Create Destination Directory
        os.makedirs(dst_path)

        # Set Enclosing Directory Permissions
        os.chmod(enc_path, 0o555)
    except (KeyboardInterrupt, Exception) as e:
        # Verify Enclosing Directory Exists
        if (os.path.exists(enc_path)):
            # Delete Enclosing Directory
            shutil.rmtree(enc_path)

        # Determine Error Handling
        if (isinstance(e, KeyboardInterrupt)):
            # Raise Interrupt
            raise e
        else:
            # Return Exception
            return (OSError("annexfs could not create new entry"))

    # Create Symbolic Link To Directory
    os.symlink(dst_path, ent_path)

    # Return Success
    return (None)

@sanity_checks
def delete(link_path):
    # Preprocess Symbolic Link Path
    link_path = os.path.abspath(os.path.expanduser(link_path))

    # Verify Symbolic Link Path
    if (not(os.path.exists(link_path))):
        # Return Error
        return (FileNotFoundError(f"link path {cli.U}{link_path}{cli.N} does not exist"))

    # Verify Destination Path Is An Internal Symbolic Link
    elif (not(os.path.islink(link_path)) or not(os.path.realpath(link_path).startswith(__ANNEXFS_ROOT))):
        # Return Error
        return (ValueError(f"destination path {cli.U}{link_path}{cli.N} is not an internal symbolic link"))

    # Get Path To Destination Directory
    dst_path = os.path.realpath(link_path)

    # Get Path To Enclosing Directory
    enc_path = os.path.dirname(dst_path)

    # Verify Path To Enclosing Directory Exists
    if (not(os.path.exists(enc_path))):
        # Return Error
        return (FileNotFoundError(f"annexfs has not stored {cli.U}{link_path}{cli.N}"))

    try:
        # Remove Symbolic Link
        os.remove(link_path)

        # Set Enclosing Directory Permissions
        os.chmod(enc_path, 0o755)

        # Remove Original Source Directory
        shutil.rmtree(enc_path)
    except (KeyboardInterrupt, Exception) as e:
        # Verify Enclosing Directory Exists
        if (os.path.exists(enc_path)):
            # Set Enclosing Directory Permissions
            os.chmod(enc_path, 0o555)

            # Recreate Symbolic Link
            os.symlink(dst_path, link_path)

        # Determine Error Handling
        if (isinstance(e, KeyboardInterrupt)):
            # Raise Interrupt
            raise e
        else:
            # Return Exception
            return (OSError("annexfs could not delete existing entry"))

    # Return Success
    return (None)

# End Linkage Functions--------------------------------------------------------------------------------------------------------------------------------------------------

@sanity_checks
def transfer_from(src_path):
    # Preprocess Source Path
    src_path = os.path.abspath(os.path.expanduser(src_path))

    # Verify Source Path Exists
    if (not(os.path.exists(src_path))):
        # Return Error
        return (FileNotFoundError(f"source path {cli.U}{src_path}{cli.N} does not exist"))

    # Verify Source Path Is An External Symbolic Link
    elif (os.path.islink(src_path) and os.path.realpath(src_path).startswith(__ANNEXFS_ROOT)):
        # Return Error
        return (ValueError(f"source path {cli.U}{src_path}{cli.N} is not an external symbolic link"))

    # Form Path To Enclosing Directory
    enc_path = os.path.join(__ANNEXFS_ROOT, hash.md5(src_path))

    # Verify Path To Enclosing Directory Does Not Exist
    if (os.path.exists(enc_path)):
        # Return Error
        return (FileExistsError(f"annexfs has stored {cli.U}{src_path}{cli.N}"))

    # Declare Source Path Components
    src_bname = src_fname = None

    # Check If Source Path Points To A File
    if (os.path.isfile(src_path)):
        # Get Filename From Source Path
        src_fname = os.path.basename(src_path)

        # Remove Filename From Source Path
        src_path = os.path.dirname(src_path)

    # Get Basename From Source Path
    src_bname = os.path.basename(src_path)

    # Form Path To Destination Directory
    dst_path = os.path.join(enc_path, src_bname)

    try:
        # Create Destination Directory
        os.makedirs(dst_path)

        # Set Enclosing Directory Permissions
        os.chmod(enc_path, 0o555)
    except (KeyboardInterrupt, Exception) as e:
        # Verify Enclosing Directory Exists
        if (os.path.exists(enc_path)):
            # Delete Enclosing Directory
            shutil.rmtree(enc_path)

        # Determine Error Handling
        if (isinstance(e, KeyboardInterrupt)):
            # Raise Interrupt
            raise e
        else:
            # Return Exception
            return (OSError("annexfs could not create new entry"))

    # Determine Transfer Type
    if (not(src_fname is None)):
        # Form Paths To Source And Destination Files
        src_file = os.path.join(src_path, src_fname)
        dst_file = os.path.join(dst_path, src_fname)

        try:
            # Copy Source File To Destination Directory
            shutil.copy2(src_file, dst_path, follow_symlinks = False)
        except (KeyboardInterrupt, Exception) as e:
            # Delete Enclosing Directory
            shutil.rmtree(enc_path)

            # Determine Error Handling
            if (isinstance(e, KeyboardInterrupt)):
                # Raise Interrupt
                raise e
            else:
                # Return Exception
                return (OSError("annexfs could not transfer file to new entry"))
        else:
            # TODO: Verify Source And Destination Sizes Are Equal

            # Remove Original Source File
            os.remove(src_file)

            # Create Symbolic Link To File
            os.symlink(dst_file, src_file)

    else:
        # Form Paths To Source And Destination Directories
        src_dir = src_path
        dst_dir = dst_path

        try:
            # Copy Files From Source To Destination
            shutil.copytree(src_dir, dst_path, dirs_exist_ok = True)
        except (KeyboardInterrupt, Exception) as e:
            # Delete Enclosing Directory
            shutil.rmtree(enc_path)

            # Determine Error Handling
            if (isinstance(e, KeyboardInterrupt)):
                # Raise Interrupt
                raise e
            else:
                # Return Exception
                return (OSError("annexfs could not transfer directory to new entry"))
        else:
            # TODO: Verify Source And Destination Sizes Are Equal

            # Remove Original Source Directory
            shutil.rmtree(src_dir)

            # Create Symbolic Link To Directory
            os.symlink(dst_dir, src_dir)

    # Return Success
    return (None)

@sanity_checks
def transfer_to(dst_path):
    # Preprocess Destination Path
    dst_path = os.path.abspath(os.path.expanduser(dst_path))

    # Verify Destination Path Exists
    if (not(os.path.exists(dst_path))):
        # Return Error
        return (FileNotFoundError(f"destination path {cli.U}{dst_path}{cli.N} does not exist"))

    # Verify Destination Path Is An Internal Symbolic Link
    elif (not(os.path.islink(dst_path)) or not(os.path.realpath(dst_path).startswith(__ANNEXFS_ROOT))):
        # Return Error
        return (ValueError(f"destination path {cli.U}{dst_path}{cli.N} is not an internal symbolic link"))

    # Get Path To Source Directory
    src_path = os.path.realpath(dst_path)

    # Verify Path To Source Directory Exists
    if (not(os.path.exists(src_path))):
        # Return Error
        return (FileNotFoundError(f"annexfs has not stored {cli.U}{dst_path}{cli.N}"))

    # Declare Source Path Components
    src_bname = src_fname = None

    # Check If Source Path Points To A File
    if (os.path.isfile(src_path)):
        # Get Filename From Source Path
        src_fname = os.path.basename(src_path)

        # Remove Filename From Source Path
        src_path = os.path.dirname(src_path)

    # Get Basename From Source Path
    src_bname = os.path.basename(src_path)

    try:
        # Remove Symbolic Link
        os.remove(dst_path)
    except (KeyboardInterrupt, Exception) as e:
        # Verify Enclosing Directory Exists
        if (os.path.exists(enc_path)):
            # Delete Enclosing Directory
            shutil.rmtree(enc_path)

        # Determine Error Handling
        if (isinstance(e, KeyboardInterrupt)):
            # Raise Interrupt
            raise e
        else:
            # Return Exception
            return (OSError("annexfs could not remove symbolic link"))

    # Get Path To Enclosing Directory
    enc_path = os.path.dirname(src_path)

    # Determine Transfer Type
    if (not(src_fname is None)):
        # Form Paths To Source And Destination Files
        src_file = os.path.join(src_path, src_fname)
        dst_file = dst_path

        try:
            # Copy Source File To Destination Directory
            shutil.copy2(src_file, dst_file, follow_symlinks = False)
        except (KeyboardInterrupt, Exception) as e:
            # Recreate Symlink To File
            os.symlink(src_file, dst_file)

            # Determine Error Handling
            if (isinstance(e, KeyboardInterrupt)):
                # Raise Interrupt
                raise e
            else:
                # Return Exception
                return (OSError("annexfs could not transfer file to destination"))
        else:
            # Set Enclosing Directory Permissions
            os.chmod(enc_path, 0o755)

            # Remove Original Source File
            os.remove(src_file)

    else:
        # Form Paths To Source And Destination Directories
        src_dir = src_path
        dst_dir = dst_path

        try:
            # Copy Files From Source To Destination
            shutil.copytree(src_dir, dst_path, dirs_exist_ok = True)
        except (KeyboardInterrupt, Exception) as e:
            # Recreate Symlink To File
            os.symlink(src_dir, dst_dir)

            # Determine Error Handling
            if (isinstance(e, KeyboardInterrupt)):
                # Raise Interrupt
                raise e
            else:
                # Return Exception
                return (OSError("annexfs could not transfer directory to destination"))
        else:
            # Set Enclosing Directory Permissions
            os.chmod(enc_path, 0o755)

            # Remove Original Source Directory
            shutil.rmtree(src_dir)

    # Remove Enclosing Directory
    shutil.rmtree(enc_path)

    # Return Success
    return (None)

# End Transfer Functions-------------------------------------------------------------------------------------------------------------------------------------------------
