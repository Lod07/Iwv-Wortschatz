import os
import xml.etree.ElementTree as ET
import spacy
import seaborn as sns
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def count_words_and_pos_tags(xml_content, nlp):
    root = ET.fromstring(xml_content)

    def extract_text(element):
        text = ' '.join(child.text for child in element if child.text)
        for child in element:
            text += extract_text(child)
        return text

    all_text = extract_text(root)

    # spaCy für POS-Tagging verwenden
    doc = nlp(all_text)

    # Dictionary zur Verfolgung der Anzahl der Wörter pro Wortart
    pos_count = {}

    # Liste für alle individuellen Wörter mit ihrer Häufigkeit und Wortart
    word_list = []

    for token in doc:
        # Ignoriere Satzzeichen und Leerzeichen
        if not token.is_punct and not token.is_space:
            # Wort und Wortart abrufen
            word = token.text.lower()  # kleinschreiben, um Groß-/Kleinschreibung zu ignorieren
            pos = token.pos_
            tag = token.tag_
            
            # Anzahl der Wörter pro Wortart zählen
            pos_count[pos] = pos_count.get(pos, 0) + 1
            
            # Informationen zu jedem Wort speichern
            word_list.append((word, pos, tag))

    return pos_count, word_list

# Pfad zum Ordner
testfile = r"E:\Studium\Master\IWV\Iwv-Wortschatz\IWV_studentProject\xmlfiles\testfile"
DatenAnalyse = r"E:\Studium\Master\IWV\Iwv-Wortschatz\IWV_studentProject\xmlfiles\DatenAnalyse"

# Gesamtanzahl aller Wörter
total_word_count = 0

# spaCy-Modell laden (deutsch)
nlp = spacy.load("de_core_news_lg")

# Dictionary zur Verfolgung der Gesamtanzahl der Wörter pro Wortart
total_pos_count = {}

# Liste für alle individuellen Wörter mit ihrer Häufigkeit und Wortart
total_word_list = []

# Alle Dateien im Ordner durchlaufen
for filename in os.listdir(testfile):
    file_path = os.path.join(testfile, filename)

    # Nur Dateien einlesen (keine Ordner)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            file_content = file.read()

        # Anzahl der Wörter und POS-Tags ermitteln
        pos_count, word_list = count_words_and_pos_tags(file_content, nlp)

        # Gesamtanzahl der Wörter aktualisieren
        total_word_count += sum(pos_count.values())

        # Gesamtanzahl der Wörter pro Wortart aktualisieren
        for pos, count in pos_count.items():
            total_pos_count[pos] = total_pos_count.get(pos, 0) + count

        # Liste aller individuellen Wörter aktualisieren
        total_word_list.extend(word_list)

# Ausgabe in gewünschter Form
output_path = os.path.join(DatenAnalyse, "Liste_Aufgabe_1.txt")
with open(output_path, 'w', encoding='utf-8') as output_file:
    output_file.write(f"Gesamtzahl aller Wörter: {total_word_count}\n\n")
    output_file.write("Anzahl Wortarten:\n")
    for pos, count in total_pos_count.items():
        output_file.write(f"{pos}: {count}\n")

    output_file.write("\nWort - Wortart nach pos - Wortart nach tag- Anzahl\n")
    for word, pos, tag in total_word_list:
        word_count = total_word_list.count((word, pos, tag))
        output_file.write(f"{word}: , {pos}, {tag} {word_count}\n")

print(f"Ausgabe wurde in der Datei {output_path} gespeichert.")

# Wordcloud erstellen
wordcloud_text = ' '.join([word for word, _, _ in total_word_list])
wordcloud = WordCloud(width=800, height=400, random_state=21, max_font_size=110, background_color='white').generate(wordcloud_text)

# Wordcloud anzeigen
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis('off')
plt.show()
