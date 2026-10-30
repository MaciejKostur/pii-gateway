# PII Gateway

Bramka filtrujaca polskie dane osobowe (PESEL, NIP, REGON, IBAN, dowod, karty, telefon, e-mail, imiona/nazwiska) przed wyslaniem promptu do LLM. Dane sa zastepowane tokenami (`<PL_PESEL_1>`), a w odpowiedzi modelu przywracane.

## Uruchomienie (Windows / PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m spacy download pl_core_news_lg
pytest -m "not slow"   # testy bez modelu
pytest                 # wszystkie testy
uvicorn pii_gateway.api:app --reload
```

## TODO
- [ ] zbior testowy (Faker pl_PL) + metryki precision/recall per typ
- [ ] streaming (tokeny rozdzielone miedzy chunkami)
- [ ] Redis jako vault
- [ ] model zagrozen (obfuskacja, base64) i sekcja ograniczen
- [ ] GitHub Actions
