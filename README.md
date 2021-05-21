# wallpaper_changer
Automatically fetch and update wallpaper.

## Instructions

- Run `./main.py` to execute the program, download an image and make it your wallpaper.
- Add a symbolic link `~/bin/wch` to `<wallpapcher_changer_path>/main.py`.
- Add a line to your `.bashrc` to export the newly created binary path `export PATH="$HOME/bin:$PATH`.
- You can now run the wallpaper changer from the terminal with `wch`.
- You can set it up to run automatically or define a job in crontabs to run it.