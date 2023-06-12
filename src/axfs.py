# Developed By Nalin Ahuja, nalinahuja

import os
import conf
import shutil

from util import cli
from util import hash

# End Imports------------------------------------------------------------------------------------------------------------------------------------------------------------

# AnnexFS Root Path
__ANNEXFS_ROOT = conf.mdata["ANNEXFS_ROOT"]

# End Constants----------------------------------------------------------------------------------------------------------------------------------------------------------

def enable_write_perms(path):
    # Set File Write Permission Bits
    os.chmod(path, 0o755)

def disable_write_perms(path):
    # Set File Write Permission Bits
    os.chmod(path, 0o555)

def get_file_size(path):
    # Get File Statistics
    file_stat = os.stat(path)

    # Return File Size
    return (file_stat.st_size)

def get_dir_size(path):
    # Initialize Directory Size
    dir_size = 0

    # Recurse Through Directory Tree
    with os.scandir(path) as it:
        # Iterate Over Tree Level
        for entry in (it):
            # Process Entry As File
            if (entry.is_file()):
                # Get File Statistics
                file_stat = entry.stat()

                # Update Directory Size
                dir_size += file_stat.st_size

            # Process Entry As Directory
            elif (entry.is_dir()):
                # Update Directory Size
                dir_size += get_dir_size(entry.path)

    # Return Directory Size
    return (dir_size)

def preprocess_path(path):
    # Expand Path Symbols
    path = os.path.expanduser(path)

    # Get Absolute Path
    path = os.path.abspath(path)

    # Return Preprocessed Path
    return (path)

def componentize_path(path):
    # Declare Path Components
    path_bname = path_fname = None

    # Check If Path Points To A File
    if (os.path.isfile(path)):
        # Get Filename From Path
        path_fname = os.path.basename(path)

        # Remove Filename From Path
        path = os.path.dirname(path)

    # Get Basename From Path
    path_bname = os.path.basename(path)

    # Return Path Components
    return (path, path_bname, path_fname)

# End Helper Functions---------------------------------------------------------------------------------------------------------------------------------------------------

def sanity_checks(fn):
    # Verify AnnexFS Root Path Is Set
    if (__ANNEXFS_ROOT is None):
        # Raise Error
        raise ValueError(f"annexfs root is {cli.U}{__ANNEXFS_ROOT}{cli.N}")

    # Verify AnnexFS Root Exists
    elif (not(os.path.exists(__ANNEXFS_ROOT))):
        # Raise Error
        raise FileNotFoundError(f"annexfs root {cli.U}{__ANNEXFS_ROOT}{cli.N} does not exist")

    # Verify AnnexFS Root Is A Directory
    elif (not(os.path.isdir(__ANNEXFS_ROOT))):
        # Raise Error
        raise NotADirectoryError(f"annexfs root {cli.U}{__ANNEXFS_ROOT}{cli.N} is not a directory")

    # Return Argument Function
    return (fn)

# End Decorator Functions------------------------------------------------------------------------------------------------------------------------------------------------

@sanity_checks
def create(ent_path):
    # Preprocess Entry Path
    ent_path = preprocess_path(ent_path)

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

    # Get Entry Path Basename Component
    ent_bname = os.path.basename(ent_path)

    # Form Path To Destination Directory
    dst_path = os.path.join(enc_path, ent_bname)

    try:
        # Create Destination Directory
        os.makedirs(dst_path)

        # Disable Enclosing Directory Writes
        disable_write_perms(enc_path)
    except (KeyboardInterrupt, Exception) as e:
        # Verify Enclosing Directory Exists
        if (os.path.exists(enc_path)):
            # Enable Enclosing Directory Writes
            enable_write_perms(enc_path)

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
    link_path = preprocess_path(link_path)

    # Verify Symbolic Link Path Exists
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
    except (KeyboardInterrupt, Exception) as e:
        # Check If Symbolic Link Was Removed
        if (os.path.exists(link_path)):
            # Return Error
            return (OSError("annexfs could not remove symbolic link"))

    try:
        # Enable Enclosing Directory Writes
        enable_write_perms(enc_path)

        # Remove Enclosing Directory
        shutil.rmtree(enc_path)
    except (KeyboardInterrupt, Exception) as e:
        # Check If Destination Directory Exists
        if (os.path.exists(dst_path)):
            # Recreate Symbolic Link
            os.symlink(dst_path, link_path)

            # Disable Enclosing Directory Writes
            disable_write_perms(enc_path)

        # Determine Error Handling
        if (isinstance(e, KeyboardInterrupt)):
            # Raise Interrupt
            raise e
        elif (os.path.exists(dst_path)):
            # Return Exception
            return (OSError("annexfs could not delete existing entry"))

    # Return Success
    return (None)

# End Linkage Functions--------------------------------------------------------------------------------------------------------------------------------------------------

@sanity_checks
def transfer_from(src_path):
    # Preprocess Source Path
    src_path = preprocess_path(src_path)

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

    # Get Source Path Components
    src_path, src_bname, src_fname = componentize_path(src_path)

    # Form Path To Destination Directory
    dst_path = os.path.join(enc_path, src_bname)

    try:
        # Create Destination Directory
        os.makedirs(dst_path)

        # Disable Enclosing Directory Writes
        disable_write_perms(enc_path)
    except (KeyboardInterrupt, Exception) as e:
        # Verify Enclosing Directory Exists
        if (os.path.exists(enc_path)):
            # Enable Enclosing Directory Writes
            enable_write_perms(enc_path)

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
            shutil.copy2(src_file, dst_file, follow_symlinks = False)
        except (KeyboardInterrupt, Exception) as e:
            # Enable Enclosing Directory Writes
            enable_write_perms(enc_path)

            # Delete Enclosing Directory
            shutil.rmtree(enc_path)

            # Determine Error Handling
            if (isinstance(e, KeyboardInterrupt)):
                # Raise Interrupt
                raise e
            else:
                # Return Exception
                return (OSError("annexfs file transfer was terminated due to error"))
        else:
            # Get Source And Destination File Sizes
            src_file_size = get_file_size(src_file)
            dst_file_size = get_file_size(dst_file)

            # Verify Source And Destination File Sizes Are Equal
            if (src_file_size != dst_file_size):
                # Enable Enclosing Directory Writes
                enable_write_perms(enc_path)

                # Delete Enclosing Directory
                shutil.rmtree(enc_path)

                # Return Error
                return (OSError("annexfs file transfer was unsuccessful"))

            # Remove Source File
            os.remove(src_file)

            # Create Symbolic Link To File
            os.symlink(dst_file, src_file)

    else:
        # Form Paths To Source And Destination Directories
        src_dir = src_path
        dst_dir = dst_path

        try:
            # Copy Files From Source To Destination
            shutil.copytree(src_dir, dst_dir, dirs_exist_ok = True)
        except (KeyboardInterrupt, Exception) as e:
            # Enable Enclosing Directory Writes
            enable_write_perms(enc_path)

            # Delete Enclosing Directory
            shutil.rmtree(enc_path)

            # Determine Error Handling
            if (isinstance(e, KeyboardInterrupt)):
                # Raise Interrupt
                raise e
            else:
                # Return Exception
                return (OSError("annexfs directory transfer was terminated due to error"))
        else:
            # Get Source And Destination Directory Sizes
            src_dir_size = get_dir_size(src_dir)
            dst_dir_size = get_dir_size(dst_dir)

            # Verify Source And Destination File Sizes Are Equal
            if (src_dir_size != dst_dir_size):
                # Enable Enclosing Directory Writes
                enable_write_perms(enc_path)

                # Delete Enclosing Directory
                shutil.rmtree(enc_path)

                # Return Error
                return (OSError("annexfs directory transfer was unsuccessful"))

            # Remove Source Directory
            shutil.rmtree(src_dir)

            # Create Symbolic Link To Directory
            os.symlink(dst_dir, src_dir)

    # Return Success
    return (None)

@sanity_checks
def transfer_to(dst_path):
    # Preprocess Destination Path
    dst_path = preprocess_path(dst_path)

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

    # Get Source Path Components
    src_path, src_bname, src_fname = componentize_path(src_path)

    # Get Path To Enclosing Directory
    enc_path = os.path.dirname(src_path)

    try:
        # Remove Symbolic Link
        os.remove(dst_path)
    except (KeyboardInterrupt, Exception) as e:
        # Check If Symbolic Link Was Removed
        if (os.path.exists(dst_path)):
            # Return Error
            return (OSError("annexfs could not remove symbolic link"))

    # Determine Transfer Type
    if (not(src_fname is None)):
        # Form Paths To Source And Destination Files
        src_file = os.path.join(src_path, src_fname)
        dst_file = dst_path

        try:
            # Copy Source File To Destination
            shutil.copy2(src_file, dst_file, follow_symlinks = False)
        except (KeyboardInterrupt, Exception) as e:
            # Check If Destination File Exists
            if (os.path.exists(dst_file)):
                # Remove Destination File
                os.remove(dst_file)

            # Recreate Symlink To File
            os.symlink(src_file, dst_file)

            # Determine Error Handling
            if (isinstance(e, KeyboardInterrupt)):
                # Raise Interrupt
                raise e
            else:
                # Return Exception
                return (OSError("annexfs file transfer was terminated due to error"))
        else:
            # Get Source And Destination File Sizes
            src_file_size = get_file_size(src_file)
            dst_file_size = get_file_size(dst_file)

            # Verify Source And Destination File Sizes Are Equal
            if (src_file_size != dst_file_size):
                # Check If Destination File Exists
                if (os.path.exists(dst_file)):
                    # Remove Destination File
                    os.remove(dst_file)

                # Recreate Symlink To File
                os.symlink(src_file, dst_file)

                # Return Error
                return (OSError("annexfs file transfer was unsuccessful"))

    else:
        # Form Paths To Source And Destination Directories
        src_dir = src_path
        dst_dir = dst_path

        try:
            # Copy Source Directory To Destination
            shutil.copytree(src_dir, dst_dir, dirs_exist_ok = True)
        except (KeyboardInterrupt, Exception) as e:
            # Check If Destination Directory Exists
            if (os.path.exists(dst_dir)):
                # Remove Destination Directory
                shutil.rmtree(dst_dir)

            # Recreate Symlink To File
            os.symlink(src_dir, dst_dir)

            # Determine Error Handling
            if (isinstance(e, KeyboardInterrupt)):
                # Raise Interrupt
                raise e
            else:
                # Return Exception
                return (OSError("annexfs directory transfer was terminated due to error"))
        else:
            # Get Source And Destination Directory Sizes
            src_dir_size = get_dir_size(src_dir)
            dst_dir_size = get_dir_size(dst_dir)

            # Verify Source And Destination File Sizes Are Equal
            if (src_dir_size != dst_dir_size):
                # Check If Destination Directory Exists
                if (os.path.exists(dst_dir)):
                    # Remove Destination Directory
                    shutil.rmtree(dst_dir)

                # Recreate Symlink To File
                os.symlink(src_dir, dst_dir)

                # Return Error
                return (OSError("annexfs directory transfer was unsuccessful"))

    # Enable Enclosing Directory Writes
    enable_write_perms(enc_path)

    # Remove Enclosing Directory
    shutil.rmtree(enc_path)

    # Return Success
    return (None)

# End Transfer Functions-------------------------------------------------------------------------------------------------------------------------------------------------
