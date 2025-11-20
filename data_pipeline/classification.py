# from torch import transformers
from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="valhalla/distilbart-mnli-12-1"
)

candidate_labels = ["tech_and_science", "health", "india"]

def predict_category(sequence_to_classify):
    result = classifier(sequence_to_classify, candidate_labels)
    return result['labels'][0]