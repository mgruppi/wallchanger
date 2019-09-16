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
    print(js)
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
            if not r.ok:
                print(r)
                return None
            for block in r.iter_content(1024):
                fout.write(block)
    except Exception as e:
        print(e)


def dump_info(js, wall_dir, file="wall_img.info"):
    path = os.path.join(wall_dir, file)
    with open(path, "w") as fout:
        json.dump(js, fout)


# Possible kwargs for gnome3/Unity:
    # picture-options: 'none', 'wallpaper', 'centered', 'scaled', 'stretched', 'zoom', 'spanned'
    # primary-color: hex-color string (e.g. '000000')
    # secondary-color: hex-color string (e.g. 'FFFFFF')
def set_wallpaper(wall_path, **kwargs):
    command = "gsettings set org.gnome.desktop.background picture-uri %s" % wall_path
    for option in kwargs:
        command += " %s %s" % (option, kwargs[option])
    os.system(command)


def main():
    # Set up path variables
    wall_dir = os.path.join(Path.home(), ".wallpapers")
    wall_path = os.path.join(wall_dir, "wall_img.jpg")
    print("Wallpaper dir:", wall_dir)

    sources = ["bing", "apod"]
    parser = argparse.ArgumentParser(description="Wallpaper changer arguments.")
    parser.add_argument("--source", metavar="s", type=str, nargs=1, choices=sources,
                        default="random", help="source of wall paper (bing, apod, default: random)")
    parser.add_argument("--random", action="store_true",
                        help="choose a random picture (default: picture of the day)")

    args = parser.parse_args()

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


if __name__ == "__main__":
    main()
