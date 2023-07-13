# app installer
A simple program to install apps that you have made.
Currently only support for Windows exists.
## How to use:
Create a app.json file something like this:
```json
{
    "name": "My Cool App",
    "icon": "logo.ico",
    "logo": "logo.png",
    "version": "v0.0.1",
    "executable": "main.exe",
    "name_safe": "a-name-safe-for-the-file-system",
    "font": "Arial",
    "publisher": "me"
}
```
Then make the directory `data` and put all of your app's files in there.
Then just run:
```sh
pip install -r requirements.txt
python3 build.py
```