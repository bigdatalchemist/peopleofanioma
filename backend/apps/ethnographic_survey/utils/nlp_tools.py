# ethnographic_survey/utils/nlp_tools.py
from transformers import pipeline

# Load summarization model once
summarizer = pipeline(
    "summarization", 
    model="sshleifer/distilbart-cnn-6-6",  # 300MB RAM
    device=-1  # Force CPU
)

def summarize_text(text, max_length=100, min_length=20):
    if len(text.strip().split()) < 20:
        return "Text too short to summarize."
    
    try:
        summary = summarizer(
            text, 
            max_length=max_length, 
            min_length=min_length, 
            do_sample=False,
            truncation=True  # Explicitly enable truncation
        )
        return summary[0]['summary_text']
    except Exception as e:
        return f"Summarization failed: {str(e)}"
