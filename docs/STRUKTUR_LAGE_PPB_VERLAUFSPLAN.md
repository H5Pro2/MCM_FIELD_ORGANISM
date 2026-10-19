# Minimaler direkter PPB-Prototypverlauf

Nur Planung. Keine Quellenregeneration, Rechnung, Tests oder Ausführung.
Die abgeschlossenen Struktur-/Lage- und PPB-Paarvergleiche bleiben unverändert.
Kein Fast-, B4-, Kontext-, Feld- oder Runtimeversuch. Gates False.

## Frage und feste Folgen

Ändert die produktive Prototypfortschreibung eine zuvor anhand der
Quellenpaare beobachtete Zuordnung? Verwendet werden ausschließlich die
vollständigen gespeicherten Rohvektoren q01…q06 aus
`reports/s2oe/structure-location-comparison-20260912-01/record.json`.
Quelle, Zeit, Payloadherkunft und Ergebnisverifikation bleiben gebunden.
Keine Formvektoren und keine manuelle Anfangsbefüllung.

| Kontrolle | Folge | Prüffrage |
| --- | --- | --- |
| K1 akzeptierte Lage | q04 → q05 → q06 | Nach B/P0→B/P1: passt B/P2 noch zum tatsächlich aktualisierten Prototyp? |
| K2 ausgeschlossene Lage | q01 → q02 → q03 | A/P1 passt nicht zu A/P0: Welche echte Spur wird bei A/P2 gewählt und fortgeschrieben? |
| K3 Strukturänderung | q01 → q03 → q04 | Nach akzeptiertem A/P0→A/P2: bleibt B/P0 gegenüber dem aktualisierten Prototyp ausgeschlossen? |

H0 bleibt der einzige Hintergrund: H1 liefert im vorhandenen Rohvergleich
keine zusätzlichen Paarentscheidungen und wird nicht wiederholt. Jede Folge
ist eine vorab festgelegte aufsteigende Teilfolge des Quellenplans; keine
Umordnung. K1, K2, K3 werden in dieser administrativen Reihenfolge verarbeitet,
aber jeweils aus einem eigenen regulären leeren PPB-Zustand. Das ist ein
kontrollierter Vergleich dreier Geschichten, keine fortlaufende Gesamtmemory.
Alle neun Übergaben sind eigenständig; wiederverwendete gespeicherte Werte
sind keine neuen unabhängigen Wahrnehmungsbelege.

Die ursprüngliche Quellenliste ist keine bereits beobachtete zeitliche
Korrespondenz. Ihr aufsteigender Zeitbezug wird hier lediglich eingehalten.
Keine Exaktkopien q13/q14 und keine zusätzlichen Wiederholungen zur Stabilisierung.

## Unveränderte produktive Regel

`mcm_field_organism/_ppb1_reference.py::initial_ppb1_bank_state` und
`advance_ppb1_bank` verwenden. Bestehende visuelle Profilkonfiguration aus
`tools/_s2jw_default_live_profile.py`: vier Slots, Grenze 0,01 inklusiv,
Updatefaktor 0,05, stabil ab Support 3, Ablauf nach 64 akzeptierten Schritten.
Geometrie, Carrierreihenfolge und Bankbindung aus der bestehenden visuellen
Konfiguration übernehmen, nicht frei nachbilden.

Auswahl: nach Ablaufprüfung alle belegten Slots mit fsum-L1/288 prüfen;
unter Treffern kleinstes (Distanz, Slot-ID). Ohne Treffer kleinste freie
Slot-ID, sonst ältester last_selected_step mit Slot-ID als Tie-Break.
MATCHED schreibt pro Komponente genau
`(1.0-update_rate)*previous + update_rate*current` fort; Support wird
`min(stable_after, support+1)`. CREATED/REPLACED übernimmt Eingabewerte und
Support 1. Keine Toleranz oder Änderung dieser Binary64-Reihenfolge.

Drei separate technische Kontaktuhren, konstant innerhalb jeder Folge:
`structure.ppb.k1`, `structure.ppb.k2`, `structure.ppb.k3`.
Quellindex i und ursprünglicher rationaler Zeitpunkt i/30 bleiben erhalten.
Versionierte Kontaktbindung: `[i,i+1)` in Ticks von 1/30 Sekunde, ohne
Umnummerierung ausgelassener Quellen. Dies ist die technische Fensterzuordnung
eines gespeicherten Bildzustands, keine nachträglich gemessene Belichtungszeit.
Die notwendige neue Bindung ist vor einem späteren Aufruf neutral abzusichern.

## Was bereits feststeht, was offen bleibt

Die erste Aufnahme jeder Folge muss den regulären CREATED-Weg nehmen.
Der zweite Schritt von K1 beziehungsweise K3 besitzt gegenüber seiner
unveränderten ersten Spur einen bestätigten Paar-Match. K2/q02 hat gegenüber
q01 keinen Paar-Match; es gibt dann noch freie Kapazität. Diese Erwartungen
sind fachliche Kontrollen, keine Vorbedingungen für den dritten Schritt.

Der dritte Schritt wird jeweils gegen den tatsächlichen Vorzustand geprüft.
Nicht aus Generatorrollen oder einer gewünschten Stabilisierung ableiten,
welche Spur gewählt wird. Alle Kandidatendistanzen, Matchmengen, ausgewählte
Slotbindung, event, Support, stable, Zeit und Prototypwerte vor/nach erhalten.

Support und Prototypänderung getrennt berichten. Eine Angleichung kann
bitgleich bleiben; das ist nicht automatisch ausgebliebene Verarbeitung.
In drei Schritten ist Support 3 höchstens erreichbar, nicht garantiert.
**Ein weiteres MATCHED nach bereits gesättigtem Support wird nicht geprüft.**
Die unveränderte Sättigungsformel wird statisch gebunden, ihre allgemeine
Qualifikation nicht wiederholt. Keine Behauptung neuer Nachsättigungsdeckung.

Mit höchstens drei Aufnahmen aus leerer Vier-Slot-Bank sind Ersetzung und
Ablauf statisch nicht erreichbar. Beide bleiben ausdrücklich ungeprüft.
Ein REPLACED wäre hier keine gewünschte Alternative, sondern ein zu klärender
Widerspruch zu Kapazität und Ausgangszustand. Keine Druckquellen ergänzen.

## Vorhandene Anschlüsse und kleine Lücke

Die Quellenauflösung und Identitätsprüfung aus `_structure_ppb_table.extract`
kann wiederverwendet werden. Sie macht keine Rezeptoraufrufe.
`_s2oe_visual_transition_diagnostic.table` erzeugt bereits vollständige
Kandidatentabellen. Dessen `verify` prüft unabhängig Auswahl, Support und
Prototypupdate aus gespeichertem Vorzustand und Eingang. Seine derzeitige
Extraktion ist an e03/e04 gebunden und darf nicht zum neuen Haupteinstieg
umetikettiert werden.

Erforderlich ist nur ein kleiner Binder für drei direkte PPB-Ketten:
gespeicherter Vektor → profilgebundener Kontakt → produktiver Übergang →
bestehende Kandidatentabelle → unabhängige Übergangsprüfung. Die bisherige
Diagnostik erwartet Herkunfts-/Generationsfelder; diese aus tatsächlicher
Neubelegung und Übergangsfolge ableiten, nicht aus K1/K2/K3-Rollen.
Keine neue Recorderplattform; vorhandene atomare Datei-/Fehlerbelege und
verlustfreie Zustandshüllen verwenden. Fachliche Auswertung erst nach
vollständigem technischem Abschluss und einmaliger read-only Gesamtprüfung.

## Arbeits- und Fehlerbudget

Vorläufige feste Obergrenzen für eine spätere Anschlussfreigabe:

- Drei Initialisierungen, neun produktive PPB-Übergänge; null Rezeptoraufrufe.
- Je Geschichte maximal 0, 1, 2 belegte Kandidaten vor den drei Schritten:
  insgesamt höchstens neun Distanzprüfungen pro Rechenweg, 36 Slotstatusprüfungen.
- Produktive Fortschreibung höchstens 2.592 Differenzen. Bestehende
  Diagnosetabelle höchstens 5.184, weil sie explizite Terme und den produktiven
  Distanzhelfer getrennt berechnet. Read-only Prüfung separat höchstens 2.592.
  Zusammen höchstens **10.368 Differenzen**, nicht als neun Einzelaufrufe versteckt.
- Höchstens sechs MATCHED-Updates: je produktivem beziehungsweise unabhängigem
  Updateweg 1.728 Komponenten mit zwei Multiplikationen und einer Addition.
  Kein zusätzlicher Replay des produktiven Übergangs bei Verifikation.
- Drei Anfangszustände und neun Nachzustände vollständig speichern, Folgeschritte
  referenzieren den vorherigen Zustand. Lokal höchstens 40.960 Byte je Zustand,
  ohne Erhöhung der bestehenden 98.304-Byte-Grenze. Zwölf Zustände: 491.520 Byte.
- Innerhalb des Gesamtbelegs zusätzlich Kandidatentabellen 196.608 Byte,
  Eingangs-/Herkunftsbelege 65.536, übrige Übergangsfelder 32.768 Byte.
  Das sind 786.432 Byte innerhalb maximal 1.048.576 Byte Gesamtbeleg.
- Alternativer Fehlerabschluss darf einen vollständigen Teilbeleg bis
  1.048.576 Byte zusätzlich zum schon veröffentlichten Gesamtbeleg erhalten.
  Primärfehler, Phase und erreichte Übergänge ungekürzt sichern; keine
  fachliche Teilauswertung oder Wiederholung.
- Gemeinsam: aktive Nichtmetadatenreferenzen maximal 1.310.720 Byte,
  Ergebnis plus mögliche Teilhülle 2.097.152, Verifikation 262.144,
  sämtliche Metadaten einschließlich Referenzen/Qualifikation/Bericht/Fehler
  98.304: maximal **3.768.320 / 4.194.304 Byte**. Tatsächliche Dateiinventare
  müssen vor einem späteren Test separat konkret passen; keine historische
  Datei verschwindet allein durch Referenzierung aus ihrer Klasse.

Dies sind statische Planobergrenzen, keine gemessene Ausgabehülle. Noch offen
ist die reale neutrale Hüllengröße des kleinen neuen Kontakt-/Kettenbinders.
Seine spätere neutrale Zusatzarbeit muss separat vorgebunden werden und darf
nicht nachträglich dem realen Neun-Schritt-Budget zugerechnet werden.

## Aussagegrenze

Ein Befund kann zeigen, ob genau diese Prototypupdates die Paarzuordnung
verändern. Er belegt weder vollständige Fast-/Memoryerhaltung noch Abruf,
Objektidentität oder eine Lernbindung. Keine Formintegration, Schwellenwahl,
weiteren Varianten oder automatische Folgeausführung. Jetzt endet der
Auftrag mit der Planung; alle neun Übergänge bleiben unausgeführt.
