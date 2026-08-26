# S2-CN: Zeitaudit-Quellrueckbindung und Intervallregression

## Korrektur

Der private Relationsbildungs-Consumer berechnet nun eine reine erwartete
Zeitauditprojektion direkt aus den vollstaendigen eingefrorenen Streams des
spaeteren Expositionsumschlags. Die Projektion verwendet exakt dieselbe
bestehende Ordnung und Intervallregel:

- auditive Frames aussen, visuelle Frames innen;
- Ueberlappungsstart als Maximum beider Feldfensterstarts;
- Ueberlappungsende als Minimum beider Feldfensterenden;
- Verwerfen nichtpositiver Schnittmengen;
- erneute Berechnung der eindeutigen, mehrdeutigen und nicht zugeordneten
  Snapshot-Inventare.

Das einmalig aufgerufene Audit muss dieser vollstaendigen Projektion exakt
entsprechen. Erst danach darf die erste read-only Probe beginnen. Fuer das
ausgewaehlte Paar gilt zusaetzlich die exakte Orientierung auditiv zu visuell.

## Adversarialer Test

Der neue Test liefert ein strukturell vollstaendiges Eins-zu-eins-Audit mit
denselben Snapshot-IDs, verschiebt aber den positiven Start des ausgewaehlten
Intervalls um einen Tick. Der Owner endet `FAILED`. Beide Proben, der
Ueberlappungsbeleg und die Relationsfortschreibung bleiben bei null Aufrufen;
ein Teilresultat entsteht nicht.

Der fokussierte Lauf besteht mit `13/13` Tests in `0.271 s`. Die bisherigen
gueltigen Ereignisse `PAIR_CREATED_PENDING`, `PAIR_CONFIRMED_STABLE` und
`KEY_MARKED_CONFLICTED` bleiben unveraendert.

## Einordnung

S2-CN schliesst ausschliesslich den S2-CM-Quellenrueckbindungsblocker. Es wurde
kein zweiter Auditaufruf, keine neue Zeitregel, keine neue Relationsmechanik
und kein oeffentlicher oder produktiver Pfad eingefuehrt.

## Naechster Schritt

S2-CO soll den korrigierten privaten Pfad statisch abschliessend pruefen. Der
Testlauf wird dabei nicht wiederholt.
