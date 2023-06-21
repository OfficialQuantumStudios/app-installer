import customtkinter
import os
import psutil
import platform
import tkinter
import sys
import shortcuts
import subprocess
import tempfile
import shutil
import argparse
import json
import winreg
import ctypes
from PIL import Image # pillow

def create_uninstaller_entry(app_name, uninstaller_cmd, icon, publisher, version, allusers=False):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\{}".format(app_name)
    t = None
    if allusers:
        t = winreg.HKEY_LOCAL_MACHINE
    else:
        t = winreg.HKEY_CURRENT_USER
    with winreg.CreateKey(t, key_path) as key:
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, app_name)
        winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, uninstaller_cmd)
        winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon)
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, publisher)
        winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, version)
    
    print("Uninstaller entry created successfully.")

def remove_uninstaller_entry(app_name, allusers=False):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\{}".format(app_name)
    try:
        t = None
        if allusers:
            t = winreg.HKEY_LOCAL_MACHINE
        else:
            t = winreg.HKEY_CURRENT_USER
        winreg.DeleteKey(t, key_path)
        print("Uninstaller entry removed successfully.")
    except OSError as e:
        print("Failed to remove uninstaller entry:", str(e))

def remove_directory(directory):
    if os.path.isdir(directory):
        try:
            for root, dirs, files in os.walk(directory, topdown=False):
                try:
                    for file in files:
                        file_path = os.path.join(root, file)
                        os.remove(file_path)
                    for dir_name in dirs:
                        dir_path = os.path.join(root, dir_name)
                        os.rmdir(dir_path)
                except OSError as e:
                    print(f"Error: {e.filename} - {e.strerror}")
            os.rmdir(directory)
        except OSError as e:
            print(f"Error deleteing directory: {directory} - {e.strerror}")


temp_dir = os.path.dirname(__file__)
exe_dir = os.path.dirname(sys.executable)
exe = sys.executable
cwd = os.getcwd()

def trytokill(dir):
    try:
        for proc in psutil.process_iter():
            try:
                if (dir in proc.exe() or dir in proc.cwd()) and not proc.exe() == exe:
                    proc.kill()
                    print('killed ' + proc.name() + '(' + proc.pid + ')')
            except:
                pass
    except:
        pass

def is_admin():
    if platform.system() == "Windows":
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    elif platform.system() == "Linux":
        try:
            return os.geteuid() == 0
        except:
            return False

class installer:
    def __init__(self, app, config, installation_directory, install_type, update=False):
            text = "Installing..."
            if update:
                text = "Updating..."
            title = customtkinter.CTkLabel(app, text=text, fg_color="transparent", font=(config["font"], 24))
            title.place(relx=0.5, rely=0.3, anchor=tkinter.CENTER)
            title.update()
            percentage = customtkinter.CTkLabel(app, text="0%", fg_color="transparent", font=(config["font"], 24))
            percentage.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)
            percentage.update()
            bar = customtkinter.CTkProgressBar(app, width=350, height=10)
            bar.set(0)
            bar.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
            bar.update()
            try:
                remove_directory(installation_directory)
                os.makedirs(installation_directory, exist_ok=True)
            except Exception as e:
                tkinter.messagebox.showerror(title="Error", message="Could not create directory. Ensure that you have permission to write there.")
                sys.exit(1)
            trytokill(installation_directory)
            files_list = os.listdir(os.path.join(temp_dir, "data"))
            i = 0
            for file in files_list:
                filepath = os.path.join(temp_dir, "data", file)
                #print(filepath, "=>", os.path.join(installation_directory, file))
                if os.path.isfile(filepath):
                    shutil.copy(filepath, os.path.join(installation_directory, file))
                else:
                    shutil.copytree(filepath, os.path.join(installation_directory, file), dirs_exist_ok=True)
                i += 1
                percent = i / len(files_list)
                percentage.configure(text=f"{percent * 100:.1f}%")
                percentage.update()
                bar.set(percent)
                bar.update()
                #print(installation_directory)
            f = open(os.path.join(installation_directory, "uninstaller.info"), "w")
            config["install_type"] = install_type
            f.write(json.dumps(config))
            f.close()
            if install_type == 2:
                shortcuts.delete_shortcut_admin(name=config["name_safe"])
                shortcuts.make_shortcut_admin(executable=os.path.join(installation_directory, config["executable"]), name=config["name_safe"], icon=os.path.join(installation_directory, config["icon"]), working_dir=installation_directory)
            else:
                shortcuts.delete_shortcut(name=config["name_safe"])
                shortcuts.make_shortcut(executable=os.path.join(installation_directory, config["executable"]), name=config["name_safe"], icon=os.path.join(installation_directory, config["icon"]), working_dir=installation_directory)
            if platform.system() == "Windows":
                allusers = False
                if install_type == 2:
                    allusers = True
                remove_uninstaller_entry(config["name_safe"], allusers)
                create_uninstaller_entry(config["name_safe"], os.path.join(installation_directory, config["name_safe"] + "-uninstaller.exe"), os.path.join(installation_directory, config["icon"]), config["publisher"], config["version"], allusers)
            bar.destroy()
            title.destroy()
            percentage.destroy()
            text = "Install done"
            if update:
                text = "Update done"
            title = customtkinter.CTkLabel(app, text=text, fg_color="transparent", font=(config["font"], 24))
            title.place(relx=0.5, rely=0.3, anchor=tkinter.CENTER)
            title.update()
            def doexit():
                try:
                    with open(os.devnull, "w") as devnull:
                        subprocess.Popen([os.path.join(installation_directory, config["executable"])], stdout=devnull, stderr=devnull, cwd=installation_directory)
                except:
                    pass
                app.destroy()
                sys.exit()
            if update:
                doexit()
            exit_button = customtkinter.CTkButton(app, text="Exit", command=doexit, height=40, font=(config["font"], 18))
            exit_button.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
            exit_button.update()

class installer_gui:
    def __init__(self):
        self.f = open(os.path.join(temp_dir, "app.json"))
        self.config = json.loads(self.f.read())
        self.f.close()
        args = argparse.ArgumentParser()
        args.add_argument("--update", default=False, action="store_true", help="Immediately uninstall and start the install without prompting anything")
        args.add_argument("--continue-as-admin-install", default=False, action="store_true", help="This is really just an internal flag for continuing the install as admin")
        args.add_argument("--installation-directory", default=False, help="Directory to install to (for --update only with --install-type=3)")
        args.add_argument("--install-type", default=False, help="Directory to install to (for --update)")
        args = args.parse_args()
        self.installation_directory = ""
        if platform.system() == "Windows":
            self.installation_directory = os.path.join(os.path.expanduser("~"), "AppData", "Local", self.config["name_safe"])
        #elif platform.system() == "Linux":
        #    self.installation_directory = os.path.join(os.path.expanduser("~"), "." + self.config["name_safe"])
        else:
            print("Unknown platform: " + platform.system(), file=sys.stderr)
            sys.exit(1)
        self.install_type = 1
        self.install_directory_textbox = False
        self.browse_button = False

        self.app = customtkinter.CTk()

        self.app.title(self.config["name"] + " installer")
        self.app.geometry("480x320")
        self.app.resizable(0, 0)
        self.app.iconbitmap(os.path.join(temp_dir, "data", self.config["icon"]))

        #self.app.overrideredirect(True)
        #self.app.grip = Grip(self.app)
        self.app.eval("tk::PlaceWindow . center")

        if args.update:
            if args.install_type:
                self.install_type = int(args.install_type)
                self.installation_directory = args.installation_directory
                if self.install_type == 1:
                    #if platform.system() == "Windows":
                    self.installation_directory = os.path.join(os.path.expanduser("~"), "AppData", "Local", self.config["name_safe"])
                    #elif platform.system() == "Linux":
                    #    self.installation_directory = os.path.join(os.path.expanduser("~"), "." + self.config["name_safe"])
                if self.install_type == 2:
                    #if platform.system() == "Windows":
                    self.installation_directory = os.path.join("C:\\", "Program Files", self.config["name_safe"])
                    #elif platform.system() == "Linux":
                    #    self.installation_directory = os.path.join("/", "usr", "share", self.config["name_safe"])
                if self.install_type == 2 and not is_admin():
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, '--update --install-type "' + str(self.install_type) + '"', None, 1)
                    sys.exit()
                if self.install_type == 3 and not args.installation_directory:
                    print("--update --install-type=3 requires --installation_directory", file=sys.stderr)
                    sys.exit(1)
                installer(self.app, self.config, self.installation_directory, self.install_type, True)
                sys.exit()
            else:
                print("--update requires --install_type", file=sys.stderr)
                sys.exit(1)

        self.version_label = customtkinter.CTkLabel(self.app, text="V" + self.config["version"], fg_color="transparent", font=(self.config["font"], 12))
        self.version_label.place(relx=0.08, rely=0.98, anchor=tkinter.CENTER)

        if args.continue_as_admin_install:
            self.install_type = 2
            #if platform.system() == "Windows":
            self.installation_directory = os.path.join("C:\\", "Program Files", self.config["name_safe"])
            #elif platform.system() == "Linux":
            #    self.installation_directory = os.path.join("/", "usr", "share", self.config["name_safe"])
            installer(self.app, self.config, self.installation_directory, self.install_type)
        else:
            self.image_logo = customtkinter.CTkImage(Image.open(os.path.join(temp_dir, "data", self.config["logo"])), size=(128, 128))
            self.logo_image = customtkinter.CTkLabel(self.app, text="", image=self.image_logo)
            self.logo_image.place(relx=0.5, rely=0.23, anchor=tkinter.CENTER)

            self.title = customtkinter.CTkLabel(self.app, text=self.config["name"] + " installer", fg_color="transparent", font=(self.config["font"], 20))
            self.title.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

            def update_install_directory():
                self.install_directory_textbox.delete("0.0", tkinter.END)
                self.install_directory_textbox.insert("0.0", tkinter.filedialog.askdirectory(title="Please select a directory to install to"))
            def make_directory_selector():
                self.install_directory_textbox = customtkinter.CTkTextbox(self.app, width=350, height=1, font=(self.config["font"], 10))
                self.install_directory_textbox.place(relx=0.415, rely=0.62, anchor=tkinter.CENTER)
                self.install_directory_textbox.insert("0.0", self.installation_directory)
                self.browse_button = customtkinter.CTkButton(self.app, text="Browse", command=update_install_directory, width=75, font=(self.config["font"], 12))
                self.browse_button.place(relx=0.87, rely=0.62, anchor=tkinter.CENTER)

            def update_install_location():
                self.install_type = self.install_location_variable.get()
                if self.install_type == 1:
                    #if platform.system() == "Windows":
                    self.installation_directory = os.path.join(os.path.expanduser("~"), "AppData", "Local", self.config["name_safe"])
                    #elif platform.system() == "Linux":
                    #    self.installation_directory = os.path.join(os.path.expanduser("~"), "." + self.config["name_safe"])
                if self.install_type == 2:
                    #if platform.system() == "Windows":
                    self.installation_directory = os.path.join("C:\\", "Program Files", self.config["name_safe"])
                    #elif platform.system() == "Linux":
                    #    self.installation_directory = os.path.join("/", "usr", "share", self.config["name_safe"])
                if self.install_type == 3:
                    make_directory_selector()
                else:
                    if self.install_directory_textbox:
                        self.install_directory_textbox.configure(state=tkinter.DISABLED)
                        self.install_directory_textbox.destroy()
                        self.install_directory_textbox = False
                    if self.browse_button:
                        self.browse_button.destroy()
                        self.browse_button = False

            self.install_location_variable = tkinter.IntVar(self.app, value=0)
            self.current_user_button = customtkinter.CTkRadioButton(self.app, text="Install for the current user",
                                                        command=update_install_location, variable=self.install_location_variable, value=1, font=(self.config["font"], 10))
            self.current_user_button.select()
            self.all_users_button = customtkinter.CTkRadioButton(self.app, text="Install for all users",
                                                        command=update_install_location, variable=self.install_location_variable, value=2, font=(self.config["font"], 10))
            self.custom_location_button = customtkinter.CTkRadioButton(self.app, text="Custom install location",
                                                        command=update_install_location, variable=self.install_location_variable, value=3, font=(self.config["font"], 10))
            self.current_user_button.place(relx=0.2, rely=0.73, anchor=tkinter.CENTER)
            self.all_users_button.place(relx=0.5, rely=0.73, anchor=tkinter.CENTER)
            self.custom_location_button.place(relx=0.8, rely=0.73, anchor=tkinter.CENTER)

            def start_install():
                if self.install_type == 3:
                    self.installation_directory = self.install_directory_textbox.get("0.0", tkinter.END).strip()
                if os.path.exists(self.installation_directory):
                    if tkinter.messagebox.askyesno(title="Confirmation", message="Directory already exists. Do you want to continue? (This will overwrite the existing installation)"):
                        if self.install_type == 2 and not is_admin():
                            self.app.destroy()
                            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "--continue-as-admin-install", None, 1)
                            sys.exit()
                        doinstall()
                else:
                    if self.install_type == 2 and not is_admin():
                        self.app.destroy()
                        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "--continue-as-admin-install", None, 1)
                        sys.exit()
                    doinstall()
                
            self.start_install_button = customtkinter.CTkButton(self.app, text="     Start Install ➡️", command=start_install, width=150, height=50, font=(self.config["font"], 18))
            self.start_install_button.place(relx=0.5, rely=0.88, anchor=tkinter.CENTER)

            

            def doinstall():
                if self.browse_button:
                    self.browse_button.destroy()
                if self.install_directory_textbox:
                    self.install_directory_textbox.destroy()
                self.start_install_button.destroy()
                self.title.destroy()
                self.custom_location_button.destroy()
                self.all_users_button.destroy()
                self.current_user_button.destroy()
                self.logo_image.destroy()
                installer(self.app, self.config, self.installation_directory, self.install_type)

        self.app.mainloop()

class uninstaller:
    def __init__(self, app, config, dir):
        title = customtkinter.CTkLabel(app, text="Uninstaling...", fg_color="transparent", font=(config["font"], 24))
        title.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)
        title.update()
        status = customtkinter.CTkLabel(app, text="Killing process(s)...", fg_color="transparent", font=(config["font"], 18))
        status.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        status.update()
        trytokill(dir)
        status.configure(text="Removing files...")
        status.update()
        remove_directory(dir)
        status.configure(text="Removing shortcuts...")
        status.update()
        if config["install_type"] == 2:
            shortcuts.delete_shortcut_admin(name=config["name_safe"])
        else:
            shortcuts.delete_shortcut(name=config["name_safe"])
        if platform.system() == "Windows":
            status.configure(text="Removing install entry...")
            status.update()
            allusers = False
            if config["install_type"] == 2:
                allusers = True
            remove_uninstaller_entry(config["name_safe"], allusers)
        status.destroy()
        title.configure(text="Uninstalled!")
        title.update()
        def doexit():
            app.destroy()
            sys.exit()
        exit_button = customtkinter.CTkButton(app, text="Exit", command=doexit, height=40, font=(config["font"], 18))
        exit_button.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        exit_button.update()

class uninstaller_gui:
    def __init__(self):
        args = argparse.ArgumentParser()
        args.add_argument("--start-from-temp-dir", default=False, action="store_true", help="This is really just an internal flag for continuing the uninstall")
        args.add_argument("--dir", help="Directory to uninstall")
        args = args.parse_args()
        if args.start_from_temp_dir:
            self.dir = args.dir
            self.f = open(os.path.join(self.dir, "uninstaller.info"))
            self.config = json.loads(self.f.read())
            self.f.close()

            self.app = customtkinter.CTk()

            self.app.title(self.config["name"] + " uninstaller")
            self.app.geometry("480x320")
            self.app.resizable(0, 0)
            self.app.iconbitmap(os.path.join(self.dir, self.config["icon"]))


            self.app.eval("tk::PlaceWindow . center")
            self.image_logo = customtkinter.CTkImage(Image.open(os.path.join(self.dir, self.config["logo"])), size=(128, 128))

            self.logo_image = customtkinter.CTkLabel(self.app, text="", image=self.image_logo)
            self.logo_image.place(relx=0.5, rely=0.23, anchor=tkinter.CENTER)

            self.title = customtkinter.CTkLabel(self.app, text=self.config["name"] + " uninstaller", fg_color="transparent", font=(self.config["font"], 20))
            self.title.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

            self.version_label = customtkinter.CTkLabel(self.app, text="V" + self.config["version"], fg_color="transparent", font=(self.config["font"], 12))
            self.version_label.place(relx=0.08, rely=0.98, anchor=tkinter.CENTER)

            def start_uninstall():
                self.start_uninstall_button.destroy()
                self.title.destroy()
                self.logo_image.destroy()
                uninstaller(self.app, self.config, self.dir)

            self.start_uninstall_button = customtkinter.CTkButton(self.app, text="     Uninstall ➡️", command=start_uninstall, width=150, height=50, font=(self.config["font"], 18))
            self.start_uninstall_button.place(relx=0.5, rely=0.7, anchor=tkinter.CENTER)

            self.app.mainloop()
        else:
            f = open(os.path.join(exe_dir, "uninstaller.info"))
            config = json.loads(f.read())
            f.close()
            file = os.path.join(tempfile.gettempdir(), os.path.basename(exe))
            shutil.copy(exe, file)
            if config["install_type"] == 2:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", file, ' --start-from-temp-dir --dir "' + exe_dir + '"', None, 1)
            else:
                subprocess.run([file, '--start-from-temp-dir', '--dir', exe_dir])