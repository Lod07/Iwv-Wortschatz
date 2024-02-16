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
#from tabulate import tabulate
import pandas as pd

import utils


import psutil
import threading
import time
import datetime
import timeit
from queue import Queue

import cProfile
import pstats
from pstats import SortKey

from performance_tracker import CProfiler, PerformanceTracker

# Pfade in besser
from pathlib import Path
# LADEBALKEN
from tqdm import tqdm

ENDINGS = ['heit', 'ie', 'ik', 'ion', 'ismus', 'ität', 'keit', 'nz', 'tur', 'ung']

# Your data
suffixes = ['heit', 'ie', 'ik', 'ion', 'ismus', 'ität', 'keit', 'nz', 'tur', 'ung']
data = {
        'heit': [0.10952380952380952, 0.4704655869250434, 0, 5, 5, 0.2213378684807256],
        'ie': [0.18412698412698414, 1.0754410463584194, 0, 14, 14, 1.156573444192492],
        'ik': [0.2222222222222222, 0.9569203984814946, 0, 10, 10, 0.9156966490299824],
        'ion': [0.36666666666666664, 1.465096562178731, 0, 18, 18, 2.1465079365079367],
        'ismus': [0.006349206349206349, 0.11250822315345618, 0, 2, 2, 0.012658100277147895],
        'ität': [0.007936507936507936, 0.13189893593995067, 0, 3, 3, 0.017397329302091213],
        'keit': [0.01904761904761905, 0.23152849106939466, 0, 4, 4, 0.053605442176870764],
        'nz': [0.07301587301587302, 0.7545010648706233, 0, 14, 14, 0.5692718568909045],
        'tur': [0.07936507936507936, 0.6349999950403024, 0, 12, 12, 0.4032249937011841],
        'ung': [1.5492063492063493, 2.3080172907850716, 0, 17, 17, 5.3269438145628625],
}
 
#@profile
def count_words_and_pos_tags(all_text, nlp):
    # spaCy für POS-Tagging verwenden
    doc = nlp(all_text)


    # Dictionary zur Verfolgung der Anzahl der Wörter pro Wortart
    pos_count = {}

    # Liste für alle individuellen Wörter mit ihrer Häufigkeit und Wortart
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

            # enferne sachen wie 1. 2. 3. usw.
            if word[-1] == "." and tag == "ADJ":
                continue
            
            if pos == "NUM":
                continue

            # Informationen zu jedem Wort speichern
            word_list.append((capitalize_word(word, pos), pos, tag))

    return pos_count, word_list


def find_unique_words(word_list):
    # Verwende Counter, um die Häufigkeit jedes Wortes zu zählen
    word_counter = Counter(word for word, _, _ in word_list)

    # Dictionary zum Verfolgen der Präfixe und ihrer zugehörigen Wörter
    prefix_to_words = {}
    

    for word, count in word_counter.items():
        if count == 1 and not word.endswith(".") and not word.startswith(".") and not any(char.isdigit() for char in word):
            # Präfix extrahieren
            word_prefix = get_prefix(word)

            # Überprüfen, ob das aktuelle Präfix bereits existiert
            if word_prefix in prefix_to_words:
                # Das aktuelle Wort wird zum Dictionary hinzugefügt, um alle Wörter mit dem gleichen Präfix zu speichern
                prefix_to_words[word_prefix].append(word)
            else:
                # Das aktuelle Wort wird zum Dictionary hinzugefügt
                prefix_to_words[word_prefix] = [word]

    # Liste der einzigartigen Wörter erstellen (nur Wörter mit einmaligem Präfix)
    unique_words = [words[0] for words in prefix_to_words.values() if len(words) == 1]

    return sorted(unique_words)

def get_prefix(word):
    # Hier können Sie die Logik für das Extrahieren des Präfixes anpassen
    # In diesem Beispiel wird das Präfix als die ersten drei Buchstaben des Wortes genommen
    return word[:3].lower()






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


def main():

    tr=PerformanceTracker()
        

    # Gesamtanzahl aller Wörter
    total_word_count = 0

    # spaCy-Modell laden (deutsch)
    tr.startTimeSection('ModelLoading')
    tr.startSystemMonitor()
    nlp = spacy.load("de_core_news_lg")
    tr.stopSystemMonitor()
    tr.endTimeSection('ModelLoading')


    # Dictionary zur Verfolgung der Gesamtanzahl der Wörter pro Wortart
    total_pos_count = {}

    # Liste für alle individuellen Wörter mit ihrer Häufigkeit und Wortart
    total_word_list = []

    options = DatasetOptions()
    options.removeMedioPoint = True
    datasetPath = Path(__file__).parent / 'xmlfiles' 



    dataset = LSNewsData(datasetPath, options)
    ending_list_per_document = []

    tr.startTimeSection('WordsEinlesen')
    tr.startSystemMonitor()

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

    document_nouns = [word for word, pos, _ in word_list if pos in ['NOUN', 'PROPN', 'NE', 'NNE']]
    document_ending_lists = find_noun_endings(document_nouns)
    ending_list_per_document.append(document_ending_lists)

    tr.stopSystemMonitor()
    tr.endTimeSection('WordsEinlesen')

    ending_means = []
    ending_max = []
    ending_std_devs = []


    tr.startTimeSection('EndungenBerechnen')
    tr.startSystemMonitor()
    for ending in ENDINGS:
        counts = []
        for doc_elists in ending_list_per_document:
            counts.append(len(doc_elists[ending]))

        counts_array = np.array(counts)
        print(ending)
        print("Min: ", counts_array.min())
        print("Max: ", counts_array.max())
        print("Spannweite: ", counts_array.max() - counts_array.min())
        print("Mittelwert: ", counts_array.mean())
        print("Standardabweichung: ", counts_array.std(ddof=0))
        print("Varianz: ", counts_array.var())
        print("                              ")
        ending_means.append(counts_array.mean())
        ending_max.append(counts_array.max())
        ending_std_devs.append(counts_array.std())
    tr.stopSystemMonitor()
    tr.endTimeSection('EndungenBerechnen')




    with open("document_ending_list.txt", "w") as f:
        for doc_elists in ending_list_per_document:
            for ending, nouns in doc_elists.items():
                f.write(f"{ending}: {len(nouns)} - {nouns}\n")
            f.write("\n-------------------------------------\n")

    print(len(total_word_list))


    tr.startTimeSection('finduniquewords')
    tr.startSystemMonitor()
    # Identifiziere Wörter, die nur einmal vorkommen
    unique_words = find_unique_words(total_word_list)
    #unique_words = [word for word in unique_words if not word.endswith(".")]
    tr.stopSystemMonitor()
    tr.endTimeSection('finduniquewords')

    # Liste für alle Substantive
    all_nouns = [word for word, pos, _ in total_word_list if pos in ['NOUN', 'PROPN', 'NE', 'NNE']]

    tr.startTimeSection('IdentifiziereSubstantive')
    tr.startSystemMonitor()
    # Identifiziere Substantive mit den gesuchten Endungen
    ending_lists = find_noun_endings(all_nouns)
    tr.stopSystemMonitor()
    tr.endTimeSection('IdentifiziereSubstantive')




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



        #Herausfiltern unique words
        output_path = os.path.join(str(datasetPath), "Liste_Aufgabe_3_unique_words.txt")
        with open(output_path, 'w', encoding='utf-8') as output_file2:
            for unique_word in unique_words:
                output_file2.write(f"{unique_word}\n")

        print(f"Ausgabe wurde in der Datei {output_path} gespeichert.")



        # #Visualisierung 

        # # Visualisierung Endungen Substantive
        # ending_counts = {ending: len(nouns) for ending, nouns in ending_lists.items()}
        # sns.barplot(x=list(ending_counts.keys()), y=list(ending_counts.values()))
        # plt.title("Anzahl der Substantive mit den gesuchten Endungen")
        # plt.xlabel("Endungen")
        # plt.ylabel("Anzahl")
        # plt.show()

        # # Bereinigung der Liste von Duplikaten
        # ending_lists_relative = {ending: list(OrderedDict.fromkeys(words)) for ending, words in ending_lists.items()}

        # # Visualisierung als Balkendiagramm
        # ending_counts_relative = {ending: len(words) for ending, words in ending_lists_relative.items()}

        # # Plot
        # sns.barplot(x=list(ending_counts_relative.keys()), y=list(ending_counts_relative.values()))
        # plt.title("Anzahl der Substantive mit den gesuchten Endungen (ohne Duplikate)")
        # plt.xlabel("Endungen")
        # plt.ylabel("Anzahl")
        # plt.show()



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

    #Eingefgügte Aufgabe 4 Visualisierung
        
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
        print("Spannweite: ", counts_array.max() - counts_array.min())
        print("Mittelwert: ", counts_array.mean())
        print("Standardabweichung: ", counts_array.std(ddof=0))
        print("Varianz: ", counts_array.var())
        print("                              ")
        ending_means.append(counts_array.mean())
        ending_max.append(counts_array.max())
        ending_std_devs.append(counts_array.std())

        tr.close()

if __name__ == "__main__":
    


    cp = CProfiler()
    cp.profileCall(main)



#FindenSynonyme
import requests
import json


dateipfad = 'D:/documents/Uni/MI_M/IWV/git/Iwv-Wortschatz/IWV_studentProject/xmlfiles/Liste_Aufgabe_1_Unique_words.txt'
unique = []
unique_final = {}

def getSynonymsWikitionary(token):
    r = requests.get(f"https://de.wiktionary.org/wiki/{token}")
    if "Dieser Eintrag existiert noch nicht!" in r.text:
        return []
    elif "Synonyme" not in r.text:
        return []

    blob = r.text.split("Synonyme:")
    
    if len(blob) <= 1:
        return []

    beginning = blob[1].split("<dd>")[1]
    end_index = beginning.index("</dd>")
    result = beginning[:end_index]

    lines = result.split("</a>")
    output = []

    for line in lines:
        if "<i>" in line:
            if not "</i>" in line:
                continue

            if not line.rfind('</i>') < line.rfind('<a'):
                continue
        
        index = line.rfind('>') + 1

        if index < len(line) - 1:
            output.append(line[index:])

    return output



#if __name__ == "__main__":

with open(dateipfad, 'r', encoding='utf-8') as datei:
    unique = datei.read().splitlines()

print(unique)

unique_final = []
synonyms_pairs = []


for wort in unique:
    synonyme = getSynonymsWikitionary(wort)
    
    # Hier werden die gefundenen Synonyme zur Liste hinzugefügt
    unique_final.extend(synonyme)
    synonyms_pairs.append(f"{wort}: {', '.join(synonyme)}")

# Ergebnisse ausgeben
print("Synonyme:")
for element in unique_final:
    print(element)

print("Synonyms-pairs:")
for pair in synonyms_pairs:
    print(pair)

output_dateipfad = 'D:/documents/Uni/MI_M/IWV/git/Iwv-Wortschatz/IWV_studentProject/xmlfiles/Synonyme_Liste.txt'
output_dateipfad_pairs = 'D:/documents/Uni/MI_M/IWV/git/Iwv-Wortschatz/IWV_studentProject/xmlfiles/Synonyms_Pairs_Liste.txt'

with open(output_dateipfad, 'w', encoding='utf-8') as output_datei:
    for element in unique_final:
        output_datei.write(element + '\n')

with open(output_dateipfad_pairs, 'w', encoding='utf-8') as output_datei_pairs:
    for pair in synonyms_pairs:
        output_datei_pairs.write(pair + '\n')


        
#Synonym-Listen vergleichen
            
# Einlesen der Wörter aus der unique-words-Datei
with open('D:/documents/Uni/MI_M/IWV/git/Iwv-Wortschatz/IWV_studentProject/xmlfiles/Liste_Aufgabe_1_Unique_words.txt', 'r', encoding='utf-8') as unique_file:
    unique_words = set(unique_file.read().splitlines())

# Einlesen der Wörter aus der Synonyme_Liste-Datei
with open('D:/documents/Uni/MI_M/IWV/git/Iwv-Wortschatz/IWV_studentProject/xmlfiles/Synonyme_Liste.txt', 'r', encoding='utf-8') as synonym_file:
    synonym_words = set(synonym_file.read().splitlines())

# Filtern der Wörter, die in beiden Dateien vorkommen
filtered_words = sorted(unique_words - synonym_words)

# Speichern der verbleibenden Wörter in einer neuen Datei
output_path = 'D:/documents/Uni/MI_M/IWV/git/Iwv-Wortschatz/IWV_studentProject/xmlfiles/Synonyme_Absolute_Liste.txt'
with open(output_path, 'w', encoding='utf-8') as output_file:
    output_file.write('\n'.join(filtered_words))

print(f"Die gefilterte Liste wurde in {output_path} gespeichert.")





