#! /usr/bin/env python3

import sys, argparse
from Bio import SeqIO
from random import sample

# Command line arguments
def readArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inFile", type=str, help="Input file name.")
    parser.add_argument(
        "--outFile",
        type=str,
        help="Output file name. The output will always be a FASTA file, you don't need to specify '.fasta' in this argument.",
    )
    parser.add_argument(
        "--number",
        type=int,
        help="Number of sequences. Defaulted to 5 for convenience.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Number of times to run the subsampler.",
    )
    args = parser.parse_args()
    return args


def main(args):
    print("Subsampling...")
    for n in range(1, args.iterations + 1):
        # Read FASTA file
        with open(args.inFile, "r") as raw:
            dataset = SeqIO.parse(raw, "fasta")
            data_array = list(dataset)
            if len(data_array) == 0:
                print("Empty array. Check array. Exiting...")
                return -1
            subset = ((seq.name, seq.seq) for seq in sample(data_array, args.number))
            for i in subset:
                with open(args.outFile + "_" + str(n) + ".fasta", "a+") as outfile:
                    outfile.write(">{}\n{}\n".format(*i))  # Write FASTA file
                outfile.close()
    print("Done.")
    return 0


if __name__ == "__main__":
    args = readArguments()
    flag = main(args)
    if flag == -1:
        print(
            "Something really devastating has happened to this code, leading it to break horribly. Check the FASTA input file and whether it has been properly converted into a list."
        )
