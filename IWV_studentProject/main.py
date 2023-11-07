from xml.dom import minidom
import glob
import studentcode

def cntChilds(object):
    return len(object.childNodes)

def lookintochild(node):
    response = ""
    try:
        tagName = node.tagName
    except:
        tagName = ""

    if tagName == "headline":
        response = response + node.firstChild.nodeValue + "."

    elif tagName == "subheadline":
        if (node.firstChild.nodeValue[-1:] not in (".", "!", "?", ":")):
            response = response + node.firstChild.nodeValue + "."
        else:
            response = response + node.firstChild.nodeValue
    else:
        if cntChilds(node) == 0:
            if (node.nodeValue != None):
                response = response + node.nodeValue
        elif cntChilds(node) == 1:
            if node.firstChild.nodeType == 3:
                response = response + node.firstChild.nodeValue
            else:
                response = response + lookintochild(node.firstChild)
        else:
            response = ""
            for newChild in node.childNodes:
                response = response + lookintochild(newChild)
    return response

# Die Funktion compute wird hier definiert. Die Funktion bekommt den Gesamttext eines Dokuments übergeben und gibt diesen in der Konsole aus.


# singlenews ist eine Liste aller Einzelnachrichten in Form von XML Dateinamen
singlenews = glob.glob('xmlfiles/singlenews/*.xml')

# newsoverview ist eine Liste aller Nachrichtenüberblicke in Form von XML Dateinamen
newsoverview = glob.glob('xmlfiles/newsoverview/*.xml')

# Programmstart! Alle Dateinamen der Liste singlenews werden iterativ in der Variable elem gespeichert
for elem in singlenews:

    # Minidom.parse öffnet die XML Datei mit dem Namen aus elem und speichert den Inhalt als Objekt in XMLDatei
    XMLDatei = minidom.parse(elem)

    # In Content werden alle Tags mit dem Tagnamen Content als DOM-Knoten gespeichert
    Content = XMLDatei.getElementsByTagName("content")

    response = ""

    # Alle Kindelemente in Content werden durchgegangen und der Textinhalt der Knoten wird in response zusammengefügt.
    for ContentElem in Content:
        response = response + (lookintochild(ContentElem))

    # Der Textinhalt wird an compute übergeben (Leerzeichen werden vorher entfernt)
    studentcode.compute(' '.join(response.split()))




