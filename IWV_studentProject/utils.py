import requests
import json


dateipfad = 'D:/documents/Uni/MI_M/IWV/git/Iwv-Wortschatz/IWV_studentProject/xmlfiles/Liste_Aufgabe_1_Unique_words.txt'
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



if __name__ == "__main__":

    with open(dateipfad, 'r', encoding='utf-8') as datei:
        unique = datei.read().splitlines()

    print(unique)

    unique_final = []

    for wort in unique:
        synonyme = getSynonymsWikitionary(wort)
        
        # Hier werden die gefundenen Synonyme zur Liste hinzugefügt
        unique_final.extend(synonyme)

    # Ergebnisse ausgeben
    print("Synonyme:")
    for element in unique_final:
        print(element)

    output_dateipfad = 'D:/documents/Uni/MI_M/IWV/git/Iwv-Wortschatz/IWV_studentProject/xmlfiles/Synonyme_Liste.txt'
    with open(output_dateipfad, 'w', encoding='utf-8') as output_datei:
        for element in unique_final:
            output_datei.write(element + '\n')
