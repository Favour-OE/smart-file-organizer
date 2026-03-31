import os
import shutil
from config import FILE_TYPES

def get_category (filename):
  for category, extensions in FILE_TYPES.items():
    for extension in extensions:
      if filename.lower().endswith(extension):
        return category
  return "Others"

def sort_files(source_folder, destination_folder):
  for file in os.listdir(source_folder):
    file_path = os.path.join(source_folder, file)

    if os.path.isfile(file_path):
      category= get_category(file_path)
      target_folder = os.path.join(destination_folder, category)

      os.makedirs(target_folder, exist_ok =True)
      shutil.move(file_path, os.path.join(target_folder, file))
      print(f"Moved {file} → {category}")

