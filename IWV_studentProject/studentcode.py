import os
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

import compare_synonyms as cs
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

'''
Optionen für das Laden der Dateien. 
includeOverviews und includeSingleNews müssen entweder true oder false gesetzt werden, je nachdem welcher Korpus geladen werden soll
'''
options = DatasetOptions()
options.removeMedioPoint = True
options.includeOverviews = True
options.includeSingleNews = True
datasetPath = Path(__file__).parent / 'xmlfiles' 
dataset = LSNewsData(datasetPath, options)

def createUniqueKey(word, pos, tag):
    return f'{word}_{pos}_{tag}'

ENDINGS = ['heit', 'ie', 'ik', 'ion', 'ismus', 'ität', 'keit', 'nz', 'tur', 'ung']


def count_words_and_pos_tags(all_text, nlp):
    doc = nlp(all_text)
    pos_count = {}
    word_list = []

    types = set()

    for token in doc:
        if not token.is_punct and not token.is_space:
            word = token.text.lower()
            pos = token.pos_
            tag = token.tag_

            uKey = createUniqueKey(word, pos, tag)
            pos_count[uKey] = pos_count.get(uKey, 0) + 1
            types.add(word)
            word_list.append((word, pos, tag))

    return pos_count, word_list



def find_unique_words(word_list):
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

# Gesamtanzahl aller Wörter
total_word_count = 0

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

    ending_list_per_document = []

    tr.startTimeSection('WordsEinlesen')
    tr.startSystemMonitor()

    for i in tqdm(range(len(dataset))):
        # Anzahl der Wörter und POS-Tags ermitteln
        document = dataset[i]
        # Gesamtanzahl der Wörter aktualisieren
        pos_count, word_list = count_words_and_pos_tags(document, nlp)
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

    #print(f"Ausgabe wurde in der Datei {output_path} gespeichert.")

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

#----------   ERGEBNISSE   -----------#

    # Ausgabe Liste Aufgabe 1&2
    output_path = os.path.join(str(datasetPath), "Liste_Aufgabe_1&2.txt")
    output_path_csv = os.path.join(str(datasetPath), "Liste_Aufgabe_1&2.csv")
    out_csv = open(output_path_csv, 'w', encoding='utf-8')
    with open(output_path, 'w', encoding='utf-8') as output_file1:
        output_file1.write(f"Gesamtzahl aller Wörter: {total_word_count}\n\n")
        
        output_file1.write("Wort                     | POS  | Count | TAG   | Lexikalische Vielfalt\n")
        out_csv.write("Wort, POS, Count, TAG, Lexikalische Vielfalt\n")
        output_file1.write("-------------------------|------|-------|-------|--------\n")


        vocabulary = set(total_word_list)

        for word, pos, tag in vocabulary:
            uKey = createUniqueKey(word, pos, tag)
            output_file1.write(f"{word.ljust(25)}| {pos.ljust(5)}| {str(total_pos_count[uKey]).ljust(6)}| {tag.ljust(6)}| {total_pos_count[uKey] * 100 / total_word_count}\n")
            out_csv.write(f"{word}, {pos}, {str(total_pos_count[uKey])}, {tag}, {total_pos_count[uKey] * 100 / total_word_count:.8f}\n")

        out_csv.close()

    '''
    output_path = os.path.join(str(datasetPath), "Liste_Aufgabe_1.txt")
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(f"Gesamtzahl aller Wörter: {total_word_count}\n\n")
        output_file.write("Anzahl Wortarten:\n")
        for pos, count in total_pos_count.items():
            output_file.write(f"{pos}: {count}\n")
    
    print(f"Ausgabe wurde in der Datei {output_path} gespeichert.")

    
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
    '''

     #Herausfiltern unique words Aufgabe 3
    output_path = os.path.join(str(datasetPath), "Liste_Aufgabe_3_unique_words.txt")
    with open(output_path, 'w', encoding='utf-8') as output_file3:
        for unique_word in unique_words:
            output_file3.write(f"{unique_word}\n")

    print(f"Ausgabe wurde in der Datei {output_path} gespeichert.")
    
    utils.create_synonyms_list()
    cs.compare_synonyms()

    #Visualisierung Aufgabe 4
    output_path = os.path.join(str(datasetPath), "Liste_Aufgabe_4.txt")
    with open(output_path, 'w', encoding='utf-8') as output_file4:
        output_file4.write("\nSubstantive mit den gesuchten Endungen:\n")
        for ending, nouns in ending_lists.items():
            output_file4.write(f"{ending}: {len(nouns)} - {nouns}\n")
    

    ending_counts = {ending:len(nouns) for ending, nouns in ending_lists.items()}
    sns.barplot(x=list(ending_counts.keys()), y=list(ending_counts.values()))
    plt.title ("Anzahl der Substantive mit den gesuchten Endungen")
    plt.xlabel ("Endungen")
    plt.ylabel ("Anzahl")
    plt.show ()

    ending_lists_relative = {ending: list(nouns) for ending, nouns in ending_lists.items()}
    ending_counts_relative = {ending: len(word) for ending, word in ending_lists_relative.items()}
       
    sns.barplot(x=list(ending_counts_relative.keys()), y=list(ending_counts_relative.values()))
    plt.title ("Anzhal der Substantive mit den gesuchten Endungen (Ohne Duplikate)")
    plt.xlabel ("Endungen")
    plt.ylabel ("Anzahl")
    plt.show ()


    plt.figure(figsize=(10, 6))
    sns.barplot (x=ENDINGS, y=ending_means, errorbar=("sd",0.1))
    plt.title ("Endungen Substantive Mittelwerte mit Standardabweichung")
    plt.xlabel ("Endungen")
    plt.ylabel ("Anzahl")
    plt.show ()

    
   
    

def compute(dokument):
    print(dokument)
    cp = CProfiler()
    cp.profileCall(main)




