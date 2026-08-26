# S1-SE: Fokussierter Testlauf und technische Abnahme der Vier-Knoten-Frischmatrixregistrierung

## Status und Umfang

S1-SE fuehrt genau den in S1-SD gebundenen unveraenderten fokussierten
Testlauf der neuen Frischmatrixregistrierung aus. Zwischen
Implementierungscommit und Lauf wurden Registrierungsdatei, Consumer und
Testdatei nicht veraendert.

Abnahmeentscheidung:

```text
ELEVEN_OF_ELEVEN_MATRIX_REGISTRATION_TESTS_PASSED
SEVENTEEN_REPLICA_AXIS_TECHNICALLY_ACCEPTED
238_CELL_AND_560_CHECKPOINT_CARDINALITIES_TECHNICALLY_ACCEPTED
S1RK_V1_MANIFEST_CROSS_VALIDATION_TECHNICALLY_ACCEPTED
NO_FRESH_BUILD_NO_MATRIX_CELL_NO_FIELD_EXECUTION
```

## Ausgefuehrter Befehl

```text
python -m unittest discover -s tests -p "test_four_node_fresh_matrix_registration.py" -v
```

Ergebnis:

```text
Ran 11 tests in 0.013s
OK
```

Der Prozess endete mit Exitcode `0`.

## Vorlaufidentitaet

Der Testlauf startete aus Commit `022b8ea`. Der Arbeitsbaum war leer, und
die drei S1-SD-Artefakte waren gegen den Commit unveraendert.

Vor dem Lauf wurden genau elf Testmethoden gezaehlt. Der Befehl wurde einmal
und ohne Korrektur oder Wiederholung ausgefuehrt.

## Technisch abgenommene Oberflaeche

Innerhalb der fokussierten Tests sind bestaetigt:

- Annahme der registrierten Datei mit Digest
  `edd3414b3dcc082c0ab7bec66f8dd278cedecd76d11e649ca7aff46a9317a4ba`;
- rekursiv unveraenderliche Registrierungsansicht;
- fail-closed Ablehnung ungueltiger Bytes, JSON-Formen und Duplikate;
- fail-closed Ablehnung unbekannter, fehlender oder falscher Schemafelder;
- Erkennung eines abweichenden Registrierungsdigests;
- exakte lueckenlose Achse mit 17 Rollen und getrennten Positionen fuer
  `U_FRESH_B_EARLY` und `U_FRESH_B_LATE`;
- Ablehnung geaenderter Reihenfolge, Duplikate und falscher Achsenlaenge;
- Ablehnung der ueberholten 16-/224-/532-Zaehler;
- exakte Ableitung von 238 Matrixzellen und 560 Pflichtrecords;
- unveraenderte v1-Basisidentitaeten;
- gemeinsame erfolgreiche Validierung mit dem registrierten
  S1-RK-v1-Frischmanifest;
- Ablehnung eines nur typgleich konstruierten, aber nicht gueltigen
  Basismanifestobjekts.

## Nicht geprueft

S1-SE prueft ausdruecklich nicht:

- den Bau von 238 Frischobjektgraphen;
- konkrete synchrone Kontakt- oder Gapintervalle;
- Ereignisplaene oder Expositionsdigests;
- Modellaufrufe, Carries oder Baselinegleichungen;
- passive Checkpointmaterialisierung oder Gesamtpaketatomaritaet;
- Comparatoren, Kandidatenfunktion oder Feldentwicklung;
- eine Faehigkeit einer hypothetischen MCM-Memory-Entwicklungsrichtung.

## Technische Bewertung

Die neue Matrixregistrierung ist innerhalb ihrer fokussierten
Testoberflaeche technisch abgenommen. Der zuvor in S1-SA gefundene
Zeitkontrollwiderspruch ist damit nicht funktional untersucht, aber seine in
S1-SB gewaehlte strukturelle Aufloesung ist technisch eindeutig
registrierbar und mit dem unveraenderten Frischmanifest verbindbar.

Die konkrete gemeinsame Ereignisgeschichte bleibt der naechste Engpass.
Alle modellwirksamen Segmente muessen weiterhin synchron und fuer alle 14
Rollen oeffentlich wertidentisch registriert werden.

## Aussagegrenze

Der bestandene Testlauf ist eine technische Registrierungsabnahme. Er ist
kein Feldlauf, kein Baselinevergleich und kein Befund einer hypothetischen
MCM-Memory-Entwicklungsrichtung.

## Genau ein naechster Schritt

S1-SF ist ausschliesslich als statischer gemeinsamer synchroner
Vier-Knoten-Expositionssegment-, Ereignisplan- und
17-Repliken-Fixturevertrag zulaessig.

S1-SF muss konkrete gemeinsame Kontakt- und Nullsegmente, Feldzeiten,
Vier-Knoten-Vektoren, Praefixidentitaeten, die zwei getrennten
U-Frischzeitkontrollen sowie alle 17 Planfolgen binden. Noch keine
Implementierung, kein Test, keine Matrixzelle, kein Comparator und kein
Forschungslauf.
