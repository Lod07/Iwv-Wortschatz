import os
from pathlib import Path

datasetPath = Path(__file__).parent / 'xmlfiles' 

def compare_synonyms():
    # Einlesen der Wörter aus der unique-words-Datei
    file_path_task3 = os.path.join(str(datasetPath), "Liste_Aufgabe_3_Unique_words.txt")
    with open(file_path_task3, 'r', encoding='utf-8') as unique_file:
        unique_words = set(unique_file.read().splitlines())

    file_path_synonyms = os.path.join(str(datasetPath), "Synonyme_Liste.txt")
    # Einlesen der Wörter aus der Synonyme_Liste-Datei
    with open(file_path_synonyms, 'r', encoding='utf-8') as synonym_file:
        synonym_words = set(synonym_file.read().splitlines())

    # Filtern der Wörter, die in beiden Dateien vorkommen
    filtered_words = sorted(unique_words - synonym_words)

    file_path_synonyms_absolute = os.path.join(str(datasetPath), "Synonyme_Absolute_Liste.txt")
    # Speichern der verbleibenden Wörter in einer neuen Datei
    with open(file_path_synonyms_absolute, 'w', encoding='utf-8') as output_file:
        output_file.write('\n'.join(filtered_words))

    print(f"Die gefilterte Liste wurde in {file_path_synonyms_absolute} gespeichert.")
