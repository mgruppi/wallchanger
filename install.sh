#!/bin/bash
## Installation and configuration of wallpaper changer (Bing/Apod)

src_path="$(pwd)"
install_path="$HOME/bin/"
mkdir -p "$install_path"

ln -fs "$src_path"/main.py "$install_path/wallchanger"

echo "export PATH=$install_path:$PATH" >> "$HOME/.bashrc"

echo "wallchanger installed successfully"
echo "You can now run wallchanger to download and change your wallpaper"

echo "Do you want wallchanger to run automatically on system startup? [y/N]"
read autorun

if [ "$autorun" == 'y' ] # || [ "$autorun" == 'Y' ]
then
  # Set up autostart config
  mkdir -p "$HOME/.config/autostart/"
  path_startup="$HOME/.config/autostart/wallchanger.desktop"
  echo "Setting up autostart config file to $path_startup"
  echo "[Desktop Entry]
  Type=Application
  Exec=wallchanger --source bing
  Hidden=false
  NoDisplay=false
  X-GNOME-Autostart-enabled=true
  Name[en_US]=Wallpaper Changer
  Name=Wallpaper Changer
  Comment[en_US]=Run wallchanger at startup
  Comment=Run wallchanger at startup." > $path_startup
fi

echo "> Done"