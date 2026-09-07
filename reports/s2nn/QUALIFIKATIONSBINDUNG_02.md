# S2-NN: einmalige Neuqualifikation nach Testkorrektur

Neue ID: `s2nn-half-profile-runtime-qualification-20260907-02`.
Ausgangscommit: `734ae99`. Der erste Fehlbefund bleibt unveraendert erhalten.

Es gelten unveraendert die 14 Pruefgruppen, neutralen Quellen, Ereignisse,
Arithmetik, Fehlerinjektionen und Ressourcenobergrenzen aus
`QUALIFIKATIONSBINDUNG.md`. Keine weiteren Testkoerper oder numerischen Faelle.
Genau ein vollstaendiger neutraler Testaufruf, keine NL-/NM-Wiederholung,
kein Retry bei erneutem Fehler und keine NH- oder Hauptausfuehrung.

Einzige Testkorrektur in Gruppe 3:

- Alter Zustand unter Halbprofil und Halbprofilzustand unter altem Profil
  werden in getrennten benannten `subTest`-Bloecken kontrolliert.
- Der direkt aufgerufene interne Validator muss `TSPM1Error` mit genau
  `TSPM1_COMPOSITE_OR_FAST_STATE_INVALID` liefern.
- Die oeffentliche NN-Konfigurationspruefung erwartet unveraendert `S2NNError`.
- Keine allgemeine Exception-Akzeptanz und keine Produktkorrektur.

Der bestehende reportlokale Qualifikationsaufruf erhaelt nur die neue ID und
diese zusaetzliche Dokumentbindung. Vor dem Test bindet er das vollstaendige
Inventar und die Quellhashes; danach vergleicht er die Hashes und prueft die
weiterhin geschlossenen Gates. Das erste Laufverzeichnis wird weder
ueberschrieben noch nachtraeglich ergaenzt. Historische Komponenten, Profile,
Regeln und Ressourcenlimits bleiben bytegleich.
