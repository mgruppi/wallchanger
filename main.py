from urllib.parse import urljoin
from pathlib import Path
import requests
import json
import os
import argparse
import random
from datetime import date as dt_date

with open("VARIABLES.ENV") as fin:
    CONFIG = json.load(fin)


def get_random_date():
    start = int(dt_date(2018, 1, 1).strftime("%s"))
    end = int(dt_date.today().strftime("%s"))
    rand_timestamp = random.randint(start, end)
    rand_date = dt_date.fromtimestamp(rand_timestamp)
    return rand_date


def fetch_bing_json(days_ago=0, randomize=False):  # randomize will override days_ago
    if randomize:
        days_ago = random.randint(0, 7)  # bing provides images from up to 7 previous days
    js = requests.get(CONFIG["BING_URL"]+"&idx=%d" % days_ago).json()
    try:
        js["url"] = urljoin(CONFIG["BING_ROOT"], js["images"][0]["url"])
        return js
    except Exception as e:
        print(e)


def fetch_apod_json(hd=True, date=None, randomize=False):  # randomize will override date
    if randomize:
        date = get_random_date()

    if date:
        s = urljoin(CONFIG["APOD_URL"], "?hd=%s&api_key=%s&date=%s" %(hd, CONFIG["APOD_KEY"], date))
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
            CHUNK_SIZE = 128
            ticks = 100
            progress = 0
            for block in r.iter_content(CHUNK_SIZE):
                fout.write(block)
                progress += len(block)
                print("|", "="*(int(progress/length)*ticks) + "-"*(int(1-progress/length)*ticks),
                      "| (%d/%d)" % (progress, length), end="\r")
    except Exception as e:
        print(e)


def dump_info(js, wall_dir, file="wall_img.log"):
    path = os.path.join(wall_dir, file)
    with open(path, "a") as fout:
        json.dump(js, fout)


# Possible kwargs for gnome3/Unity:
    # picture-options: 'none', 'wallpaper', 'centered', 'scaled', 'stretched', 'zoom', 'spanned'
    # primary-color: hex-color string (e.g. '000000')
    # secondary-color: hex-color string (e.g. 'FFFFFF')
def set_wallpaper(wall_path, **kwargs):
    gsettings_command = "gsettings set org.gnome.desktop.background "
    os.system("%s picture-uri %s" % (gsettings_command, wall_path))
    os.system("%s picture-options zoom" % gsettings_command)
    for option in kwargs:
        os.system("%s %s %s" % (gsettings_command, option, kwargs[option]))



def main():
    # Args
    sources = ["bing", "apod"]
    parser = argparse.ArgumentParser(description="Wallpaper changer arguments.")
    parser.add_argument("--source", metavar="s", type=str, nargs=1, choices=sources,
                        default="random", help="source of wall paper (bing, apod, default: random)")
    parser.add_argument("--random", action="store_true",
                        help="choose a random picture (default: picture of the day)")
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
        random_choice = random.choice(sources)
    if random_choice == "bing":
        js = fetch_bing_json(randomize=args.random)
    elif random_choice == "apod":
        js = fetch_apod_json(randomize=args.random)

    # Download image and info
    download_image(js["url"], wall_dir)
    dump_info(js, wall_dir)

    # Set wallpaper
    set_wallpaper(wall_path)

    for key in js:
        print("%s: %s" % (key, js[key]))


if __name__ == "__main__":
    main()
