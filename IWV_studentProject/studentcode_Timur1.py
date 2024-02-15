import os
import xml.etree.ElementTree as ET
import spacy
import seaborn as sns
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
from dataLoader import LSNewsData, DatasetOptions
from tabulate import tabulate

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

    # Liste für alle individuellen Wörter mit ihrer Häufigkeit, Wortart und TTR
    word_list = []

    types = set()

    for token in doc:
        # Ignoriere Satzzeichen und Leerzeichen
        if not token.is_punct and not token.is_space:
            # Wort und Wortart abrufen
            word = token.text.lower()  # kleinschreiben, um Groß-/Kleinschreibung zu ignorieren
            pos = token.pos_
            tag = token.tag_

            # Anzahl der Wörter pro Wortart zählen
            pos_count[f'{pos}_{word}'] = pos_count.get(f'{pos}_{word}', 0) + 1


            types.add(word)

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
nlp.max_length = 3000000

# Dictionary zur Verfolgung der Gesamtanzahl der Wörter pro Wortart
total_pos_count = {}

# Liste für alle individuellen Wörter mit ihrer Häufigkeit und Wortart
total_word_list = []


# def calculate_individual_ttr(word_list):
#     # Liste aller verschiedenen Wörter
#     types = set()

#     # Dictionary zur Verfolgung der Anzahl der Vorkommen jedes Wortes
#     word_counts = Counter()

#     # Dictionary zur Verfolgung der TTR für jedes Wort
#     individual_ttr = {}

#     # Berechne TTR für jedes Wort
#     for word, pos, tag in word_list:
#         # Type-Token Ratio (TTR) berechnen
#         types.add(word)
#         ttr = len(types) / len(word_list)

#         # Speichere den TTR-Wert für das Wort im Dictionary
#         individual_ttr[word] = ttr

#     return individual_ttr

# Lexikalische Vielfalt für jedes Wort berechnen
# individual_ttr_values = calculate_individual_ttr([(word, pos, tag) for word, pos, tag in total_word_list])

options = DatasetOptions()
options.removeMedioPoint = True
datasetPath = Path(__file__).parent / 'xmlfiles'

dataset = LSNewsData(datasetPath, options)

# corpus_text = ' '.join([dataset[i] for i in range(len(dataset))])
# doc = nlp(corpus_text)
for i in tqdm(range(len(dataset))):
    # Stellen Sie sicher, dass total_word_list initialisiert ist
    if not total_word_list:
        total_word_list = []

    pos_count, word_list = count_words_and_pos_tags(dataset[i], nlp)

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
    
    # Write table header
    output_file.write("Wort       | POS  | Count | TTR\n")
    output_file.write("-----------|------|-------|--------\n")

    # Write each row in the table
    for word, pos, _ in total_word_list:
        output_file.write(f"{word.ljust(11)}| {pos.ljust(5)}| {str(total_pos_count[f'{pos}_{word}']).ljust(6)}| {total_pos_count[f'{pos}_{word}'] / total_word_count}\n")

    # Daten umformatieren hier
    final = {}
    for word, pos, tag in total_word_list:
        if not word in final:
            final[word] = { tag: 1 }
        else:
            if not tag in final[word]:
                final[word][tag] = 1
            else:
                final[word][tag] += 1

print(f"Ausgabe wurde in der Datei {output_path} gespeichert.")

# Open a new file handle for the second section of the code
output_path_2 = os.path.join(str(datasetPath), "Liste_Aufgabe_3_unique_words.txt")
with open(output_path_2, 'w', encoding='utf-8') as output_file2:
    for unique_word in unique_words:
        output_file2.write(f"{unique_word}\n")

print(f"Ausgabe wurde in der Datei {output_path_2} gespeichert.")

# Open another new file handle for the third section of the code
output_path_3 = os.path.join(str(datasetPath), "Liste_Aufgabe_4_Substantive mit gewissen Endungen.txt")
with open(output_path_3, 'w', encoding='utf-8') as output_file3:
    output_file3.write("\nSubstantive mit den gesuchten Endungen:\n")
    for ending, nouns in ending_lists.items():
        output_file3.write(f"{ending}: {len(nouns)} - {nouns}\n")

print(f"Ausgabe wurde in der Datei {output_path_3} gespeichert.")




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