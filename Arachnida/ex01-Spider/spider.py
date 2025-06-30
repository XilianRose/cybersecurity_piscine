#!/usr/bin/env python3

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import argparse, os, requests

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
	parser = argparse.ArgumentParser(description='Web scraper to extract images from a webpage.')
	parser.add_argument('-r', action='store_true', help='Recursively downloads the images in a URL received as a parameter')
	parser.add_argument('-l', type=int, default=5, help='Indicates the maximum depth level of the recursive download')
	parser.add_argument('-p', type=str, default='./data/', help='Indicates the path where the downloaded files will be saved')
	parser.add_argument('url', help='The URL of the webpage to scrape')
	return parser.parse_args()

args = get_args()
url = args.url
recursion = args.r
max_depth = args.l
path = args.p

print(f"🕷️ {LILAC} Starting web scraper...{NC}")

print(f"URL		: {url}")
print(f"Recursion	: {recursion}")
print(f"Max Depth	: {max_depth}")
print(f"Path		: {path}")

if not os.path.exists(path):
	try:
		os.makedirs(path, exist_ok=True)
	except Exception as e:
		print(f"{RED}Error creating directory {path}{NC}: {e}")
		exit(1)

def sanitize_filename(filename):
	return ''.join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip().replace('"', '&quot;')

def scrape_images(url, path):
	response = requests.get(url)
	if response.status_code != 200:
		print(f"{RED}Error{NC}: Unable to access {url}")
		print(f"Status code: {response.status_code}")
		exit(1)
	soup = BeautifulSoup(response.text, 'html.parser')
	images = soup.find_all('img')
	if not images:
		print(f"No images found at {url}")
		exit(0)
	for img in images:
		img_url = img.get('src')
		if not img_url:
			continue
		if not img_url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
			print(f"{GRAY}Skipping non-image URL: {img_url}{NC}")
			continue
		if not img_url.startswith(('http://', 'https://')):
			img_url = requests.compat.urljoin(url, img_url)
		try:
			img_response = requests.get(img_url)
			if img_response.status_code == 200:
				filename = os.path.join(path, sanitize_filename(img_url.split('/')[-1]))
				if os.path.exists(filename):
					print(f"{GRAY}File {filename} already exists, skipping download...{NC}")
					continue
				with open(filename, 'wb') as f:
					f.write(img_response.content)
				print(f"{GREEN}Downloaded{NC}: {filename}")
			else:
				print(f"{RED} Failed to download {img_url}{NC}: {img_response.status_code}")
		except Exception as e:
			print(f"{RED} Error downloading {img_url}{NC}: {e}")

visited_urls = set(url)

def recursive_scrape(url, depth):
	if depth > max_depth:
		return
	if url in visited_urls:
		print(f"{GRAY}Already visited {url}, skipping...{NC}")
		return
	visited_urls.add(url)
	print(f"{LILAC}Scraping {url} at depth {depth}{NC}")
	scrape_images(url, path)
	response = requests.get(url)
	if response.status_code != 200:
		print(f"Error: Unable to access {url}")
		return
	soup = BeautifulSoup(response.text, 'html.parser')
	links = soup.find_all('a', href=True)
	for link in links:
		next_url = link['href']
		if not next_url.startswith(('http://', 'https://')):
			next_url = urljoin(url, next_url)
		if urlparse(next_url).netloc == urlparse(url).netloc:
			recursive_scrape(next_url, depth + 1)

if recursion:
	recursive_scrape(url, 0)
else:
	scrape_images(url, path)