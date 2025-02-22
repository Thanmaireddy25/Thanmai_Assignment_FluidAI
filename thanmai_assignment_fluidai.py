# -*- coding: utf-8 -*-
"""Thanmai_Assignment_FluidAI.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1yNaMiLwVDJf4tTFX2jfZGMcrrMS223qL
"""

# Install required libraries (only run once)
!pip install PyMuPDF spacy transformers torch accelerate

import fitz  # PyMuPDF
import re
import spacy
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Using Local Open-Source Model
model_name = "sshleifer/distilbart-cnn-12-6"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text.strip()

# Function to extract key financial insights
def extract_relevant_sections(text):
    sections = {
        "Growth Prospects": [],
        "Business Changes": [],
        "Key Triggers": [],
        "Material Effects on Earnings": [],
        "Financial Highlights": [],
    }

    keywords = {
        "Growth Prospects": ["growth", "expansion", "future", "opportunity", "outlook",
                             "increase", "forecast", "scaling", "potential", "market size",
                             "trajectory", "trend", "demand", "penetration", "new market",
                             "diversification", "customer base", "capacity expansion"],

        "Business Changes": ["acquisition", "merger", "restructuring", "strategy", "business model",
                             "shift", "adjustment", "pivot", "realignment", "new focus", "change",
                             "investment", "vertical integration", "cost optimization", "innovation"],

        "Key Triggers": ["market trend", "competition", "demand", "regulation", "inflation",
                         "supply chain", "logistics", "export growth", "raw material cost",
                         "OEM partnerships", "industry trend"],

        "Material Effects on Earnings": ["profit", "loss", "revenue impact", "costs", "guidance",
                                         "financial outlook", "CAPEX", "return on investment",
                                         "EBITDA growth", "debt servicing"],

        "Financial Highlights": ["earnings", "EBITDA", "margins", "cash flow", "debt", "PAT",
                                 "gross profit", "net profit", "financial performance", "revenue breakdown"]
    }

    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]

    for sentence in sentences:
        for category, words in keywords.items():
            if any(word in sentence.lower() for word in words):
                sections[category].append(sentence)

    return sections

# Function to summarize extracted text
def batch_summarization(text, chunk_size=300):
    sentences = text.split(". ")
    chunks = [" ".join(sentences[i:i+chunk_size]) for i in range(0, len(sentences), chunk_size)]

    summaries = []
    for chunk in chunks:
        try:
            summary = summarizer(chunk, max_length=150, min_length=50, truncation=True)
            summaries.append(summary[0]['summary_text'].strip())
        except:
            continue
    return " ".join(summaries)

def summarize_text(section_text, category):
    if not section_text:
        return f"No significant insights found for {category}."

    text = " ".join(section_text)
    text = re.sub(r'\s+', ' ', text).strip()  # Clean text

    return batch_summarization(text)  # Call batch summarization


# Main function to process the PDF and extract insights
def process_pdf(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    sections = extract_relevant_sections(text)

    structured_summary = {}
    for category, content in sections.items():
        summary = summarize_text(content, category)

        # Ensure bullet points for "Key Triggers"
        if category == "Key Triggers":
            summary = "- " + "\n- ".join(summary.split(". "))

        structured_summary[category] = summary

    return structured_summary

# Run the script on the uploaded PDF file
pdf_file_path = "/content/SJS Transcript Call.pdf"
summary_results = process_pdf(pdf_file_path)

# Print extracted insights with structured formatting
for category, summary in summary_results.items():
    print(f"\n**{category}**")
    print(summary.strip())
    print("-" * 80)


