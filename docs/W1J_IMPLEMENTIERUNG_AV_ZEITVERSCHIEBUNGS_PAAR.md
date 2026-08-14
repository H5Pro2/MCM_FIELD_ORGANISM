# W1-J: Implementierung des AV-Zeitverschiebungs-Paars

Stand: 2026-08-07

Entscheidung: `W1J_TIME_SHIFTED_AV_PAIR_IMPLEMENTED_UNDER_FAKES`

Forschungslauf: nein

Realer Browser gestartet: nein

## Ergebnis

Der in W1-I gebundene A0/C0-Vertrag ist implementiert und unter zwei
vollstaendigen Fake-Browserlebenszyklen technisch abgenommen. Das Modul
erzeugt zwei frische Felder, prueft die gemeinsamen Eingangsgrenzen und
reduziert den Paarvergleich auf skalare Werte.

Es gibt in W1-J kein Konsolenwerkzeug und keinen impliziten realen
Playwright-Import. Eine reale Paarwelt bleibt dadurch technisch ausserhalb
dieser Scheibe.

## Implementierte Komponenten

`mcm_field_organism/browser_payload_timing_pair.py` implementiert:

- feste A0- und C0-Weltvertraege;
- gemeinsame Quellen- und Rezeptorfabriken;
- `BrowserPayloadTimingArmReceipt`;
- `BrowserPayloadTimingPairReceipt`;
- `run_browser_payload_timing_pair()` mit verpflichtend injizierter
  Playwright-Factory;
- skalare JSON- und Rollenprojektionen;
- direkten L1-/Linf-Vergleich korrespondierender Feldneuronen.

Der Paarlauf besitzt keine eingebaute reale Factory. Tests uebergeben zwei
Fake-Manager; eine spaetere reale Scheibe muss den Start ausdruecklich und
separat binden.

## Eng begrenzte Vertragserweiterung

Der bestehende `BrowserWorldContract` akzeptiert weiterhin die unveraenderte
drei-phasige W1-H-Form. Zusaetzlich akzeptiert er genau eine vier-phasige
Kontrollform:

```text
static -> moving -> static -> static
```

In dieser Form darf genau Phase 1 oder Phase 2 den einzigen Tonabschnitt
tragen. Erste und letzte Phase bleiben stumm. Dadurch koennen A0 und C0 mit
demselben allgemeinen Browserasset ausgedrueckt werden, ohne den bisherigen
W1-H-Vertragsdigest zu veraendern.

Der unveraenderte W1-H-Weltdigest wurde im Test erneut bestaetigt:

```text
8d896d7e55fd56c4193f3f25570a1c560fc5e1035f96f16e3f0640f8a06f7261
```

## Skalare Audioenergierolle

`BrowserPayloadCaptureReceipt` enthaelt nun `audio_total_energy`. Die Energie
wird waehrend des ohnehin erfolgenden PCM-Streamings als Float64-Summe der
quadrierten Samples berechnet. Es werden keine Samples im Receipt oder in
einer Reportdatei gehalten.

Die vorab gebundene relative Energietoleranz lautet:

```text
1e-12
```

Eine Energieabweichung oberhalb dieser Grenze verwirft das Paar als unfair.
Die Toleranz ist vor jeder realen Ausfuehrung im Code gebunden und darf nicht
nach Ergebnisansicht geaendert werden.

## Gemeinsame Runtimepruefung

Die zuvor interne W1-G-Dateidriftpruefung ist als
`verify_browser_payload_runtime_binding()` in die allgemeine Runtimegrenze
verschoben. W1-H-Smoke und W1-J-Paar verwenden damit denselben Check fuer:

- Requirementsdigest;
- Manifestdigest;
- Binarygroesse und Binarydigest;
- fehlende oder durch Symlink ersetzte Dateien.

W1-J prueft zusaetzlich die weiterhin gebundenen drei Assetdigests, bevor die
injizierte Factory aufgerufen werden kann.

## Paar-Lifecycle

Jede Bedingung besitzt einen eigenen Lifecycle:

```text
injizierten Manager betreten
-> Browser erzeugen
-> frischen isolierten Kontext erzeugen
-> Seite erzeugen
-> Payloads unmittelbar reduzieren
-> frisches Feld aufbauen und entwickeln
-> nur skalaren Arm-Receipt bilden
-> Seite schliessen
-> Kontext schliessen
-> Browser schliessen
-> Manager verlassen
```

A0 und C0 teilen weder Kontext noch Feldzustand. Auch ein Fehler im zweiten
Arm schliesst alle dort bereits erzeugten Ressourcen. Ein unvollstaendiges
Paar erzeugt keinen positiven Paar-Receipt.

## Fake-Abnahme

Die synthetische Abnahme bestaetigt:

- 1,2 Sekunden je Bedingung;
- 36 PNGs und 120 PCM-Hops je Bedingung;
- 111 auditive und 36 visuelle Rezeptorzustaende je Bedingung;
- 147 zugewiesene Feldereignisse je Bedingung;
- exakt gleiche visuelle Rezeptorwertfolgen;
- Audioenergiegleichheit innerhalb `1e-12`;
- frische identische Feldanatomie;
- skalare positive L1-/Linf-Differenz der schnellen Feldendzustande unter den
  synthetischen zeitverschobenen Daten;
- exakt inaktive Afterimage-Lage;
- vollstaendigen Abschluss beider Fake-Lifecycles;
- Abbruch bei Energieabweichung;
- Abschluss aller Ressourcen bei PCM-Fehler im zweiten Arm;
- Runtime-Driftstopp vor dem ersten Factory-Aufruf;
- keine Rohpayload-, Report-, Z4- oder Lauf-197-Rolle.

Der relevante Verbund bestand mit `49 passed` und 9 Subtests. Die bekannte
Pytest-Cachewarnung `WinError 183` betrifft ausschliesslich den lokalen
Cachepfad.

## Aussagegrenze

Die unter Fakes beobachtete Feldendzustandsdifferenz belegt nur, dass der
Comparator eine kontrollierte Zeitverschiebung technisch unterscheiden kann.
Sie ist kein realer Browserbefund und kein Nachweis von Wahrnehmung, Nachhall,
Feldzeit, Praegung, Memory, Organisation, Semantik, Selbstregulation oder KI.

Die Entscheidung
`TECHNICAL_FIELD_INPUT_TIMING_SENSITIVITY_OBSERVED` ist eine technische
Klassifikation des Comparators, keine Organismusfunktion und kein Claim.

## W1-J-Entscheidung

```text
A0/C0-Vertraege:                 implementiert
gemeinsame Quellen/Rezeptoren:   implementiert
skalare Energiepruefung:         implementiert
skalare Feldvergleiche:          implementiert
zwei frische Felder:             technisch abgesichert
Fake-Lifecycles:                 bestanden
Fehler- und Driftgrenzen:        bestanden
implizite reale Factory:         nein
Konsolenwerkzeug:                nein
realer Browserstart:             nein
Forschungslauf:                  nein
```

## Bester naechster Schritt

W1-K bindet ein einmaliges Konsolenwerkzeug an die bereits in W1-H bestaetigte
lokale Runtime und fuehrt danach genau ein technisches A0/C0-Realpaar aus.
Vor dem Start muessen Runtime-, Asset- und Toleranzidentitaet erneut bestehen.
Es gibt keine automatische Wiederholung, keine Laufnummer und keine
Forschungsaussage.
