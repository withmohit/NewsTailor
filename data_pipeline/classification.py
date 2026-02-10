# from torch import transformers
from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="valhalla/distilbart-mnli-12-1"
)

candidate_labels = ["science technology", "crime", "india", "politics", "religion", "sports", "international"]

def predict_category(sequence_to_classify):
    result = classifier(sequence_to_classify, candidate_labels)
    return result['labels'][0]