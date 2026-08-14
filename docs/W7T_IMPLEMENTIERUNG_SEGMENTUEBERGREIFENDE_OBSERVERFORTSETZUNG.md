# W7-T: Implementierung der segmentuebergreifenden Observerfortsetzung

## Entscheidung

`SEPARATE_OBSERVER_CONTINUATION_ADAPTER_IMPLEMENTED`

W7-T implementiert den in W7-S gebundenen Fortsetzungsadapter fuer LEAK,
SAT und NORM. Er verarbeitet nur explizit uebergebene W7-R-Produktionen,
W7-P-Treiber und vorhandene Observerzustaende im Arbeitsspeicher.

## Implementierter Umfang

Das Modul `mcm_field_organism/w7t_observer_continuation.py` stellt bereit:

- einmalige modell- und pfadgebundene Nullstarts;
- vollstaendige latente W7-N-Fortsetzungszustaende;
- lueckenlose segmentweise Fortsetzung ueber W7-R/W7-P;
- `observer_`-Messungen aus fortgesetzten statt neu initialisierten
  Zustaenden;
- passive Checkpointreferenzen;
- unveraenderliche Praefixkopien fuer getrennte Zielpfade;
- Zustands-, Fortsetzungs- und Pfaddigests.

## Zustandsbindung

Jeder Zustand bindet Matrix, Pfad, Modell, Gleichung, Parameter, Uhr,
Endtick, originale Neuronenreihenfolge, vollstaendige W7-N-Latenz,
Vorgaengerdigest, optionalen Verzweigungsdigest und alle bereits
verarbeiteten Treiberdigests.

Ein Treiber darf nur fortgesetzt werden, wenn W7-R-Produktion, W7-P-Treiber
und Observerzustand in Matrix, Pfad, Quelle, Intervall und Geometrie
uebereinstimmen. Bereits verarbeitete Treiber werden vor jeder erneuten
Zeitpruefung abgelehnt.

## Modelltrennung

LEAK, SAT und NORM erhalten dieselbe Treiberdigestfolge, besitzen aber
verschiedene Zustands- und Fortsetzungsdigests. SAT transformiert nur seine
Ausgabe. NORM setzt den Leaky-Latentzustand fort; die normalisierte Ausgabe
wird nicht zurueckgefuehrt.

Checkpointreferenzen enthalten nur Modell, Pfad, Checkpoint, Endtick und
Zustandsdigest. Pfadkopien uebernehmen denselben unveraenderlichen
Praefixzustand, erhalten jedoch neue Pfad- und Zustandsdigests.

## Technische Abnahme

Der fokussierte W7-T-Bestand besteht mit:

```text
11 tests, OK
```

Der direkte W7-M/N/P/R/T-Verbund besteht mit:

```text
48 tests, OK
```

Der erweiterte relevante Verbund aus W7-T, W7-R, W7-P, W7-N, W7-M,
kapazitaetsbegrenzten Kopplungs- und Runtimepfaden, F3- und
Baselinekopplungen, K2-B-Quellen sowie API-/Architekturverbrauchern besteht
mit:

```text
128 tests, OK
```

Geprueft sind unabhaengige Nullstarts, gleiche Treiberdigestfolgen,
Modelltrennung, exakte segmentierte Fortsetzung, NORM-Latenz, passive
Checkpoints, unabhaengige Pfadkopien, Determinismus, Duplikat- und
Intervallsperren, manipulationssichere Zustandsdigests,
Eingabeunveraenderlichkeit und fehlender Export aus `current_api`.

## Unveraenderte Grenzen

Unveraendert blieben:

- `mcm_field_organism.__init__` und `current_api`;
- P0-, Feld- und Produktionsruntime;
- Snapshot-Schemata;
- Browser-, Video- und Audiopfade;
- Reports und formale Forschungslaeufe;
- Lauf 197 und W6-I.

W7-T belegt nur die technische Fortsetzbarkeit externer
Erklaerungsbaselines. Es belegt keine Feldfunktion, kein Memory, keine
Ressourcenwiederverwendung, keine Feldzeit, Organisation, Semantik,
Selbstregulation oder KI.

## Naechster Schritt

W7-U muss statisch pruefen, ob das eingefrorene W7-M-Quelleninventar jeden
der sieben Pfade segmentweise und symmetrisch belegen kann. Insbesondere ist
zu klaeren, ob fuer die gespiegelte B-A-Linie gebundene einzelne A-Schritte
vorhanden sind oder als additive, vor jeder Auswertung eingefrorene
Quellenfamilie fehlen. Noch keine Pfadmatrix oder Ausfuehrung.
