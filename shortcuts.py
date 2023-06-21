import platform
import os


DESKTOP_FORM = """[Desktop Entry]
Name={name:s}
Type=Application
Path={workdir:s}
Comment={desc:s}
Terminal={term:s}
Icon={icon:s}
Exec={exe:s} {args:s}
"""


def make_shortcut(name, executable, icon=None, description=None, working_dir=None, args=None):
    """
    Create a shortcut on the current user's desktop and/or start menu.

    Args:
        name (str): The name of the shortcut
        executable (str): The path of the executable file
        icon (str, optional): The path of the icon file. Defaults to None.
        description (str, optional): The description of the shortcut. Defaults to the name.
        working_dir (str, optional): The working directory of the shortcut. Defaults to "/".
        args (str, optional): The arguments to pass to the executable. Defaults to None.
    """
    home = os.path.expanduser('~')
    if platform.system() == "Linux":
        text = DESKTOP_FORM.format(name=name, desc=description or name,
                                   workdir=working_dir or "/",
                                   exe=executable,
                                   icon=icon or "",
                                   args=args or "",
                                   term='true')
        with open(f"{home}/Desktop/{name}.desktop", 'w') as fout:
            fout.write(text)
        # = octal 755 / rwxr-xr-x
        os.chmod(f"{home}/Desktop/{name}.desktop", 493)
    elif platform.system() == "Windows":
        import win32com.client
        _WSHELL = win32com.client.Dispatch("Wscript.Shell")
        wscript = _WSHELL.CreateShortCut(
            f"{home}\\Desktop\\{name}.lnk")
        wscript.Targetpath = executable
        wscript.Arguments = args or ""
        wscript.WorkingDirectory = working_dir or "C:\\"
        wscript.WindowStyle = 0
        wscript.Description = description or name
        wscript.IconLocation = icon
        wscript.save()
        wscript = _WSHELL.CreateShortCut(
            f"{home}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\{name}.lnk")
        wscript.Targetpath = executable
        wscript.Arguments = args or ""
        wscript.WorkingDirectory = working_dir or "C:\\"
        wscript.WindowStyle = 0
        wscript.Description = description or name
        wscript.IconLocation = icon
        wscript.save()


def make_shortcut_admin(name, executable, icon=None, description=None, working_dir=None, args=None):
    """
    Create a shortcut for an application on the public desktop and/or start menu.

    Args:
        name (str): The name of the shortcut.
        executable (str): The path to the executable of the application.
        icon (str, optional): The path to the icon file. Defaults to None.
        description (str, optional): The description of the shortcut. Defaults to the name.
        working_dir (str, optional): The working directory of the application. Defaults to "/".
        args (str, optional): The arguments to pass to the application. Defaults to None.

    """
    if platform.system() == "Linux":
        text = DESKTOP_FORM.format(name=name, desc=description or name,
                                   workdir=working_dir or "/",
                                   exe=executable,
                                   icon=icon or "",
                                   args=args or "",
                                   term='true')
        with open(f"/usr/share/applications/{name}.desktop", 'w') as fout:
            fout.write(text)
        # = octal 755 / rwxr-xr-x
        os.chmod(f"/usr/share/applications/{name}.desktop", 493)
    elif platform.system() == "Windows":
        import win32com.client
        _WSHELL = win32com.client.Dispatch("Wscript.Shell")
        wscript = _WSHELL.CreateShortCut(
            f"C:\\Users\\Public\\Desktop\\{name}.lnk")
        wscript.Targetpath = executable
        wscript.Arguments = args or ""
        wscript.WorkingDirectory = working_dir or "C:\\"
        wscript.WindowStyle = 0
        wscript.Description = description or name
        wscript.IconLocation = icon
        wscript.save()
        wscript = _WSHELL.CreateShortCut(
            f"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\{name}.lnk")
        wscript.Targetpath = executable
        wscript.Arguments = args or ""
        wscript.WorkingDirectory = working_dir or "C:\\"
        wscript.WindowStyle = 0
        wscript.Description = description or name
        wscript.IconLocation = icon
        wscript.save()


def delete_shortcut(name):
    """
    Deletes a shortcut from the current user's desktop and/or start menu.

    Args:
        name (str): The name of the shortcut file to be deleted (without the file extension).
    """
    home = os.path.expanduser('~')
    if platform.system() == "Linux":
        try:
            os.unlink(f"{home}/Desktop/{name}.desktop")
        except:
            pass
    elif platform.system() == "Windows":
        try:
            os.unlink(f"{home}\\Desktop\\{name}.lnk")
            os.unlink(
                f"{home}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\{name}.lnk")
        except:
            pass


def delete_shortcut_admin(name):
    """
    Deletes a shortcut from the public desktop and/or start menu.

    Args:
        name (str): The name of the shortcut file to be deleted (without the file extension).
    """
    if platform.system() == "Linux":
        try:
            os.unlink(f"/usr/share/applications/{name}.desktop")
        except:
            pass
    elif platform.system() == "Windows":
        try:
            os.unlink(f"C:\\Users\\Public\\Desktop\\{name}.lnk")
            os.unlink(
                f"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\{name}.lnk")
        except:
            pass
