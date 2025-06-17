# ethnographic_survey/utils/nlp_tools.py
from transformers import pipeline

# Load summarization model once
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text, max_length=130, min_length=30):
    if len(text.strip().split()) < 30:
        return "Text too short to summarize."
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']
