from xml.dom import minidom
import glob
from pathlib import Path
from tqdm import tqdm

import os

# Interessante Funktionen
# LSNewsData:
#   def getFullTextOriginalXML(index) - gibt die originale XML struktur zurück
#   def getParagraphsForText(index) - gibt den text zurück als liste der entsprechenden absätze als text
#   def getParagraphXMLS(index) - das selbe wie oben aber gibt die daten als XML zurück
#   def getContentFromXML(object) - wandlet einen XML block in den entsprechenden BEREINIGTEN text um
#   def clean(text) - reinigt den entsprechenden text (wird beim abrufen der daten automatisch gemacht)
# 
# !!! BEISPIEL AM ENDE DES SCRIPTS !!!
#
# Data Cleaning Explained
# 1. Entfernen des Mediopunktes
# 2. Entfernen des Aufzählungspunktes
# 3. Korrigieren eventueller falscher Punkturierung
# 4. Aufzählungen werden umformatiert
#   Es wird sichergestellt dass am ender der Aufzählung ein "." steht
#   Aufzählungselemente werden als normale Sätze gewertet (ein-wort-punkte werden entsprechend zu ein-wort-sätzen)

# Default DataSet options (können hier global oder alternativ zum zeitpunkt der erstellung gesetzt werden)
class DatasetOptions:
    includeSingleNews: bool = True
    includeOverviews: bool = True
    removeMedioPoint: bool = True
    removeNumerics: bool = False

    def __init__(self, includeOverviews = True, includeSingleNews = True):
        self.includeOverviews = includeOverviews
        self.includeSingleNews = includeSingleNews


# UTILITY
ENUM_POINT = "•"
MEDIO_POINT = "·"

def lookintochild(node: minidom.Node, convert_enum=False):
    response = ""
    try:
        tagName = node.tagName
    except:
        tagName = ""

    # ENUMERATION CLEANING - UGLY ABER KLAPPT
    if convert_enum:
        if tagName == "enumeration":
            for a in node.childNodes:
                try:
                    tagName2 = a.tagName
                except:
                    tagName2 = ""
                if tagName2 == "statement":
                    text = a.firstChild.nodeValue
                    if text != None and not "." in a.firstChild.nodeValue:
                        if text[-1] == " ":
                            a.firstChild.nodeValue = a.firstChild.nodeValue[:-1]

                        a.firstChild.nodeValue = a.firstChild.nodeValue + "."

                        if a.firstChild.nodeValue == ".":
                            a.firstChild.nodeValue = ""

    if tagName == "headline":
        response = response + node.firstChild.nodeValue + "."

    elif tagName == "subheadline":
        if (node.firstChild.nodeValue[-1:] not in (".", "!", "?", ":")):
            response = response + node.firstChild.nodeValue + "."
        else:
            response = response + node.firstChild.nodeValue
    else:
        if len(node.childNodes) == 0:
            if (node.nodeValue != None):
                response = response + node.nodeValue
        elif len(node.childNodes) == 1:
            if node.firstChild.nodeType == 3:
                response = response + node.firstChild.nodeValue
            else:
                response = response + lookintochild(node.firstChild, convert_enum)
        else:
            response = ""
            for newChild in node.childNodes:
                response = response + lookintochild(newChild, convert_enum)
    return response

def xmlHasChildWithTag(node, tag):
    for child in node.childNodes:
        try:
            if child.tagName == tag:
                return True
        except:
            continue
        
    return False

# UTILITY ENDE

# Interface, für den fall dass wir später noch weitere Datensätze erhalten
class Dataset:

    def isValid(self):
        pass
    
    def __getitem__(self, index):
        pass
    
    def __len__(self):
        pass
    
    def getFullText(self, index):
        pass
    
    def getParagraphsForText(self, index):
       pass
    
    def getParagraphXMLS(self, index):
        pass

class LSNewsData(Dataset):

    def __init__(self, path = "", options: DatasetOptions = DatasetOptions()):

        if path == "":
            root_path = Path(__file__).parent.parent / 'xmlfiles'
        else:
            root_path = Path(path)

        if (root_path / 'newsoverview/2020-04-15_14-30_5-2.xml').exists():
            print("removed duplicate file")
            os.remove(root_path / 'newsoverview/2020-04-15_14-30_5-2.xml')

        if (root_path / 'newsoverview/2020-04-15_14-30_5-1.xml').exists():
            print("removed duplicate file")
            os.remove(root_path / 'newsoverview/2020-04-15_14-30_5-1.xml')

        if (root_path / 'singlenews/2019-06-11_14-00_320.xml').exists():
            print("removed duplicate file")
            os.remove(root_path / 'singlenews/2019-06-11_14-00_320.xml')

        self.options = options

        self.xmlFiles = []
        if options.includeSingleNews:
            self.xmlFiles += glob.glob(str(root_path / 'singlenews/*.xml'))

        if options.includeOverviews:
            self.xmlFiles += glob.glob(str(root_path / 'newsoverview/*.xml'))

    def isValid(self):
        return len(self.xmlFiles) > 0
    
    def __getitem__(self, index):
        return self.getFullText(index)
    
    def __len__(self):
        return len(self.xmlFiles)
    
    def clean(self, text):
        text = text.replace(ENUM_POINT, '')

        if(self.options.removeMedioPoint):
            text = text.replace(MEDIO_POINT, '')

        text = text.replace('  ', ' ')
        return text.replace(" . ", ". ")
    
    def getFullText(self, index):
        XMLDatei = minidom.parse(self.xmlFiles[index])
        Content = XMLDatei.getElementsByTagName("content")

        response = ""

        for ContentElem in Content:

            response = response + (lookintochild(ContentElem, True))

        before_cleaning = ' '.join(response.split())

        return self.clean(before_cleaning)
    
    def getFullTextOriginalXML(self, index):
        XMLDatei = minidom.parse(self.xmlFiles[index])
        Content = XMLDatei.getElementsByTagName("content")
        return Content
    
    def getParagraphsForText(self, index):
        XMLDatei = minidom.parse(self.xmlFiles[index])
        sections = XMLDatei.getElementsByTagName("section")

        response = []

        for section in sections:
            raw = lookintochild(section, True)
            response.append(self.clean(' '.join(raw.split())))

        return response
    
    def getParagraphXMLS(self, index):
        XMLDatei = minidom.parse(self.xmlFiles[index])
        sections = XMLDatei.getElementsByTagName("section")

        return sections
    
    def getContentFromXML(self, object):
        raw = lookintochild(object, True)
        return self.clean(' '.join(raw.split()))

# Beispielverwendung:
if __name__ == "__main__":


    datasetOptions = DatasetOptions()
    datasetOptions.includeOverviews = True
    datasetOptions.includeSingleNews = True
    datasetOptions.removeMedioPoint = True

    # Das hier macht aktuell noch nichts, ist nur ein placeholder
    datasetOptions.removeNumerics = False
    
    # hier könnt ihr den Pfad zu euren "xmlfiles" ordner angeben, nicht vergessen dass "\" kein gültiges string zeichen ist, ihr als "\\" verwenden müsst
    # unter Mac und Linux verwendet ihr dann einfach das normale "/"
    dataFull = LSNewsData("E:\\Work\\Uni\\MASTER\\InterdisziplinaereWE\\Workspace\\IWV_studentProject\\xmlfiles", datasetOptions)
    # unter verwendung keines parameters werden die Default werte (siehe oben) verwendet
    # dataFull = LSNewsData()

    for i in tqdm(range(10)):
        a = dataFull[i]
        print(a)
        print("----------")


    




