# S2-SFA: Neutrale Budgetqualifikation

**Qualifikations-ID:** `s2sfa-budget-qualification-20260919-01`  
**Status:** `2/2 QUALIFIED` für lokale Record- und Publikationsgrenzen

Der einmalige Aufruf

```text
C:\Python314\python.exe -m unittest tests.test_s2sfa_budget_profile
```

endete mit Exitcode 0; zwei neutrale Budgetkontrollen wurden ausgeführt.
Bestätigt sind Grenzgleichheit, typisierte Überschreitung, atomare temporäre
Veröffentlichung und Fehlerabschluss. Es wurden keine Planframes oder
Rezeptor-/Feld-/Memorypfade verarbeitet.

## Quellenhash-Klärung

Die Regel lautet `BIND_BEFORE_ANALYSIS`: Der zukünftige, aus Rezept erzeugte
RGB-Frame wird vor `analyze()` gehasht und dieser Hash im Laufbeleg gebunden.
Es existiert derzeit kein unabhängig vorversiegelter Payload-Sollhash. Der
Vorgang darf deshalb nicht als Sollhashprüfung bezeichnet werden.

## Verbleibende Bilanzlücke

Die 2-MiB-Recordgrenze trägt auch die derzeitige redundante Erfolgsform. Die
konservativ gezählten Vektorwerte aus Rezeptorwerten, Rohfolgen und gefrorenem
Zustand benötigen höchstens 441.792 Byte vor JSON-Struktur; die Differenz zur
2.097.152-Byte-Grenze ist ausreichend für die fest geformten Metadaten,
Digests, Scores und Fehleralternative.

Die Vorbindung behauptete fälschlich, Roh-/Merkmalsfolgen würden nicht mehr
gespeichert. Tatsächlich enthält der aktuelle Record sie weiterhin. Dieser
Widerspruch wird nicht rückwirkend verändert.

Der Publisher setzt bisher nur Record plus temporäre Kopie gegen die
8-MiB-Grenze durch. Referenzen, Qualifikationsbelege, Verifikationsausgabe und
Auswertung werden noch nicht als gemeinsames, vorab geprüftes Gesamtledger
gezählt. Daher ist der reale Methodenlauf weiterhin **nicht ausführungsbereit**.
Eine weitere explizite Anschlussentscheidung wäre nötig, bevor diese
Gesamtbilanz ergänzt und qualifiziert werden kann.
