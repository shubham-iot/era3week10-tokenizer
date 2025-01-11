import re

def clean_punjabi_text(text: str) -> str:
    # Define regex patterns and their replacements
    cleaning_patterns = [
        # Remove HTML entities (like &ndash; &amp; &#231;)
        (r'&[a-zA-Z]+;|&#[0-9]+;', ''),
        
        # Remove square brackets and their contents
        (r'\[[^\]]*\]', ''),
        
        # Remove curly braces and their contents
        (r'\{[^}]*\}', ''),
        
        # Remove parentheses and their contents
        (r'\([^)]*\)', ''),
        
        # Remove English characters and numbers
        (r'[a-zA-Z0-9]', ''),
        
        # Remove special characters except Punjabi-specific ones
        (r'[^\u0A00-\u0A7F\s]', ''),
        
        # Remove URLs
        (r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ''),
        
        # Remove multiple spaces
        (r'\s+', ' '),
        
        # Remove lines with less than 3 Punjabi characters
        # Keeps only Punjabi Unicode characters (U+0A00 to U+0A7F) and whitespace
        (r'^[^\u0A00-\u0A7F]*[^\u0A00-\u0A7F]{0,2}[^\u0A00-\u0A7F]*$', '')
    ]
    
    # Apply each pattern
    cleaned_text = text
    for pattern, replacement in cleaning_patterns:
        cleaned_text = re.sub(pattern, replacement, cleaned_text)
    
    # Strip whitespace
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text

# Example usage and testing
if __name__ == "__main__":
    # Read corpus
    with open('pa_corpus.txt', 'r', encoding='utf-8') as f:
        corpus = f.read()
    
    # Clean text
    cleaned_corpus = clean_punjabi_text(corpus)
    
    # Save cleaned corpus
    with open('pa_corpus_cleaned.txt', 'w', encoding='utf-8') as f:
        f.write(cleaned_corpus)
    
    # Print sample for verification
    print("Sample of cleaned text:")
    print(cleaned_corpus[:500])
    
    # Print statistics
    print("\nStatistics:")
    print(f"Original length: {len(corpus)}")
    print(f"Cleaned length: {len(cleaned_corpus)}")
    print(f"Reduction: {(1 - len(cleaned_corpus)/len(corpus))*100:.2f}%")