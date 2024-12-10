#!/usr/bin/python3
from urllib.parse import urljoin
from pathlib import Path
import requests
import json
import os
import argparse
import random
from datetime import date as dt_date


CONFIG = {
            "APOD_URL": "https://api.nasa.gov/planetary/apod", "APOD_KEY":"DEMO_KEY",
            "BING_ROOT": "https://bing.com",
            "BING_URL": "https://www.bing.com/HPImageArchive.aspx?format=js&n=1&mkt=en-US"
        }


def get_random_date():
    start = int(dt_date(2018, 1, 1).strftime("%s"))
    end = int(dt_date.today().strftime("%s"))
    rand_timestamp = random.randint(start, end)
    rand_date = dt_date.fromtimestamp(rand_timestamp)
    return rand_date


def json_to_txt(data):
    """
    Given a JSON object `data`, return it as a text file, one line per field.
    :param data: JSON object
    :return: text (str) Text to display.
    """

    if "images" in data:
        data = data["images"][0]

    lines = [("%s : %s" % (k, data[k])) for k in data]
    return "\n".join(lines)


def fetch_bing_json(days_ago=0, randomize=False, mkt="en-US"):  # randomize will override days_ago
    if randomize:
        days_ago = random.randint(0, 7)  # bing provides images from up to 7 previous days
    js = requests.get(CONFIG["BING_URL"]+"&idx=%d" % days_ago + "&mkt=%s" % mkt).json()
    try:
        js["url"] = urljoin(CONFIG["BING_ROOT"], js["images"][0]["url"])
        return js
    except Exception as e:
        print(e)


def fetch_apod_json(hd=True, date=None, randomize=False):  # randomize will override date
    if randomize:
        date = get_random_date()

    if date:
        s = urljoin(CONFIG["APOD_URL"], "?hd=%s&api_key=%s&date=%s" % (hd, CONFIG["APOD_KEY"], date))
    else:
        s = urljoin(CONFIG["APOD_URL"], "?hd=%s&api_key=%s" % (hd, CONFIG["APOD_KEY"]))
    js = requests.get(s).json()
    if hd:
        js["url"] = js["hdurl"]
    return js


def download_image(url, wall_dir, file="wall_img.jpg"):
    path = os.path.join(wall_dir, file)
    if not os.path.isdir(wall_dir):
        os.mkdir(wall_dir)
    print("Saving image to %s" % path)
    try:
        with open(path, "wb") as fout:
            r = requests.get(url, stream=True)
            length = int(r.headers.get("content-length"))
            if not r.ok:
                print(r)
                return None
            # Write a little progress bar
            CHUNK_SIZE = 1048576  # size of cunks in bytes (1 MB)
            ticks = 100
            progress = 0
            length = length//1024  # Length in KB
            for block in r.iter_content(CHUNK_SIZE):
                fout.write(block)
                progress += len(block)//1024  # Track progress in KB
                print("|", "="*(int(progress/length)*ticks) + "-"*(int(1-progress/length)*ticks),
                      "| (%d/%d KB)" % (progress, length), end="\r")
    except Exception as e:
        print(e)


def dump_info(text, wall_dir, file="wall_img.log"):
    path = os.path.join(wall_dir, file)
    with open(path, "w") as fout:
        fout.write(text)
    # with open(path, "w") as fout:
    #     for key in js:
    #         fout.write("%s: %s\n" % (key, js[key]))


# Possible kwargs for gnome3/Unity:
    # picture-options: 'none', 'wallpaper', 'centered', 'scaled', 'stretched', 'zoom', 'spanned'
    # primary-color: hex-color string (e.g. '000000')
    # secondary-color: hex-color string (e.g. 'FFFFFF')
def set_wallpaper(wall_path, **kwargs):
    gsettings_command = "gsettings set org.gnome.desktop.background "
    os.system("%s picture-uri file://%s" % (gsettings_command, wall_path))
    os.system("%s picture-options zoom" % gsettings_command)
    for option in kwargs:
        os.system("%s %s %s" % (gsettings_command, option, kwargs[option]))


def main():
    # Args
    sources = ["bing", "apod"]
    parser = argparse.ArgumentParser(description="Wallpaper changer arguments.")
    parser.add_argument("--source", metavar="s", type=str, choices=sources,
                        default="random", help="source of wall paper (bing, apod, default: random)")
    parser.add_argument("--random", action="store_true",
                        help="choose a random picture (default: picture of the day)")
    parser.add_argument("--mkt", type=str, default="en-US", help="Select the region to fetch wallpaper from.")
    parser.add_argument("--wallpaper_path", type=str, help="where to save wallpapers")

    args = parser.parse_args()

    # Set up path variables
    if args.wallpaper_path:
        wall_dir = args.wallpaper_path
    else:
        wall_dir = os.path.join(Path.home(), "Pictures")
    wall_path = os.path.join(wall_dir, "wall_img.jpg")
    print("Wallpaper dir:", wall_dir)

    if args.source == "random":
        args.source = random.choice(sources)
    if args.source == "bing":
        js = fetch_bing_json(randomize=args.random, mkt=args.mkt)
    elif args.source == "apod":
        js = fetch_apod_json(randomize=args.random)

    # Download image and info
    text = json_to_txt(js)
    print(text)

    download_image(js["url"], wall_dir)
    dump_info(text, wall_dir)

    # Set wallpaper
    set_wallpaper(wall_path)


if __name__ == "__main__":
    main()
