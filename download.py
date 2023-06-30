#! /usr/bin/env python
from bs4 import BeautifulSoup
import argparse
import os
import pathlib
import shutil
import requests
from typing import Optional


def main(
    rtf_input: str, target_folder: str, xml_input: Optional[str], dry_run: bool
) -> None:
    # Load existing players
    existing_uids = set()
    if xml_input:
        with open(pathlib.Path(xml_input), "r") as f_xml_in:
            for line in f_xml_in.readlines():
                if line.strip().startswith("<record from"):
                    existing_uids.add(int(line.split("/")[-3]))
    print(f"There are {len(existing_uids)} existing players")

    # Identify players
    downloadable_uids = set()
    with open(pathlib.Path(rtf_input), "r") as f_rtf_in:
        # Data is: uid, nationality, second_nationality, name, hair_length, hair_colour, skin_tone
        for line in f_rtf_in.readlines():
            if line.startswith("| -"):
                continue
            try:
                uid = int(line.split("|")[1].strip())
                if uid not in existing_uids:
                    downloadable_uids.add(uid)
            except (IndexError, ValueError):
                pass
    print(f"There are {len(downloadable_uids)} new players to check")

    # Download images
    target_folder = pathlib.Path(target_folder).resolve()
    os.makedirs(target_folder, exist_ok=True)
    n_downloaded, n_non_existent, n_no_image = 0, 0, 0
    for idx, uid in enumerate(sorted(downloadable_uids), start=1):
        try:
            if idx % 100 == 0:
                print(
                    f"Working on player {idx}/{len(downloadable_uids)}: downloaded {n_downloaded}, no face data {n_no_image}, non-existent {n_non_existent}."
                )
            # Look for player
            r_search = requests.get(f"https://sortitoutsi.net/search/database?search={uid}&type=person")
            s_search = BeautifulSoup(r_search.content, "html.parser")
            if not [link for link in s_search.find_all("a") if "football-manager-2021/person" in str(link)]:
                # UID {uid} does not exist in FM21
                n_non_existent += 1
                continue
            # Download image
            url = f"https://sortitoutsi.b-cdn.net/uploads/face/{uid}.png"
            response_exists = requests.get(url)
            if (response_exists.status_code == 200) and (len(response_exists.content) > 100):
                if dry_run:
                    print(
                        f"Skipping image download for {uid}."
                    )
                else:
                    with open(target_folder / f"{uid}.png", "wb") as out_file:
                        r_image = requests.get(url, stream=True)
                        r_image.raise_for_status()
                        shutil.copyfileobj(r_image.raw, out_file)
                        # Downloaded image for {uid}.
                        n_downloaded += 1
                        del r_image
            else:
                # No image available for {uid}
                n_no_image += 1
        except Exception as exc:
            print(f"Error retrieving face for UID {uid} ({str(exc)})")
    print(f"Downloaded {n_downloaded}, non-existent players {n_non_existent}, players without face data {n_no_image}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dry-run", help="Target image folder", action="store_true")
    parser.add_argument("-r", "--rtf", help="Input RTF file", required=True)
    parser.add_argument("-t", "--target", help="Target image folder", required=True)
    parser.add_argument("-x", "--xml", help="Input XML file (sortitoutsi)", required=False, default=None)

    args = parser.parse_args()
    main(
        args.rtf,
        args.target,
        args.xml,
        args.dry_run,
    )
