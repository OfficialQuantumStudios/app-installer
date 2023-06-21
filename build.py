import os
import json
import platform
import shutil
appconfig = json.loads(open("app.json").read())
os.system(f'pyinstaller --onefile --noconsole --icon "data/{appconfig["icon"]}" --name "{appconfig["name_safe"]}-uninstaller" uninstaller.py')
shutil.copy(f'dist/{appconfig["name_safe"]}-uninstaller' + ('.exe' if platform.system() == 'Windows' else ''), f'data/{appconfig["name_safe"]}-uninstaller' + ('.exe' if platform.system() == 'Windows' else ''))
os.system(f'pyinstaller --onefile --noconsole --add-data "data/' + (';' if platform.system() == 'Windows' else ':') + 'data/" --add-data "app.json' + (';' if platform.system() == 'Windows' else ':') + f'." --icon "data/{appconfig["icon"]}" --name "{appconfig["name_safe"]}-installer" installer.py')
os.remove(f'dist/{appconfig["name_safe"]}-uninstaller' + ('.exe' if platform.system() == 'Windows' else ''))
try:
    os.remove(f'dist/app' + ('.exe' if platform.system() == 'Windows' else ''))
except:
    pass
shutil.move(f'dist/{appconfig["name_safe"]}-installer' + ('.exe' if platform.system() == 'Windows' else ''), f'dist/app' + ('.exe' if platform.system() == 'Windows' else ''))