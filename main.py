import argparse
import os
import sys
from sorter import sort_files

DEFAULT_SOURCE = os.path.join(os.path.dirname(__file__), "test_folder_1")
DEFAULT_DEST = os.path.join(os.path.dirname(__file__), "test_folder_2")

def main():
  parser = argparse.ArgumentParser(
    description="Smart File Organizer - Sort files into category folders",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""Examples:
  python main.py                                    # Use default folders
  python main.py -s ./my_files -d ./organized       # Custom folders
  python main.py --source ./downloads               # Source only
"""
  )
  parser.add_argument("-s", "--source", default=DEFAULT_SOURCE, help="Source folder (default: test_folder_1)")
  parser.add_argument("-d", "--dest", "--destination", dest="destination", default=DEFAULT_DEST, help="Destination folder (default: test_folder_2)")
  args = parser.parse_args()

  if not os.path.isdir(args.source):
    print(f"Error: Source folder not found: {args.source}", file=sys.stderr)
    sys.exit(1)

  if not os.path.isdir(args.destination):
    print(f"Error: Destination folder not found: {args.destination}", file=sys.stderr)
    sys.exit(1)

  print(f"Sorting files...")
  print(f"  Source:      {args.source}")
  print(f"  Destination: {args.destination}")
  print()

  counts = sort_files(args.source, args.destination)

  print()
  print("=" * 40)
  print("SUMMARY")
  print("=" * 40)
  total = sum(counts.values())
  for category in sorted(counts.keys()):
    print(f"  {category:12} {counts[category]:3} files")
  print("-" * 40)
  print(f"  {'TOTAL':12} {total:3} files")
  print("=" * 40)

if __name__ == "__main__":
  main()
