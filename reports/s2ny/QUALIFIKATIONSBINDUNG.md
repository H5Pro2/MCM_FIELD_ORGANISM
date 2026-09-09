# S2-NY: einmalige rezeptorfreie Quellenqualifikation

Vor dem Testaufruf gebunden; kein Funktionslauf und keine Vorabmaterialisierung.
Qualifikations-ID: `s2ny-source-binding-qualification-20260909-01`.
Genau ein Aufruf von `python -m reports.s2ny.qualify_once` aus dem Workspace,
darin genau ein `unittest -v -f`, 24 Testgruppen, kein Retry.
Pruefinventar und alle Quellhashes werden vor dem Unterprozess gespeichert.

## Festes Inventar

01 Quellenfolge/Identitaet; 02 native Zeiten; 03 Exaktrezepte/getrennte Quellen;
04 Phasen/Nullpartialposition; 05 Gruppen-/Gain-/lokale Zeitfolge;
06 einmalige Float32-Rundung; 07 Renderergrenzen; 08 unabhaengige Vollbindung;
09 Quellen-/Zeitmanipulation; 10 Reihenfolge/Zaehler; 11 Zukunfts-/Fehlerstellen;
12 LOCAL-Stellen/Reset; 13 funktionale Metadatenabschottung;
14 zwanzig Kriterien/absolute MAE und Gewinne/W nicht garantiert;
15 Ressourcen/Zaehler; 16 Unveraenderlichkeit/Evaluationswurzel;
17 Built-in-math; 18 neutrale Freeze-Payloads; 19 Ergebnis-/Pruefbindung;
20 Freeze-Phase/Profil; 21 vertauschte Historien/Statebindungen;
22 geschlossene Nachfolgebindung/Importmanipulation;
23 historischer read-only Import und vollstaendige Metadatenhuellen;
24 ausgeschlossene Imports/Aufrufe/Gates.

## Grenzen und Aussage

NY-Fenstererzeugung und historische `pcm_window`-Einstiege sind in allen
Testkoerpern durch Aufrufsperren ausgeschlossen. Nur sechs neutrale Samples
(24 Byte insgesamt, maximal 12 Byte je Payload) in den Tests 05/06;
hoechstens 32 Sinusaufrufe und 32.768 Metadaten-Digestpruefungen.
Keine Rezeptor-, NJ-, Lern-, Empfehlungs-, LOCAL-, Fehler- oder Systemrechnung.
Historische NX-Ergebnis-/Verifikationsdateien werden nur fuer Bindung und
Freeze-Extraktion gelesen; keine Trainings- oder Prognoserechnung.

Metadaten je Wurzel/Vorregistrierung maximal 65.536 Byte, Freeze-Payload
4.096 Byte. Spaetere Funktionsbudgets nur als Metadaten, unveraendert nach
NY-Plan. Die acht W-Bedingungen sind offene Verlustprognosen, keine Startgates.
Empfehlung und LOCAL nutzen dieselbe skalare Struktur mit unterschiedlicher
Erfahrungsbasis: absolute MAE und Gewinne muessen spaeter sichtbar bleiben;
strikte Binary64-Vorteile belegen keine allgemeine Robustheit. Keine Toleranz.

Nur bei 24/24 ist genau `s2ny-source-preseal-20260909-01` freigegeben:
30 Fenster einmal erzeugen, ein Live-Payload, keine Rohdaten speichern.
Danach genau eine read-only Bindungspruefung ohne PCM-Regeneration.
Diese prueft Quellen-/Zeit-/Wurzel-/Freeze-Bindungen, nicht numerische
Rezeptorgueltigkeit oder kausale Empfehlungsausfuehrung. Formeln und Budgets
sind gemeinsame feste Metadaten; Quellen und Stellen werden im Verifikator
unabhaengig rekonstruiert. Keine historische NX-Neuverifikation.
Hauptgate `False`, ME/MI gesperrt. Jeder Fehler beendet den freigegebenen Pfad.
