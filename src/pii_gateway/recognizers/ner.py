"""Recognizer korzystajacy z NER spaCy (pl_core_news_lg)."""
from presidio_analyzer import EntityRecognizer, RecognizerResult

# etykiety modelu pl_core_news_* -> encje Presidio
LABEL_MAP = {
    "persName": "PERSON",
    "placeName": "LOCATION",
    "geogName": "LOCATION",
    "orgName": "ORGANIZATION",
}


class PolishSpacyNER(EntityRecognizer):
    def __init__(self, score: float = 0.85):
        self._score = score
        super().__init__(
            supported_entities=sorted(set(LABEL_MAP.values())),
            supported_language="pl",
            name="PolishSpacyNER",
        )

    def load(self) -> None:  # model laduje silnik NLP Presidio
        pass

    def analyze(self, text, entities, nlp_artifacts=None):
        if nlp_artifacts is None:
            return []
        results = []
        for ent in nlp_artifacts.entities:
            mapped = LABEL_MAP.get(ent.label_)
            if mapped and (not entities or mapped in entities):
                results.append(RecognizerResult(mapped, ent.start_char, ent.end_char, self._score))
        return results
