import requests
import bz2
import xml.etree.ElementTree as ET
import re
from tqdm import tqdm
import os
from datetime import datetime
import humanize

def get_file_size(filepath):
    """Get human readable file size"""
    size_bytes = os.path.getsize(filepath)
    return humanize.naturalsize(size_bytes)

def download_wiki_dump():
    """Download the latest Punjabi Wikipedia dump"""
    url = "https://dumps.wikimedia.org/pawiki/latest/pawiki-latest-pages-articles.xml.bz2"
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting download of Punjabi Wikipedia dump...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    print(f"Total download size: {humanize.naturalsize(total_size)}")
    
    with open('pawiki-latest.xml.bz2', 'wb') as file, tqdm(
        desc='Downloading',
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            pbar.update(size)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Download completed")
    print(f"Compressed dump size: {get_file_size('pawiki-latest.xml.bz2')}")


    #==========================================================


def main():
    start_time = datetime.now()
    print(f"Starting corpus extraction at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not os.path.exists('pawiki-latest.xml.bz2'):
        download_wiki_dump()
    else:
        print(f"Using existing dump file: {get_file_size('pawiki-latest.xml.bz2')}")
    
     
    # Clean up
   # os.remove('pawiki-latest.xml.bz2')
    #print("\nCleanup completed - removed downloaded dump file")
    
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\nTotal processing time: {duration}")

if __name__ == "__main__":
    main()