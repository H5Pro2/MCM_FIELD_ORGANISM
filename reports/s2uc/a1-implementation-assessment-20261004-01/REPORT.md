# A1-Implementierung und neutrale technische Qualifikation

A1 ist als separate, standardmäßig deaktivierte Option implementiert. Die
Prüfkriterien A01–A11 sind abgedeckt und bestanden; A10 wurde nach Korrektur
einer falschen Testannahme gezielt erneut bestanden. Drei ergänzende Prüfpakete
bestehen ebenfalls. Es wurde kein T1-/F-Replay und kein Forschungsvergleich
ausgeführt. Ein Forschungsvorteil ist weiterhin nicht nachgewiesen.

## Implementierung und Schnittstelle

`tools/_s2uc_a1.py` ergänzt `create(..., admission_policy=...)`:
Default `disabled` liefert exakt den bisherigen MultiErrorAdapter mit
FactorRecencyArm. A1 erfordert ausdrücklich `unique_partial_admission_v1` und
die bestehende aktivierte Multi-Fehlerpolicy. Kein K1-Arm und keine K1-Frist.
Bestehende U-Dateien wurden nicht geändert.

Die neue A1Adapter-Unterklasse verändert ausschließlich den Receipt-/Zulassungspfad:
eindeutige berechtigte Kandidatenhypothese prüfen, vorhandene vollständige
Bestätigung bevorzugen, gegebenenfalls älteste Retained-Spur entfernen,
Originalframes verschieben, vorhandene Zellen mit der geerbten Promotionslogik
umschlüsseln, Revision erhöhen, tatsächlichen Bestand erneut lesen, neue Prognose
und Tickets einfrieren, Hinweisframes durch den geerbten Pfad aufnehmen.

Die ursprüngliche Frametupel-Identität bleibt erhalten. `_observation_end` der
zugelassenen Spur beginnt beim Ende ihrer ursprünglichen Aufnahme, nicht beim
Teilhinweis. Weitere Retained-Abrufe verjüngen die Spur nicht. Kein neuer
persistenter Armzustand, kein Zusatzslot und keine zusätzliche Fehlerbank.

Receiptbelege tragen `PARTIAL_RETRIEVAL_ADMISSION`, `full_repeat=false`,
Originalordinalen/Offset, Hinweisordinalen, alte/neue Schlüssel und konkretes
Verdrängungsopfer. Alle A1-Receipts kennzeichnen die Retained-Bedeutung als
`ADMITTED_NOT_FULL_REPEAT_PROOF`; der bisherige Status CONFIRMED_RETAINED_MATCH
wird dort zu RETAINED_ORIGINAL_MATCH. Diese Daten bestätigen Abrufrelevanz,
keine vollständige Wiederholung. Eine A1-Zulassung zählt im neuen Referenzbeleg
als eigenes Ereignis, nicht als vollständige Promotion.

Die bisherigen eingefrorenen U/K1-Auswerter und Runner bleiben unverändert und
sind nicht für A1 freigegeben oder an A1 angeschlossen. Ihre Revisionserwartung
und die Interpretation des Retained-Bestands dürfen nicht stillschweigend auf
A1 übertragen werden. Ein künftiger A1-Auswerter muss die explizite Semantik
berücksichtigen; Kompatibilität mit alten Auswertungen wird nicht behauptet.

## Fehleratomarität

Die Zulassung wird im synchronen Adapter als nicht öffentlich nutzbarer
Zwischenzustand durchgeführt. Ein Fehler vor, während oder nach der Übertragung
führt zum vorhandenen schließenden Fehlerabschluss: Arm geschlossen, Kandidat,
Retained-Spuren, bildende Frames, eingefrorene Referenzen und Bank geleert.
Es bleibt kein teilweise veränderter **weiterverwendbarer** Bestand zurück.
Das ist ausdrücklich Fail-closed, kein Rollback auf einen weiterhin offenen
alten Bestand. Ein Return mit teilweise erfolgter Zulassung ist ausgeschlossen.

Neun gezielte Fehlerstellen wurden geprüft: Vorbereitung, Opferentfernung,
Originalverschiebung, Generations- und Rollenumschreibung der Zellen, abgeschlossene
Zellübertragung, Revision, eingefrorene Prognose und endgültiger Receipt.
Scope-, Generations- und bereits-offene-Prognosefehler führen ebenfalls zum
geschlossenen bereinigten Zustand. Kein Wiederaufleben toter Schlüssel.

## Dateien und unabhängige Referenz

- `tools/_s2uc_a1.py`: Produktionsoption und Zulassungsbelege.
- `tools/_s2uc_a1_reference.py`: unabhängige A1-Entscheidung auf eigenen
  Beobachterlisten und Werten, ohne Produktions-Zulassungsaufruf. Unveränderte
  U-Viererabschlüsse stammen aus der bereits unabhängigen Referenzmaschine.
- `tools/_s2uc_a1_probe.py`: neutrale Fortschreibung mit eigener Bestands-,
  Fehler-, Auswahl-, Revisions- und Ticketprüfung; getrennte Heap-/Trace-Pässe.
- `tests/test_s2uc_a1.py`, `tools/s2uc_a1_qualify.py`: Prüfkriterien und
  unveränderlich erhaltene Versuche samt Quelltext-Snapshots.
- `tools/s2uc_a1_supplement.py`: sechs berechtigte Hypothesen und Faktorausschluss.
- `tools/s2uc_a1_warm_stock_check.py`: volle sechs Fehlerzellen mit tatsächlicher
  Zulassung, warmer Auswahl, Opferentfernung und Originalübertragung.
- `tools/s2uc_a1_full_candidate_check.py`: eindeutiger Teilmatch bei gleichzeitig
  vollständiger Kandidatenwiederkehr; U-Bestätigung erhält Vorrang.
- `tools/s2uc_a1_check_binding.py`: rein lesender endgültiger Bindungsprüfer.

Die Referenz entscheidet anhand der eigenen lebenden Originalspuren und der
bereits eingetroffenen Hinweiswerte. Sie zählt berechtigte Hypothesen selbst,
prüft die vollständige Konkurrenz, verschiebt ihre eigene Originalspur und
führt die normale U-Segmentierung fort. Im Probe-Pfad werden Bestand,
vorzielliche Fehlerzellen, Tickets, Auswahl und Revision mit der Produktion
verglichen. Referenzdaten und zukünftige Zielwerte gelangen nicht in die Policy.

## Prüfergebnisse und nachvollziehbare Korrektur

| ID | Umfang | Endgültiger Nachweis |
| --- | --- | --- |
| A01 | Zulassung, lebendiges Feedback, erneuter warmer Abruf, neue Kandidatenaufnahme | PASS in02 |
| A02 | Mehrere Spuren/Offsets, auch identische Nachfolger | PASS in02 |
| A03 | Vollständige Retained-Bestätigung hat Vorrang | PASS in02 |
| A04 | Selbst-/Überlappungsausschluss und Match ohne Nachfolger | PASS in02 |
| A05 | Originalidentität, beide Fehleroffsets, gültige neue Schlüssel, Opfer und Revision | PASS in02 |
| A06 | Irreführender Hinweis und Verlust einer zuvor warmen verdrängten Spur | PASS in02 |
| A07 | Keine Verjüngung durch Retained-Abruf | PASS in02 |
| A08 | Neun injizierte Zulassungs-/Veröffentlichungsfehler, danach geschlossen und leer | PASS in02 |
| A09 | Default aus, Scope/Generation/Pending, unvollständiges Storyende | PASS in02 |
| A10 | Getrennte Heap-/Frame-Pässe und tatsächliche Zwei-Ausgabe-Kontextwahl | PASS in03 |
| A11 | U-Fabrik identisch zur bisherigen Klasse; geerbte Methoden unverändert | PASS in02 |

Versuch01 bestand als fokussierte Vorprüfung10 Tests. Versuch02 führte alle11
Tests aus; zehn bestanden. A10 scheiterte ausschließlich an der Erwartung,
die Verdrängungssequenz müsse zwei Ausgabeslots erzeugen. Tatsächlich gab sie
maximal einen aus und verletzte keine Ressourcengrenze. Die gespeicherten
Heap-/Trace-Ergebnisse stimmten in Prognosen und Fehlern überein.

Korrigiert wurde nur diese Testannahme: Der Verdrängungsfall prüft höchstens
zwei Slots; eine zusätzliche kurze Sequenz mit tatsächlicher warmer Kontextwahl
muss exakt zwei erreichen. Versuch03 wiederholte gezielt A10 und bestand.
Produktion, Referenz und Probe blieben bytegleich. Ein AST-Abgleich bestätigt,
dass die übrigen zehn Testmethoden unverändert sind; sie wurden nicht erneut
ausgeführt. Der Qualifikator erhielt lediglich eine Auswahl für gezielte Tests.
Es gibt somit keinen als vollständig grün ausgegebenen Versuch02: Dessen
FAILED-Abschluss bleibt unverändert sichtbar. Der endgültige Nachweis kombiniert
die gültigen zehn Kriterien aus02 mit der bestandenen Korrektur03.

Zusatzprüfungen: `a1-six-hypotheses-20261004-01`,
`a1-warm-stock-20261004-01`, `a1-full-candidate-20261004-01`: jeweils PASS.
Die letzte ergänzt den Vorrang der vollständigen Kandidatenbestätigung bei
genau einer berechtigten Teilhypothese, also ohne bloß wegen Mehrdeutigkeit
untätig zu bleiben.

Die drei Qualifikationsversuche umfassen19 gespeicherte Probe-Ausführungen
mit390 Eingangspositionen, einschließlich getrennter Messpässe und Teilstory.
Die U-Fabrikprüfung vergleicht zusätzlich je zwei U-Adapter über12 Positionen
in01 und02. Direkte neutrale Bestands-/Fehlerfixtures und Zusatzprüfungen sind
davon getrennt; daraus wird keine Forschungsfallzahl gemacht.

## Gemessene Ressourcen

| Ressource | Maximum im qualifizierten Umfang | Grenze |
| --- | --- | --- |
| Zusatz-Pythonheap | 6.679 Byte | 16.384 Byte |
| Verschiedene Originalframes im separaten Trace | 16 | 18 |
| Ausgabeslots | 2 | 2 |
| Gleichzeitig gemessene kombinierte Belegung | 17 | 20 |
| Konservative kombinierte Obergrenze im Heap-Pfad | 18 | 20 |
| Gepackte Fehler-/Ticketbank | 416 Byte | 416 Byte |
| Receipt einschließlich A1-Semantik und Zulassungsbeleg | 1.473 Byte | 16.384 Byte |
| Abgeleitete UTF8-Obergrenze | 2.946 Byte | 32.768 Byte |

Die volle Sechshypothesenprüfung misst den längsten Receipt; die volle
Sechszellenprüfung umfasst warme Zulassung und Verdrängung. Der Trace verfolgt
auch temporäre Produktionsreferenzen, insbesondere Kandidat, Opfer und
vorherigen Bestand während der Übertragung. Unterschiedliche Maxima werden
nicht fälschlich zu einem gleichzeitig beobachteten Maximum addiert.

Heap und Trace wurden getrennt erhoben. Nullwerte deaktivierter Messarten
bedeuten nicht gemessen. Die Trace-Qualifikation ist langsam: Versuch02 etwa
112,465s, die gezielte Ressourcenprüfung03 etwa140,950s. Das sind Messwerkzeug-
Laufzeiten, keine Aussage zur Laufzeit eines späteren Forschungsreplays.
Zusatzheap ist kein Gesamtprozess-RAM. Die Zahlen gelten für den neutral
qualifizierten Umfang; ein späterer Vergleich muss seine Grenzen erneut
während der Ausführung überwachen.

## Neutrale Erfahrung und Verlustseite

Die neutralen Werte verwenden .125+(Index+1)/512+j/262144 und keine T1-/F-Quelle.
Die symbolische Erfolgsfolge erzeugt bei Hinweis7–8 eine A1-Zulassung,
Feedback bei9 und erneute warme Kontextwahl für13. A1-MAE0 gegenüber
U-MAE0,001953125. Das ist ein technischer vollständiger Erfahrungszyklus,
kein Nachweis eines allgemeinen Vorhersagevorteils.

Im irreführenden Gegenfall ist derselbe warme Nachfolger bei13 falsch:
A1-MAE0,00390625 gegenüber U-MAE0,001953125. Im Verdrängungsfall wird die zuvor
warme Originalspur1–4 bei24 zugunsten einer neuen Teilabrufzulassung entfernt.
Beim späteren Ziel29 erzielt A1-MAE0,001953125, U-MAE0. Die verdrängte Fehlerzelle
war vor dem Opferereignis belegt; ihre spätere fehlende Nutzung wird nicht
als bloß theoretischer Preis ausgewiesen.

## Codebindung und Anschluss

Eindeutige endgültige Bindung:
`docs/S2UC_A1_IMPLEMENTIERUNGSBINDUNG_20261004.json`.
Sie bindet geerbten unveränderten Code, A1-Code, Referenz, Tests, Konzept und
gespeicherte Prüfnachweise. Ihr SHA256 steht in der Abschlussversiegelung
dieses Ordners. Rein lesender Prüfbefehl im Workspace:

```powershell
& C:\Python314\python.exe -m tools.s2uc_a1_check_binding
```

Empfehlung an den Projektleiter: A1 im dokumentierten neutralen Umfang technisch
abnehmen. Anschließend genau einen fest gebundenen U/A1-Vergleich vorbereiten,
der eigene Referenzen, die zusätzliche Revisionsänderung, Teilzulassungen und
vollständige Bestätigung getrennt auswertet. Die vorhandenen Nutzen- und
Schadenskriterien bleiben bestehen. Quellenmaterialisierung, Forschungsreplay
und Einmalausführung sind nicht Teil dieses Abschlusses und nicht erfolgt.
