#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from subprocess import check_call
import re
import shutil
from typing import Dict

import attr


@attr.s
class FreqFileResult:
    path: Path = attr.ib()
    freq: str = attr.ib()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", "-o", help="Name of output directory.", required=True)
    ap.add_argument(
        "--insertgaps",
        "-ingap",
        help="the position where you would like to insert gap characters.",
    )
    ap.add_argument(
        "--number", "-n", type=int, help="Number of 6 sequence samples.", required=True
    )
    ap.add_argument(
        "--seed",
        "-s",
        type=int,
        help="The seed(s) you want to set for the MCMC random generator.",
    )
    ap.add_argument(
        "--sameclonedata",
        "-scd",
        required=True,
        metavar=("dirname", "pattern"),
        nargs=2,
        help="The location of the file(s) from which you sample your original 6 sequences, as well as the added sequences acting as the 'same clone' addition.",
    )
    ap.add_argument(
        "--diffclonedata",
        "-dcd",
        required=True,
        metavar=("dirname", "pattern"),
        nargs=2,
        help="The location of the file(s) from which you sample the additional sequences from a different clone. Must not be the same file(s) as those specified by --sameclonedata.",
    )
    A = ap.parse_args()

    output_base_path = Path(A.output).resolve()

    SAMPLE_COUNT = int(A.number)

    # This function checks if the output folder exists and if not, creates it. Then, it runs the subsampler to randomly sample 1 sequence from either the same or different clone to combine with the original 6 sequence samples that were pre-created.
    def create_output_directory(
        freq: str, case: str, combined_from_path: Path = None, is_same_clone=False
    ):
        is_combined = combined_from_path is not None

        out = output_base_path / f"freq{freq}" / case
        sameclone_path = output_base_path / f"freq{freq}" / "sameclone"

        try:
            out.mkdir(parents=True)
        except FileExistsError:
            print(f"Skipping existing MCMC run folder {out!s}.")
            return

        print(f"Created MCMC run folder {out!s}.")

        # Want to generate the 6 sequence samples only once
        if is_same_clone:
            check_call(
                [
                    "subsamplefasta.py",
                    "--inFile",
                    str(combined_from_path),
                    "--outFile",
                    "6seq_samp",
                    "--number",
                    "6",
                    "--iterations",
                    str(SAMPLE_COUNT),
                ],
                cwd=str(out),
            )

        if is_combined:
            check_call(
                [
                    "subsamplefasta.py",
                    "--inFile",
                    str(combined_from_path),
                    "--outFile",
                    "1seq_samp",
                    "--number",
                    "1",
                    "--iterations",
                    str(SAMPLE_COUNT),
                ],
                cwd=str(out),
            )

        # Name input files
        inputs = []
        for i in range(1, SAMPLE_COUNT + 1):
            input_name = f"{case}_samp_{i}.fasta"

            with open(out / input_name, "wb") as wfile:
                with open(sameclone_path / f"6seq_samp_{i}.fasta", "rb") as rfile:
                    shutil.copyfileobj(rfile, wfile)

                # Append the file to be combined
                if is_combined:
                    with open(out / f"1seq_samp_{i}.fasta", "rb") as rfile:
                        shutil.copyfileobj(rfile, wfile)

            inputs.append(input_name)

        # Write metadata for this MCMC run
        meta = {
            "origin.is_combined": is_combined,
            "origin.freq": freq,
            "origin.prefix": case,
            "inputs": inputs,
            "mcmc.nst": 6,
            "mcmc.rates": "invgamma",
            "mcmc.ngammacat": 4,
            "mcmc.brlenspr": "unconstrained:GammaDir(1.0,0.100,1.0,1.0)",
            "mcmc.shapepr": "exp(1.0)",
            "mcmc.statefreqpr": "dirichlet(1.0,1.0,1.0,1.0)",
            "mcmc.revmatpr": "Dirichlet(1.0,1.0,1.0,1.0,1.0,1.0)",
            "mcmc.seed": None if A.seed is None else int(A.seed),
            "mcmc.ngen": 10_000_000,
            "mcmc.samplefreq": 1000,
            "mcmc.printfreq": 1000,
            "mcmc.burninfrac": 0.1,
            "mcmc.nchains": 4,
            "mcmc.nruns": 2,
            "mcmc.autoclose": True,
            "mcmc.nowarnings": True,
            "fasta_to_nexus.insert_gap_at": None
            if A.insertgaps is None
            else int(A.insertgaps),
        }
        if is_combined:
            meta["origin.combine_path"] = str(combined_from_path)

        (out / "parameters.json").write_text(
            json.dumps(meta, indent=2), encoding="utf-8"
        )

    def find_files_by_pattern(dirname_and_pattern) -> Dict[float, FreqFileResult]:
        dirname, pattern = dirname_and_pattern

        if pattern == "":
            pattern = "freq([.0-9]+)"

        files = {}
        for path in Path(dirname).iterdir():
            m = re.search(pattern, path.name)
            print(path.name)
            print(m)
            if not m:
                continue

            freq = m.group(1)

            files[float(freq)] = FreqFileResult(path=path, freq=freq)

        return files

    sameclone_files = find_files_by_pattern(A.sameclonedata)
    diffclone_files = find_files_by_pattern(A.diffclonedata)

    for freq, sameclone_file in sameclone_files.items():
        freq_str = sameclone_file.freq

        diffclone_file = diffclone_files[freq]

        # Blocks below determine the clone categories (the original 6 sequences or combined with a sequence from the same or different clone) and also define important variables
        create_output_directory(
            freq=freq_str,
            is_same_clone=True,
            combined_from_path=sameclone_file.path.resolve(),
            case="sameclone",
        )

        create_output_directory(freq=freq_str, combined_from_path=None, case="baseline")

        create_output_directory(
            freq=freq_str,
            combined_from_path=diffclone_file.path.resolve(),
            case="diffclone",
        )


if __name__ == "__main__":
    main()
