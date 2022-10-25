#! /usr/bin/env python
import argparse


def main(xml_input, rtf_input, rtf_output):
    existing_uids = set()
    face_ids = set()
    output_lines = []
    n_duplicate_faces, n_path_errors = 0, 0
    with open(xml_input, "r") as f_xml:
        for line in f_xml.readlines():
            output_line = line
            if line.startswith("<record from="):
                category, face_id = line.split('"')[1].split("/")
                if not face_id.startswith(category):
                    n_path_errors += 1
                    face_category = "".join([char for char in face_id if not char.isdigit()])
                    output_line = output_line.replace(f"{category}/{face_category}", f"{face_category}/{face_category}")
                if face_id in face_ids:
                    n_duplicate_faces += 1
                face_ids.add(face_id)
                uid = int(line.split(" ")[-1].split("/")[3])
                existing_uids.add(uid)
            output_lines.append(output_line)
    print(f"Loaded {len(existing_uids)} players from XML")
    print(f"Found {n_duplicate_faces} duplicated faces")
    print(f"Found {n_path_errors} incorrect image paths")

    if n_path_errors:
        xml_output_path = f"{xml_input}.fixed"
        with open(xml_output_path, "w", newline="\r\n") as f_xml_out:
            for line in output_lines:
                f_xml_out.write(line)
            print(f"Wrote fixed XML output to {xml_output_path}")

    missing_players = []
    with open(rtf_input, "r") as f_rtf_in:
        # Data is: uid, nationality, second_nationality, name, hair_length, hair_colour, skin_tone
        for line in f_rtf_in.readlines():
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
        with open(rtf_output, "w") as f_rtf_out:
            f_rtf_out.write(
                "| UID       | Nat       | 2nd Nat   | Name                                      |           |           |           |\n"
            )
            for player in missing_players:
                f_rtf_out.write(
                    "| ------------------------------------------------------------------------------------------------------------------|\n"
                )
                f_rtf_out.write(player)
            f_rtf_out.write(
                "| ------------------------------------------------------------------------------------------------------------------|\n"
            )
        print(f"Wrote RTF output for missing players to {rtf_output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--xml", help="Input XML file")
    parser.add_argument("--rtf", help="Input RTF file")
    parser.add_argument("--out", help="Output RTF file")
    args = parser.parse_args()
    main(args.xml, args.rtf, args.out)
