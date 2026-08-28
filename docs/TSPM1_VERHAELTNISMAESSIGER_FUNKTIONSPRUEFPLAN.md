# TSPM-1: begrenzter funktionaler Pruefplan

Stand: 28.08.2026. Dokumentierte Strategieaenderung, kein Lauf und keine
Implementierungs- oder Ausfuehrungsfreigabe. Grundlage ist die
[Bestandskonsolidierung](BESTANDSKONSOLIDIERUNG_NACH_PLATTFORMSTOPP.md).
Der geschlossene Supervisor-/Child-Plattformpfad bleibt geschlossen.
S2-FC und die bisherige 56-Zellen-Matrix bleiben gesperrt. Dieser Plan
betrifft denselben fachlichen Vergleich, keinen umbenannten Ersatzlauf.

## Ziel und Aussagegrenze

Geprueft werden Aufnahme, Erhaltung, Aktualisierung, Konsolidierung und
read-only Abruf verdichteter auditiver und visueller Zustaende. Ein bekanntes
Verfahren darf die geeignete technische Speicherloesung sein. Gleichwertigkeit
ist eine Engineeringeinordnung, kein automatischer Stopp der Entwicklung.
Semantik, innerer Kontext, Feldrueckwirkung, API und Snapshot bleiben ausserhalb.

Der Versuch soll beantworten, welche dieser Funktionen TSPM-1 im festen
Aufgabenpaket erfuellt und welchen Nutzen seine zweite Speicherebene gegenueber
einfacheren Verfahren hat. Er prueft keine neue MCM-Feldursache.

## Fester Umfang

Unveraendert gelten die Werte, Zeitlagen, Konfigurationen und Operatorregeln
aus [S2-DQ](S2DQ_TSPM1_STATISCHER_KORREKTUR_UND_VERGLEICHSMATERIALISIERUNGSVERTRAG.md).
Fuer funktionale Bewertung und Operationszaehlung hat
[S2-EE, Abschnitte 1 bis 3](S2EE_TSPM1_STATISCHER_KORREKTUR_UND_AUSFUEHRUNGSBINDUNGSVERTRAG.md)
Vorrang vor den aelteren architekturabhaengigen Kriterien.

| Geschichte | Geordnete Bildung | Read-only Proben nach Bildungsschritt |
| --- | --- | --- |
| H1 | AX | 1: AX |
| H2 | AX, AX, AX, AX | 1: AX; 4: AX |
| H3 | AX, AX, AX, AX, D1, D2, D3, D4, D5, D6, D7, D8 | 12: AX |
| H4 | AX, AX, AX, AX, AY, BX | 6: AX, AY, BX |
| H5 | AX, AX, AX, AX, P2, P3, P2, P4 | 8: AX, P4 |
| H6 | AX, AX, AX, AX, D1, D3, D8 | 7: AX, D1, D3, D8 |
| H7 | AX, AX, AX, AX | 4: AX, NEAR, PARTIAL_OUT, OUTSIDE, FAR |

Acht Arme bleiben erhalten: `TSPM1`, `B0` (ohne Speicher), `B1_DIRECT`
(PPB-1 direkt), `B1_BUDGET_MATCHED` (PPB-1 an Konsolidierungsindizes), `B2`
(adaptive Online-Prototypbank), `B3` (Nachhall), `B4` (kurzfristiger FIFO)
und `R0` (unabhaengige generische Zwei-Ebenen-Kontrolle).
Das sind **56 Zellen, 336 Bildungsangebote und 144 Proben**; pro Arm
42 Angebote und 18 Proben. B1_DIRECT nutzt alle 42, B1_BUDGET_MATCHED die
bereits gebundenen 19 Schreibindizes je Modalitaet. Keine Zusatzangebote.

Jede Zelle beginnt frisch; nur innerhalb ihrer Geschichte wird Zustand
fortgesetzt. Jeder Schritt ruft den echten Bildungsoperator auf, danach
gegebenenfalls die echte Probe. H2/1 veraendert insbesondere nicht H2/4.
Vorbereitete Endzustaende, Ergebnisvorlagen, Probeinput als Abrufpayload und
synthetisches Replay zur Konsolidierung sind ausgeschlossen. Die Protokollierung
darf Zustandsketten aufzeichnen, sie aber keinem Arm als Zusatzspeicher zufuehren.
H3-Ablauf, H4-Konflikt, H5-Verdrangung, H6-Kapazitaetsfall und alle negativen
H7-Proben werden weder entfernt noch nach dem Ergebnis angepasst.

## Funktionsbewertung

Jede Probe berichtet nativen Abruf, tatsaechlich ausgewaehlte AV-Werte,
Herkunft im Zustand sowie getrennte auditive und visuelle Sollabweichung.
Sollwerte kennt nur die Auswertung. Positive Faelle sind korrekt bei positivem
Abruf und normalisierter mittlerer L1-Abweichung von hoechstens 0.2 je
Modalitaet; negative Faelle nur bei verweigertem Abruf. NEAR erwartet AX;
PARTIAL_OUT, OUTSIDE und FAR in H7 erwarten keinen Abruf.

| Kennzahl | Unveraenderte funktionale Bedingung |
| --- | --- |
| P1, fruehe Aufnahme | H1/1/AX korrekt |
| P2, Erhaltung | H3/12/AX korrekt |
| P3, Konflikt und Erhaltung | H2/4/AX sowie H4/6/AX, AY, BX korrekt; ausgewaehlte AX-Werte zwischen H2 und H4 exakt gleich |
| P4, Kapazitaetsverhalten | H5/8/AX, P4 sowie H6/7/AX, D1, D3, D8 korrekt |
| P5, Selektivitaet | Alle fuenf H7-Proben korrekt |

Zusaetzlich: alle 18 Einzelentscheidungen, Fehlzuordnungen, verfehlte Abrufe,
numerische Abweichungen, funktionale Schreibkosten und H2-Aufnahmelatenz.
Letztere ist nur bei Schritt 1 oder 4 beobachtet; sonst `NOT_OBSERVED`
mit historischem Rangwert 5. Keine erfundene Messung bei Schritt 2 oder 3.
Fast-/Slow-Abruf, Aktualisierung, Ablauf, Konsolidierung und Verdrangung sind
getrennte technische Diagnosen. Flags, Digestwechsel oder zwei Speicherebenen
geben keine Funktionspunkte. Eine Baseline darf ohne Verdrangung erfolgreich sein.

Auswertungsreihenfolge: vollstaendige Aufzeichnung, methodische Gueltigkeit,
dann Einzelbefunde und P1-P5, zuletzt Engineeringvergleich. Quell-, Owner-,
Budget- oder R0-Abweichungen machen den Vergleich methodisch ungueltig.
R0 muss weiterhin die vollstaendige gebundene Projektion erklaeren, einschliesslich
Bank-, Konfigurations- und Slotidentitaeten. Eine Abweichung ist kein Vorteil.
Ein fachlich falscher Abruf wird dagegen gezaehlt; er beendet nicht die Erhebung.

Die S2-EE-Rangfolge bleibt nachvollziehbar: Anzahl erfuellter P-Kriterien,
Fehlersumme, Aufnahmelatenz, Schreibsumme, zuletzt ASCII-ID zur Berichtssortierung.
Ein Gleichstand ist kein TSPM-1-Vorteil. Fuer die Engineeringwahl gilt ergaenzend:
Bei gleichem funktionalem Profil aller 18 Korrektheitsentscheidungen, gleicher
AX-Erhaltung und gleicher beobachteter Latenz wird die Loesung mit weniger
Schreibarbeit, danach kleinerem deklarierten Speicherbedarf bevorzugt.
Bei weiterem Gleichstand hat eine einzelne Speicherebene Vorrang vor zwei Ebenen.
Numerische Abruffehler bleiben sichtbar; ihre Gleichheit wird damit nicht behauptet.
Bei unterschiedlichen Profilen werden Zielkonflikte berichtet, kein universeller
Sieger aus einer Gesamtpunktzahl behauptet. Fehlende P-Kriterien begrenzen die
Eignung im Aufgabenpaket, widerlegen aber nicht jede technische Speicherfunktion.

## Ressourcen und Aufzeichnung

Verbindlich bleiben maximal **269 logische 64-Bit-Woerter**, **293 funktionale
Schreibwoerter je Bildung**, **234 L1-Koordinatenterme je Bildung oder Probe**
einschliesslich Validierungsarbeit und **null funktionale Probeschreibwerte**.
Kleinere Armkapazitaeten bleiben unveraendert; keine Saldierung zwischen Schritten.
Die externe Sollauswertung zaehlt ihre maximal 26 Terme je Probe gesondert.
Grenzen und Verbrauch bleiben getrennt; Ueberschreitungen lehnt unveraendert
`validate_s2dr_cell_result` relational ab. 269 Woerter sind kein Python-RAM-Limit.

Der spaetere lokale Ablauf ist sequenziell, in einer ausdruecklich autorisierten
Projektumgebung, ohne neue Supervisor-, Bootstrap- oder Plattforminfrastruktur:

1. Vor dem ersten Zustandsaufruf: Freigabereferenz und einmalige Lauf-ID binden;
   exklusives Versuchsverzeichnis ohne Ueberschreiben anlegen. Manifest mit
   tatsaechlichen Quellbytes/SHA-256, Git-Stand samt Abweichungen, Runtimeversion,
   Abhaengigkeiten, Konfigurationen, Fixtures, Armregeln und Auswertungsversion
   schreiben. Hashes belegen Identitaet, keine unabhaengige Runtime-Abnahme.
2. Zellen in H1-H7-/Armreihenfolge bilden und pruefen. Vollstaendige Ereignis-,
   Zustands-, Probe-, Kosten-, Owner- und Receiptbelege je Zelle zuordnen.
   Fehlerprotokoll einschliesslich leerem Fehlerbestand fuehren. Jeder Befund
   bindet Lauf-ID, Zellplan, Quellen, Konfiguration sowie Vor- und Nachzustand.
3. Nach allen Zellen den vollstaendigen Comparator anwenden. Fehler im technischen
   Ablauf stoppen sofort; vorhandene Teilbelege bleiben erhalten. Keine noch
   ausstehende Zelle und kein fehlender Befund wird durch eine Vorlage ersetzt.
4. Einzeldateien vollstaendig schreiben, dateibezogen flushen und schliessen;
   Ergebnisindex temporaer im selben Verzeichnis schreiben und atomar veroeffentlichen.
   Eine lesende Dateipruefung kontrolliert Schema, Hashes, Referenzen, eindeutige
   56 Zellen, 336 Angebote, 144 Proben und vollstaendigen Abschluss. Keine neuen
   Modellaufrufe fuer die Pruefung. Terminalstatus und Exit-Code werden mit erfasst.

`COMPLETE` erfordert vollstaendige, widerspruchsfreie Dateien und einen belegten
normalen Abschluss. Blosse Lesbarkeit reicht nicht. Fehlender Abschluss, defekte
Datei oder Aufzeichnungsfehler bedeutet `NOT_EVALUABLE`, unabhaengig von Teilwerten.
Ein vollstaendig protokollierter Methodenfehler bleibt `METHOD_INVALID`.
Nur bei vollstaendiger und methodisch gueltiger Erhebung wird Funktion bewertet.
Keine Zusicherung von Persistenz nach Stromausfall oder beliebigem Prozessverlust.

Verstrichene Laufzeit und verfuegbarer Prozessspeicher-Hoechststand werden separat
als Betriebsdaten erfasst, nicht als funktionales Budget. Nicht verfuegbare
Speichermessung wird `NOT_MEASURED`, nicht null. Eine bedienerseitige Unterbrechung
ist zulaessig und macht den Versuch ohne vollstaendigen Abschluss nicht auswertbar;
eine garantiert begrenzte native Blockierung wird nicht behauptet.
**Keine automatische Wiederholung oder Teilfortsetzung.** Ein weiterer Versuch
benoetigt dokumentierte Ursache und ausdrueckliche neue Freigabe, neue Lauf-ID
und frische Anfangszustaende fuer alle Zellen. Keine Auswahl guter Teilresultate,
kein Loeschen eines Fehlversuchs und kein stilles Nachjustieren von Parametern.

## Ersetzte Ausfuehrungsanforderungen

Diese Aenderungen gelten fuer den hier geplanten Funktionsversuch, nicht als
nachtraegliche Abnahme alter Belege oder Freigabe des alten Publishers:

| Bisherige Eingangsvoraussetzung | Verhaeltnismaessiger Ersatz |
| --- | --- |
| S2-FC, S2-EM und erfolgreiche abhaengige Plattformbelege vor jedem Vergleich | Keine Voraussetzung dieses Funktionsversuchs; der betreffende Pfad bleibt geschlossen beziehungsweise gesperrt |
| Volume-Zugriff/-Flush, unabhaengiger nativer Layout-/Bootstrap-/Ownernachweis vor erstem Read | Autorisierte lokale Ausfuehrung, gebundene Quellen/Runtime und nachvollziehbare Lauf-/Zellowner; keine erhoehten Rechte |
| Unabhaengiger Starter, Abschlussbeobachter und Supervisor-/Child-Huelle | Ein lokaler sequenzieller Runner und nachpruefbare Ergebnisdateien; kein unabhaengiger Plattformnachweis behauptet |
| Dauerhafte globale Einmaligkeit auch nach beliebigem Verlust oder Reload | Exklusiver Versuchspfad und Einmalverbrauch je expliziter Freigabe; Wiederholung nur nach neuer Entscheidung, keine manipulationssichere globale Garantie |
| Universelle Zeit-, Handle-, Import- und Prozessspeichergarantie als Starttor | Bestehende funktionale Kostenlimits; Laufzeit/RAM separat beobachten; Abbruch ohne Abschluss nicht auswertbar |
| Dauerhafte Crash-/Stromausfallgarantie fuer Abschluss und Publikation | Vollstaendige Dateien, Datei-Flush/Close, atomarer Ergebnisindex und lesende Integritaetspruefung im normalen Betrieb |
| Infrastrukturverlust als unspezifischer negativer Versuchsabschluss | Explizit `NOT_EVALUABLE`, ohne Aussage gegen die Speicherfunktion |

## Eng begrenzte Umsetzung nach Freigabe

Wiederverwendet werden unveraendertes PPB-1 und TSPM-1, die Registry, reale
Initialisierung/Bildung/Probe, B0-B4, unabhaengige R0-Zustaende, Operationszaehler,
relationale Zellvalidatoren sowie vollstaendige Projektion und P1-P5-Auswertung aus
[`_tspm1_s2dr_private_comparison.py`](../mcm_field_organism/_tspm1_s2dr_private_comparison.py).
`S2DRCellOwner.consume_once` bildet bereits echte geordnete Zustandsfolgen.

Notwendig sind genau drei fachlich begrenzte Dateiarbeiten:

- Bestehendes `_tspm1_s2dr_private_comparison.py`: funktionale Aggregation von der `_S2EFAttempt`-Abnahme trennen, alte Eintrittssperre erhalten.
- Vorgesehenes `tools/_tspm1_functional_study.py`: privater lokaler Runner und lesende Ergebnispruefung; Ablage unter `reports/tspm1_functional/<lauf-id>/`.
- Vorgesehenes `tests/test_tspm1_functional_study.py`: acht fokussierte Tests der geaenderten Grenzen.

Diese neuen Dateien und Ergebnisverzeichnisse werden jetzt nicht angelegt. Keine Aenderung an
Speicherkernen, Parametern, Fixtures oder Feldpfad. Neue Quellen und Ergebnisse
erhalten eigene Versions-/Digestbindungen; alte Hashbelege werden nicht umgedeutet.
Der bisherige gesperrte Einstieg und `_EXECUTION_RELEASE_ENABLED = False` bleiben
erhalten. Kein Dummy-Attest, kein Ersatz-Plattformbeleg und keine Verwendung der
geschlossenen Plattformmodule. Auch der neue Einstieg darf dieselben 56 Zellen
erst nach ausdruecklicher Freigabe dieses geaenderten Ausfuehrungsprotokolls starten.

Vorgeschlagenes Qualifikationsbudget: acht fokussierte Tests, noch nicht freigegeben:
echte Miniatur-Bildung vor Probe; frischer Zellzustand/read-only Probe;
neutrale Sollauswertung und Gleichstand; ungueltige vollstaendige R0-Projektion;
Budgetueberschreitung einschliesslich Validierungsarbeit; unvollstaendige oder
beschaedigte Aufzeichnung; doppelte Laufnutzung/kein Retry; weiterhin gesperrter
Alt-Einstieg und Ausschluss geschlossener Plattformmodule. Nur kleine synthetische
Fixtures, keine H1-H7-Zelle und keine versteckte Vollmatrix als Qualifikationstest.
Vorhandene Testbelege bleiben historisch; keine pauschale Gesamttestwiederholung.

Verbleibende Entscheidungen sind konkret: erst die drei Dateiarbeiten und die
acht fokussierten Tests freigeben; danach anhand deren Befund genau einen
56-Zellen-Funktionslauf mit diesem Aufzeichnungs- und Wiederholungsprotokoll
freigeben oder stoppen. Keine weitere allgemeine Vertragsaudit-Kaskade.
Ein neuer sachlicher Widerspruch wird benannt, nicht durch Umbenennung umgangen.

## Danach: Qualitaet der Wahrnehmungsrepraesentation

Die jetzigen 8 auditiven und 18 visuellen Traegerwerte wiederholen je Modalitaet
einen konstanten Skalar. Es variieren nur zwei unabhaengige Werte; raeumliche
Struktur, abgestufte Merkmalsverteilungen oder reichhaltige zeitliche Muster
werden damit nicht geprueft. Auch ein vollstaendiger Speichererfolg loest diese
konzeptionelle Frage nicht. H1-H7 prueft insbesondere keine kontinuierliche
Merkmalsdrift und erlaubt keine statistische Generalisierung aus einem Lauf.

Nach dem Funktionsbefund ist gezielt zu entscheiden, welche Information der
bestehende Rezeptorpfad fuer den Zweck erhalten muss: abgestufte Merkmale,
Nachbarschaft/Anordnung oder Reihenfolge zeitlicher Uebergaenge. Eine spaetere
Pruefung sollte gleiche Einzelwerte bei unterschiedlicher Anordnung beziehungsweise
Reihenfolge sowie kontrollierte Merkmalsabstufungen unterscheiden koennen.
Das bleibt eine offene Folgeaufgabe, keine neue Mechanik oder Ausfuehrung dieses Plans.
