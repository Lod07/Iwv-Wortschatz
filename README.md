# Iwv-Wortschatz
## Gruppe 4 
Wortschatz erstellen
## Autoren 
Timur Friederici und Philip Schneider
## Benutzung 
Bei Nutzung des Projekts müssen die genutzen Pakete gegebenenfalls nochmal installiert werden.

Numpy:
```bash
pip install numpy
```
Seaborn:
```bash
pip install seaborn
```
Pandas:
```bash
pip install pandas
```
Matplotlib:
```bash
python -m pip install -U pip
python -m pip install -U matplotlib
```
SpaCy:
```bash
pip install -U pip setuptools wheel
pip install -U spacy
```

Gegebenfalls muss folgender Command genutzt werden, um das Sprachmodell herunterzuladen. 
```bash
python -m spacy download de_core_news_lg
```

Innerhalb der studentcode.py muss für die einzelnen Datenkorpora den Boolean für den jeweiligen Datenkorpus auf true/false gesetzt werden. 

## Ergebnisse
Die Performance-Messungen und die statistischen Werte werden jeweils als Textdatei abgespeichert. Die Performance-Messungen
sind im Ordner [logs](./IWV_studentProject/logs/log.txt) zu finden. Die statistische Auswertung für alle 3 Korpora ist im Ordner [statistics](./IWV_studentProject/statistics/results.txt)
zu finden. Alle erstellten Diagramme werden im Ordner [diagrams](./IWV_studentProject/diagrams) abgespeichert.
