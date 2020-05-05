#!/usr/bin/env python3

import argparse
import bz2
import gzip
import json
import os
import sys


def ensure_dir(path, name="directory"):
    if os.path.exists(path):
        if not os.path.isdir(path):
            print(
                f"Error: {name} '{path}' exists but is not a directory. Exiting...",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        print(f"Creating {name} '{path}'", file=sys.stderr)
        os.makedirs(path)


def extract_refsnp_merged(args):
    entry = 0
    split, refsnp_merged, output_path = args.split, args.refsnp_merged, args.output_path

    if split > 1:
        ensure_dir(output_path, "output_path")
        f_outs = [
            gzip.open(os.path.join(output_path, f"{n:02}.gz"), "wb")
            for n in range(1, split + 1)
        ]
    else:
        f_outs = [gzip.open(output_path, "wb")]

    try:
        with bz2.open(refsnp_merged, "rt", encoding="utf-8") as f_in:
            for line in f_in:
                rsmerge_obj = json.loads(line)
                refsnp_id = rsmerge_obj["refsnp_id"]
                merged_into = rsmerge_obj.get("merged_snapshot_data", {}).get("merged_into", [])

                if merged_into:
                    entry += 1
                    f_out = f_outs[entry % split]
                    f_out.write(
                        ("\t".join([refsnp_id, merged_into[0]]) + "\n").encode()
                    )
    finally:
        for f_out in f_outs:
            f_out.close()


def main(argv):
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description="Generate gzipped tsv file or gzipped tsv split-files from NCBI refsnp-merged.json.bz2",
    )

    parser.add_argument("--split", type=int, default=1)
    parser.add_argument("refsnp_merged")
    parser.add_argument("output_path")

    args = parser.parse_args(argv)

    extract_refsnp_merged(args)


if __name__ == "__main__":
    main(sys.argv[1:])
