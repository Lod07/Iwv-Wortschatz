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

def createUniqueKey(word, pos, tag):
    return f'{word}_{pos}_{tag}'

ENDINGS = ['heit', 'ie', 'ik', 'ion', 'ismus', 'ität', 'keit', 'nz', 'tur', 'ung']
 
#@profile
def count_words_and_pos_tags(all_text, nlp):
    # spaCy für POS-Tagging verwenden
    doc = nlp(all_text)


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

if __name__ == "__main__":
    nlp = spacy.load("de_core_news_lg")
    options = DatasetOptions()
    options.removeMedioPoint = True
    datasetPath = Path(__file__).parent / 'xmlfiles'

    dataset = LSNewsData(datasetPath, options)
def main():

    tr=PerformanceTracker()
        

# Liste für alle individuellen Wörter mit ihrer Häufigkeit und Wortart
total_word_list = []

    # spaCy-Modell laden (deutsch)
    tr.startTimeSection('ModelLoading')
    tr.startSystemMonitor()
    nlp = spacy.load("de_core_news_lg")
    tr.stopSystemMonitor()
    tr.endTimeSection('ModelLoading')

dataset = LSNewsData(datasetPath, options)

    # Dictionary zur Verfolgung der Gesamtanzahl der Wörter pro Wortart
    total_pos_count = {}

    # Liste für alle individuellen Wörter mit ihrer Häufigkeit und Wortart
    total_word_list = []

    options = DatasetOptions()
    options.removeMedioPoint = True
    datasetPath = Path(__file__).parent / 'xmlfiles' 

    # Liste aller individuellen Wörter aktualisieren
    total_word_list.extend(word_list)


    dataset = LSNewsData(datasetPath, options)
    ending_list_per_document = []

    tr.startTimeSection('WordsEinlesen')
    tr.startSystemMonitor()

    for i in tqdm(range(len(dataset))):
        # Anzahl der Wörter und POS-Tags ermitteln
        document = dataset[i]
        pos_count, word_list = count_words_and_pos_tags(document, nlp)
    output_path = os.path.join(str(datasetPath), "Liste_Aufgabe_1.txt")
    output_path_csv = os.path.join(str(datasetPath), "Liste_Aufgabe_1.csv")
    out_csv = open(output_path_csv, 'w', encoding='utf-8')
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(f"Gesamtzahl aller Wörter: {total_word_count}\n\n")
        
        output_file.write("Wort                     | POS  | Count | TAG   | Lexikalische Vielfalt\n")
        out_csv.write("Wort, POS, Count, TAG, Lexikalische Vielfalt\n")
        output_file.write("-------------------------|------|-------|-------|--------\n")

        vocabulary = set(total_word_list)

        for word, pos, tag in vocabulary:
            uKey = createUniqueKey(word, pos, tag)
            output_file.write(f"{word.ljust(25)}| {pos.ljust(5)}| {str(total_pos_count[uKey]).ljust(6)}| {tag.ljust(6)}| {total_pos_count[uKey] * 100 / total_word_count}\n")
            out_csv.write(f"{word}, {pos}, {str(total_pos_count[uKey])}, {tag}, {total_pos_count[uKey] * 100 / total_word_count:.8f}\n")
        # Gesamtanzahl der Wörter pro Wortart aktualisieren
        for pos, count in pos_count.items():
            total_pos_count[pos] = total_pos_count.get(pos, 0) + count

        out_csv.close()
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

print(f"Ausgabe wurde in der Datei {output_path} gespeichert.")

    #Visualisierung 

output_path = os.path.join(str(datasetPath), "Liste_Aufgabe_1_unique_words.txt")
with open(output_path, 'w', encoding='utf-8') as output_file2:
    for unique_word in unique_words:
        output_file2.write(f"{unique_word}\n")

print(f"Ausgabe wurde in der Datei {output_path} gespeichert.")

    # # Iteriere über jeden Balken und füge einen individuellen Fehlerbalken hinzu
    # for i, mean in enumerate(ending_means):
    #     std_dev = ending_std_devs[i]
    #     plt.errorbar(i, mean, yerr=std_dev, color='black', capsize=5)  


    '''
    for ending in ENDINGS:    
        sns.boxplot(data = counts)
        plt.title(f'Boxplot für Endung "{ending}"')
        plt.show()
    '''

    # # Daten für Boxplot vorbereiten
    # boxplot_data = {ending: pd.Series([len(doc_elists[ending]) for doc_elists in ending_list_per_document]) for ending in ENDINGS}



    # # Daten für Boxplot in DataFrame umwandeln
    # data = pd.DataFrame(boxplot_data)

    # # Boxplot erstellen
    # plt.figure(figsize=(12, 8))
    # sns.boxplot(data=data, flierprops=dict(markerfacecolor='0.50', markersize=2))
    # plt.yticks(np.arange(0, max(ending_max)+1, 2))
    # plt.ylim(0, max(ending_max)+1)
    # plt.title("Boxplot für Substantiv-Endungen")
    # plt.xlabel("Endungen")
    # plt.ylabel("Anzahl")
    # plt.show()


    # # Boxplot erstellen
    # plt.figure(figsize=(12, 8))
    # #sns.boxplot(data=data, flierprops=dict(markerfacecolor='0.50', markersize=2))
    # sns.boxplot(data=data, showfliers = False)
    # plt.yticks(np.arange(0, max(ending_max)+1, 2))
    # plt.ylim(0, 2)
    # plt.title("Boxplot für Substantiv-Endungen")
    # plt.xlabel("Endungen")
    # plt.ylabel("Anzahl")
    # plt.show()

    '''
    boxplot_data = {ending: [] for ending in ENDINGS}

    for doc_elists in ending_list_per_document:
        for ending in ENDINGS:
            noun_count = len(doc_elists[ending])
            # Überprüfen, ob die Liste leer ist
            #if noun_count > 0:
            #    boxplot_data[ending].append(noun_count)
            #else:
            #    boxplot_data[ending].append(np.nan)

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

    '''



    # sns.barplot(x=ENDINGS, y=ending_means)
    # plt.title("Endungen Substantive Mittelwerte")
    # plt.xlabel("Endungen")
    # plt.ylabel("Anzahl")
    # plt.show()

    # sns.barplot(x=ENDINGS, y=ending_max)
    # plt.title("Endungen Substantive Maxima")
    # plt.xlabel("Endungen")
    # plt.ylabel("Anzahl")
    # plt.show()

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



    #Herausfiltern unique words
    output_path = os.path.join(str(datasetPath), "Liste_Aufgabe_1_unique_words.txt")
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
    tr.close()

if __name__ == "__main__":
    


    cp = CProfiler()
    cp.profileCall(main)




