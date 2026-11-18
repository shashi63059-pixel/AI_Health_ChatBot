# Healthcare Chatbot

This is a Python-based project for dealing with human symptoms and predicting their possible outcomes.

#### Project Goal
The primary goal of this project is to forecast the disease so that patients can get the desired output according to their primary symptoms. 
 
## Technology used
We used **[TKinter](https://docs.python.org/3/library/tkinter.html)** to create a desktop-based application and **[Spacy](https://spacy.io/)** for NLP-based processes like ***text sentence tokenization and lemmatization***, and we used a **[Huggingface](https://huggingface.co/)** pretrained model to extrat disease names from a given sentence ***( or ner processing)***.

#### Huggingface
Downloading pre-trained model from [Huggingface Model](https://huggingface.co/raynardj/ner-disease-ncbi-bionlp-bc5cdr-pubmed)
```python

from transformers import pipeline
PRETRAINED = "raynardj/ner-disease-ncbi-bionlp-bc5cdr-pubmed"
ners = pipeline(task="ner",model=PRETRAINED, tokenizer=PRETRAINED)

```

#### Spacy

Download [spacy](https://spacy.io/usage) For window, Linux, MacOS
```bash
pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_sm
```


## Installation

Desktop app (Tkinter): install the desktop dependencies.

```bash
pip install -r requirements-desktop.txt
python Health_Care_App.py
```

Web app (FastAPI, used for Vercel): install the runtime dependencies only.

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

## Deployment on Vercel

`app.py` is the FastAPI entrypoint and `index.html` is the chat UI that it serves.

| Vercel field | Value |
| --- | --- |
| Framework Preset | FastAPI (auto-detected) |
| Root Directory | `./` |
| Build Command | default (leave empty) |
| Output Directory | leave empty |
| Install Command | `pip install -r requirements.txt` |
| Environment Variables | none |

`torch` is not installed on Vercel. When it is missing, `bot.py` loads `nn_numpy.pkl` and runs the neural network forward pass with numpy, so the same greeting/fallback answers are produced.

API routes: `GET /api/health`, `GET /api/symptoms`, `POST /api/chat` (`{"message": "..."}` or `{"symptoms": ["itching", "skin_rash"]}`).
