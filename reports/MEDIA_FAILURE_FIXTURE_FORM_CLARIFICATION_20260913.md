# Fehlerform: Abweichende neutrale Fixture

## Anlass und Stand

Statische Eingangsprüfung zur freigegebenen Diagnosekompaktierung.
Repositorybasis: `537109994cf777f8d36cda617aafe12226806c25`, bestehender
Arbeitsbaum unverändert übernommen. Kein Testaufruf in dieser Klärung,
keine Payload-, Decoder-, Rezeptor-, Memory- oder Medienausführung.

## Belegter Unterschied

- `tools/_media_restart_checkpoint.py:275` legt die aktuelle Ausnahme als
  `self.failure["details"]` ab.
- `tools/_media_restart_checkpoint.py:303` publiziert die Hülle
  `status`, `failure`, `gate`. Ein zusätzliches oberstes `details`-Feld
  wird dort nicht erzeugt.
- Der gespeicherte historische Fehler
  `media-restart-real-20260913-01/reference/failure.json` hat genau diese
  Verschachtelung; seine historischen Details stehen unter `failure.details`.
- `tests/test_media_publication_plan.py:182` setzt hingegen
  `fixture["details"] = error.details`. Die historischen inneren Details
  bleiben unverändert und die neuen werden zusätzlich außen gespeichert.
- Die folgende Größenassertion in Zeile 183 misst diese abweichende
  Doppelhülle. Sie ergibt im gespeicherten Testlog 4.593 Byte. Die
  Publikation in Zeile 184 und die Einmaligkeitskontrolle wurden nicht erreicht.

Damit ist eine fehlerhafte neutrale Eingangsform statisch belegt. Die Zahl
4.593 ist eine gültige Messung dieser Fixture, aber noch kein Nachweis,
dass der produktive aktuelle Sitzungsfehler die 4.096-Byte-Grenze verletzt.
Die historischen und neuen Details sind zudem nicht identische Werte;
ihre Zusammenlegung als vermeintlich verlustfreie Dubletten wäre falsch.

## Kleinste Korrekturrichtung

Zunächst wäre eine neue neutrale Fixture mit der tatsächlichen
Sitzungshülle zu binden: aktuelle Details ausschließlich an der vorgesehenen
Stelle `failure.details`, historische Herkunft separat und unverändert.
Eine explizite Formkontrolle muss die versehentliche zusätzliche oberste
Ablage ausschließen. Danach wären Größe, vollständige Veröffentlichung
und Einmaligkeit gezielt zu prüfen. Das ist eine Testbindungskorrektur,
noch keine begründete Änderung der produktiven Fehlerdarstellung.

Die Größe dieser korrigierten Form wurde hier nicht berechnet. Es wird
weder behauptet, dass sie passt, noch dass die Kompaktierung nötig bleibt.
Eine neue Referenzmechanik wird nicht auf Grundlage der falschen Fixture
implementiert. Falls die korrekt gebundene Form weiterhin zu groß ist,
bleibt die freigegebene verlustfreie Diagnosekompaktierung die danach zu
prüfende Richtung; keine Grenzerhöhung.

## Abschlussgrenze

`media-publication-plan-qualification-20260913-01` bleibt unverändert
`NOT_QUALIFIED` mit 11/12 bestandenen Gruppen. Frühere Fehlerdateien,
Testquellen, Logs und Zahlen wurden nicht ersetzt. Keine Neuqualifikation
verbraucht, keine Produktkorrektur vorgenommen, Gates False.

RÜCKMELDUNG ERFORDERLICH: Den Nachfolgeauftrag auf die zunächst notwendige
Fixture-/Formkorrektur beziehen. Eine produktive Kompaktierung ist aus dem
vorliegenden Größenfehler allein nicht begründet. Die Medien-Erfolgshülle
bleibt unabhängig davon offen.
