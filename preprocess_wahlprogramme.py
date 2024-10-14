import os
import PyPDF2
import re
import pandas as pd
from collections import defaultdict

# Funktion zum Laden der Stopwörter aus einer Datei
def load_stopwords(file_path):
    with open(file_path, "r") as file:
        stop_words = {line.strip() for line in file}
    return stop_words

# Stopwörter laden
STOPWORDS_PATH = "german_stopwords.txt"
stop_words = load_stopwords(STOPWORDS_PATH)

# Verzeichnis der Wahlprogramme
DATA_DIR = "Bundestagswahlprogramme"

# Funktion zum Extrahieren von Text aus PDF
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        return text.lower()
    except Exception as e:
        print(f"Fehler beim Lesen der PDF {pdf_path}: {e}")
        return ""

# Funktion zur Bereinigung und Tokenisierung von Text
def clean_and_tokenize(text):
    # Entferne nicht-alphanumerische Zeichen und splitte in Wörter
    words = re.findall(r'\b\w+\b', text)
    # Entferne Stopwörter
    relevant_words = [word for word in words if word not in stop_words]
    return relevant_words

# Alle Parteien sammeln
parties = [party for party in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, party))]

# Datenstruktur für Wortzählungen und Rankings
results = []

# Datenverarbeitung
for party in parties:
    party_dir = os.path.join(DATA_DIR, party)
    # Dynamisch alle PDF-Dateien im Parteiordner durchsuchen
    pdf_files = [f for f in os.listdir(party_dir) if f.endswith(".pdf")]
    
    for pdf_file in pdf_files:
        # Jahr aus dem Dateinamen extrahieren (z.B. 2013.pdf -> 2013)
        year = re.findall(r'\d{4}', pdf_file)
        if year:
            year = year[0]  # Extrahiere das Jahr als Zeichenfolge
            pdf_path = os.path.join(party_dir, pdf_file)
            text = extract_text_from_pdf(pdf_path)
            words = clean_and_tokenize(text)
            # Zähle die Wörter
            counts = defaultdict(int)
            for word in words:
                counts[word] += 1
            # Sortiere nach Häufigkeit und weise Ränge zu
            sorted_words = sorted(counts.items(), key=lambda item: item[1], reverse=True)
            for rank, (word, count) in enumerate(sorted_words, start=1):
                results.append({
                    "Partei": party,
                    "Jahr": year,
                    "Wort": word,
                    "Vorkommen": count,
                    "Rang": rank
                })

# Konvertiere die Ergebnisse in einen DataFrame
df = pd.DataFrame(results)

# Speichern als Excel und CSV
df.to_excel("wahlprogramme_analysis.xlsx", index=False)
df.to_csv("wahlprogramme_analysis.csv", index=False)

print("Die Vorverarbeitung ist abgeschlossen. Die Daten wurden in Excel- und CSV-Dateien gespeichert.")