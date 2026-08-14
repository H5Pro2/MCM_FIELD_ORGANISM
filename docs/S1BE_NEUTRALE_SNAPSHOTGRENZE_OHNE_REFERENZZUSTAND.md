# S1-BE: Neutrale Snapshotgrenze ohne Referenzzustand

## Status

Technische Zustands- und Serialisierungsabsicherung. Keine neue Mechanik,
kein Browserlauf, kein Forschungslauf und kein Memory-, Substrat- oder
KI-Befund.

## Frage

Enthalten Snapshots der beiden aktiven neutralen Weltzufuhren optionale C_i-,
F3- oder S1B-Zustaende, obwohl kein Referenzarm explizit zugeschaltet wurde?

## Snapshotrollen

`SharedMCMFieldSnapshot` besitzt drei klar getrennte Schemata:

```text
Schema 1 = neutrales S/H-Feld
Schema 2 = Feld mit explizitem F3-Substratzustand
Schema 3 = Feld mit explizitem S1B-Entwicklungszustand
```

C_i ist kein Feld des `SharedMCMFieldSnapshot`. Seine Referenzbaseline fuehrt
einen eigenstaendigen `CIState`, der nur durch explizite C_i-Funktionen
fortgeschrieben wird.

## Befund

Sowohl der synthetische AV-End-to-End-Consumer als auch die kontrollierte
Browser-Testwelt-Rezeptorbruecke erzeugen ohne Referenzarm exakt Schema 1.
Der kanonische Snapshot enthaelt nur:

```text
schema_version
layer
docks
last_distribution
```

Nicht enthalten sind:

```text
substrate    (F3)
development  (S1B)
C_i-Zustand
```

Die restaurierten Felder behalten `substrate is None` und
`development is None`.

## Dauerhafte Absicherung

Beide aktiven Consumer-Tests pruefen jetzt:

1. `schema_version == 1`;
2. die exakte Root-Schluesselmenge des kanonischen Snapshots;
3. identischen Digest nach Restore;
4. fehlenden F3- und S1B-Zustand im restaurierten Feld.

Eine spaetere implizite Referenzzustandsaufnahme bricht damit den jeweiligen
End-to-End-Test.

## Aussagegrenze

Snapshot/Restore ist technische Runtime-Serialisierung und kein
MCM-Memory. Das vorhandene schnelle Nachhallfeld H gehoert zum neutralen
Neuronenzustand und ist keine Praegung oder langsames Memorysubstrat.

## Bester naechster Schritt

Die aktive AV-Engineeringoberflaeche ist von Quelle bis Snapshot sauber von
den Referenzarmen getrennt. Als naechstes wird der aktuelle Dokumentations-
und API-Wortlaut auf missverstaendliche Gleichsetzungen von Snapshot,
Nachhall, Substrat und Memory geprueft; nur aktive Leitseiten und Docstrings
werden dabei betrachtet.

