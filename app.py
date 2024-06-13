from flask import Flask, render_template, request, jsonify
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

app = Flask(__name__)

# Load GPT-2 tokenizer and model
gpt2_tokenizer = GPT2Tokenizer.from_pretrained('gpt2-large')
gpt2_model = GPT2LMHeadModel.from_pretrained('gpt2-large', pad_token_id=gpt2_tokenizer.eos_token_id)

# Loading LLAMA 2 model
model_name_or_path = "TheBloke/Llama-2-13B-chat-GGML"
model_basename = "llama-2-13b-chat.ggmlv3.q5_1.bin"
model_path = hf_hub_download(repo_id=model_name_or_path, filename=model_basename)
llama_model = Llama(
    model_path=model_path,
    n_threads=2,
    n_batch=512,
    n_gpu_layers=32
)


@app.route("/")
def index():
    return render_template("index.html")


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


@app.route("/api", methods=["POST"])
def api():
    try:
        message = request.json.get("message")
        if message is None:
            return jsonify({'error': 'Message not provided'}), 400

        if request.json.get("model") == "llama2":
            generated_text = generate_response_llama(message)
        else:
            generated_text = generate_response_gpt2(message)

        return jsonify({'response': generated_text}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generate_response_gpt2(prompt):
    numeric_ids = gpt2_tokenizer.encode(prompt, return_tensors='pt')
    result = gpt2_model.generate(numeric_ids, max_length=100, num_beams=5, no_repeat_ngram_size=2, early_stopping=True)
    generated_text = gpt2_tokenizer.decode(result[0], skip_special_tokens=True)
    actual_response = extract_gpt2_response(generated_text, prompt)
    return actual_response


def generate_response_llama(prompt):
    prompt_template = f'''SYSTEM: You are a helpful, respectful and honest assistant. Always answer as helpfully.

USER: {prompt}

ASSISTANT:
'''
    response = llama_model(prompt=prompt_template, max_tokens=256, temperature=0.5, top_p=0.95,
                           repeat_penalty=1.2, top_k=150, echo=True)
    full_response = response["choices"][0]["text"]
    actual_response = extract_llama_response(full_response)
    return actual_response


def extract_gpt2_response(generated_text, prompt):
    if generated_text.startswith(prompt):
        return generated_text[len(prompt):].strip()
    return generated_text


def extract_llama_response(full_response):
    lines = full_response.split('\n')
    assistant_lines = []
    capture = False
    for line in lines:
        if line.startswith("ASSISTANT:"):
            capture = True
            continue
        if capture:
            assistant_lines.append(line)
    return ' '.join(assistant_lines).strip()


if __name__ == '__main__':
    app.run()
