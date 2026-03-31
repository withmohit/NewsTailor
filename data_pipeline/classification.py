# from torch import transformers
# import transformers
from transformers import pipeline

candidate_labels = ["science technology", "crime", "india", "politics", "religion", "sports", "international"]


def predict_category(sequence_to_classify):
    classifier = pipeline(
                "zero-shot-classification",
                model="valhalla/distilbart-mnli-12-1"
                )

    result = classifier(sequence_to_classify, candidate_labels)
    return result['labels'][0]