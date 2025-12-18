import argparse
from pathlib import Path
import bpy
from .export_sollumz import run_export


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--log")
    parser.add_argument("--resource-name", required=True)
    args = parser.parse_args()
    run_export("ui_final", Path(args.output), args.resource_name, args.log)


if __name__ == "__main__":
    main()
