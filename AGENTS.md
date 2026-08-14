# Verbindliche Arbeitsregeln

## Operative Grundlage

Vor jeder neuen Aufgabe ist `AKTUELLER_FORSCHUNGSWEG.md` zu lesen. Dieses
Dokument hat fuer neue Arbeiten Vorrang vor historischen Forschungsplaenen und
aelteren Architekturabschnitten.

Die aktuelle fachliche Ausarbeitung steht ausserdem in
`docs/FORSCHUNGSRICHTUNG_FELDZEIT_INNERER_KONTEXT.md`.

## Manueller Arbeitsmodus

Bis zu einer ausdruecklichen Neukonfiguration des Orchestrators wird die
Forschungsrichtung im Hauptchat manuell festgelegt. Keine automatische
Weitergabe, Agentenschleife oder fortlaufende Freigabe- und Abnahmekette
starten. Code, Tests und Versuchslaeufe nur nach einem konkreten
Benutzerauftrag ausfuehren.

## Aktuelle Testwelt-Grenze

Erlaubt sind ausschliesslich kontrollierte Browser-, Video- und
Audio-Testwelten, kontrollierte audiovisuelle Dateien und technisch
abgegrenzte oeffentliche Medienquellen.

Nicht erlaubt sind Kamera, Mikrofon als Live-Sensor, reale physische Sensorik,
physische Aufbauabnahmen, Markerlaeufe, direkte Bildschirm-Kamera-Kopplung und
physische Feld-Welt-Feld-Laeufe. Vorhandener Altcode dieser Pfade darf gelesen
und als historische Regression erhalten werden, aber nicht ohne neue
Benutzerentscheidung ausgefuehrt oder weiterentwickelt werden.

## Laufnummern

Nur ein tatsaechlich ausgefuehrter Untersuchungs-, Experiment- oder
Programmdurchlauf erhaelt eine Laufnummer.

Nicht als Lauf zaehlen:

- Gespraeche und konzeptionelle Rueckmeldungen;
- reine Dokumentationsaenderungen;
- README-Anpassungen;
- Planung, Vorregistrierung und Architekturtexte;
- statische Code-, Sicherheits- oder Machbarkeitsanalysen;
- Freigaben, Korrekturen und Workflow-Uebergaben;
- Commits und Pushes ohne ausgefuehrte Untersuchung.

Dateipraefixe sind Dokumentnummern. Sie duerfen nicht als Laufstand ausgegeben
werden. Historische Dokumente mit abweichender Benennung werden nicht als
Vorlage fuer neue Berichte verwendet.

Berichte ueber einen tatsaechlichen Lauf beginnen mit:

```text
Lauf XX
```

Die naechste Laufnummer wird erst unmittelbar vor einer realen Ausfuehrung aus
dem letzten nachweislich ausgefuehrten Lauf bestimmt. Sie wird nicht aus der
hoechsten Dokumentnummer abgeleitet.

Nach jedem tatsaechlichen Lauf wird der kleinste sinnvolle naechste Schritt
angegeben. Ohne neue entscheidungsrelevante Information wird keine weitere
Freigabe- oder Abnahmekette erzeugt.

## Evidenzgrenze

Jedes Ergebnis trennt:

- beobachtete Messung;
- technische Interpretation;
- Hypothese;
- Nichtnachweis;
- offene oder nicht gepruefte Annahme.

Vorzustandswirkung, Nachhall, Persistenz oder Reproduzierbarkeit sind fuer sich
kein Nachweis von MCM-Memory, Organisation, Topologie, Bedeutung oder KI.

## Verbotene Vorprogrammierung

Nicht in den Organismuspfad eingebaut werden:

- Wenn-X-dann-Y-Regeln als Organismusfunktion;
- Labels, Bedeutung, Reward oder Zielverhalten;
- gewuenschte Feldmuster oder Zieltopologien;
- Rohdaten-, Datenbank- oder Embedding-Speicher als MCM-Memory;
- Ergebnisabhaengige Aenderungen an Hypothesen, Schwellen oder Versuchsarmen.

## Rollen

Die bisherigen Rollen bleiben als spaetere Workflow-Struktur dokumentiert,
sind im manuellen Arbeitsmodus aber nicht automatisch aktiv. Eine spaetere
Neukonfiguration muss MCM-Forschungsagent und Forschungshelfer auf den neuen
Feldzeit- und Innerer-Kontext-Weg ausrichten und ihre Rollen weiterhin sauber
trennen.
