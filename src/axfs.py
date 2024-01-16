# Developed By Nalin Ahuja, nalinahuja

import os
import config
import shutil

from util import id
from util import cli
from util import sig

from util.sig import SignalProtector

# End Imports------------------------------------------------------------------------------------------------------------------------------------------------------------

# AnnexFS Root Path
__ANNEXFS_ROOT = config.mdata["ANNEXFS_ROOT"]

# End Constants----------------------------------------------------------------------------------------------------------------------------------------------------------

def expand_path(path):
    # Expand Path Symbols
    path = os.path.expanduser(path)

    # Get Absolute Path
    path = os.path.abspath(path)

    # Return Expanded Path
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

def get_dir_size(path):
    # Initialize Directory Size
    dir_size = 0

    # Recurse Through File Tree
    with os.scandir(path) as ft:
        # Iterate Over File Tree Entries
        for entry in (ft):
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

def get_file_size(path):
    # Get File Statistics
    file_stat = os.stat(path)

    # Return File Size
    return (file_stat.st_size)

def enable_write_perms(path):
    # Set File Write Permission Bits
    os.chmod(path, 0o755)

def disable_write_perms(path):
    # Set File Write Permission Bits
    os.chmod(path, 0o555)

def sanity_checks(func):
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

    # Return Callback Function
    return (func)

def rm_onerror(func, path, info):
    # Check For Write Permissions
    if (not(os.access(path, os.W_OK))):
        # Enable Write Permissions
        enable_write_perms(path)

        # Execute Callback Function
        func(path)
    else:
        # Raise Non-Access Error
        raise

# End Helper Functions--------------------------------------------------------------------------------------------------------------------------------------------------

@sanity_checks
def create(link_path):
    # Expand Symbolic Link Path
    link_path = expand_path(link_path)

    # Verify Symbolic Link Path Does Not Exist
    if (os.path.exists(link_path)):
        # Return Error
        return (FileExistsError(f"link path {cli.U}{link_path}{cli.N} exists"))

    # Get Symbolic Link Directory
    link_dir = os.path.dirname(link_path)

    # Verify Symbolic Link Directory Exists
    if (not(os.path.exists(link_dir))):
        # Return Error
        return (FileNotFoundError(f"link directory {cli.U}{link_dir}{cli.N} does not exist"))

    # Form Enclosing Path Until Unique
    while (True):
        # Form Path To Enclosing Directory
        enc_path = os.path.join(__ANNEXFS_ROOT, id.generate(link_path))

        # Verify Enclosing Path Is Unique
        if (not(os.path.exists(enc_path))):
            # Break Loop
            break

    # Form Path To Destination Directory
    dst_path = os.path.join(enc_path, os.path.basename(link_path))

    try:
        # Create Destination Directory
        os.makedirs(dst_path)

        # Disable Enclosing Directory Writes
        disable_write_perms(enc_path)
    except (KeyboardInterrupt, Exception) as e:
        # Protect Cleanup From SIGINT
        with SignalProtector(sig.SIGINT):
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

    # Protect Symlink Creation From SIGINT
    with SignalProtector(sig.SIGINT):
        # Create Symbolic Link To Directory
        os.symlink(dst_path, link_path)

    # Return Success
    return (None)

@sanity_checks
def delete(link_path):
    # Expand Symbolic Link Path
    link_path = expand_path(link_path)

    # Verify Symbolic Link Path Exists
    if (not(os.path.exists(link_path))):
        # Return Error
        return (FileNotFoundError(f"link path {cli.U}{link_path}{cli.N} does not exist"))

    # Get Path To Destination Directory
    dst_path = os.path.realpath(link_path)

    # Verify Destination Path Is An Internal Symbolic Link
    if (not(os.path.islink(link_path)) or not(dst_path.startswith(__ANNEXFS_ROOT))):
        # Return Error
        return (ValueError(f"destination path {cli.U}{link_path}{cli.N} is not an internal symbolic link"))

    # Get Path To Enclosing Directory
    enc_path = os.path.dirname(dst_path)

    # Verify Path To Enclosing Directory Exists
    if (not(os.path.exists(enc_path))):
        # Return Error
        return (FileNotFoundError(f"annexfs has not stored {cli.U}{link_path}{cli.N}"))

    try:
        # Enable Enclosing Directory Writes
        enable_write_perms(enc_path)

        # Remove Enclosing Directory
        shutil.rmtree(enc_path)
    except (KeyboardInterrupt, Exception) as e:
        # Protect Cleanup From SIGINT
        with SignalProtector(sig.SIGINT):
            # Check If Destination Directory Exists
            if (os.path.exists(dst_path)):
                # Disable Enclosing Directory Writes
                disable_write_perms(enc_path)

        # Determine Error Handling
        if (isinstance(e, KeyboardInterrupt)):
            # Raise Interrupt
            raise e
        elif (os.path.exists(dst_path)):
            # Return Exception
            return (OSError("annexfs could not delete existing entry"))

    # Protect Symlink Deletion From SIGINT
    with SignalProtector(sig.SIGINT):
        # Remove Symbolic Link
        os.remove(link_path)

    # Return Success
    return (None)

# End Linkage Functions--------------------------------------------------------------------------------------------------------------------------------------------------

@sanity_checks
def transfer_from(src_path):
    # Expand Source Path
    src_path = expand_path(src_path)

    # Verify Source Path Exists
    if (not(os.path.exists(src_path))):
        # Return Error
        return (FileNotFoundError(f"source path {cli.U}{src_path}{cli.N} does not exist"))

    # Verify Source Path Is An External Symbolic Link
    elif (os.path.islink(src_path) and os.path.realpath(src_path).startswith(__ANNEXFS_ROOT)):
        # Return Error
        return (ValueError(f"source path {cli.U}{src_path}{cli.N} is not an external symbolic link"))

    # Form Enclosing Path Until Unique
    while (True):
        # Form Path To Enclosing Directory
        enc_path = os.path.join(__ANNEXFS_ROOT, id.generate(src_path))

        # Verify Enclosing Path Is Unique
        if (not(os.path.exists(enc_path))):
            # Break Loop
            break

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
        # Protect Cleanup From SIGINT
        with SignalProtector(sig.SIGINT):
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
            # Protect Cleanup From SIGINT
            with SignalProtector(sig.SIGINT):
                # Enable Enclosing Directory Writes
                enable_write_perms(enc_path)

                # Delete Enclosing Directory
                shutil.rmtree(enc_path, onerror = rm_onerror)

            # Determine Error Handling
            if (isinstance(e, KeyboardInterrupt)):
                # Raise Interrupt
                raise e
            else:
                # Return Exception
                return (OSError("annexfs file transfer was terminated due to error"))

        # Protect Post Copy Instructions From SIGINT
        with SignalProtector(sig.SIGINT):
            # Get Source And Destination File Sizes
            src_file_size = get_file_size(src_file)
            dst_file_size = get_file_size(dst_file)

            # Verify Source And Destination File Sizes Are Equal
            if (src_file_size != dst_file_size):
                # Enable Enclosing Directory Writes
                enable_write_perms(enc_path)

                # Delete Enclosing Directory
                shutil.rmtree(enc_path, onerror = rm_onerror)

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
            # Protect Cleanup From SIGINT
            with SignalProtector(sig.SIGINT):
                # Enable Enclosing Directory Writes
                enable_write_perms(enc_path)

                # Delete Enclosing Directory
                shutil.rmtree(enc_path, onerror = rm_onerror)

            # Determine Error Handling
            if (isinstance(e, KeyboardInterrupt)):
                # Raise Interrupt
                raise e
            else:
                # Return Exception
                return (OSError("annexfs directory transfer was terminated due to error"))

        # Protect Post Copy Instructions From SIGINT
        with SignalProtector(sig.SIGINT):
            # Get Source And Destination Directory Sizes
            src_dir_size = get_dir_size(src_dir)
            dst_dir_size = get_dir_size(dst_dir)

            # Verify Source And Destination File Sizes Are Equal
            if (src_dir_size != dst_dir_size):
                # Enable Enclosing Directory Writes
                enable_write_perms(enc_path)

                # Delete Enclosing Directory
                shutil.rmtree(enc_path, onerror = rm_onerror)

                # Return Error
                return (OSError("annexfs directory transfer was unsuccessful"))

            # Remove Source Directory
            shutil.rmtree(src_dir, onerror = rm_onerror)

            # Create Symbolic Link To Directory
            os.symlink(dst_dir, src_dir)

    # Return Success
    return (None)

@sanity_checks
def transfer_to(dst_path):
    # Expand Destination Path
    dst_path = expand_path(dst_path)

    # Verify Destination Path Exists
    if (not(os.path.exists(dst_path))):
        # Return Error
        return (FileNotFoundError(f"destination path {cli.U}{dst_path}{cli.N} does not exist"))

    # Get Path To Source Directory
    src_path = os.path.realpath(dst_path)

    # Verify Destination Path Is An Internal Symbolic Link
    if (not(os.path.islink(dst_path)) or not(src_path.startswith(__ANNEXFS_ROOT))):
        # Return Error
        return (ValueError(f"destination path {cli.U}{dst_path}{cli.N} is not an internal symbolic link"))

    # Get Source Path Components
    src_path, src_bname, src_fname = componentize_path(src_path)

    # Get Path To Enclosing Directory
    enc_path = os.path.dirname(src_path)

    # Verify Path To Enclosing Directory Exists
    if (not(os.path.exists(enc_path))):
        # Return Error
        return (FileNotFoundError(f"annexfs has not stored {cli.U}{dst_path}{cli.N}"))

    try:
        # Remove Symbolic Link
        os.remove(dst_path)
    except (KeyboardInterrupt, Exception) as e:
        # Determine Error Handling
        if (isinstance(e, KeyboardInterrupt)):
            # Raise Interrupt
            raise e
        else:
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
            # Protect Cleanup From SIGINT
            with SignalProtector(sig.SIGINT):
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

        # Protect Post Copy Instructions From SIGINT
        with SignalProtector(sig.SIGINT):
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
            # Protect Cleanup From SIGINT
            with SignalProtector(sig.SIGINT):
                # Check If Destination Directory Exists
                if (os.path.exists(dst_dir)):
                    # Remove Destination Directory
                    shutil.rmtree(dst_dir, onerror = rm_onerror)

                # Recreate Symlink To File
                os.symlink(src_dir, dst_dir)

            # Determine Error Handling
            if (isinstance(e, KeyboardInterrupt)):
                # Raise Interrupt
                raise e
            else:
                # Return Exception
                return (OSError("annexfs directory transfer was terminated due to error"))

        with SignalProtector(sig.SIGINT):
            # Get Source And Destination Directory Sizes
            src_dir_size = get_dir_size(src_dir)
            dst_dir_size = get_dir_size(dst_dir)

            # Verify Source And Destination File Sizes Are Equal
            if (src_dir_size != dst_dir_size):
                # Check If Destination Directory Exists
                if (os.path.exists(dst_dir)):
                    # Remove Destination Directory
                    shutil.rmtree(dst_dir, onerror = rm_onerror)

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
