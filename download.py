#! /usr/bin/env python
import argparse
import os
import pathlib
import shutil
import requests


def main(
    rtf_input: pathlib.Path, target_folder: pathlib.Path, xml_input: pathlib.Path, dry_run: bool
) -> None:
    # Load existing players
    existing_uids = set()
    with open(xml_input, "r") as f_xml_in:
        for line in f_xml_in.readlines():
            if line.strip().startswith("<record from"):
                existing_uids.add(int(line.split('"')[1].split("/")[1]))
    print(f"There are {len(existing_uids)} existing players")

    # Identify players
    downloadable_uids = set()
    with open(rtf_input, "r") as f_rtf_in:
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
    os.makedirs(target_folder, exist_ok=True)
    for idx, uid in enumerate(sorted(downloadable_uids), start=1):
        try:
            if idx % 1000 == 0:
                print(
                    f"Working on player {idx}/{len(downloadable_uids)}..."
                )
            url = f"https://sortitoutsi.b-cdn.net/uploads/face/{uid}.png"
            response_exists = requests.get(url)
            if (response_exists.status_code == 200) and (len(response_exists.content) > 100):
                if dry_run:
                    print(
                        f"Skipping image download for {uid}"
                    )
                else:
                    with open(target_folder / f"{uid}.png", "wb") as out_file:
                        response_raw = requests.get(url, stream=True)
                        response_raw.raise_for_status()
                        shutil.copyfileobj(response_raw.raw, out_file)
                        print(
                            f"Downloaded image for {uid}"
                        )
                        del response_raw
            del response_exists
        except Exception as exc:
            print(f"Error retrieving face for UID {uid} ({str(exc)})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dry-run", help="Target image folder", action="store_true")
    parser.add_argument("-r", "--rtf", help="Input RTF file", required=True)
    parser.add_argument("-x", "--xml", help="Input XML file", required=True)
    parser.add_argument("-t", "--target", help="Target image folder", required=True)

    args = parser.parse_args()
    main(
        pathlib.Path(args.rtf).resolve(),
        pathlib.Path(args.target).resolve(),
        pathlib.Path(args.xml).resolve(),
        args.dry_run,
    )
