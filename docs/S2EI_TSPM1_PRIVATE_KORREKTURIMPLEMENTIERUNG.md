# S2-EI: Private Korrekturimplementierung

## Auftrag und Stand

Die ausdrueckliche Benutzerfreigabe erlaubt die Umsetzung des S2-EH-Vertrags
in genau zwei bestehenden privaten Dateien und die Anpassung der neun
gebundenen Testdefinitionen. Ausgangscommit:
`67e6c306b48cae9f73555d841f1e460900c64f47`.

`PRIVATE_CORRECTIONS_IMPLEMENTED_NO_EXECUTION`.

Dies ist eine technische Korrektur des Vergleichswerkzeugs, keine neue
Speicherfunktion. Die anschliessende statische Abnahme steht getrennt in
`S2EG_REPEAT_AFTER_S2EI_TSPM1_STATISCHER_AUDIT.md`.

## Umgesetzt

- K1: Ein privater Quellmatcher bindet den einzigen zugelassenen
  S1-WU-Generator an Quellpfad, Blob, Rohbytes, L1-Call-Zeile und eindeutiges
  Codeobjekt. Am Erfassungsort werden auch das tatsaechliche Caller-Codeobjekt,
  der Callee und gleiche Operandenlaengen von 8 oder 18 geprueft. Die spaetere
  Belegpruefung verwendet dieselbe Zuordnung. Es gibt keine allgemeine
  Generatorfreigabe und keine neuen Belegfelder.
- K2: Die private Abschlusssequenz setzt die Final-Flush-Bestaetigung erst
  nach erfolgreicher Rueckkehr aus `publish`. Auf die vollstaendige
  Finalpruefung folgt die exklusive `COMPLETED`-Journalzeile 114, verkettet mit
  `SEALED` an Position 113. Der bestehende Recordtyp und seine Hashregeln
  bleiben erhalten. Die spaetere Zeile wird nicht im Artefakt referenziert.
- K2: Eine nur sichtbare Finaldatei ergibt bei unbestaetigtem Abschluss
  `ABORTED_INCOMPLETE`; die Reservierung bleibt verbraucht. Ein alleiniger
  Terminal-Flush-Fehler kann nur nach erfolgreichem Final-Flush und mit
  vollstaendig lesbarer Terminalkette einen Abschluss tragen. Es gibt keinen
  Retry. Ein bereits vollstaendig gepruefter Abschluss wird intern an seinen
  Artefaktdigest gebunden und durch einen spaeteren I/O-Fehler nicht umgedeutet.
- K3: T01, T34-T39, T46 und T51 sowie deren private Helfer sind angepasst.
  Alle 51 Testdefinitionen bleiben erhalten. G1-G5 und P1-P9 sind Unterfaelle
  innerhalb der gebundenen Definitionen, keine neue Testfamilie.

## Testgrenzen

Die Comparator-Pruefungen verwenden literale 18-Proben-Beobachtungen und
reine Test-Datentraeger. Der echte Comparator wird nur innerhalb eines
lokalen Attestationsmocks erreicht. Vor und nach diesem Mock muss die echte
Grenze dieselben Daten verwerfen. Aufruf und Argumente werden kontrolliert.
Es werden weder native Armzustaende gebildet noch Zell-Owner verbraucht.

Die Veroeffentlichungsunterfaelle verwenden ausschliesslich In-Memory-Pfade
und einen simulierten Store. Die Artefakt-Inhaltspruefung wird dort isoliert;
die echte Journalverkettung und Abschlusssteuerung bleiben Gegenstand der
Unit-Pruefung. Diese Definitionen sind kein Beleg fuer echte Dateisystem- oder
Produktionsdauerhaftigkeit. Sie rufen weder `run_once` noch Windows-APIs auf.

## Unveraenderte Bestandteile

Unveraendert bleiben H1-H7, alle acht Arme, die 18 neutralen Sollproben,
P1-P5, Kapazitaeten, Operationsgrenzen, Wortbreiten, Comparator, Tie-Regeln,
R0-Projektion, kanonische Hashverfahren und historische Belegdokumente.
TSPM-1-Grundkern, PPB-1, S1-WU, oeffentliche API und Feldpfad sind unveraendert.
`_EXECUTION_RELEASE_ENABLED` bleibt `False`.

Die beiden geaenderten Dateien erhalten neue Rohbyte- und Git-Blob-Belege
im JSON-Anhang. Rohbytehashes beschreiben die geprueften lokalen LF-Bytes;
Git-Blobs binden die versionierte Darstellung unabhaengig von einem spaeteren
CRLF-Checkout. Historische Rohbytebelege werden nicht ueberschrieben.

## Verifikation und Grenze

Durchgefuehrt: Lesen, Diffpruefung, AST, Compile-only, Symbolauflosung,
Record-Feldabgleich und Hashvergleich. Kein kompiliertes Projektcodeobjekt
wurde ausgefuehrt; kein Projektmodul wurde fuer die Pruefung importiert.

Nicht durchgefuehrt: Test-Collection, Tests, Zustandsfunktionen, Proben,
Comparatoraufrufe, Vergleichszellen, Matrix, Plattformfaehigkeitspruefung
oder reale Veroeffentlichung. Die strukturelle Wahrnehmungsrepraesentation
bleibt unbewertet. Kein Memory- oder Feldwirkungsbefund.

WEITER: Am besten geht es jetzt mit der getrennten statischen
S2-EG-Wiederholungsabnahme dieses Quellstands weiter.
