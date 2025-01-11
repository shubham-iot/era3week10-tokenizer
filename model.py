import pickle
import os

def read_corpus(corpus_path: str):
    """Utility function to read the corpus file"""
    with open(corpus_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

class BPEPunjabiTokenizer:
    def __init__(self, corpus_path: str = None, max_vocab_size: int = 5000, sample_size: int = 20000):
        """
        Initialize tokenizer either for training (if corpus_path provided) 
        or for inference (if loading pre-trained)
        """
        if corpus_path:  # Training mode
            self.corpus = read_corpus(corpus_path)
            self.max_vocab_size = max_vocab_size
            self.corpus_vocab = sorted(list(set(self.corpus)))
            self.corpus_vocab_size = len(self.corpus_vocab)
            self.stoi = {ch: i for i, ch in enumerate(self.corpus_vocab)}
            self.itos = {i: ch for i, ch in enumerate(self.corpus_vocab)}
            self.sample_size = sample_size
            self.vocab, self.merges = self.train_bpe(self.corpus, self.max_vocab_size, self.sample_size)
        else:  # Inference mode - will be initialized by load()
            self.vocab = None
            self.merges = None

    # === Training-related methods (used only during training) ===
    
    def get_stats(self, ids):
        """Count frequency of adjacent pairs during training"""
        counts = {}
        for pair in zip(ids, ids[1:]):
            counts[pair] = counts.get(pair, 0) + 1
        return counts

    def merge(self, ids, pair, idx):
        """Merge frequent pairs during training"""
        newids = []
        i = 0
        while i < len(ids):
            if i < len(ids) - 1 and ids[i] == pair[0] and ids[i+1] == pair[1]:
                newids.append(idx)
                i += 2
            else:
                newids.append(ids[i])
                i += 1
        return newids

    def train_bpe(self, corpus, max_vocab_size, sample_size=None):
        """Train the BPE tokenizer on the corpus"""
        self.vocab = {idx: bytes([idx]) for idx in range(256)}
        if sample_size:
            corpus = corpus[:sample_size]
        
        num_merges = max_vocab_size - len(self.vocab)
        tokens = corpus.encode('utf-8')
        tokens = list(map(int, tokens))
        ids = list(tokens)
        self.merges = {}  # (int, int) -> int

        print(f"Starting training with {len(ids)} tokens...")
        
        for i in range(num_merges):
            stats = self.get_stats(ids)
            if not stats:
                break
            pair = max(stats, key=stats.get)
            idx = len(self.vocab) + i
            ids = self.merge(ids, pair, idx)
            self.merges[pair] = idx
            
            # merge the vocab
            self.vocab[idx] = self.vocab[pair[0]] + self.vocab[pair[1]]
            
            if (i + 1) % 100 == 0:
                print(f"Processed {i + 1}/{num_merges} merges...")

        print(f"Training complete. Compression ratio: {len(tokens) / len(ids):.2f}X")
        return self.vocab, self.merges

    # === Inference-related methods (used during normal operation) ===

    def encode(self, text):
        """Convert text to tokens using trained merges"""
        if self.vocab is None or self.merges is None:
            raise ValueError("Tokenizer not initialized. Either train or load a pre-trained model.")
            
        tokens = list(text.encode("utf-8"))
        while len(tokens) >= 2:
            stats = self.get_stats(tokens)
            pair = min(stats, key=lambda p: self.merges.get(p, float("inf")))
            if pair not in self.merges:
                break
            idx = self.merges[pair]
            tokens = self.merge(tokens, pair, idx)
        return tokens

    def decode(self, tokens):
        """Convert tokens back to text"""
        if self.vocab is None:
            raise ValueError("Tokenizer not initialized. Either train or load a pre-trained model.")
            
        tokens = b"".join(self.vocab[idx] for idx in tokens)
        text = tokens.decode("utf-8", errors="replace")
        return text

    # === Serialization methods (for saving/loading trained model) ===




    # === Serialization methods (for saving/loading trained model) ===
    def save(self, directory: str = "./saved_models", filename: str = "bpe_tokenizer.pkl"):
        """Save the trained tokenizer to a file"""
        if self.vocab is None or self.merges is None:
            raise ValueError("Cannot save untrained tokenizer")

        # Ensure the save directory exists
        os.makedirs(directory, exist_ok=True)
        save_path = os.path.join(directory, filename)

        # Save the tokenizer
        state = {
            'vocab': self.vocab,
            'merges': self.merges
        }
        with open(save_path, 'wb') as f:
            pickle.dump(state, f)

        print(f"Tokenizer saved to: {os.path.abspath(save_path)}")


    @classmethod
    def load(cls, directory: str = "./saved_models", filename: str = "bpe_tokenizer.pkl"):
        """Load a pre-trained tokenizer from a file"""
        save_path = os.path.join(directory, filename)
        if not os.path.isfile(save_path):
            raise FileNotFoundError(f"No tokenizer file found at {os.path.abspath(save_path)}")

        print(f"Loading tokenizer from {os.path.abspath(save_path)}...")
        with open(save_path, 'rb') as f:
            state = pickle.load(f)

        tokenizer = cls()  # Initialize without training
        tokenizer.vocab = state['vocab']
        tokenizer.merges = state['merges']
        print("Tokenizer loaded successfully!")
        return tokenizer
        
    
if __name__ == "__main__":
    tokenizer = BPEPunjabiTokenizer(corpus_path="pa_corpus_cleaned.txt", max_vocab_size=5000, sample_size=20000)
    tokenizer.save() 
    print("Save successful")


    # Later - just load the trained model
    # tokenizer = BPEPunjabiTokenizer.load()  # Much faster than training again
    # print("loaded model from saved location")

    print("Testing Punjabi tokenizer...")


    # Test sentences in Punjabi
    sentences = [
        "ਤੁਸੀਂ ਕੀ ਕਰ ਰਹੇ ਹੋ?",
        "ਮੈਨੂੰ ਚਾਹ ਪੀਣੀ ਹੈ",
        "ਇਹ ਬਹੁਤ ਵਧੀਆ ਹੈ",
        "ਇਹ ਕਿਤਾਬ ਬਹੁਤ ਦਿਲਚਸਪ ਹੈ"
    ]
    
    for sentence in sentences:
        print("Original:", sentence)
        encoded = tokenizer.encode(sentence)
        print("Encoded:", encoded)
        decoded = tokenizer.decode(encoded)
        print("Decoded:", decoded)
        print("Match:", decoded == sentence)
        print("---")