# W7-AA: Implementierung des P0-only-Siebenpfad-Verbrauchers

## Entscheidung

`P0_ONLY_SEVEN_PATH_PLAN_CONSUMER_IMPLEMENTED`

W7-AA implementiert den W7-Z-Vertrag als isolierte In-Memory-Verarbeitung
der in W7-Y gebundenen Quellen. Ausgefuehrt wird ausschliesslich der
substratfreie W7-R-P0-S/H-Arm. Es wurde kein Report und kein formaler
Forschungslauf erzeugt.

## 1. Implementierter Umfang

Das Modul `mcm_field_organism/w7aa_p0_seven_path_consumer.py` erzeugt:

- sieben getrennte P0-Hauptketten;
- vier Kontaktstarts bei Tick 0;
- drei sourcefreie U-Starts bei Tick 4;
- 32 Hauptproduktionen;
- 35 Checkpointresultate;
- 35 tief kopierte und getrennt ausgefuehrte Probeaeste;
- eine Reihenfolge-Gegenkontrolle an AB/Checkpoint 0;
- sieben Pfadverbrauchsdigests und einen Gesamtverbrauchsdigest.

Der Verbraucher rekonstruiert den erwarteten W7-Y-Plan vor jeder
Verarbeitung und lehnt abweichende Planobjekte ab.

## 2. P0-Kopiergrenze

Vor jeder Probe wird das private P0-Feld tief kopiert und anschliessend durch
den vorhandenen `W7RP0State`-Konstruktor erneut validiert. Am Kopierpunkt
gelten:

- gleicher Zustand-, Matrix-, Pfad-, Uhr- und Tickdigest;
- bitgleiche S/H-Vektoren;
- verschiedene Zustands- und P0-Feldobjekte;
- verschiedene Layer-, Dock- und vorhandene Distributionsobjekte;
- kein Substrat und kein Entwicklungszustand.

Die Probe verarbeitet nur ihre Kopie. Hauptzustand, Hauptfortsetzung und
andere Probeaeste erhalten keinen Probeendzustand.

## 3. Haupt- und Probeproduktionen

Kontaktpfade verarbeiten ihren kombinierten Praefix und vier
Fortsetzungen. U-Pfade beginnen direkt mit einem P0-Nullzustand bei Tick 4
und verarbeiten vier Fortsetzungen. Alle Hauptketten enden bei Tick 8.

Jede Probe P0 bis P4 verwendet das im zugehoerigen W7-Y-Checkpoint gebundene
Quellsegment und laeuft exakt eine Sekunde ab ihrem Checkpointtick. Jede
Produktion wird weiterhin vollstaendig durch W7-R an Quelle, Intervall,
Pfad, Anfangs- und Endzustand gebunden.

## 4. Reihenfolge-Gegenkontrolle

An AB/Checkpoint 0 werden Probe und naechstes Hauptsegment aus je neuen
Kopien in beiden Reihenfolgen ausgefuehrt:

```text
Probe -> Haupt
Haupt -> Probe
```

Die rollenbezogenen Produktionsdigests bleiben exakt gleich und stimmen mit
der regulaeren AB-Haupt- und Probeproduktion ueberein. Dies weist nur die
fehlende technische Rueckwirkung zwischen diesen P0-Objekten nach.

## 5. Gebundener Gesamtverbrauchsdigest

```text
2303230f9dfc2837d0043c6e1b6c7e0aa72042ff6c271eb025a971d4501c0440
```

Der Digest bindet W7-Y-Gesamtplan, die sieben Pfadverbrauchsdigests und die
Reihenfolge-Gegenkontrolle. Es wird keine Pfadrangfolge, Bewertung oder
Interpretation aufgenommen.

## 6. Verifikation

Die neue W7-AA-Suite enthaelt 13 Tests und besteht mit:

```text
Ran 13 tests
OK
```

Der breitere W7-Verbund besteht mit:

```text
Ran 86 tests
OK
```

Geprueft wurden Startrollen, Hauptanzahl, Plan- und Intervallbindung,
lueckenlose Fortsetzung, Substratfreiheit, tiefe Objekttrennung,
Probeisolation, terminaler Tick 8, Reihenfolge-Gegenkontrolle,
deterministische Wiederholung, Eingabeunveraenderlichkeit und manipulierte
Checkpoint-, Pfad- und Gesamtdigests.

W7-AA wird weder aus dem Paketwurzelmodul noch aus `current_api` exportiert.

## 7. Aussagegrenze

W7-AA ist eine technische Ausfuehrung der P0-Fast-State-Gegenbaseline. Die
erzeugten S/H-Verlaeufe wurden nicht als Funktion bewertet und nicht mit
gekoppelten Modellen verglichen. Daraus folgen keine Feldfunktion, kein
Memory, keine Feldzeit, Organisation, Topologie, Semantik, Selbstregulation
oder KI.

## 8. Naechster Schritt

W7-AB soll statisch die Uebergabe der W7-AA-Haupt- und Probeproduktionen an
getrennte LEAK-, SAT- und NORM-Observerketten binden. Observer muessen ihre
eigenen Haupt- und Probecheckpointzustaende besitzen und duerfen niemals auf
P0 zurueckwirken. Noch keine Observerausfuehrung, gekoppelte Matrix, kein
Browser, Report oder Forschungslauf.
