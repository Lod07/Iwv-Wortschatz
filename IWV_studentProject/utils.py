import requests
import json

import os
from pathlib import Path

datasetPath = Path(__file__).parent / 'xmlfiles' 


dateipfad = os.path.join(str(datasetPath), "Liste_Aufgabe_3_Unique_words.txt")
unique = []
unique_final = {}

'''def getSynonymsWikitionary(token):
    r = requests.get(f"https://de.wiktionary.org/wiki/{token}")
    if("Dieser Eintrag existiert noch nicht!" in r.text):
        return []
    else:
        if not "Synonyme" in r.text:
            return []
        

        blob = r.text.split("Synonyme:")[1]
        beginning = blob.split("<dd>")[1]
        end_index = beginning.index("</dd>")
        result = beginning[:end_index]
        
        # < a ... > ... < /a >  BOESE: </i>

        lines = result.split("</a>")
        output = []
        for line in lines:
            # print(line)
            if "<i>" in line:
                if not "</i>" in line:
                    continue

                if not line.rfind('</i>') < line.rfind('<a'):
                    continue
            
            index = line.rfind('>') + 1

            if(index < len(line) - 1):
                output.append(line[index:])

        return output'''


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

def create_synonyms_list():
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

    output_dateipfad = os.path.join(str(datasetPath), "Synonyme_Liste.txt")
    output_dateipfad_pairs = os.path.join(str(datasetPath), "Synonyms_Pairs_Liste.txt")

    with open(output_dateipfad, 'w', encoding='utf-8') as output_datei:
        for element in unique_final:
            output_datei.write(element + '\n')

    with open(output_dateipfad_pairs, 'w', encoding='utf-8') as output_datei_pairs:
        for pair in synonyms_pairs:
            output_datei_pairs.write(pair + '\n')



if __name__ == "__main__":

    create_synonyms_list()

