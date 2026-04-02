import os
import shutil
import time
from datetime import datetime
from config import FILE_TYPES

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "activity_log.txt")

def get_category(filename):
  for category, extensions in FILE_TYPES.items():
    if not extensions:
      continue
    for extension in extensions:
      if filename.lower().endswith(extension):
        return category
  return "Others"

def should_sort(category, categories):
  if categories is None:
    return True
  return category in categories

def log_to_file(message):
  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  with open(LOG_FILE, "a", encoding="utf-8") as f:
    f.write(f"[{timestamp}] {message}\n")

def sort_files(source_folder, destination_folder, categories=None, recursive=False, log=False, duplicate_handling=True):
  counts = {}
  for entry in os.scandir(source_folder):
    if entry.is_file(follow_symlinks=True):
      category = get_category(entry.name)
      if not should_sort(category, categories):
        continue
      result = _move_file(entry.path, destination_folder, category, entry.name, log, duplicate_handling)
      counts[category] = counts.get(category, 0) + 1
      if log and result:
        log_to_file(result)
    elif recursive and entry.is_dir(follow_symlinks=True):
      sub_counts = sort_files(entry.path, destination_folder, categories, recursive, log, duplicate_handling)
      for cat, cnt in sub_counts.items():
        counts[cat] = counts.get(cat, 0) + cnt
  return counts

def _move_file(src, dest_root, category, filename, log, duplicate_handling=True):
  target_folder = os.path.join(dest_root, category)
  dest_path = os.path.join(target_folder, filename)
  os.makedirs(target_folder, exist_ok=True)
  
  result = None
  if os.path.exists(dest_path):
    if duplicate_handling:
      base, ext = os.path.splitext(filename)
      counter = 1
      while os.path.exists(os.path.join(target_folder, f"{base}_{counter}{ext}")):
        counter += 1
      dest_path = os.path.join(target_folder, f"{base}_{counter}{ext}")
    else:
      return None
  
  shutil.move(src, dest_path)
  if log:
    result = f"Moved: {filename} -> {category}/"
    print(result)
  return result

def reverse_sort(source_folder, destination_folder, categories=None, recursive=False, log=False, duplicate_handling=True):
  counts = {}
  for entry in os.scandir(destination_folder):
    if entry.is_dir(follow_symlinks=True):
      category = entry.name
      if not should_sort(category, categories):
        continue
      for file_entry in os.scandir(entry.path):
        if file_entry.is_file(follow_symlinks=True):
          dest_path = os.path.join(source_folder, file_entry.name)
          if os.path.exists(dest_path):
            if duplicate_handling:
              base, ext = os.path.splitext(file_entry.name)
              counter = 1
              while os.path.exists(os.path.join(source_folder, f"{base}_{counter}{ext}")):
                counter += 1
              dest_path = os.path.join(source_folder, f"{base}_{counter}{ext}")
            else:
              continue
          shutil.move(file_entry.path, dest_path)
          result = None
          if log:
            result = f"Restored: {file_entry.name} <- {category}/"
            print(result)
            log_to_file(result)
          counts[category] = counts.get(category, 0) + 1
      if not os.listdir(entry.path):
        os.rmdir(entry.path)
    elif recursive:
      sub_counts = reverse_sort(entry.path, source_folder, categories, recursive, log, duplicate_handling)
      for cat, cnt in sub_counts.items():
        counts[cat] = counts.get(cat, 0) + cnt
  return counts

def watch_folder(source_folder, destination_folder, categories=None, recursive=False, log=False, duplicate_handling=True):
  try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
  except ImportError:
    print("Error: watchdog required for watch mode. Run: pip install watchdog", file=sys.stderr)
    sys.exit(1)
  
  import sys
  
  class SortHandler(FileSystemEventHandler):
    def __init__(self, dest, cats, lg, dup):
      self.dest = dest
      self.cats = cats
      self.lg = lg
      self.dup = dup
    
    def on_created(self, event):
      if event.is_directory:
        return
      category = get_category(os.path.basename(event.src_path))
      if should_sort(category, self.cats):
        time.sleep(0.1)
        result = _move_file(event.src_path, self.dest, category, os.path.basename(event.src_path), self.lg, self.dup)
        if self.lg and result:
          log_to_file(result)
  
  event_handler = SortHandler(destination_folder, categories, log, duplicate_handling)
  observer = Observer()
  observer.schedule(event_handler, source_folder, recursive=recursive)
  observer.start()
  
  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    observer.stop()
  observer.join()
