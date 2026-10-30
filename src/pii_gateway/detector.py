from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider

from .models import Entity
from .recognizers import PolishSpacyNER, build_recognizers

NLP_CONFIG = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "pl", "model_name": "pl_core_news_lg"}],
}


class Detector:
    def __init__(self, min_score: float = 0.5):
        self.min_score = min_score
        nlp_engine = NlpEngineProvider(nlp_configuration=NLP_CONFIG).create_engine()
        registry = RecognizerRegistry(supported_languages=["pl"])
        for rec in build_recognizers():
            registry.add_recognizer(rec)
        registry.add_recognizer(PolishSpacyNER())
        self._analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine, registry=registry, supported_languages=["pl"]
        )

    def detect(self, text: str) -> list[Entity]:
        results = self._analyzer.analyze(text=text, language="pl")
        return [
            Entity(r.entity_type, r.start, r.end, r.score)
            for r in results
            if r.score >= self.min_score
        ]
