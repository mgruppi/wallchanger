# Wallchanger - Wallpaper changer for gnome
Automatically fetch and update wallpaper on Gnome.
Currently supported wallpaper sources are Bing and NASA Astronomy Picture of the Day (APOD).

## Instructions

### Automatic installation

- Close or download this repository on a gnome desktop environment.
- Run `install.sh` to link and add it to your startup applications (if wanted).

### Manual installation and execution
- Run `./main.py` to execute the program, download an image and make it your wallpaper.
- Add a symbolic link `~/bin/wch` to `<wallpapcher_changer_path>/main.py`.
- Add a line to your `.bashrc` to export the newly created binary path `export PATH="$HOME/bin:$PATH`.
- You can now run the wallpaper changer from the terminal with `wch`.
- You can set it up to run automatically or define a job in crontabs to run it.