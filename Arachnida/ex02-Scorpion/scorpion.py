#!/usr/bin/env python3

import argparse, datetime
from PIL import Image
import os

RED = "\33[0;91m"
GREEN = "\33[0;92m"
YELLOW = "\33[0;93m"
BLUE = "\33[0;94m"
MAGENTA = "\33[0;95m"
CYAN = "\33[0;96m"
LILAC = "\33[38;5;141m"
GRAY = "\33[38;5;242m"
NC = "\33[0m"

def get_args():
	parser = argparse.ArgumentParser(description='Extract metadata from an image file.')
	parser.add_argument('filenames', type=str, nargs='+', help='One or more image files to extract EXIF data from.')
	return parser.parse_args()

def get_exif_data(filename, image):
	try:
		exif_data = image._getexif()
		if not exif_data:
			print(f"{YELLOW}No EXIF data found in {filename}{NC}")
			return None
		return exif_data
	except Exception as e:
		print(f"{RED}Error reading EXIF data from {filename}: {e}{NC}")
		return None
	
def print_exif_data(exif_data):
	if not exif_data:
		return
	print(f"{GREEN}	EXIF Data extracted:{NC}")
	for tag, value in exif_data.items():
		try:
			tag_name = Image.ExifTags.TAGS.get(tag, tag)
			print(f"{CYAN}{tag_name}{NC}: {value}")
		except Exception as e:
			print(f"{RED}Error processing tag {tag}: {e}{NC}")

def print_basic_attributes(filename, image):
	try:
		file_size = os.path.getsize(filename)
		created_time = datetime.datetime.fromtimestamp(os.path.getctime(filename))
		last_modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
		print(f"{GREEN}	Basic Attributes:{NC}")
		print(f"{LILAC}File{NC}: {filename}")
		print(f"{LILAC}Size{NC}: {file_size} bytes")
		print(f"{LILAC}Format{NC}: {image.format}")
		print(f"{LILAC}Mode{NC}: {image.mode}")
		print(f"{LILAC}Dimensions{NC}: {image.size[0]}x{image.size[1]} pixels")
		print(f"{LILAC}Created{NC}: {created_time}")
		print(f"{LILAC}Last Modified{NC}: {last_modified_time}")
	except Exception as e:
		print(f"{RED}Error retrieving file attributes for {filename}: {e}{NC}")

for filename in get_args().filenames:
	if not os.path.isfile(filename):
		print(f"{RED}File {filename} does not exist.{NC}")
		continue
	if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
		print(f"{GRAY}Skipping non-image file: {filename}{NC}")
		continue
	image = Image.open(filename)
	print_basic_attributes(filename, image)
	exif_data = get_exif_data(filename, image)
	print_exif_data(exif_data)