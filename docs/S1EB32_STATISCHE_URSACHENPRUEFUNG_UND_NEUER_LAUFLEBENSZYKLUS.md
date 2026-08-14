# S1-EB32: Statische Ursachenpruefung und neuer Lauflebenszyklus

## Status

```text
STATIC_ROOT_CAUSE_CONFIRMED
S1_EB31_REMAINS_TERMINAL
NEW_EXECUTION_NOT_AUTHORIZED
```

S1-EB32 ist eine rein statische Ursachenpruefung. Es wurde kein Test, kein
Runner und kein weiterer kanonischer Lauf gestartet. Der erhaltene
S1-EB31-Attempt wurde weder entfernt noch veraendert.

## Bestaetigte Ursache

Der S1-EB31-Worker prueft zuerst die freien Zielpfade, erstellt danach Lock
und Attempt und ruft erst dann die kanonische Rechenkette auf. Diese
Rechenkette konstruiert den S1-EB-Vertrag jedoch erneut. Dessen
`__post_init__` verlangt weiterhin, dass Report, Attempt und Lock gleichzeitig
frei sind. Die Anforderungen widersprechen sich nach dem vorgeschriebenen
Setzen des Attempts.

Der Widerspruch ist nicht auf den ersten Stacktrace begrenzt. Drei
nachgelagerte Stellen rekonstruieren denselben pfadpruefenden Vertrag:

```text
e1_confirmation_canonical_formation_adapter._canonical_inputs
e1_confirmation_canonical_probe_handoff._canonical_probe_binding
e1_confirmation_canonical_probe_adapter._canonical_probe_inputs
```

Eine Korrektur nur am Formation-Adapter wuerde den Fehler deshalb lediglich
in die Probe-Uebergabe verschieben.

## Technische Einordnung

Die freie Zielpfadpruefung ist eine Vorstartbedingung und keine Invariante
des Rechenkerns. Nach Beginn eines Exactly-once-Versuchs muss der Attempt
vorhanden sein. Formation, Probe und Auswertung duerfen in dieser Phase den
bereits validierten Vertrag konsumieren, aber keine erneute
Vorstartkonstruktion ausloesen.

Dies ist ein technischer Lauflebenszyklusfehler. Es gibt daraus weder einen
positiven noch einen negativen Forschungsbefund zu E1 oder MCM-Memory.

## Verbindlicher Korrekturvertrag fuer eine neue Identitaet

Ein spaeterer, separat autorisierter Lauf muss die Phasen strikt trennen:

1. Bei freien neuen Zielpfaden genau einmal Vertrag, Quellen, Plaene,
   Geometrie, Anfangsfeld und Anfangszustand bilden und validieren.
2. Diese Werte in einem unveraenderlichen In-Memory-Ausfuehrungsbundle
   binden; seine Digests muessen mit dem neuen Kettenvertrag uebereinstimmen.
3. Den Same-Session-Preflight gegen genau dieses Bundle abschliessen.
4. Lock und danach Attempt exklusiv erstellen.
5. Formation, Probe-Uebergabe und Probe ausschliesslich aus dem gebundenen
   Bundle speisen. Nach dem Attempt darf kein Konstruktor mit einer
   Zielpfad-Freiheitspruefung mehr aufgerufen werden.
6. Bericht weiterhin atomar veroeffentlichen; Attempt nur nach erfolgreicher
   Ruecklesepruefung entfernen; Lock im `finally` freigeben.

Die Korrektur darf die bestehende S1-EB31-Identitaet und ihre Pfade nicht
wiederverwenden. Alte Implementierungsdigests und Freigaben gelten nicht
automatisch fuer die korrigierte Kette.

## Gegenpruefungen vor einer neuen Autorisierung

Eine neue Ausfuehrungsidentitaet darf erst zur Freigabe vorgelegt werden,
wenn statisch und mit ausschliesslich temporaeren synthetischen Pfaden gezeigt
ist:

- kein pfadpruefender Vertragsaufbau nach Erstellung des Attempts;
- exakt ein gebundenes Bundle fuer Formation und Probe;
- ein absichtlich vorhandener temporaerer Attempt blockiert den Rechenkern
  nicht, waehrend ein zweiter Laufstart weiterhin blockiert wird;
- Fehler nach Attempt erhalten den Attempt und entfernen den Lock;
- Erfolg veroeffentlicht genau einen Bericht und entfernt erst danach den
  Attempt;
- S1-EA6 und der terminale S1-EB31-Attempt bleiben unveraendert.

Diese Gegenpruefungen autorisieren keinen kanonischen Lauf.

## Unveraenderte Artefakte

```text
S1-EA6 report SHA-256:
adf8b2b6c1b9fdda48062dbb1cd9149fcde462a3dc77a348aa2dfb0cb1fcaa47

S1-EB31 attempt SHA-256:
695f8170011d3c7afe1a0c8816021fb4814ac409c71fef36253f2ce9ce091782
```

## Evidenzgrenze

S1-EB32 aendert keine fachliche Bewertung. Insbesondere bestehen weiterhin
kein S1-EB-Ergebnis und kein neuer Memory-, Feldzeit-, Bedeutungs-,
Organisations-, Topologie- oder KI-Nachweis.

## Bester naechster Schritt

Als naechstes sollte die korrigierte Bundle-Architektur unter einer neuen
Entwicklungsidentitaet implementiert und ausschliesslich mit temporaeren
synthetischen Pfaden abgenommen werden. Ein neuer kanonischer Lauf bleibt bis
zu einer danach ausgesprochenen separaten Projekteigner-Autorisierung
gesperrt.
