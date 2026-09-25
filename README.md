# 😂 Humor Detection in Code-Mixed Telugu–English (Tenglish) Text

> A hybrid NLP system that detects humor in Romanized Telugu–English ("Tenglish") text by combining a fine-tuned **MuRIL** transformer with a rule-based **heuristic engine** for emojis, slang and stylistic cues. It benchmarks **10 transformer models**.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?logo=pytorch&logoColor=white)
![Transformers](https://img.shields.io/badge/🤗%20Transformers-MuRIL%20%7C%20XLM--R%20%7C%20mBERT-FFD21E)
![Gradio](https://img.shields.io/badge/Gradio-web%20app-F97316?logo=gradio&logoColor=white)

---

## 📌 Why this is hard

Tenglish, the way millions of Telugu speakers text, mixes two languages in Latin script with no fixed spelling:

> *"naa DBMS professor chala fast bro, notes ledu, brain ledu, hope ledu 😭"*

The same word appears as *cheppadu / chepadu / cheppdu*. Humor relies on sarcasm, exaggeration,
slang (*vammo, keka, bokka*) and emojis (💀 😂 🤣). Standard English models don't understand this,
so the project combines multilingual Indian-language transformers with hand-crafted linguistic rules.

## ✨ Highlights

- 🧪 **Tenglish Humor Dataset v3**: 10,000 balanced samples (5,000 humorous / 5,000 non-humorous)
- 🏁 **Benchmark of 10 transformers**: MuRIL, XLM-RoBERTa, mBERT, IndicBERT, DistilBERT-multilingual, RoBERTa, BERT, ELECTRA, ALBERT, DeBERTa
- 🧠 **Hybrid inference**: neural probabilities blended with a heuristic humor score
- 🖥️ **Polished Gradio web app**: live predictions, confidence bars, triggered-rule explanations, history, and light/dark mode

## 📊 Results

Test-set results from the project report ([`Humour_10_Transformer.md`](Humour_10_Transformer.md)), 80/10/10 stratified split:

| Rank | Model | Accuracy | Precision | Recall | F1 |
|:---:|---|:---:|:---:|:---:|:---:|
| 🥇 | **MuRIL (base) + Heuristic Engine** | **92.4%** | **0.912** | **0.925** | **0.918** |
| 🥈 | MuRIL (base) | 90.1% | 0.895 | 0.902 | 0.898 |
| 🥉 | XLM-RoBERTa (base) | 88.5% | 0.874 | 0.888 | 0.881 |
| 4 | IndicBERT | 87.2% | 0.865 | 0.871 | 0.868 |
| 5 | mBERT | 85.8% | 0.842 | 0.860 | 0.851 |
| 6 | DistilBERT (multilingual) | 83.4% | 0.821 | 0.835 | 0.828 |
| 7 | RoBERTa (base) | 79.5% | 0.780 | 0.792 | 0.786 |
| 8 | DeBERTa (base) | 78.2% | 0.771 | 0.785 | 0.778 |
| 9 | BERT (base, uncased) | 74.5% | 0.732 | 0.740 | 0.736 |
| 10 | ALBERT (base) | 72.1% | 0.710 | 0.725 | 0.717 |

**Takeaways**
- **MuRIL wins** because it was pre-trained on Indian languages *and their transliterated (Romanized) forms*.
- **English-only models** (BERT, ALBERT, RoBERTa) trail far behind on code-mixed grammar.
- The **heuristic engine adds ~2.3 points** on top of MuRIL by catching cues the model can miss.

## 🧠 How the hybrid model works

```
Input text ──► MuRIL classifier ──────────────► P(humor)_model ─┐
     │                                                          ├─► Blend ─► HUMOROUS / NON-HUMOROUS
     └──────► Heuristic engine ─► heuristic humor score ────────┘         + confidence + reasons
```

The **heuristic engine** scores several families of signals:

| Signal | Examples |
|---|---|
| Funny emojis | 😂 🤣 💀 😭 🤡 (vs. "serious" emojis like 🙏 ✅ 📢) |
| English internet slang | *lol, lmao, bruh, no cap, skill issue, plot twist* |
| Telugu slang | *vammo, odiyamma, keka, bokka, kiraak, arachakam* |
| Stylistic cues | stretched words (*loool, ammooo*), `!!` / `??`, ALL-CAPS emphasis, dramatic `...` |
| Emoticons | `:D`, `xD`, `T_T`, `^_^` |
| Serious-context suppression | *hospital, police, urgent, "results announced", "dear sir"* push the score **down** |

**Blending rules:** a strong heuristic score (≥ 0.30) marks the text humorous; a moderate one (0.15–0.30) is
blended 60/40 with the model; a strongly negative one (≤ −0.20) leans non-humorous; otherwise the model decides.

## 🗂️ Project structure

```
humor-detection-in-code-mixed-telugu-english-text/
├── app.py                       # Gradio web app (MuRIL + heuristic engine)
├── train_all_transformers.py    # Fine-tunes & evaluates all 10 transformers, writes a leaderboard CSV
├── generate_dataset.py          # Builds the Tenglish humor dataset
├── humor_dataset_v2.csv         # 5,000 samples
├── humor_dataset_v3.csv         # 10,000 samples (used for training)
├── Humour_10_Transformer.md     # Results & evaluation write-up
├── capstone_project_notes.pdf   # Capstone project notes
└── requirements.txt
```

## 🧪 Dataset

`generate_dataset.py` creates the Tenglish corpus **programmatically**. It uses templates across 6 humor
categories (college life, family, sarcasm, Tollywood, relationships, daily life) plus 4 kinds of neutral
statements (daily life, opinions, news, instructions), filled with Telugu names, places,
foods, Tollywood references and apps, with **realistic spelling variants** (*nuvvu / nuvu / nuwu*) and emoji/slang
noise. Both classes are exactly balanced, and there are no duplicate texts.

> Because the corpus is template-generated, the scores above measure performance on this synthetic distribution.
> Validating on real social-media Tenglish is the natural next step.

## 🚀 Getting started

**1. Install**

```bash
pip install -r requirements.txt
pip install pandas scikit-learn datasets   # extra packages needed for training
```

**2. Train and benchmark all 10 models** (a GPU is recommended; the script also runs in Google Colab)

```bash
python train_all_transformers.py
```

Settings: max length 128, batch size 16, learning rate 2e-5, weight decay 0.01, best checkpoint chosen by F1.
Results are saved to `all_10_models_evaluation_results.csv`.

**3. Run the web app.** Copy the trained MuRIL model into a folder named `muril_humor_model/` next to `app.py`
(it must contain `config.json`, `model.safetensors` and `tokenizer.json`), then:

```bash
python app.py
```

The app opens at **http://localhost:7863**.

## 🧰 Tech stack

**PyTorch** · **Hugging Face Transformers & Datasets** · **MuRIL** · **scikit-learn** · **pandas** · **Gradio**

## 👩‍💻 Author

**Rishitha Naga Durga Gona**: [@rishithagona28](https://github.com/rishithagona28)
