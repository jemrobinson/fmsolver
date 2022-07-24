#! /usr/bin/env python
import argparse


def main(xml_input, rtf_input, rtf_output):
    existing_uids = set()
    face_ids = set()
    with open(xml_input, "r") as f_xml:
        for line in f_xml.readlines():
            if line.startswith("<record from="):
                category, face_id = line.split('"')[1].lower().split("/")
                if not face_id.startswith(category):
                    print(f"Face '{face_id}' does not belong to '{category}'")
                if face_id in face_ids:
                    print(f"Duplicate face: {face_id}")
                face_ids.add(face_id)
                uid = int(line.split(" ")[-1].split("/")[3])
                existing_uids.add(uid)
    print(f"Loaded {len(existing_uids)} players from XML")

    missing_players = []
    with open(rtf_input, "r") as f_rt_in:
        # Data is: uid, nationality, second_nationality, name, hair_length, hair_colour, skin_tone
        for line in f_rt_in.readlines():
            if line.startswith("| -"):
                continue
            try:
                uid = int(line.split("|")[1].strip())
                if uid not in existing_uids:
                    missing_players.append(line)
            except (IndexError, ValueError):
                pass
    print(f"Found {len(missing_players)} players without faces in RTF")

    if missing_players:
        with open(rtf_output, "w") as f_rt_out:
            f_rt_out.write(
                "| UID       | Nat       | 2nd Nat   | Name                                      |           |           |           |\n"
            )
            for player in missing_players:
                f_rt_out.write(
                    "| ------------------------------------------------------------------------------------------------------------------|\n"
                )
                f_rt_out.write(player)
            f_rt_out.write(
                "| ------------------------------------------------------------------------------------------------------------------|\n"
            )
        print(f"Wrote RTF output to {rtf_output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--xml", help="Input XML file")
    parser.add_argument("--rtf", help="Input RTF file")
    parser.add_argument("--out", help="Output RTF file")
    args = parser.parse_args()
    main(args.xml, args.rtf, args.out)
