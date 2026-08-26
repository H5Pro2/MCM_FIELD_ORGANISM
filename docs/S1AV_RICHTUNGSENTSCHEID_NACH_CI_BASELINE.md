# S1AV: Richtungsentscheid nach Abschluss der C_i-Baseline

## Entscheidung

Die C_i-Linie ist als technische Referenzbaseline abgeschlossen. Die
passiven N0-, N1- und N2-Laeufe sowie der amplitudenkontrollierte leaky-
Vergleich zeigen keine eigenstaendige Substratsignatur.

```text
C_i technisch implementiert:                 ja
C_i von leaky im Nullkontakt getrennt:       nein
Feldkopie-Rueckwirkung reproduzierbar:       ja
MCM-Memory nachgewiesen:                     nein
neuer Substratkandidat freigegeben:          nein
```

## Konsequenz

Die Substratlinie wird nicht durch weitere Parameter, Gap-Laengen oder
Rueckwirkungsverstaerkungen fortgesetzt. Das waere nur eine weitere
Engineering-Variante ohne bestandene statische Nichtreduktionsbedingung.

Aktiv bleibt die technische Feld-Engineeringlinie:

```text
kontrollierte AV-Testwelt
-> Rezeptorsequenzen
-> gemeinsames MCM-Feld
-> S/H-Zustand
-> transparente Referenzarme
-> Snapshot, Zeit- und Reproduzierbarkeitspruefung
```

Zulaessig sind weiterhin Stabilitaet, Zeituebergabe, Snapshot/Restore,
Rezeptorpfad, Baseline-Kompatibilitaet und kontrollierte Feldvergleiche.

## Forschungsgrenze

Ein neuer Substratkandidat darf erst wieder geoeffnet werden, wenn er vor der
Implementierung das Wiedereroeffnungstor aus S1-AA erfuellt. Insbesondere
muss er eine eigene, vorhersagbare Naturrolle besitzen und sich statisch von
leaky, Integrator, Hysterese, F3 und Standardmaterial unterscheiden.

Bis dahin bleiben Begriffe wie Praegung, Vergessen, episodisches Speichern,
innerer Kontext, Feldzeit oder Memory reine Zielhypothesen und werden nicht
als Projektbefund verwendet.

## Naechster konkreter Arbeitsweg

Die naechste technische Arbeit ist kein neuer Memory-Lauf, sondern die
Bereinigung und Staerkung der aktiven Feld-Engineeringoberflaeche: aktuelle
AV-Testwelt, Rezeptorsequenz, Feldschritt, Snapshot und Baselines muessen
weiterhin reproduzierbar und getrennt von historischen oder gesperrten
Substratpfaden bleiben.
