import bz2
import xml.etree.ElementTree as ET
import re
from tqdm import tqdm
import os
import humanize
from datetime import datetime

def is_punjabi_text(text, threshold=0.05):
    """Check if text contains Punjabi characters"""
    if not isinstance(text, str) or not text:
        return False

    # Count Punjabi characters (Gurmukhi script)
    punjabi_chars = len(re.findall(r'[\u0A00-\u0A7F]', text))
    total_chars = len(text)

    try:
        punjabi_ratio = punjabi_chars / total_chars if total_chars > 0 else 0
        return punjabi_chars > 0 and punjabi_ratio > threshold
    except ZeroDivisionError:
        return False

def clean_text(text):
    """Clean the extracted text"""
    if not isinstance(text, str) or not text:
        return "", 0, 0

    try:
        original_length = len(text)

        # Basic cleaning
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'http\S+|www\S+', '', text)
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\{\{[^\}]+\}\}', '', text)
        text = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', text)
        text = re.sub(r'\s+', ' ', text)
        text=  re.sub('<U\+[A-Z0-9]+>','', text)
        
        
        text = text.strip()

        cleaned_length = len(text)
        return text, original_length, cleaned_length
    except Exception as e:
        print(f"Error in clean_text: {str(e)}")
        return "", 0, 0


def process_wiki_dump(input_file):
    """Process the wiki dump file"""
    print(f"\nProcessing Wikipedia dump from {input_file}")
    output_file = 'pa_corpus.txt'

    articles_processed = 0
    articles_kept = 0
    total_original_chars = 0
    total_cleaned_chars = 0

    try:
        with bz2.open(input_file, 'rt', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:

            # Detect namespace dynamically
            namespace = None
            for event, elem in ET.iterparse(infile, events=('start', 'end')):
                if event == 'start' and elem.tag.endswith('mediawiki'):
                    namespace = re.match(r'\{.*\}', elem.tag).group(0)
                    print(f"Detected XML namespace: {namespace}")
                    break

            infile.seek(0)  # Reset file pointer

            # Add progress bar
            print("Initializing progress bar...")
            total_articles = sum(1 for _, elem in ET.iterparse(infile, events=('end',)) if elem.tag.endswith('page'))
            infile.seek(0)  # Reset file pointer
            pbar = tqdm(total=total_articles, desc="Processing articles", unit="article")

            for event, elem in ET.iterparse(infile, events=('end',)):
                if elem.tag.endswith('page'):
                    articles_processed += 1
                    pbar.update(1)

                    text_elem = elem.find(f'.//{namespace}text')
                    title_elem = elem.find(f'.//{namespace}title')

                    if text_elem is not None and text_elem.text:
                        # Debug first 5 articles
                        if articles_processed <= 5:
                            print(f"\nProcessing article #{articles_processed}")
                            print(f"Title: {title_elem.text if title_elem is not None else 'No title'}")
                            print(f"Original text sample: {text_elem.text[:200]}")

                        clean_content, orig_len, cleaned_len = clean_text(text_elem.text)

                        if clean_content and len(clean_content) > 50:
                            is_punjabi = is_punjabi_text(clean_content)

                            if articles_processed <= 5:
                                print(f"Is Punjabi: {is_punjabi}")
                                print(f"Clean text sample: {clean_content[:200]}")

                            if is_punjabi:
                                outfile.write(clean_content + '\n')
                                articles_kept += 1
                                total_original_chars += orig_len
                                total_cleaned_chars += cleaned_len

                    elem.clear()

            pbar.close()

    except Exception as e:
        print(f"Error during processing: {str(e)}")
        return None

    return {
        'articles_processed': articles_processed,
        'articles_kept': articles_kept,
        'total_original_chars': total_original_chars,
        'total_cleaned_chars': total_cleaned_chars
    }





def main():
    input_file = '.\pawiki-latest.xml.bz2' 

    # if not os.path.exists(input_file):
    #     print(f"Error: Could not find {input_file}")
    #     print("Please download it from: https://dumps.wikimedia.org/pawiki/latest/pawiki-latest-pages-articles.xml.bz2")
    #     return

    print(f"Found input file: {input_file}")
    print(f"File size: {humanize.naturalsize(os.path.getsize(input_file))}")

    start_time = datetime.now()
    stats = process_wiki_dump(input_file)

    if stats:
        print("\n=== Processing Statistics ===")
        print(f"Articles processed: {stats['articles_processed']:,}")
        print(f"Articles kept: {stats['articles_kept']:,}")

        if stats['articles_kept'] > 0:
            print(f"Original content size: {humanize.naturalsize(stats['total_original_chars'])} characters")
            print(f"Cleaned content size: {humanize.naturalsize(stats['total_cleaned_chars'])} characters")
            compression = (stats['total_cleaned_chars'] / stats['total_original_chars'] * 100) if stats['total_original_chars'] > 0 else 0
            print(f"Compression ratio: {compression:.1f}%")

        if os.path.exists('pa_corpus.txt'):
            print(f"Output file size: {humanize.naturalsize(os.path.getsize('pa_corpus.txt'))}")

    end_time = datetime.now()
    print(f"\nTotal processing time: {end_time - start_time}")

if __name__ == "__main__":
    main()
