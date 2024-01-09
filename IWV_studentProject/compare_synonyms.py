# Einlesen der Wörter aus der unique-words-Datei
with open('D:/documents/Uni/MI_M/IWV/git/Iwv-Wortschatz/IWV_studentProject/xmlfiles/Liste_Aufgabe_1_Unique_words.txt', 'r', encoding='utf-8') as unique_file:
    unique_words = set(unique_file.read().splitlines())

# Einlesen der Wörter aus der Synonyme_Liste-Datei
with open('D:/documents/Uni/MI_M/IWV/git/Iwv-Wortschatz/IWV_studentProject/xmlfiles/Synonyme_Liste.txt', 'r', encoding='utf-8') as synonym_file:
    synonym_words = set(synonym_file.read().splitlines())

# Filtern der Wörter, die in beiden Dateien vorkommen
filtered_words = unique_words - synonym_words

# Speichern der verbleibenden Wörter in einer neuen Datei
output_path = 'D:/documents/Uni/MI_M/IWV/git/Iwv-Wortschatz/IWV_studentProject/xmlfiles/Synonyme_Absolute_Liste.txt'
with open(output_path, 'w', encoding='utf-8') as output_file:
    output_file.write('\n'.join(filtered_words))

print(f"Die gefilterte Liste wurde in {output_path} gespeichert.")
