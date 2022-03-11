#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path
from subprocess import check_call

# https://creativecommons.org/share-your-work/public-domain/cc0/


def strip_suffix(string: str, suffix: str) -> str:
    assert string.endswith(suffix)
    return string[: -len(suffix)]


def main():
    ap = argparse.ArgumentParser()

    ap.add_argument("parameters", help="JSON file with parameters", type=Path)
    ap.add_argument(
        "--prepare",
        help="prepare files and generate inputs for mb",
        action="store_true",
    )
    ap.add_argument("--run", help="actually run mb", action="store_true")
    ap.add_argument("--postprocess", help="postprocess output", action="store_true")

    A = ap.parse_args()
    input_path = A.parameters.resolve()  # to absolute path
    os.chdir(str(input_path.parent))  # change directory to MCMC simulation folder

    meta = json.loads(input_path.read_text(encoding="utf-8"))

    conv_files = [f"{strip_suffix(f, '.fasta')}_conv.fasta" for f in meta["inputs"]]
    nexus_files = [f"{strip_suffix(f, '.fasta')}.nexus" for f in conv_files]

    if A.prepare:
        # construct arguments for mbblock
        mbblock_args = []
        for key, value in meta.items():
            _, sep, name = key.partition("mcmc.")
            if sep and name:
                if isinstance(value, bool):
                    value = "yes" if value else "no"
                elif isinstance(value, (int, float)):
                    value = str(value)

                assert isinstance(
                    value, str
                ), f"key {key} with value {value} is not string"

                mbblock_args.append(f"--{name}")
                mbblock_args.append(value)

        check_call(["charconverter.py", "--inFile"] + meta["inputs"])

        insert_gap_at = meta["fasta_to_nexus.insert_gap_at"]
        check_call(
            ["fasta_to_nexus.py", "--inFile"]
            + conv_files
            + ([] if insert_gap_at is None else ["--insert-gap-at", str(insert_gap_at)])
        )

        print("Calling mbblock with arguments", mbblock_args)
        check_call(
            ["mbblock_maker.py"]
            + mbblock_args
            + ["--outfile", "mbblock", "--inpath"]
            + nexus_files
        )

    if A.run:
        check_call(["mb", "mbblock.nexus"])

    if A.postprocess:
        for index, nexus_file_name in enumerate(nexus_files, 1):
            prefix = f"samp{index}"
            listfile_path = Path(f"{prefix}_listfile.txt")
            listfile_path.write_text(
                "".join(
                    f"{nexus_file_name}.run{run_index}.t\n"
                    for run_index in range(1, 2 + 1)
                )
            )
            check_call(
                [
                    "galax",
                    "--listfile",
                    str(listfile_path),
                    "--outfile",
                    f"{prefix}merged",
                ]
            )


if __name__ == "__main__":
    main()
