import os
import shutil
import time
from config import FILE_TYPES

def get_category(filename):
  for category, extensions in FILE_TYPES.items():
    for extension in extensions:
      if filename.lower().endswith(extension):
        return category
  return "Others"

def should_sort(category, categories):
  if categories is None:
    return True
  return category in categories

def sort_files(source_folder, destination_folder, categories=None, recursive=False, log=False):
  counts = {}
  for entry in os.scandir(source_folder):
    if entry.is_file(follow_symlinks=True):
      category = get_category(entry.name)
      if not should_sort(category, categories):
        continue
      _move_file(entry.path, destination_folder, category, entry.name, log)
      counts[category] = counts.get(category, 0) + 1
    elif recursive and entry.is_dir(follow_symlinks=True):
      sub_counts = sort_files(entry.path, destination_folder, categories, recursive, log)
      for cat, cnt in sub_counts.items():
        counts[cat] = counts.get(cat, 0) + cnt
  return counts

def _move_file(src, dest_root, category, filename, log):
  target_folder = os.path.join(dest_root, category)
  dest_path = os.path.join(target_folder, filename)
  os.makedirs(target_folder, exist_ok=True)
  
  if os.path.exists(dest_path):
    base, ext = os.path.splitext(filename)
    dest_path = os.path.join(target_folder, f"{base}_1{ext}")
  
  shutil.move(src, dest_path)
  if log:
    print(f"Moved {filename} → {category}/")

def watch_folder(source_folder, destination_folder, categories=None, recursive=False, log=False):
  try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
  except ImportError:
    print("Error: watchdog required for watch mode. Run: pip install watchdog", file=sys.stderr)
    sys.exit(1)
  
  import sys
  
  class SortHandler(FileSystemEventHandler):
    def on_created(self, event):
      if event.is_directory:
        return
      if recursive and event.src_path.startswith(source_folder):
        pass
      category = get_category(os.path.basename(event.src_path))
      if should_sort(category, categories):
        time.sleep(0.1)
        _move_file(event.src_path, destination_folder, category, os.path.basename(event.src_path), log)
  
  event_handler = SortHandler()
  observer = Observer()
  observer.schedule(event_handler, source_folder, recursive=recursive)
  observer.start()
  
  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    observer.stop()
  observer.join()
