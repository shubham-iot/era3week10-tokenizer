import gradio as gr
from model import BPEPunjabiTokenizer



# Initialize tokenizer globally
tokenizer = None




def initialize_tokenizer():
    global tokenizer
    
    try:
        # Load the pre-trained tokenizer instead of training
        # Load the pre-trained tokenizer
        tokenizer = BPEPunjabiTokenizer.load(directory="./saved_models", filename="bpe_tokenizer.pkl")

        return "✅ Tokenizer loaded successfully!"
    except Exception as e:
        return f"❌ Error loading tokenizer: {str(e)}"
    


def process_text(text):
    if tokenizer is None:
        return "Please initialize the tokenizer first!", "", "", "", ""
    
    try:
        encoded = tokenizer.encode(text)
        decoded = tokenizer.decode(encoded)
        compression_ratio = len(text) / len(encoded) if len(encoded) > 0 else 0

        return text, f"Tokens: {encoded}", decoded, f"Match: {decoded == text}", f"Compression Ratio: {compression_ratio:.2f}"
    except Exception as e:
        return f"Error: {str(e)}", "", "", "", ""

def decode_tokens(token_string):
    if tokenizer is None:
        return "Please initialize the tokenizer first!"

    try:
        # Sanitize input by removing commas and ensuring valid integer conversion
        sanitized_tokens = token_string.replace(',', '').strip()
        tokens = list(map(int, sanitized_tokens.split()))
        return tokenizer.decode(tokens)
    except ValueError:
        return "Error decoding tokens: Please enter space-separated integers only."
    except Exception as e:
        return f"Error decoding tokens: {str(e)}"

# Create the Gradio interface
with gr.Blocks(title="Punjabi BPE Tokenizer") as demo:
    gr.Markdown("""
    # Punjabi BPE Tokenizer
    This tokenizer implements Byte-Pair Encoding for Punjabi text. 
    
    **Steps to use:**
    1. Click 'Initialize Tokenizer' button and wait for tokenizer initilization (approx 45 sec). 
    2. Enter Punjabi text in the input box or use the example sentences
    3. Click 'Process' 
    4. Optionally, input token sequences to decode manually.
    """)

    # Initialize section
    with gr.Row():
        init_btn = gr.Button("Initialize Tokenizer", variant="primary")
        status = gr.Textbox(label="Status", interactive=False)

    # Main interface
    with gr.Row():
        with gr.Column():
            text_input = gr.Textbox(
                label="Input Punjabi Text",
                placeholder="ਇੱਥੇ ਪੰਜਾਬੀ ਟੈਕਸਟ ਲਿਖੋ",
                lines=3
            )
            process_btn = gr.Button("Process", variant="secondary")

        with gr.Column():
            original_out = gr.Textbox(label="Original Text", interactive=False)
            encoded_out = gr.Textbox(label="Encoded Tokens", interactive=False)
            #decoded_out = gr.Textbox(label="Decoded Text", interactive=False)
            #match_out = gr.Textbox(label="Original vs Decoded Match", interactive=False)
            #compression_out = gr.Textbox(label="Compression Ratio", interactive=False)

    # Token decoding panel
    with gr.Row():
        token_input = gr.Textbox(
            label="Input Tokens (space-separated integers)",
            placeholder="e.g., 1 23 45",
            lines=2
        )
        decode_btn = gr.Button("Decode Tokens", variant="secondary")
        token_decoded_out = gr.Textbox(label="Decoded from Tokens", interactive=False)

    # Example sentences
    gr.Examples(
        examples=[
            ["ਤੁਸੀਂ ਕੀ ਕਰ ਰਹੇ ਹੋ?"],
            ["ਮੈਨੂੰ ਚਾਹ ਪੀਣੀ ਹੈ"],
            ["ਇਹ ਬਹੁਤ ਵਧੀਆ ਹੈ"],
            ["ਇਹ ਕਿਤਾਬ ਬਹੁਤ ਦਿਲਚਸਪ ਹੈ"]
        ],
        inputs=text_input,
        outputs=[original_out, encoded_out], # decoded_out, match_out, compression_out],
        fn=process_text,
        cache_examples=True
    )

    # Set up event handlers
    init_btn.click(
        fn=initialize_tokenizer,
        outputs=status
    )

    process_btn.click(
        fn=process_text,
        inputs=text_input,
        outputs=[original_out, encoded_out] # decoded_out, match_out, compression_out]
    )

    decode_btn.click(
        fn=decode_tokens,
        inputs=token_input,
        outputs=token_decoded_out
    )

    # Also process on pressing Enter in the input box
    text_input.submit(
        fn=process_text,
        inputs=text_input,
        outputs=[original_out, encoded_out] # decoded_out, match_out, compression_out]
    )

if __name__ == "__main__":
    demo.launch()