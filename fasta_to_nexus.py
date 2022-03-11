#! /usr/bin/env python3

import argparse
from pathlib import Path
import sys


def readArguments():
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()
    required = parser.add_argument_group("Required Arguments")
    required.add_argument(
        "--inFile",
        type=str,
        nargs="*",
        required=True,
        help="Input file name, has to be a FASTA file. Usage: fasta-to-nexus.py --inFile <path/to/fasta> --outFile <path/to/nexus>",
    )
    optional = parser.add_argument_group("Optional Arguments")
    optional.add_argument(
        "--insert-gap-at",
        type=int,
        help="If the sequences don't have the same length, insert a gap at this index. If this option is absent, truncate the sequences that are shorter than the minimum sequence length",
    )
    args = parser.parse_args()
    return args


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, "%s: error: %s\n" % (self.prog, message))


# Parse fasta file
def prepinfile(infile):
    with open(infile, "r", encoding="utf-8") as fasta:
        seqs = {}
        order_seq = None
        lines = fasta.readlines()
        for i in lines:
            i = i.replace("\n", "").replace("\r", "")
            if i:
                if i.startswith(">"):
                    label = i[1:]
                    seqs[label] = []
                    order_seq = seqs[label]
                else:
                    if order_seq is None:
                        raise Exception("Sequence data found before label")
                    order_seq.extend(i.replace(" ", ""))
    return seqs


# Convert into nexus
def genNexus(outfile, seqs, insert_gap_at):
    with open(outfile, "w+", encoding="utf-8") as nexus:
        nexus.write("#NEXUS\n")

        # Sets the value of nchar depending on the value of the argument insert_gap_as
        if insert_gap_at is not None:
            nchar = max(len(s) for s in seqs.values())
        else:
            nchar = min(len(s) for s in seqs.values())

        nexus.write("begin data;\n")
        nexus.write(f"dimensions ntax={len(seqs)} nchar={nchar};\n")
        nexus.write("format datatype=dna missing=? gap=-;\n")
        nexus.write("matrix\n")
        for taxlabel, seq in sorted(seqs.items()):
            seq_string = "".join(seq).upper()
            if len(seq_string) != nchar:
                # Add gap characters if requested by user
                if insert_gap_at is not None:
                    seq_string = (
                        seq_string[:insert_gap_at]
                        + "-" * (nchar - len(seq_string))
                        + seq_string[insert_gap_at:]
                    )
                else:
                    # Truncate
                    seq_string = seq_string[:nchar]
            nexus.write(f"{taxlabel} {seq_string}\n")
        nexus.write("\t;\n")
        nexus.write("end;\n")
    return


# Carries out the functions from above and names the output files
def main(args):
    """Usage: Argument after --inFile should either be listed manually or expanded using $(find [directory] -name [filename])."""
    for n, f in enumerate(args.inFile):
        f = Path(f)
        seqs = prepinfile(f)
        output_path = f.with_suffix(".nexus")
        genNexus(output_path, seqs, args.insert_gap_at)
    print(f"{n+1} FASTA files converted successfully.")
    return


if __name__ == "__main__":
    args = readArguments()
    main(args)
