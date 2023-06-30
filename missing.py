#! /usr/bin/env python
import argparse
from typing import Optional


def main(
    xml_input: str, rtf_input: str, rtf_output: str, xml_players: Optional[str] = None
) -> None:
    real_uids = set()
    if xml_players:
        with open(xml_players, "r") as f_xml:
            for line in f_xml.readlines():
                output_line = line
                if line.strip().startswith("<record from="):
                    uid = int(line.split(" ")[-1].split("/")[3])
                    real_uids.add(uid)
        print(f"Loaded {len(real_uids)} real players from XML")
    existing_uids = set(real_uids)
    face_ids = set()
    output_lines = []
    n_duplicate_faces, n_real_players, n_path_errors = 0, 0, 0
    try:
        with open(xml_input, "r") as f_xml:
            for line in f_xml.readlines():
                output_line = line
                if line.strip().startswith("<record from="):
                    uid = int(line.split(" ")[-1].split("/")[3])
                    existing_uids.add(uid)
                    if uid in real_uids:
                        n_real_players += 1
                        continue
                    category, face_id = line.split('"')[1].split("/")
                    if not face_id.startswith(category):
                        n_path_errors += 1
                        face_category = "".join(
                            [char for char in face_id if not char.isdigit()]
                        )
                        output_line = output_line.replace(
                            f"{category}/{face_category}",
                            f"{face_category}/{face_category}",
                        )
                    if "Italmed/ItalMed" in output_line:
                        n_path_errors += 1
                        output_line = output_line.replace(
                            "Italmed/ItalMed", "ItalMed/ItalMed"
                        )
                    if face_id in face_ids:
                        n_duplicate_faces += 1
                    face_ids.add(face_id)
                output_lines.append(output_line)
        print(f"Loaded {len(existing_uids)} players from XML")
        print(f"Found {n_real_players} incorrectly included real players")
        print(f"Found {n_duplicate_faces} duplicated faces")
        print(f"Found {n_path_errors} incorrect image paths")

        if n_path_errors:
            xml_output_path = xml_input.replace(".xml", ".fixed.xml")
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
    except FileNotFoundError as exc:
        print(f"Could not load input files.\n{str(exc)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rtf", help="Input RTF file", required=True)
    parser.add_argument("--xml", help="Input XML file", required=True)
    parser.add_argument("--out", help="Output RTF file", required=False)
    parser.add_argument(
        "--players", help="Input XML file of real players", default=None, required=False
    )
    args = parser.parse_args()
    if not args.out:
        args.out = args.rtf.replace(".rtf", ".missing.rtf")
    main(args.xml, args.rtf, args.out, args.players)
