# Kurze visuelle Folgen: Aufgaben- und Pruefplan

**Status: ausschliesslich Planung. Keine Implementierung oder Ausfuehrung.**
Basis ist `897bf23`. B4 und die technisch vorgegebene L1-KAL-Schwelle
`44/765` bleiben begrenzte Arbeitsreferenzen. Der abgeschlossene
[Kalibrierungsbefund](../reports/tspm1_functional/calibration-20260828-01/BEFUND.md)
bleibt unveraendert; G1 wird nicht durch weitere Mechanik bearbeitet.

## 1. Bestand und konkrete Luecke

Der private [B4-Kern](../mcm_field_organism/_tspm1_s2dr_private_comparison.py)
enthaelt `_FIFOEntry.values`, `formation_index` und `_B4State.accepted_count`.
`_advance_b4` uebernimmt den **vom Caller uebergebenen** Bildungsindex und
erhoeht den Bankzaehler. Er erzeugt oder validiert die zeitliche Herkunft
dieses Arguments nicht selbst. Diese Bindung muss der private Versuchsadapter leisten.

`_probe_joint_slots` und der private
[kalibrierte Einzelabruf](../tools/_visual_l1_calibration_probe.py) waehlen
einen passenden Eintrag. Der Index dient dabei nur als Tie-Breaker;
eine geordnete Vier-Bild-Folge wird nicht verglichen. **Vorhandene Indizes
sind daher noch kein nachgewiesener Sequenzabruf.**

Erforderlich waere eine kleine private read-only Erweiterung: vier
empfangene Probevektoren gegen vier anhand ihrer gespeicherten
Bildungsindizes geordnete Eintraege pruefen. Kein neuer Bankzustand,
keine erlernte Regel, kein oeffentlicher oder feldinterner Abrufpfad.

## 2. Eingaben und Zeitraster

Unveraendertes Rezeptorprofil: 120 x 80 RGB-Pixel, 3 x 2 Zellen mit je
40 x 40 Pixeln, drei gleiche Kanalwerte je Zelle, 18 visuelle Werte.
Auditiv bleiben alle acht Werte null. Die Buchstaben dieser Tabelle sind
neue aeussere Versuchsbezeichnungen, nicht die alten A/B/C-Entwicklungsbilder:

| Bild | Obere Zeile | Untere Zeile |
|---|---|---|
| A | 48, 48, 48 | 176, 176, 176 |
| B | 48, 176, 48 | 176, 48, 176 |
| C | 176, 48, 48 | 48, 176, 176 |
| D | 176, 176, 176 | 48, 48, 48 |

Alle Bilder haben dieselben lokalen Werte, je drei helle und drei dunkle
Zellen und die globale Kanalhelligkeit 112/255. Ihre Ortsanordnungen sind
verschieden. Aus der Konstruktion folgt fuer verschiedene Bilder bei den
zugelassenen Offsets ein L1-Abstand von mindestens `128/765`, deutlich
ueber `44/765`; zum eigenen Bild bei +/-8 ist es `8/255`. Dies ist eine
analytische Eingangsvoraussetzung, **kein bereits gemessener neuer Befund**.
Spaeter sind die tatsaechlichen Rezeptorwerte und Paarabstaende zu pruefen,
mit den ohnehin vorgesehenen Abstandstabellen, ohne zusaetzliche Bildanalysen.

Zwei getrennte Episoden mit frischen Banken:

| Episode | Tatsaechliche Bildungsfolge, Delta 0 | Vertauschte Gegenfolge |
|---|---|---|
| E1 | A, B, C, D | A, C, B, D |
| E2 | A, C, B, D | A, B, C, D |

Beide haben dieselben Einzelbilder, Haeufigkeiten, vier Positionen,
gleichen Anfang A und Abschluss D. Kein Bild wird ausgelassen oder wiederholt.
Das vorhandene 30-FPS-Profil bleibt bestehen. Technisch gilt ein
Frame-Tick pro Bild: Bildung bei `frame_index` 0 bis 3. Pro Folgeprobe
vier weitere lueckenlose Ticks, beginnend bei 4 und dann 8, 12, 16, 20, 24.
`from_visual_receptor_state` liefert dazu die bestehenden Fenster
`[frame_index, frame_index+1)`. Das ist ein festes synthetisches Zeitraster,
kein gemessener Echtzeitabstand und keine Pruefung von Tempo-Invarianz.

Je Episode genau sechs spaetere Folgeproben in dieser Reihenfolge:
Original 0, Gegenfolge 0, Original -8, Gegenfolge -8, Original +8,
Gegenfolge +8. Der Offset wird einheitlich auf alle Zellen aller vier
Bilder einer Probe angewendet. Kein Clipping, kein lokales Rauschen und
keine wechselnden Offsets innerhalb einer Folge. Bei gleichem Offset
stimmen Histogramme und Gesamthelligkeit der beiden Folgen ueberein.

## 3. Bildung, Quellen und drei Pruefebenen

**Rezeptorfolge:** Jedes Bild wird genau einmal in Empfangsreihenfolge
analysiert. Pruefung von Quellbild, Kanalreihenfolge, Werten und Tickfenstern;
danach unveraendertes `frame_to_b4(..., "B4_SPATIAL")`. Buchstaben,
Episoden-IDs und Sollfolgen duerfen nicht in den 26-Werte-Vektor gelangen.

**Speichererhaltung:** Pro Episode vier echte `_advance_b4`-Uebergaenge.
Der Adapter leitet vor jedem Aufruf den Index allein als validierten
`prestate.accepted_count + 1` ab. Nur der vollstaendig abgenommene Nachzustand
wird fortgesetzt. Er muss genau diesen Zaehler, den neuen Index und die
aktuellen Rezeptorwerte enthalten; vorhandene Eintraege bleiben unveraendert.
Nach vier erfolgreichen Bildungen: vier belegte Plaetze mit eindeutigen
Indizes 1 bis 4, fuenf leere Plaetze, `accepted_count == 4`, keine Verdraengung.
Keine vorbereiteten Endzustaende, kein Index aus Bildlabel, Solltabelle,
Dateinamen oder Recorder. Fehler, Luecken oder doppelte Indizes stoppen.

**Abrufentscheidung:** Nur die entstandene Bank und die vier jetzt
empfangenen Probevektoren werden uebergeben. Die gespeicherte Reihenfolge
stammt ausschliesslich aus `formation_index`, niemals aus `slot_id`,
Containerposition, alten Frame-IDs oder aufgezeichneten Ereignissen.
Probenreihenfolge ist die aktuelle Empfangsreihenfolge; sie wird nicht
nach Inhalt oder Kennung sortiert. Tick-/Quellbelege dienen nur der
Eingabeabnahme, nicht dem Vergleich mit den absoluten Bildungsticks.

Waehrend der Bildung ist ausser der Bank nur der aktuelle Frame erforderlich.
Der spaetere Vier-Vektor-Probeinput ist ein ausdruecklicher, fluechtiger
Abfragepuffer, kein zweiter Langzeitspeicher. Er wird zwischen Folgeproben
nicht als Kontext fortgesetzt. Der Recorder ist eine reine Ausgabesenke;
Solltabellen werden nur ausserhalb der Abruffunktion zum Bewerten verwendet.

## 4. Zwei read-only Entscheidungen auf gleichen Inhalten

Eine gemeinsame Abstandstabelle enthaelt alle 16 Kombinationen aus vier
Probevektoren und vier belegten Speicherwerten. Pro Kombination werden die
bestehenden normalisierten mittleren L1-Distanzen getrennt fuer acht auditive
und 18 visuelle Werte berechnet. Annahme bleibt inklusiv: auditiv `<= 0.2`,
visuell `<= 44/765`; keine neue Sequenzschwelle, Mittelung ueber Positionen
oder nachtraegliche Auswahl. Jeder Probevektor muss unter diesen festen
Grenzen genau einen der vier Inhalte treffen, jeder Inhalt genau einmal.
Andernfalls ist die Voraussetzung isolierter Reihenfolge nicht erfuellt:
als Eingabe-/Aufgabenverletzung ausweisen, keine Schwellenkorrektur.

| Sicht | Entscheidung | Zulaessige Herkunft |
|---|---|---|
| GEORDNET | Alle vier positionsgleichen Paare treffen; Position 1 ist der kleinste gespeicherte Bildungsindex. | Bankwerte, gespeicherte Bildungsindizes, aktuelle Probevektoren in Empfangsfolge |
| REIHENFOLGEBLIND | Es existiert eine bijektive Zuordnung aller vier Probevektoren zu den vier gespeicherten Inhalten. | Dieselben Werte und Abstaende, aber keine Bildungsindizes, Zeit-/Slot- oder Versuchskennungen |

Die reihenfolgeblinde Entscheidung ist unter beliebiger Vertauschung der
Tabellenzeilen und -spalten invariant.
Konkretes endliches Verfahren: alle 24 Zuordnungen der vier Spalten pruefen,
je vier Annahmebits; kein mehrfaches Verwenden desselben Speicherinhalts.
Die gemeinsame Tabelle verwendet technische lokale Spaltennummern, keine
gelernten Labels. Nur GEORDNET erhaelt zusaetzlich die Zuordnung dieser
Spalten zu den gespeicherten Bildungsindizes. Diese Zuordnung erreicht
die blinde Kontrolle nicht. Keine zweite Bank oder weitere Bildung je Sicht.

Zurueckgegeben werden je Sicht nur Annahme/Ablehnung, die zugehoerigen
Einzelabstaende/Annahmebits und Bankdigest vor/nach der Probe. GEORDNET
liefert bei Annahme ausserdem die vier **gespeicherten Originalvektoren** in
Indexreihenfolge; bei Ablehnung keine vervollstaendigte oder korrigierte Folge.
Die blinde Kontrolle liefert nur einen Inhaltsbefund, keine behauptete
Rekonstruktion zeitlicher Ordnung. Tie-Breaker einzelner Treffer duerfen
keine fehlende Eindeutigkeit oder Reihenfolgenentscheidung ersetzen.
Digests werden ausserhalb der Entscheidungsfunktionen an die Befunde
gebunden; sie duerfen insbesondere nicht die verborgene Reihenfolge verraten.

## 5. Begrenzter Umfang und Ressourcen

Vorgesehener Hauptumfang, noch nicht freigegeben:

- Zwei Episoden mit vier Bildungen: **acht B4-Bildungen**.
- Zwoelf Folgeprobeinputs zu je vier Bildern: **48 Probebilder**.
- Zusammen **56 Bildanalysen**, **zwoelf Folgeproben**, **24 read-only Sichtentscheidungen**.
- Neun FIFO-Plaetze und Maximum 255 logische Bankwoerter bleiben unveraendert;
  vier Plaetze belegt. Acht Bildungen kosten 232 funktionale Schreibwoerter.
- Je Folgeprobe 16 AV-Paarvergleiche, je 26 L1-Terme: 416 funktionale Terme.
  Gesamt 4992, von beiden Sichten geteilt und nicht doppelt als Leistung gezaehlt.
  Unabhaengiges Nachrechnen live maximal weitere 4992 L1-Terme.
- Die bestehende Grenze 234 gilt weiterhin je elementarem Probevektor:
  vier Speicherpaare ergeben 104 funktionale plus 104 Validierungsterme,
  zusammen 208. Der **neue Vier-Bild-Aufruf** besteht aus vier solchen
  Zeilen und darf insgesamt 832 inklusive Validierung kosten; nicht als
  alter Einzelaufruf unter 234 ausgeben. Schreibgrenze je Bildung bleibt 293.
- Zusatzarbeit separat: vier positionsbezogene Bitpruefungen fuer GEORDNET;
  24 mal vier fuer REIHENFOLGEBLIND. Beide Sichten haben denselben Zugriff
  auf Inhalte und dieselben Budgetobergrenzen; geringerer Verbrauch bleibt sichtbar.
- Zusaetzlicher fluechtiger Arbeitsbereich: 104 Probe-Werte, 32 Distanzen,
  16 Annahmebits, hoechstens acht Eintragsreferenzen und vier Zuordnungsindizes.
  Keine Kopie der Bildungsfolge ausserhalb der Bank. Bildpuffer (je 28800
  Bytes), Validierung, Digests, Kontrollmittelwerte und Aufzeichnung werden
  separat bilanziert; logische Bankwoerter sind keine Prozess-RAM-Angabe.

Wiederverwenden: Rezeptor/Frameadapter, `_B4State`, `_advance_b4`, L1-Distanz,
eingefrorene Schwellen und lokale Aufzeichnung. Die frueheren Einzelbild-
Recorder `form`/`validate_storage` sind auf genau eine Bildung zugeschnitten
und deshalb **nicht unveraendert fuer vier Bildungen geeignet**. Notwendig
waeren `tools/_visual_sequence_memory_probe.py` und die zugehoerige
`tests/test_visual_sequence_memory_probe.py`. Der geplante private Einstieg
`probe_visual_sequence_read_only(bank, ordered_probe_values)` erhaelt nur
die Bank und vier Vektoren; er bildet die Tabelle einmal, trennt die beiden
Entscheidungen und schreibt keinen Bankzustand. Der Folgeadapter ergaenzt
die erforderliche Uebergangsvalidierung fuer vier echte Bildungen. Bestehende
Kerne, Einzelabrufe, Rezeptorregressionen und Versuchseinstiege bleiben unberuehrt.

Vorgesehen sind acht kleine fokussierte Tests, getrennt vom Hauptumfang:
Indexableitung aus fortgesetztem Zustand; Reihenfolge unabhaengig von
Slot-/Containerordnung und aeusseren IDs; fehlende/doppelte/fremde Indizes;
eingefrorene L1-Grenzen; bijektive inhaltsgleiche Blindkontrolle;
Rueckgabewerte und Unveraenderlichkeit; Quellen-/Ergebnisbindung;
unvollstaendige Aufzeichnung und Einmaligkeit. Keine vorgezogene Ausfuehrung
der Hauptfolgen in diesen Tests und keine pauschale neue Regressionskaskade.

## 6. Auswertung, Grenzen und naechste Entscheidung

Pro Episode und Offset getrennt: Rezeptorabweichungen, Index-/Werteerhaltung,
alle 16 Paarabstaende, beide Entscheidungen, Fehlgleichsetzungen,
falsche Ablehnungen, Rueckgabefehler, Unveraenderlichkeit und Kosten.
Erwartet fuer GEORDNET: sechs Originalfolgen angenommen und sechs
Gegenfolgen abgewiesen, ohne Rueckgabefehler oder Bankaenderung.
Die vertauschten Mittelpositionen duerfen nicht durch gleichen Anfang/Abschluss
oder eine Mittelung verdeckt werden. Nur wenn alle drei Pruefebenen bestehen,
ist der begrenzte technische Reihenfolgeabruf bestaetigt.

REIHENFOLGEBLIND soll alle zwoelf inhaltsgleichen Proben annehmen. Seine
sechs Gleichsetzungen der Gegenfolgen werden vollstaendig, aber **separat
diagnostisch** berichtet, nicht als Fehler eines behaupteten Sequenzabrufs.
Ein Vorteil von GEORDNET waere die erwartbare Nutzung expliziter
Bildungsindizes, kein Beleg eines neuartigen Speichermechanismus.

Fachlich falsche Entscheidungen bleiben Ergebnisse. Verletzte Quellen,
Bildungs-/Indexbindung, unerwartete Mehrdeutigkeit oder unvollstaendige
Aufzeichnung machen die entsprechende funktionale Schlussfolgerung
nicht auswertbar und stoppen den Versuch; keine automatische Wiederholung,
Teilfortsetzung oder Anpassung. Quellen, Eingaben und Konfiguration vor
Beginn binden; spaetere Belegpruefung ohne erneute Rezeptor-/Speicheraufrufe.

Nicht enthalten: automatische Segmentierung, variable Folgenlaenge,
wiederholte mehrdeutige Einzelzustaende, Zeitmasslernen, Tempo-Invarianz,
Vorhersage, FIFO-Ueberlauf, Langzeitverdichtung, Semantik oder Feldwirkung.
Die extern festgelegte Vierergrenze ist keine selbst erkannte Episode.
TSPM-1, PPB-1, API und Snapshot bleiben unveraendert. Alte Matrix-, Plattform-,
Kalibrierungs- und Ortsstruktureinstiege bleiben gesperrt.

Naechste konkrete Entscheidung: begrenzte private Umsetzung plus acht
fokussierte Tests und bei deren Bestehen genau dieser Hauptumfang. Dieser
Plan selbst erteilt **keine** Implementierungs- oder Ausfuehrungsfreigabe;
keine zusaetzliche allgemeine Vertragsaudit-Kaskade.
