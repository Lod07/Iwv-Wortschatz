import os
import xml.etree.ElementTree as ET
import spacy
from pathlib import Path
from tqdm import tqdm

def count_words_and_pos_tags(all_text, nlp):
    doc = nlp(all_text)
    pos_count = {}
    word_list = []

    for token in doc:
        if not token.is_punct and not token.is_space:
            word = token.text.lower()
            pos = token.pos_
            tag = token.tag_

            pos_count[pos] = pos_count.get(pos, 0) + 1

            if word[-1] == "." and tag == "ADJ":
                continue

            if pos == "NUM":
                continue

            word_list.append((capitalize_word(word, pos), pos, tag))

    return pos_count, word_list

def find_noun_endings(noun_list):
    endings = ['heit', 'ie', 'ik', 'ion', 'ismus', 'ität', 'keit', 'nz', 'tur', 'ung']
    ending_lists = {ending: [] for ending in endings}

    for noun in noun_list:
        for ending in endings:
            if noun.endswith(ending):
                ending_lists[ending].append(noun)

    return ending_lists

def capitalize_word(word, pos):
    if pos in ['NOUN', 'PROPN', 'NE', 'NNE']:
        return word.capitalize()
    return word

total_word_count = 0
nlp = spacy.load("de_core_news_lg")
total_pos_count = {}
total_word_list = []

xml_files_path = Path(r'D:\documents\Uni\MI_M\IWV\git\Iwv-Wortschatz\IWV_studentProject\xmlfiles\singlenews')

for file_path in tqdm(xml_files_path.glob('*.xml')):
    with open(file_path, 'r', encoding='utf-8') as file:
        document = file.read()
        pos_count, word_list = count_words_and_pos_tags(document, nlp)

        total_word_count += sum(pos_count.values())

        for pos, count in pos_count.items():
            total_pos_count[pos] = total_pos_count.get(pos, 0) + count

        total_word_list.extend(word_list)

print(len(total_word_list))

all_nouns = [word for word, pos, _ in total_word_list if pos in ['NOUN', 'PROPN', 'NE', 'NNE']]
ending_lists = find_noun_endings(all_nouns)

output_path = os.path.join(str(xml_files_path), "Liste_Aufgabe_1_.txt")
with open(output_path, 'w', encoding='utf-8') as output_file:
    output_file.write(f"Gesamtzahl aller Wörter: {total_word_count}\n\n")
    output_file.write("Anzahl Wortarten:\n")
    for pos, count in total_pos_count.items():
        output_file.write(f"{pos}: {count}\n")

    final = {}
    for word, pos, tag in total_word_list:
        word = capitalize_word(word, pos)
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
