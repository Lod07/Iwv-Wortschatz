import os
import xml.etree.ElementTree as ET
import spacy
import seaborn as sns
import numpy as np
import statistics
from collections import OrderedDict
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
from dataLoader import LSNewsData, DatasetOptions
import pandas as pd

import utils

# Pfade in besser
from pathlib import Path
# LADEBALKEN
from tqdm import tqdm

ENDINGS = ['heit', 'ie', 'ik', 'ion', 'ismus', 'ität', 'keit', 'nz', 'tur', 'ung']
 

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
            word_list.append((capitalize_word(word, pos), pos, tag))

    return pos_count, word_list

def find_unique_words(word_list):
    # Verwende Counter, um die Häufigkeit jedes Wortes zu zählen
    word_counter = Counter(word for word, _, _ in word_list)

    # Liste für Wörter, die nur einmal vorkommen
    unique_words = sorted([word for word, count in word_counter.items() if count == 1])
    return unique_words



def find_noun_endings(noun_list):
    # Listen für Substantive mit den gesuchten Endungen
    ending_lists = {ending: [] for ending in ENDINGS}

    for noun in noun_list:
        for ending in ENDINGS:
            if noun.endswith(ending):
                ending_lists[ending].append(noun)

    return ending_lists

# Funktion zur Überprüfung der Großschreibung
def capitalize_word(word, pos):
    if pos in ['NOUN', 'PROPN', 'NE', 'NNE']:
        return word.capitalize()
    return word


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
ending_list_per_document = []

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

    document_nouns = [word for word, pos, _ in word_list if pos in ['NOUN', 'PROPN', 'NE', 'NNE']]
    document_ending_lists = find_noun_endings(document_nouns)
    ending_list_per_document.append(document_ending_lists)

ending_means = []
ending_max = []
ending_std_devs = []

for ending in ENDINGS:
    counts = []
    for doc_elists in ending_list_per_document:
        counts.append(len(doc_elists[ending]))

    counts_array = np.array(counts)
    print(ending)
    print("Min: ", counts_array.min())
    print("Max: ", counts_array.max())
    print("Mean: ", counts_array.mean())
    print("Std Dev: ", counts_array.std(ddof=0))
    print("Variance: ", counts_array.var())
    ending_means.append(counts_array.mean())
    ending_max.append(counts_array.max())
    ending_std_devs.append(counts_array.std())


#sns.boxplot(counts)
#plt.title(f'Boxplot für Endung "{ending}"')
#plt.show()



boxplot_data = {ending: [] for ending in ENDINGS}

for doc_elists in ending_list_per_document:
    for ending in ENDINGS:
        noun_count = len(doc_elists[ending])
        # Überprüfen, ob die Liste leer ist
        if noun_count > 0:
            boxplot_data[ending].append(noun_count)
        else:
            boxplot_data[ending].append(np.nan)

# Daten für Boxplot in DataFrame umwandeln
data = pd.DataFrame(boxplot_data)

# Boxplot erstellen
plt.figure(figsize=(12, 8))
sns.boxplot(data=data, flierprops = dict(markerfacecolor = '0.50', markersize = 2))
# Hier setzt du die Einteilung der y-Achse in Zweierschritten
plt.yticks(np.arange(0, max(counts_array)+1, 2))
plt.ylim(0,16)
plt.title("Boxplot für Substantiv-Endungen")
plt.xlabel("Endungen")
plt.ylabel("Anzahl")
plt.show()



sns.barplot(x=ENDINGS, y=ending_means)
plt.title("Endungen Substantive Mittelwerte")
plt.xlabel("Endungen")
plt.ylabel("Anzahl")
plt.show()


sns.barplot(x=ENDINGS, y=ending_max)
plt.title("Endungen Substantive Maxima")
plt.xlabel("Endungen")
plt.ylabel("Anzahl")
plt.show()

with open("document_ending_list.txt", "w") as f:
    for doc_elists in ending_list_per_document:
        for ending, nouns in doc_elists.items():
            f.write(f"{ending}: {len(nouns)} - {nouns}\n")
        f.write("\n-------------------------------------\n")

print(len(total_word_list))

# Identifiziere Wörter, die nur einmal vorkommen
unique_words = find_unique_words(total_word_list)

# Liste für alle Substantive
all_nouns = [word for word, pos, _ in total_word_list if pos in ['NOUN', 'PROPN', 'NE', 'NNE']]

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
        word = capitalize_word(word, pos)  # Großschreibung hinzufügen
        if not word in final:
            final[word] = {tag: 1}
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

'''
# Wordcloud erstellen
wordcloud_text = ' '.join([word for word, _, _ in total_word_list])
wordcloud = WordCloud(width=800, height=400, random_state=21, max_font_size=110, background_color='white').generate(wordcloud_text)

# Wordcloud anzeigen
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis('off')
plt.show()
'''

# Visualisierung Endungen Substantive
ending_counts = {ending: len(nouns) for ending, nouns in ending_lists.items()}
sns.barplot(x=list(ending_counts.keys()), y=list(ending_counts.values()))
plt.title("Anzahl der Substantive mit den gesuchten Endungen")
plt.xlabel("Endungen")
plt.ylabel("Anzahl")
plt.show()

# Bereinigung der Liste von Duplikaten
ending_lists_relative = {ending: list(OrderedDict.fromkeys(words)) for ending, words in ending_lists.items()}

# Visualisierung als Balkendiagramm
ending_counts_relative = {ending: len(words) for ending, words in ending_lists_relative.items()}

# Plot
sns.barplot(x=list(ending_counts_relative.keys()), y=list(ending_counts_relative.values()))
plt.title("Anzahl der Substantive mit den gesuchten Endungen (ohne Duplikate)")
plt.xlabel("Endungen")
plt.ylabel("Anzahl")
plt.show()