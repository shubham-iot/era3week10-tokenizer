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

def is_punjabi_text(text):
    """Check if text contains Punjabi characters"""
    punjabi_pattern = re.compile(r'[\u0A00-\u0A7F]')  # Punjabi Unicode range
    return bool(punjabi_pattern.search(text))

def clean_text(text):
    """Clean the extracted text"""
    if not text:
        return "", 0, 0
        
    original_length = len(text)
    
    # Remove XML/HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Remove references like [1], [2], etc.
    text = re.sub(r'\[\d+\]', '', text)
    
    # Remove special Wiki markup
    text = re.sub(r'\{\{[^\}]+\}\}', '', text)
    text = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', text)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    cleaned_length = len(text)
    return text, original_length, cleaned_length

def process_wiki_dump():
    """Process the downloaded Wiki dump and extract clean text"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting Wikipedia dump processing...")
    
    output_file = 'pa_corpus.txt'
    stats = {
        'total_articles': 0,
        'total_articles_kept': 0,
        'total_original_chars': 0,
        'total_cleaned_chars': 0,
        'shortest_article': float('inf'),
        'longest_article': 0,
        'articles_below_threshold': 0,
        'non_punjabi_articles': 0
    }
    
    with bz2.open('pawiki-latest.xml.bz2', 'rt', encoding='utf-8') as file, \
         open(output_file, 'w', encoding='utf-8') as out_file:
        
        context = ET.iterparse(file, events=('end',))
        
        for event, elem in tqdm(context, desc="Processing articles"):
            if elem.tag.endswith('page'):
                stats['total_articles'] += 1
                
                try:
                    text_elem = elem.find('.//{http://www.mediawiki.org/xml/export-0.10/}text')
                    title_elem = elem.find('.//{http://www.mediawiki.org/xml/export-0.10/}title')
                    
                    if text_elem is not None and text_elem.text:
                        # Debug print for every 1000th article
                        if stats['total_articles'] % 1000 == 0:
                            print(f"\nProcessing article {stats['total_articles']}")
                            if title_elem is not None:
                                print(f"Title: {title_elem.text}")
                            print(f"Text preview: {text_elem.text[:100]}...")
                        
                        # Check if text contains Punjabi
                        if not is_punjabi_text(text_elem.text):
                            stats['non_punjabi_articles'] += 1
                            elem.clear()
                            continue
                        
                        clean_content, orig_len, cleaned_len = clean_text(text_elem.text)
                        
                        if clean_content and len(clean_content) > 50 and is_punjabi_text(clean_content):
                            out_file.write(clean_content + '\n')
                            stats['total_articles_kept'] += 1
                            stats['total_original_chars'] += orig_len
                            stats['total_cleaned_chars'] += cleaned_len
                            stats['shortest_article'] = min(stats['shortest_article'], cleaned_len)
                            stats['longest_article'] = max(stats['longest_article'], cleaned_len)
                        else:
                            stats['articles_below_threshold'] += 1
                            
                except Exception as e:
                    print(f"\nError processing article {stats['total_articles']}: {str(e)}")
                
                elem.clear()
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Processing completed")
    print("\n=== Corpus Statistics ===")
    print(f"Total articles processed: {stats['total_articles']:,}")
    print(f"Articles kept: {stats['total_articles_kept']:,}")
    print(f"Articles below threshold: {stats['articles_below_threshold']:,}")
    print(f"Non-Punjabi articles: {stats['non_punjabi_articles']:,}")
    
    if stats['total_articles_kept'] > 0:
        print(f"\nOriginal content size: {humanize.naturalsize(stats['total_original_chars'])} characters")
        print(f"Cleaned content size: {humanize.naturalsize(stats['total_cleaned_chars'])} characters")
        print(f"Compression ratio: {stats['total_cleaned_chars']/stats['total_original_chars']:.2%}")
        print(f"\nShortest article: {stats['shortest_article']:,} characters")
        print(f"Longest article: {stats['longest_article']:,} characters")
        print(f"Average article length: {stats['total_cleaned_chars']/stats['total_articles_kept']:,.0f} characters")
    else:
        print("\nWarning: No articles were processed successfully!")
        
    if os.path.exists(output_file):
        print(f"\nFinal corpus file size: {get_file_size(output_file)}")
    print("=====================")

def main():
    start_time = datetime.now()
    print(f"Starting corpus extraction at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        if not os.path.exists('pawiki-latest.xml.bz2'):
            download_wiki_dump()
        else:
            print(f"Using existing dump file: {get_file_size('pawiki-latest.xml.bz2')}")
        
        process_wiki_dump()
        
        # Clean up
        os.remove('pawiki-latest.xml.bz2')
        print("\nCleanup completed - removed downloaded dump file")
        
    except Exception as e:
        print(f"\nError during processing: {str(e)}")
        raise
    
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\nTotal processing time: {duration}")

if __name__ == "__main__":
    main()