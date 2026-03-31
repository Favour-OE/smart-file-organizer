import argparse
import os
import sys
from sorter import sort_files, watch_folder

DEFAULT_SOURCE = os.path.join(os.path.dirname(__file__), "test_folder_1")
DEFAULT_DEST = os.path.join(os.path.dirname(__file__), "test_folder_2")

def main():
    parser = argparse.ArgumentParser(
    description="Smart File Organizer - Sort files into category folders",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""Examples:
  python main.py                                    # Use default folders
  python main.py -s ./my_files -d ./organized       # Custom folders
  python main.py -m watch                           # Watch mode
  python main.py --recursive --categories Audio Video  # Recursive, Audio+Video only
"""
  )
    parser.add_argument("-s", "--source", default=DEFAULT_SOURCE, help="Source folder (default: test_folder_1)")
    parser.add_argument("-d", "--dest", "--destination", dest="destination", default=DEFAULT_DEST, help="Destination folder (default: test_folder_2)")
    parser.add_argument("-m", "--mode", choices=["sort", "watch"], default="sort", help="Mode: 'sort' once or 'watch' continuously (default: sort)")
    parser.add_argument("-r", "--recursive", action="store_true", help="Include files in subfolders")
    parser.add_argument("--log", action="store_true", help="Log each file move")
    parser.add_argument("--categories", nargs="+", help="Categories to sort (default: all)")
    args = parser.parse_args()

    if not os.path.isdir(args.source):
        print(f"Error: Source folder not found: {args.source}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(args.destination):
        print(f"Error: Destination folder not found: {args.destination}", file=sys.stderr)
        sys.exit(1)

    print(f"Smart File Organizer")
    print(f"  Mode:        {args.mode}")
    print(f"  Source:      {args.source}")
    print(f"  Destination: {args.destination}")
    print(f"  Recursive:   {args.recursive}")
    print(f"  Categories:  {args.categories or 'all'}")
    print()

    if args.mode == "watch":
        print("Watching for changes... (Ctrl+C to stop)")
        watch_folder(
            args.source, args.destination, args.categories, args.recursive, args.log
        )
    else:
        counts = sort_files(
            args.source, args.destination, args.categories, args.recursive, args.log
        )
        line = "=" * 40
        print()
        print(line)
        print("SUMMARY")
        print(line)
        total = sum(counts.values())
        for category in sorted(counts.keys()):
            print(f"  {category:12} {counts[category]:3} files")
        print(line)
        print(f"  {'TOTAL':12} {total:3} files")
        print(line)

if __name__ == "__main__":
  main()
