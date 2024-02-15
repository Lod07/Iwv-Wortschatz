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

from performance_tracker import CProfiler, PerformanceTracker

# Pfade in besser
from pathlib import Path
# LADEBALKEN
from tqdm import tqdm

def main():

    tr=PerformanceTracker()

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

    tr.startTimeSection('ModelLoading')
    tr.startSystemMonitor(250)
    # spaCy-Modell laden (deutsch)
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
        print("Spannweite: ", counts_array.max() - counts_array.min())
        print("Mittelwert: ", counts_array.mean())
        print("Standardabweichung: ", counts_array.std(ddof=0))
        print("Varianz: ", counts_array.var())
        print("                              ")
        ending_means.append(counts_array.mean())
        ending_max.append(counts_array.max())
        ending_std_devs.append(counts_array.std())
        




    # Liste für alle Substantive
    all_nouns = [word for word, pos, _ in total_word_list if pos in ['NOUN', 'PROPN', 'NE', 'NNE']]
    ending_lists = find_noun_endings(all_nouns)
    ending_counts = {ending: len(nouns) for ending, nouns in ending_lists.items()}


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

    # # Create a DataFrame
    # df = pd.DataFrame(data)

    # # Plotting
    # plt.figure(figsize=(14, 8))
    # sns.boxplot(data=df, width=0.7, palette='Set2')
    # plt.title('Boxplot of Additional Statistics for each Ending')
    # plt.show()


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


    # sns.barplot(x=ENDINGS, y=ending_means, errorbar='sd')
    # plt.title("Endungen Substantive Mittelwerte")
    # plt.xlabel("Endungen")
    # plt.ylabel("Anzahl")
    # plt.show()


    # sns.barplot(x=ENDINGS, y=ending_max, errorbar='sd')
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

    # Identifiziere Wörter, die nur einmal vorkommen
    unique_words = find_unique_words(total_word_list)

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



    # # Visualisierung Endungen Substantive
    # sns.barplot(x=list(ending_counts.keys()), y=list(ending_counts.values()), errorbar='sd')
    # plt.title("Anzahl der Substantive mit den gesuchten Endungen")
    # plt.xlabel("Endungen")
    # plt.ylabel("Anzahl")
    # plt.show()

    # # Bereinigung der Liste von Duplikaten
    # ending_lists_relative = {ending: list(OrderedDict.fromkeys(words)) for ending, words in ending_lists.items()}

    # # Visualisierung als Balkendiagramm
    # ending_counts_relative = {ending: len(words) for ending, words in ending_lists_relative.items()}

    # # Plot
    # sns.barplot(x=list(ending_counts_relative.keys()), y=list(ending_counts_relative.values()), errorbar='sd')
    # plt.title("Anzahl der Substantive mit den gesuchten Endungen (ohne Duplikate)")
    # plt.xlabel("Endungen")
    # plt.ylabel("Anzahl")
    # plt.show()
    tr.close()

if __name__ == "__main__":
    


    cp = CProfiler()
    cp.profileCall(main)

