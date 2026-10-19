# K1-Implementierung: Abschluss und technische Abnahmevorlage

K1 ist optional implementiert und neutral qualifiziert. K01–K10:10/10 PASS;
K08b und K05c/K06c:PASS. Der aktuelle Code entspricht der Bindung der erfolgreichen
Qualifikation 02. Defaults bleiben deaktiviert. Kein Forschungsvorteil ist damit
nachgewiesen; der 24-Fälle-Vergleich wurde nicht ausgeführt.

## Änderungen und Codebindung

- `tools/_s2uc_k1.py`: ausschließlich zusätzliche Kandidatenabschlussregel;
  Erhaltung am ersten abweichenden Folgeblock, Ende spätestens am zweiten;
  exakte Promotion auch am Fristende. Keine zusätzlichen persistenten Armfelder.
  Eigener exakter K1-Typcheck im ansonsten gleichartigen Adapterkonstruktor;
  Abruf, Feedback, Promotion, Pruning und Auswahl sind geerbte Methoden.
- `tools/_s2uc_k1_reference.py`: unabhängige Beobachterregel für U und K1,
  ohne Aufruf der Produktions-Abschlussregel. Keine Beobachterdaten als Policyinput.
- `tools/_s2uc_k1_probe.py`: neutraler Prüfpfad, eigener Referenzzustand,
  Fehlerzellen-/Entscheidungsprüfung, getrennte Heap- und Frame-Messungen.
- `tests/test_s2uc_k1.py`, `tools/s2uc_k1_qualify.py`: K01–K10 samt Belegexport.
- `tools/s2uc_k1_resource_check.py`, `tools/s2uc_k1_ticket_check.py`:
  ergänzende Ausgabe- und Ticketprüfungen.
- `tools/s2uc_k1_check_package.py`: neuer rein lesender Integritätsprüfer.
- Neue Implementierungsbindung und Aufrufspezifikation in `docs/`, dieser
  Bericht mit maschinenlesbarem Abgleich; README und Forschungsweg aktualisiert.

Die endgültige Bindung ist
`docs/S2UC_K1_IMPLEMENTIERUNGSBINDUNG_20261003.json`.
Sie umfasst die unveränderten historischen Code-/Referenzbindungen, die neuen
K1-Dateien und alle hier zugeordneten Prüfbelege. Ihr SHA256 steht in closure.json
dieses Abschlussordners. Historische Archive wurden nicht verändert.

## Prüfbelege und behobener Fehler

| Prüfung | Nachweis | Ergebnis |
| --- | --- | --- |
| K01–K03 | Erhalten ohne versteckte Spur; fristgerechte Ersetzung; Promotion ursprünglicher Frames | PASS |
| K04 | Bestätigungspriorität/Recency und Fristfreigabe trotz anderer Bestätigung | PASS |
| K05–K06 | Tote Schlüssel ohne Wiederbelebung; erlaubte Promotionszellen | PASS |
| K07 | Default aus, Scope/Ordinalfehler, Ende/Teilblock, Generationgrenzen | PASS |
| K08 | Voller Bestand, sechs berechtigte Hypothesen, Heap/Frame-Bilanz | PASS |
| K09 | Verlorene neue Erfahrung und neutraler Schadensfall | PASS |
| K10 | Unveränderte geerbte Policy und jeweils eigene Referenz | PASS |
| K08b | Tatsächliche Kontextwahl mit zwei Ausgabeslots | PASS |
| K05c/K06c | Tickets, Prognose-/Nachfolgeridentitäten vor und nach Aufnahme identisch | PASS |

Primärbeleg: `../k1-neutral-qualification-20261003-02/` mit 15 Probes und258
Eingangspositionen, jeweils Referenzgleichheit und erfolgreicher Bereinigung.
Gesamtdauer188,7442188 s; unittest188,674 s. Keine Fehler, Fehlschläge oder Skips.

Versuch01 bleibt als FAILED erhalten: Vier direkte Testfixtures verwendeten
ein ungültiges Profil `neutral` statt einer64-stelligen Profilbindung und
scheiterten mit FRAME_BINDING_INVALID. Korrigiert wurde ausschließlich das
Testprofil. Die Produktion, Referenz, Probe und Qualifikationshülle blieben
zwischen01 und02 bytegleich. Die ursprüngliche Testdatei ist unter
`../k1-neutral-repair-20261003-01/` archiviert; ihr Hash stimmt mit Bindung01
überein. Vier fokussierte Reparaturprüfungen bestanden, danach die Gesamtprüfung02.

Zusatzbelege: `../k1-two-output-qualification-20261003-01/` und
`../k1-ticket-qualification-20261003-01/`. Diese Skripte importieren dieselben
K1-Module. Ihre damaligen Ergebnisdateien enthalten jedoch keine eigene
Vorstart-Codebindung. Ihre Zuordnung zum unveränderten Kern wird jetzt durch
Abgleich, Quellprüfung und gemeinsame Versiegelung nachvollziehbar gemacht;
dies ist keine nachträglich behauptete damalige Vorstartversiegelung.

Insgesamt wurden zuvor31 neutrale Probe-Ausführungen mit528 Eingangs- und
Referenzpositionen sowie drei Ticketprüfungen mit52 Eingangspositionen ausgeführt:
34 Adapterdurchläufe/580 Positionen, zusätzlich direkte Arm-Unitfixtures.
Im jetzigen Abschluss wurden nur Dateien/Hashes und vorhandene Belege geprüft;
keine bestandenen Verhaltenstests wurden wiederholt.

## Ressourcen und Aussagegrenzen

| Ressource | Beobachtetes Maximum | Grenze |
| --- | --- | --- |
| Zusatz-Pythonheap im bestehenden Messumfang | 9.136 Byte | 16.384 Byte |
| Verschiedene Originalframes, separate Trace-Messung | 16 | 18 |
| Ausgabeslots, Zusatzprüfung K08b | 2 | 2 |
| Kombiniert, tatsächlich gleichzeitig gemessen | 17 | 20 |
| Konservative kombinierte Bilanz im Heap-Prüfpfad | 18 | 20 |
| Gepackte Bank | 416 Byte | 416 Byte |
| Receipt | 1.468 Byte | 16.384 Byte |
| Abgeleitete UTF8-Obergrenze | 2.936 Byte | 32.768 Byte |

Heap und Frame-Trace sind getrennte Messungen. Nullwerte der jeweils deaktivierten
Messart bedeuten nicht gemessen. Maxima verschiedener Zeitpunkte werden nicht
addiert. Kein Gesamtprozess-RAM-Nachweis und keine vollständige Ressourcen- oder
Laufzeitqualifikation des noch fehlenden Vergleichsexecutors. Nach Abschluss
sind Kandidat, bestätigte Spuren, bildender Block, eingefrorene Referenzen und
Bank im geprüften Umfang bereinigt. Keine neuen persistenten Kandidatenmetadaten.

## Nachteile und neutraler Schaden

1. P,Q,Q: K1 verwirft den neuen Zwischenblock Q. U kann dessen Originalframes5–8
   beim nächsten Q bestätigen; K1 besitzt diese bestätigte Q-Spur dann nicht.
2. P,P,Q,P,P: K1 entfernt den Q-Kandidaten bei Position20 aufgrund der festen
   Frist. U behält ihn während der Bestätigungen von P. Längere Erhaltung ist
   somit keine allgemeine Dominanz gegenüber U.
3. Neutraler Schadensfall P,(0,1,2,12),(0,1,0,14): Bei Ziel11 wählt K1 den
   warmen alten Nachfolger. Sein MAE ist um1/256=0,00390625 größer als bei U.
   Das ist ein realer neutraler Gegenbefund, kein Ergebnis des reservierten F3.

Die neutralen Vektoren verwenden .25+(i+1)/256+j/65536, nicht die reservierte
F-Fixtureformel. F1–F8 wurden nicht erzeugt; T1 wurde nicht erneut abgespielt.
Ein neutral bestandener Schadensnachweis ist kein Nutzenbeleg.

## Anschlussentscheidung und offene Startgrenze

Das Implementierungspaket ist zur technischen Abnahme vorgelegt. Der Analyst
kann Regel, Nachweise und Nachteile anhand dieser Bindung beurteilen.
`docs/S2UC_K1_VERGLEICH_AUFRUF_20261003.md` fixiert alle24 Fälle und den
vorgesehenen Aufrufumfang sowie den ausführbaren Integritätsaufruf.

Ein ausführbarer U/K1-Vergleichsaufruf kann noch nicht geliefert werden: Ein
qualifizierter24-Fälle-Executor samt Auswerter, Quellen-/Maskenbindung und
Startqualifikation fehlt. Der vorhandene T1-Start darf dafür nicht eingesetzt
werden. Dies ist die konkrete verbleibende Lücke zu Punkt4 des Abschlussauftrags.
Empfehlung: K1 technisch abnehmen und als nächsten begrenzten Auftrag genau
diese Vergleichsvorbereitung freigeben; anschließend anhand ihrer neutralen
Qualifikation über die separate Einmalausführung entscheiden. Keine Regeländerung,
neue Variante oder pauschale Wiederholung der K1-Tests.
