# S2-NY: neutrale Empfehlungs-/LOCAL-Anbindung

Vor dem einzigen Testaufruf gebunden. Keine NY-Hauptlauffreigabe.
Qualifikations-ID: `s2ny-prediction-qualification-20260909-01`.
Aufruf aus dem Workspace: `C:/Python314/python.exe -m reports.s2ny.qualify_prediction_once`.
Dieser startet genau einmal die 30 Tests mit `unittest -v -f`; kein Retry.
AST-Inventar, Interpreterumgebung und vollstaendige Quellhashes werden vorher
in `preregistration.json` gespeichert und danach auf Gleichheit geprueft.

## Fester Pruefumfang

- 01-04: vollstaendige neutrale Komposition, unveraenderliche Freeze-Eingaenge,
  fehlende Evidenz an k=2 und Gleichstand ohne Ersatzprognose oder Nullfehler.
- 05-09: fremde Folge, vertauschte Historien, manipulierte Primaer-/Direktfehler,
  falsche Freeze-Bindung sowie veraltete oder fehlende Vorstellenbelege.
- 10-12: kein Zielzugriff ohne Bindung, nachtraegliche Aenderung abweisen,
  alle Prognosearme einschliesslich LOCAL und Direktrechnung vor Ziel-Reader.
- 13-18: frische LOCAL-Schaetzung, vorgebundene Reihenfolge, Nullnenner,
  Subnormale/Produktunterlauf, ungueltige Werte/Profile, unabhaengige Rechnung,
  keine Quellenfelder oder Clipping, identische funktionale Praefixe.
- 19-23: Freeze-Manipulation, Ruecksetzung/Lifecycle, phasengenauer Abbruch,
  keine fachliche Teilauswertung, manipulierte/fehlende/vertauschte Belege.
- 24-26: NEXT_BEST trotz Verlust gegen LOCAL/PERSIST, getrennte 20 Kriterien,
  leere Nenner und nicht eingetretene W-Verlustprognosen technisch gueltig.
- 27-30: Arbeits-/Groessenlimits, atomarer Schreibkonflikt, geschlossenes Gate,
  tatsaechlicher neutraler Audio-/NJ-Adapter und vollstaendige Ergebnishuellen
  einschliesslich Quellhashes sowie Auswertungssperre vor Verifikation.

## Neutralitaet und endliche Arbeit

Zwei vollstaendige synthetische Sechserbestaende und ein synthetischer
Fehlerabschluss; hoechstens 24 weitere kleine Praefixinstanzen. Synthetische
Freeze-Payloads stammen aus dem vorhandenen neutralen NX-Formbeleg, nicht aus
einer erneuten Lernkette. Keine realen NY-Rezeptorwerte werden verwendet.
Ein echter Adaptertest verwendet ausschliesslich fuenf Null-PCM-Fenster:
fuenf Analysen und fuenf NJ-Projektionen, 96.000 erzeugte PCM-Byte insgesamt,
hoechstens 19.200 Byte gleichzeitig, keine Rohpayloadablage.
NY-Generatoren und reale Planeinstiege sind waehrend der Tests gesperrt.

Pro vollstaendigem neutralem Bestand gelten die unveraenderten spaeteren
NY-Grenzen: 18 Stellen, 12 LOCAL-Schaetzungen, je Implementierung 66
Prognosevektoren, 2.304 Subtraktionen/Multiplikationen/Additionen,
1.152 LOCAL-Differenzen/Produkte/Additionen, maximal 12 Divisionen,
3.168 Fehlerterme und 96 Gewinndifferenzen. Offline-Arbeit ist separat
gebunden: zweimal diese Rechenarbeit plus 1.440 Halbierungspruefungen.
Die konservativen Suite-Obergrenzen stehen vor Ausfuehrung vollstaendig in
der Vorregistrierung; sie vergroessern keine spaeteren NY-Laufgrenzen.

Gesamtbeleg maximal 2.097.152 Byte, Prognosebindung 65.536 Byte,
Freeze-Payload 4.096 Byte, Verifikation und Auswertung je 262.144 Byte.
Der Huellentest serialisiert einen vollstaendigen neutralen Gesamtbeleg mit
allen Quellen-, Roh-/Halb-, Prognose-, Fehler-, Freeze- und Codebindungen.

## Aussagegrenzen

Die kontrollierte Aufruffolge verhindert Zielverarbeitung vor Bindung und
prueft ausschliesslich unmittelbar vorhergehende Fehler derselben Folge.
Sie ist keine Betriebssystem-Sandbox gegen beliebigen fremden Pythoncode.
Offline lassen sich gespeicherte Arithmetik, Halbierungen und Belegketten
nachrechnen, nicht allein aus Digests die historische Wandzeit beweisen.
LOCAL hat keinen fortgeschriebenen Lernzustand. Die Empfehlung waehlt nur
eine bereits gebundene Historienprognose; sie erzeugt keine Ersatzwerte.
Keine NY-Payloads, Owneroeffnung, Lernupdates oder Memory-/Feld-/Runtimeaufrufe.
Alle Hauptgates bleiben False; ME/MI bleiben gesperrt.
