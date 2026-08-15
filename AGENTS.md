# Verbindliche Arbeitsregeln

## Projektgrenze

Arbeite ausschliesslich an `MCM_FIELD_ORGANISM`. Ziele, Regeln, Rollen,
Steuerungsdateien oder technische Komponenten anderer Projekte duerfen nicht
uebernommen oder eingebunden werden.

## Operative Grundlage

Vor jeder neuen Aufgabe sind mindestens `AKTUELLER_FORSCHUNGSWEG.md`,
`README.md` und die Dokumente des neuesten aktiven Forschungsabschnitts zu
lesen. Der aktuelle Forschungsweg hat fuer neue Arbeiten Vorrang vor
historischen Plaenen und aelteren Architekturabschnitten.

Die fachliche Richtung steht ausserdem in:

- `docs/MCM_MEMORY_SUBSTRAT_ENTWICKLUNGSRICHTUNG.md`
- `docs/FORSCHUNGSRICHTUNG_FELDZEIT_INNERER_KONTEXT.md`

## Manueller MCM-Arbeitsmodus

Die Forschungsrichtung wird im aktuellen Hauptchat durch den Benutzer und den
bearbeitenden Codex festgelegt. Es gibt keine automatische Weiterleitung,
keine externen Rollen und keine fortlaufende Freigabe- oder Abnahmeschleife.
Code, Tests und Versuchslaeufe werden nur fuer einen konkreten Benutzerauftrag
ausgefuehrt.

Schreibt der Benutzer `okay weiter`, wird der zuletzt genannte kleinste
sinnvolle naechste Schritt selbststaendig bearbeitet. Eine bereits klar
gestellte zwingende Rueckfrage wird dadurch nicht beantwortet.

## Rueckmeldung und Abschluss

Kann die Arbeit normal fortgesetzt werden, endet die Rueckmeldung mit:

```text
WEITER: Am besten geht es jetzt mit ... weiter.
```

Fehlt eine zwingende fachliche Entscheidung oder eine ausdrueckliche
Einmallauffreigabe, wird sie mit `RUECKMELDUNG ERFORDERLICH` gekennzeichnet.
Bis zur konkreten Antwort bleibt nur die davon abhaengige Arbeit geschlossen.

Besitzt eine Forschungslinie keine neue Gegenprognose mehr oder wiederholt nur
eine bereits erklaerte Baseline, wird sie mit `STOPP` beendet. Dabei ist klar
zu trennen, ob nur der Teilzweig oder das Gesamtprojekt betroffen ist.

## Aktuelle Testweltgrenze

Erlaubt sind kontrollierte Browser-, Video- und Audio-Testwelten,
kontrollierte audiovisuelle Dateien und technisch abgegrenzte oeffentliche
Medienquellen.

Nicht aktiv sind Kamera, Mikrofon als Live-Sensor, reale physische Sensorik,
physische Aufbauabnahmen, Markerlaeufe, direkte Bildschirm-Kamera-Kopplung und
physische Feld-Welt-Feld-Laeufe. Vorhandener historischer Code darf gelesen
und als Regression erhalten, aber nicht ohne neue Benutzerentscheidung
ausgefuehrt oder weiterentwickelt werden.

## Laufnummern

Nur ein tatsaechlich ausgefuehrter Untersuchungs-, Experiment- oder
Programmdurchlauf erhaelt eine Laufnummer. Gespraeche,
Dokumentationsaenderungen, Planung, Vorregistrierung, statische Analysen,
Commits und Pushes sind keine Laeufe.

Dateipraefixe sind Dokumentnummern und keine Laufstaende. Die naechste
Laufnummer wird erst unmittelbar vor einer realen Ausfuehrung aus dem letzten
nachweislich ausgefuehrten Lauf bestimmt.

## Evidenzgrenze

Jedes Ergebnis trennt:

- beobachtete Messung;
- technische Interpretation;
- Hypothese;
- Nichtnachweis;
- offene oder nicht gepruefte Annahme.

Vorzustandswirkung, Nachhall, Persistenz, Snapshot, Reproduzierbarkeit,
Zustandsweitergabe oder feste Adapterwirkung sind fuer sich kein Nachweis von
MCM-Memory, Feldzeit, innerem Kontext, Organisation, Topologie, Bedeutung,
Selbstregulation oder KI.

## Verbotene Vorprogrammierung

Nicht in den Organismuspfad eingebaut werden:

- Wenn-X-dann-Y-Regeln als Organismusfunktion;
- Speicher-, Lern-, Abruf- oder Vergessenskommandos;
- Labels, Bedeutung, Reward oder Zielverhalten;
- gewuenschte Feldmuster oder Zieltopologien;
- Objekt-, Episoden-, Partner-, Wort- oder Cluster-IDs;
- Rohdaten-, Datenbank- oder Embedding-Speicher als MCM-Memory;
- ergebnisabhaengige Aenderungen an Hypothesen, Schwellen oder Versuchsarmen.

## Arbeitsfolge

```text
Projektstand lesen
-> aktuelle Forschungsfrage bestimmen
-> Evidenz und Baselines pruefen
-> kleinsten zulaessigen Schritt festlegen
-> umsetzen oder untersuchen
-> fokussiert und regressiv testen
-> Messung und Grenzen dokumentieren
-> besten naechsten Schritt nennen
```

Vor Dateianderungen ist der Git-Status zu pruefen. Bestehende fremde
Aenderungen werden weder verworfen noch ungefragt in eigene Commits
aufgenommen.
