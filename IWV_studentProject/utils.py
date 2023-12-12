import requests
import json


dateipfad = 'D:/documents/Uni/MI_M/IWV/git/Iwv-Wortschatz/IWV_studentProject/xmlfiles/Liste_Aufgabe_1_Unique_words.txt'
unique = []
unique_final = {}

def getSynonymsWikitionary(token):
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

        return output


if __name__ == "__main__":


    
    output = getSynonymsWikitionary("Arzt")
    output2 = getSynonymsWikitionary("schleichen")
    output3 = getSynonymsWikitionary("trinken")

    out_dict = {}
    out_dict["Arzt"] = output
    out_dict["schleichen"] = output2
    out_dict["trinken"] = output3

    with open("out.json", "w") as f:
        json.dump(out_dict, f)

    with open("out.json", "r") as f:
        data = json.load(f)

    
    print(data)
    print(data["Arzt"])

    with open(dateipfad, 'r', encoding='utf-8') as datei:
        unique = datei.read().splitlines()

    print(unique)

    for wort in unique:
        synonyme = getSynonymsWikitionary(wort)
        unique_final = synonyme

    #Ergebnisse ausgeben
    print("Synonyme:")
    for element in unique_final:
        print(element)
