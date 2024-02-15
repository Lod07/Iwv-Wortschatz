import requests
from bs4 import BeautifulSoup

dateipfad = 'D:/documents/Uni/MI_M/IWV/git/Iwv-Wortschatz/IWV_studentProject/xmlfiles/Liste_Aufgabe_1_Unique_words2.txt'
unique = []
unique_final = []

def getSynonymsWiktionary(token):
    r = requests.get(f"https://de.wiktionary.org/wiki/{token}")
    if "Dieser Eintrag existiert noch nicht!" in r.text:
        return []

    soup = BeautifulSoup(r.text, 'html.parser')

    # Finden Sie das <span>-Element mit der Klasse "mw-headline" und dem Text "Synonyme"
    synonym_heading = soup.find('span', class_='mw-headline', string='Synonyme')
    if not synonym_heading:
        return []

    # Suchen Sie nach den folgenden Geschwister-<li>-Elementen als Synonyme
    synonyms_list_items = synonym_heading.find_next('div', class_='mw-parser-output').find_all('li')
    if not synonyms_list_items:
        return []

    output = [item.text.strip() for item in synonyms_list_items]
    return output

if __name__ == "__main__":
    with open(dateipfad, 'r', encoding='utf-8') as datei:
        unique = datei.read().splitlines()

    print(unique)

    unique_final = []

    for wort in unique:
        synonyme = getSynonymsWiktionary(wort)
        unique_final.extend(synonyme)

    # Ergebnisse ausgeben
    print("Synonyme:")
    for element in unique_final:
        print(element)
