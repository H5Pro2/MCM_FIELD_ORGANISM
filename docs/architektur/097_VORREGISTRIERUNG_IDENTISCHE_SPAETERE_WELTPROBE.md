# Vorregistrierung: identische spätere Weltprobe

## Status

```text
reine Null- und Wiederholbarkeitskontrolle: freigegeben
neue Zustandsmechanik:                      ausgeschlossen
Memory-Prüfung:                             ausgeschlossen
Runtime-Änderung:                           ausgeschlossen
```

## Frage

Reagiert die bestehende Runtime nach zwei verschiedenen Weltgeschichten bei
vollständig angeglichener bekannter Gegenwart gleich?

Die erwartete Antwort lautet aufgrund der vorhandenen Runtime:

```text
ja
```

Der Lauf sucht keinen Memory-Effekt. Er prüft die bekannte Zustandsgrenze.

## Vorgeschichten

Verwendet werden unverändert H0 und H1 aus Lauf 095:

```text
H0: 2 -> 3 -> 4 -> 5 -> 6 -> 7
H1: 2 -> 3 -> 4 -> 3 -> 2 -> 1
```

Geometrie, Zeitbudget, Verdeckungsmaske, Rezeptorstärke und MCM-Anatomie
bleiben identisch.

## Gemeinsame spätere Probe

Nach beiden Vorgeschichten folgen zwei identische sichtbare Proberahmen an
Position `8`:

```text
Probe A: Position 8, Angleichungsrahmen
Probe B: Position 8, identische Holdoutprobe
```

Position `8` wurde vor dem Lauf festgelegt. Sie wird weder aus einem
Feldergebnis noch aus einer Observerauswertung gewählt.

Die Probe ist eine kontrollierte gemeinsame Weltprojektion und keine
Behauptung einer ununterbrochenen natürlichen Bahn von H0 oder H1.

## Erwartete Zeitordnung

Nach Probe A wird getrennt geprüft:

```text
aktueller Rezeptorkontakt gleich
activation gleich
afterimage gleich
```

Der vollständige Snapshot darf hier wegen der bekannten lokalen Feldprobe des
vorherigen Takts noch verschieden sein.

Nach Probe B wird geprüft:

```text
Rezeptorverteilung gleich
activation gleich
afterimage gleich
lokale Feldproben gleich
vollständige MCM-Neuronenschicht gleich
vollständiger SharedMCMFieldSnapshot gleich
```

## Pflichtkontrollen

- Beide Zweige verwenden dieselben zwei Proberahmen.
- Die Proben verwenden dieselbe Geometrie, Stärke, Zeitlage und Position.
- `receptor_projection_baseline` bleibt unverändert.
- Kein Zustand wird vor Probe A oder Probe B manuell zurückgesetzt.
- Keine Ereignis-, Zweig- oder Phasenkennung erreicht die Runtime.
- Es gibt keine künstliche Rauschquelle.
- Es gibt keine künstliche Varianzregel.
- Es gibt keine Glättung.
- Es gibt keine Nullpunkt- oder Ruhepunktdynamik.
- Zweigreihenfolge und Wiederholung dürfen das Ergebnis nicht verändern.
- Der Observer schreibt nicht zurück.

## Zulässiger Befund

Bei vollständiger Gleichheit nach Probe B darf nur gesagt werden:

> Die bestehende Runtime reagiert nach Angleichung aller bekannten aktuellen
> Zustände reproduzierbar gleich.

Das ist ein Nullbefund und kein Memory-Hinweis.

## Unerwarteter Rest

Bleibt nach Probe B ein Unterschied, wird zuerst geprüft:

- unvollständige lokale Zustandsangleichung;
- Zeit- oder Frame-Index-Unterschied;
- abweichende Rezeptorverteilung;
- Zweig- oder Ereigniskennung in einer Runtime-Rolle;
- Observer-Rückschreibung;
- versteckter technischer Zustand.

Ein Rest darf nicht unmittelbar als Memory bezeichnet werden.

## Nicht geprüft

Nicht geprüft werden:

- organisches Memory;
- semantische Resonanz;
- innere Bezeichnung;
- entwickelte Topologie;
- Feldrückwirkung;
- Lernen;
- Anpassung;
- Feldintelligenz.

## Stopplinie

Der Lauf endet nach Probe B. Es folgen keine weiteren Zyklen und keine neue
Mechanik.

## Wie es am besten weitergeht

Als nächster Schritt wird ausschließlich diese zweistufige Nullkontrolle
implementiert. Danach wird entschieden, ob die bekannte Runtimegrenze
vollständig beschrieben ist. Eine neue MCM-Speicherhypothese darf daraus
weder bei Gleichheit noch bei einem zunächst unerklärten Rest automatisch
abgeleitet werden.
