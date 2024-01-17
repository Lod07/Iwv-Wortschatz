import os
import spacy
import seaborn as sns
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
from dataLoader import LSNewsData, DatasetOptions

# Pfade in besser
from pathlib import Path
# LADEBALKEN
from tqdm import tqdm

def createUniqueKey(word, pos, tag):
    return f'{word}_{pos}_{tag}'


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
    unique_words = [word for word, count in word_counter.items() if count == 1]
    return unique_words


def find_noun_endings(noun_list):
    endings = ['heit', 'ie', 'ik', 'ion', 'ismus', 'ität', 'keit', 'nz', 'tur', 'ung']
    ending_lists = {ending: [] for ending in endings}

    for noun in noun_list:
        for ending in endings:
            if noun.endswith(ending):
                ending_lists[ending].append(noun)

    return ending_lists


if __name__ == "__main__":
    nlp = spacy.load("de_core_news_lg")
    options = DatasetOptions()
    options.removeMedioPoint = True
    datasetPath = Path(__file__).parent / 'xmlfiles'

    dataset = LSNewsData(datasetPath, options)


    total_word_count = 0
    total_pos_count = {}
    total_word_list = []

    for i in tqdm(range(len(dataset))):

        pos_count, word_list = count_words_and_pos_tags(dataset[i], nlp)
        total_word_count += len(word_list)

        for key in pos_count:
            total_pos_count[key] = total_pos_count.get(key, 0) + pos_count[key]

        total_word_list.extend(word_list)

    assert total_word_count == len(total_word_list)
    print(len(total_word_list))

    unique_words = find_unique_words(total_word_list)
    all_nouns = [word for word, pos, _ in total_word_list if pos == 'NOUN']
    ending_lists = find_noun_endings(all_nouns)


    ###################### AUSGABE ######################


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

        out_csv.close()

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

    #Hi bin a commentar <- noice