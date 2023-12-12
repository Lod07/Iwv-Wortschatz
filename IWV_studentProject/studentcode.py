import os
import xml.etree.ElementTree as ET
import spacy
import seaborn as sns
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
from dataLoader import LSNewsData, DatasetOptions

import utils

# Pfade in besser
from pathlib import Path
# LADEBALKEN
from tqdm import tqdm
 

def count_words_and_pos_tags(all_text, nlp):
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

            # enferne sachen wie 1. 2. 3. usw.
            if word[-1] == "." and tag == "ADJ":
                # TODO: hier dringend mal nachschauen dass keine falschen wörter entfernt werden!!!!
                continue
            
            if pos == "NUM":
                continue

            # Informationen zu jedem Wort speichern
            word_list.append((word, pos, tag))

    return pos_count, word_list

def find_unique_words(word_list):
    # Verwende Counter, um die Häufigkeit jedes Wortes zu zählen
    word_counter = Counter(word for word, _, _ in word_list)

    # Liste für Wörter, die nur einmal vorkommen
    unique_words = [word for word, count in word_counter.items() if count == 1]
    return unique_words


def find_noun_endings(noun_list):
    # Liste der gesuchten Wort-Endungen
    endings = ['heit', 'ie', 'ik', 'ion', 'ismus', 'ität', 'keit', 'nz', 'tur', 'ung']

    # Listen für Substantive mit den gesuchten Endungen
    ending_lists = {ending: [] for ending in endings}

    for noun in noun_list:
        for ending in endings:
            if noun.endswith(ending):
                ending_lists[ending].append(noun)

    return ending_lists


# Gesamtanzahl aller Wörter
total_word_count = 0

# spaCy-Modell laden (deutsch)
nlp = spacy.load("de_core_news_lg")

# Dictionary zur Verfolgung der Gesamtanzahl der Wörter pro Wortart
total_pos_count = {}

# Liste für alle individuellen Wörter mit ihrer Häufigkeit und Wortart
total_word_list = []

options = DatasetOptions()
options.removeMedioPoint = True
datasetPath = Path(__file__).parent / 'xmlfiles'

dataset = LSNewsData(datasetPath, options)

for i in tqdm(range(len(dataset))):
    # Anzahl der Wörter und POS-Tags ermitteln
    document = dataset[i]
    pos_count, word_list = count_words_and_pos_tags(document, nlp)

    # Gesamtanzahl der Wörter aktualisieren
    total_word_count += sum(pos_count.values())

    # Gesamtanzahl der Wörter pro Wortart aktualisieren
    for pos, count in pos_count.items():
        total_pos_count[pos] = total_pos_count.get(pos, 0) + count

    # Liste aller individuellen Wörter aktualisieren
    total_word_list.extend(word_list)

print(len(total_word_list))

# Identifiziere Wörter, die nur einmal vorkommen
unique_words = find_unique_words(total_word_list)

# Liste für alle Substantive
all_nouns = [word for word, pos, _ in total_word_list if pos == 'NOUN']

# Identifiziere Substantive mit den gesuchten Endungen
ending_lists = find_noun_endings(all_nouns)


# Ausgabe 
output_path = os.path.join(str(datasetPath), "Liste_Aufgabe_1.txt")
with open(output_path, 'w', encoding='utf-8') as output_file:
    output_file.write(f"Gesamtzahl aller Wörter: {total_word_count}\n\n")
    output_file.write("Anzahl Wortarten:\n")
    for pos, count in total_pos_count.items():
        output_file.write(f"{pos}: {count}\n")


    # daten umformatieren hier
    final = {}
    for word, pos, tag in total_word_list:
        if not word in final:
            final[word] = { tag: 1 }
        else:
            if not tag in final[word]:
                final[word][tag] = 1
            else:
                final[word][tag] += 1

    output_file.write("\nWort - Wortart nach pos - Wortart nach tag- Anzahl\n")
    for word_info in final:
        output_file.write(str(word_info) + " " + str(final[word_info]) + "\n")

    

    output_file.write("\nSubstantive mit den gesuchten Endungen:\n")
    for ending, nouns in ending_lists.items():
        output_file.write(f"{ending}: {len(nouns)} - {nouns}\n")

print(f"Ausgabe wurde in der Datei {output_path} gespeichert.")


output_path = os.path.join(str(datasetPath), "Liste_Aufgabe_1_unique_words.txt")
with open(output_path, 'w', encoding='utf-8') as output_file2:
    for unique_word in unique_words:
        output_file2.write(f"{unique_word}\n")

print(f"Ausgabe wurde in der Datei {output_path} gespeichert.")



#Visualisierung 

# Wordcloud erstellen
wordcloud_text = ' '.join([word for word, _, _ in total_word_list])
wordcloud = WordCloud(width=800, height=400, random_state=21, max_font_size=110, background_color='white').generate(wordcloud_text)

# Wordcloud anzeigen
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis('off')
plt.show()


# Visualisierung Endungen Substantive
ending_counts = {ending: len(nouns) for ending, nouns in ending_lists.items()}
sns.barplot(x=list(ending_counts.keys()), y=list(ending_counts.values()))
plt.title("Anzahl der Substantive mit den gesuchten Endungen")
plt.xlabel("Endungen")
plt.ylabel("Anzahl")
plt.show()



#Hi bin a commentar