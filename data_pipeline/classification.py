# from torch import transformers
from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="valhalla/distilbart-mnli-12-1"
)

sequence_to_classify = "This popular YouTuber's account got hacked: What happened and tips to safeguard your account"
candidate_labels = ["talent", "tech", "terrorism"]

result = classifier(sequence_to_classify, candidate_labels)
print(result)