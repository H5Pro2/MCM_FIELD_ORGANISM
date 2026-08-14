# Z1: technischer F3/B3-Mehrarmrunner

Stand: 2026-08-06

> **Aktueller Status:** Dieses Dokument beschreibt die technische Freigabe
> vor der Ausfuehrung. Der reale Runner wurde inzwischen genau einmal in
> [Lauf 195](forschung/LAUF_195_Z1_FELDTRAJEKTORIEN_KOVARIANZAUDIT.md)
> aufgerufen.

## Status

Der gebundene Z1-Mehrarmrunner ist implementiert und seine Orchestrierung ist
technisch geprueft. Die reale F3/B3-Paketfunktion wurde nicht aufgerufen. Es
liegen keine Z1-Feldmesswerte, keine Forschungsentscheidung und kein Lauf 195
vor.

## Implementierter Ausfuehrungsplan

`mcm_field_organism/mcm_f3_z1_runner.py` bindet:

```text
2 Mechaniken:
F3-Kandidat und lineare gekoppelte B3-Feldbaseline

7 Quellenarme:
Referenz, technische Teilung, Dehnung, Kompression,
Umkehrung, Blockpermutation und unabhaengige Kontrolle

4 Aufgaben je Mechanik und Quellenarm:
n, 2n, 4n und unabhaengige 4n-Reproduktion

Gesamt:
2 * 7 * 4 = 56 eindeutige Aufgaben
```

Jede Aufgabe startet aus demselben neutralen gemeinsamen Layer. Der
Startzustand wird ueber dessen vorhandenen Layer-Digest gebunden. Ein
Snapshot wird vor dem ersten Rezeptorabschluss nicht kuenstlich erzeugt.

## Handoff-Kontrollen

Die Vorbereitung prueft fuer jeden der sieben Arme ohne Feldfortschreibung:

- keine Abschluesse vor oder am Start;
- keine Abschluesse hinter dem Horizont;
- jedes reduzierte Ereignis genau einmal zugeordnet;
- zugeordnete Ereigniszahl entspricht dem festen Armvertrag;
- Vorschlagsschritte decken den Armhorizont lueckenlos.

Alle sieben Handoffs bestehen diese statische beziehungsweise technische
Vorbereitung.

## Technisches Paket

Die noch nicht aufgerufene Funktion
`execute_mcm_f3_z1_technical_packet()` wuerde fuer jede Aufgabe liefern:

- vollstaendige passive S/H/M-Trajektorie;
- finalen Snapshot-Digest nach erfolgter Feldfortschreibung;
- Anzahl der Integrationsdiagnosen;
- maximalen Massenerhaltungsfehler;
- minimale lokale Masse;
- maximale absolute S- und H-Auslenkung.

Das Paket prueft nur:

- feste Quellenvertraege;
- vollstaendige Handoffs;
- bitgleiche 4n-Reproduktionen;
- Massen- und Wertebereiche;
- abnehmenden finalen n/2n/4n-Fehler.

Es besitzt absichtlich weder `run_id` noch `research_decision` und schreibt
keine Ergebnisdatei.

## Technische Pruefung

Die 56-Aufgaben-Orchestrierung wurde mit einem kontrollierten Ersatz-Executor
getestet. Dadurch wurden Aufgabeninventar, Reproduktionspaarung,
Kontrollaggregation und die Abwesenheit einer Forschungsentscheidung
geprueft, ohne F3- oder B3-Felddaten zu erzeugen.

Gemeinsam mit Quellen-, Observer-, Metrik- und bestehenden F3-Tests bestehen
38 fokussierte Tests. Paketimport, oeffentliche API und Python-Kompilation
sind ebenfalls geprueft.

## Aussagegrenze

Die technische Existenz des Runners ist kein Befund zu Teilungsinvarianz,
Zeitkovarianz, Ordnungssensitivitaet oder relativer Feldzeit. Ebenso bestehen
keine Claims zu Memory, Organisation, Topologie, Semantik, Selbstregulation
oder KI.

## Bester naechster Schritt

Die inzwischen
[implementierte Entscheidungs- und Serialisierungsschicht](Z1_ENTSCHEIDUNG_SERIALISIERUNG_UND_LAUFSPERRE.md)
ist synthetisch geprueft. Als Naechstes darf der unveraenderte one-shot
Einstieg genau einmal als Lauf 195 aufgerufen werden. Ein separates
Vollmatrix-Preflight findet nicht statt.
