#!/usr/bin/env python3

import argparse
import json
import re
import io
import pandas as pd
from pathlib import Path
from typing import List


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inpath", help="Input JSON parameters files.", type=Path, nargs="*")
    A = ap.parse_args()

    rows = []
    for parameters_json in A.inpath:
        rows.extend(process_parameter(parameters_json))

    # pass in list of dicts to DataFrame constructor
    df = pd.DataFrame(rows)
    print(df)
    df.to_csv("test.csv")


def process_parameter(parameters_json: Path) -> List[dict]:
    """
    Read ``parameter.json`` and parse the galax output files in the
    directory. Return a list of dictionaries corresponding to each of
    the galax output files.

    Each dictionary contains the the "galax_information" and
    "file_index" keys, as well as a ``param.whatever`` key for each of
    the ``whatever`` keys in the ``parameters.json``.
    """
    meta = json.loads(parameters_json.read_text(encoding="utf-8"))

    # this will be used for all the rows generated out of this parameter file
    basedict = {"param." + k: v for k, v in meta.items()}

    result = []
    for index, input_file_name in enumerate(meta["inputs"], 1):
        # we don't actually do anything with input_file_name

        # parse in galax information metric output
        galax_output_path = parameters_json.parent / f"samp{index}merged.txt"
        df = parse_galax_information_table_output(
            galax_output_path.read_text(encoding="utf-8")
        )

        # create information for this row by copying parameters dict
        rowdata = basedict.copy()
        rowdata["galax_information"] = df.iloc[2, 6]
        rowdata["file_index"] = index
        result.append(rowdata)

    return result


def parse_galax_information_table_output(text):
    m = re.search("\n\n" r"(\s*treefile)\s+unique\s+coverage", text)
    assert m, "Can't find table."
    first_column_length = m.end(1) - m.start(1)
    table_lines = []
    for line in text[m.start(1) :].split("\n"):
        if not line:
            break
        line = "_".join(line[:first_column_length].split()) + line[first_column_length:]
        table_lines.append(line)
    print(table_lines)
    df = pd.read_table(io.StringIO("\n".join(table_lines)), sep=r"\s+")
    return df


if __name__ == "__main__":
    main()
