import requests
import json


dateipfad = 'D:/documents/Uni/MI_M/IWV/git/Iwv-Wortschatz/IWV_studentProject/xmlfiles/Liste_Aufgabe_1_Unique_words.txt'
unique = []
unique_final = {}


def getSynonymsWiktionary(token):
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

if __name__ == "__main__":
    with open(dateipfad, 'r', encoding='utf-8') as datei:
        unique = datei.read().splitlines()

    print(unique)

    synonyms_pairs = []

    for wort in unique:
        synonyme = getSynonymsWiktionary(wort)
        
        # Hier werden die gefundenen Synonyme zur Liste hinzugefügt
        synonyms_pairs.append(f"{wort}: {', '.join(synonyme)}")

    # Ergebnisse ausgeben
    print("Synonyms-pairs:")
    for pair in synonyms_pairs:
        print(pair)

    output_dateipfad_synonyms = 'D:/documents/Uni/MI_M/IWV/git/Iwv-Wortschatz/IWV_studentProject/xmlfiles/Synonyme_Liste.txt'
    output_dateipfad_pairs = 'D:/documents/Uni/MI_M/IWV/git/Iwv-Wortschatz/IWV_studentProject/xmlfiles/Synonyms_Pairs_Liste.txt'
    
    with open(output_dateipfad_synonyms, 'w', encoding='utf-8') as output_datei_synonyms, open(output_dateipfad_pairs, 'w', encoding='utf-8') as output_datei_pairs:
        for synonym in unique_final:
            output_datei_synonyms.write(synonym + '\n')
        
        for pair in synonyms_pairs:
            output_datei_pairs.write(pair + '\n')
