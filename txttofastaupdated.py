#!/usr/bin/env python3

import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--infile", help="Name of input file", required=True)
    ap.add_argument(
        "--outfile", help="Name of output file. Include file suffix", required=True
    )
    ap.add_argument(
        "--delimiter",
        type=str,
        help="Type of delimiter inside text files. , or \t are common examples.",
        required=True,
    )
    A = ap.parse_args()

    FileOutput = open(ap.outfile, "w")

    with open(ap.infile, "r") as FileInput:
        print("Converting to FASTA...")
        for strLine in FileInput:

            # Split strings on user-defined character
            splice = strLine.split(str(a.delimiter))

            # Output the header
            FileOutput.write("> " + splice[0])
            FileOutput.write("\n" + splice[1])

    FileOutput.close()
    print("Done.")


if __name__ == "__main__":
    main()
