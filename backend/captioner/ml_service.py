"""Loads the trained models once (lazily) and exposes generate_caption()."""
import pickle
import threading
from pathlib import Path

import numpy as np
from PIL import Image

ML_DIR = Path(__file__).parent / "ml"
_lock = threading.Lock()
_state = {}


def _load():
    if _state:
        return _state
    with _lock:
        if _state:
            return _state
        # Imported here so Django starts fast and errors are reported per-request
        from tensorflow.keras.applications.vgg16 import VGG16
        from tensorflow.keras.models import Model, load_model

        model_path = ML_DIR / "model.h5"
        tok_path = ML_DIR / "tokenizer.pkl"
        if not model_path.exists():
            raise FileNotFoundError(f"Place your trained model at {model_path}")

        caption_model = load_model(model_path, compile=False)
        with open(tok_path, "rb") as f:
            tokenizer = pickle.load(f)

        vgg = VGG16()  # downloads ImageNet weights on first run (~500MB)
        extractor = Model(vgg.inputs, vgg.layers[-2].output)

        # Inputs are [image(4096), text(max_length)]; find the text one by shape
        shapes = [tuple(i.shape) for i in caption_model.inputs]
        max_length = next(s[1] for s in shapes if s[1] != 4096)

        _state.update(
            model=caption_model,
            tokenizer=tokenizer,
            extractor=extractor,
            max_length=int(max_length),
            index_word={i: w for w, i in tokenizer.word_index.items()},
        )
    return _state


def extract_features(file, extractor):
    from tensorflow.keras.applications.vgg16 import preprocess_input

    img = Image.open(file).convert("RGB").resize((224, 224))
    arr = np.asarray(img, dtype="float32").reshape(1, 224, 224, 3)
    return extractor.predict(preprocess_input(arr), verbose=0)


def generate_caption(file):
    from tensorflow.keras.preprocessing.sequence import pad_sequences

    s = _load()
    feat = extract_features(file, s["extractor"])
    text = "startseq"
    for _ in range(s["max_length"]):
        seq = s["tokenizer"].texts_to_sequences([text])[0]
        seq = pad_sequences([seq], maxlen=s["max_length"])
        probs = s["model"].predict([feat, seq], verbose=0)
        word = s["index_word"].get(int(np.argmax(probs)))
        if word is None or word == "endseq":
            break
        text += " " + word
    return text.replace("startseq", "", 1).strip()
