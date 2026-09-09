# S2-NZ: neutrale diagnostische Laufanbindung

Vorab gebundene Qualifikations-ID:
`s2nz-diagnostic-qualification-20260909-01`.
Ein Aufruf `C:/Python314/python.exe -m reports.s2nz.qualify_diagnostic_once`
aus dem Workspace, 24 Testgruppen mit unittest -v -f. Kein Retry.
AST-Inventar, Code-/Quellenhashes und Budgets vor dem Unterprozess publizieren.
Keine NZ-Payloads; keine separate reale Materialisierung oder Hauptgeschichte.

## Kleinster Anschluss

`tools/_s2nz_private_diagnostic_run.py` bindet die unveraenderte NZ-
Vorversiegelung an `NY.execute`, `PrefixStream`, `FrozenInputs` und den
vorhandenen NW/NV-AudioReader. Keine historische Hauptfunktion aufrufen,
umetikettieren oder veraendern. NY-Arithmetik, Direktrechnung, Werteformen,
Zeitvalidierung und atomare Dateioperationen bleiben unveraendert.
Die neue NZ-Huelle enthaelt den original versionierten NY-Kompositionsbeleg
als `core`; dessen Schema und Digest werden nicht als neue Rechnung ausgegeben.

Der private Einmaleinstieg bleibt Gate False. Spaeter Quellenhashpruefung vor
Rezeptoranalyse, NJ vor Kontaktbildung (hier entstehen keine Kontakte),
sechs frische Praefixe und Fehlerhistorien, unveraenderte Freeze-Eingaenge.
Die Generatorfunktion erhaelt nur die gebundene gerade freigegebene Quelle.
Die Praediktoren erhalten ausschliesslich unveraenderte NY-Funktionseingaben:
Profil-/Freeze-Skala, verfuegbare Vektoren und unmittelbar vorherige Fehler.
Saubere Gegenfolgen sind kein operativer Eingang und kein Ersatz-Ziel.

Die unabhaengige technische Verifikation delegiert die numerische
Nachrechnung an den unveraenderten NY-Direktpruefer und bindet zusaetzlich
die NZ-Huelle. Die getrennte NZ-Auswertung verwendet keine NY-R/L/P/W-
Erfolgskriterien. Nur diagnostische Einzelwerte, keine praktische Schwelle,
keine Robustheit und keine nachtraegliche Auswahl eines besseren Arms.

## Testinventar

01-06: vollstaendige synthetische Komposition, alle Arm-/LOCAL-Bindungen vor
Zielzugriff, fehlende/geaenderte Bindung, vier unabhaengige Fehlerherkunfts-
manipulationen und identische funktionale Praefixe trotz anderer Kennungen.
07-11: sauberen Eingang oder Ersatz-Ziel abweisen, fremden Zielbeleg ablehnen,
Fehler gegen den eigenen beobachteten Zustand, Ruecksetzung je Folge,
Freeze-Unveraenderlichkeit, Mutation und Freigabe ohne Owner/Lernupdates.
12-15: vier Fokusstellen trotz teilweiser oder vollstaendiger Enthaltung,
D separat, keine Ersatzprognose/Nullfehler; ausschliesslich negative Gewinne
gegen LOCAL technisch gueltig; NEXT_BEST kann gegen beide Kontrollen verlieren.
16-20: unabhaengige Rechnung ohne primaere Prognosehelfer, fehlende/fremde
Belege, unveraenderte Nullnenner-/Extrapolationsrechnung ohne Clipping,
Arbeits-/Groessenlimits, atomarer Schreibkonflikt und phasengenauer Fehlerabschluss.
21-24: Quellenzeit, Profil, Gate False; echter neutraler AudioReader mit
fuenf Null-PCM-Fenstern und Prognosebindung vor Erzeugung; einmalige lesende
Dateipruefung vor Auswertung; vollstaendige Ausgabehuelle und Auswertungssperre.

## Endliche Grenzen

Unveraenderte spaetere NY/NZ-Arbeitsgrenzen: 30 Analysen und NJ-Projektionen,
18 Stellen, zwoelf LOCAL-Fits, pro Implementierung je 2.304 Prognose-
Subtraktionen/Multiplikationen/Additionen, 864 Persistenzkopien, je 1.152
LOCAL-Differenzen/Produkte/Additionen, maximal zwoelf Divisionen,
3.168 Fehlerterme, 66 MAE und hoechstens 96 Gewinndifferenzen.
Offline separat: 1.440 Halbierungen und die bisherigen doppelten NY-
Rechengrenzen; keine Rezeptor- oder Payloadwiederholung.

Diagnostische Auswertung: 24 direkte H1/H2-Gewinndifferenzen gegen LOCAL
an den zwoelf Stellen; uebrige absolute Gewinne aus gespeicherten NY-Scores.
Hoechstens 96 verschiedene WIN/TIE/LOSS-Beziehungen (48 gegen PERSIST,
24 feste Historien gegen LOCAL, maximal 24 Empfehlung gegen LOCAL/PERSIST)
und 18 Empfehlungsurteile. Gruppensummen zaehlen vorhandene Statusformen,
keine weitere numerische Klassifikation. Relevanzvergleiche null.
N=4 fuer p05/p06/p11/p12 fest, D ausgegebener Empfehlungen separat.
Sauber/gestoert und H1/H2/Empfehlung getrennt, Wechselziele einzeln sichtbar.

Neutral: drei vollstaendige synthetische Bestaende, zwei Fehlerabschluesse,
hoechstens zwoelf zusaetzliche Praefixinstanzen. Keine NZ-Quellen erzeugen;
alle historischen und NZ-Payloadgeneratoren gesperrt. Fuenf echte neutrale
Nullfenster: fuenf Analysen und NJ-Projektionen, 96.000 PCM-Byte, hoechstens
19.200 Byte gleichzeitig. Sonst ausschliesslich synthetische Vektoren,
Freeze-Fixtures und vollstaendige neutrale Quellen-/Rezeptmetadaten.
Suite-Summenobergrenzen fuer aktive und Offline-Rechnung stehen vorab in
preregistration.json. Sie erweitern keine Grenze eines spaeteren Hauptlaufs.

Gesamtbeleg maximal 2.097.152 Byte einschliesslich NZ-Huelle, originalem
NY-Core, Quellen, Roh-/Halbwerten, Prognosen, Fehlern und Codehashes;
Stelle 65.536, Freeze 4.096, Verifikation/Auswertung jeweils 262.144 Byte.
Der neutrale Vollbeleg wird gespeichert. Kein Platzhalter-Huellennachweis.

## Aussagegrenzen

Qualifiziert wird der kontrollierte Funktionsaufruf, keine Sandbox gegen
beliebigen Pythoncode. Offline lassen sich Werte, Fehler und Bindungsketten
pruefen, nicht allein durch Digests die historische CPU-Aufrufordnung.
Kein prognostischer oder praktischer NZ-Nutzen aus neutralen Fixtures.
Keine Quellen-/Seed-/Stoerstaerkenaenderung, Owneroeffnung, Lernupdates oder
Memory-/Feld-/Systemintegration. Gates False, ME/MI gesperrt.
