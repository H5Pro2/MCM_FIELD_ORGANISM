# S2-DH: Privater TSPM-1-Fast-Kern und atomarer Koordinator

## Auftrag und Grenze

S2-DH implementiert ausschliesslich den privaten TSPM-1-Fast-Kern, gebundene
Expositions- und Probehuellen, einen atomaren Konsolidierungskoordinator und
synthetische Vertragstests. Die bestehende PPB-1-Implementierung bleibt
unveraendert.

Nicht Gegenstand sind oeffentliche API, Feldsnapshot, Feldpfad, Produktion,
reale Sensor- oder Feldlaeufe, synthetisches Replay, Semantik oder ein
weitergehender Funktionsclaim.

## Implementierter privater Grundpfad

`mcm_field_organism._tspm1_private` bindet eine auditive und eine visuelle
Exposition an dieselbe validierte Rezeptorhuelle. Die Bindung akzeptiert nur
die bereits im jeweiligen Stream enthaltenen Timed-Frame-Objekte und leitet
ihre funktionalen IDs und Digests deterministisch ab.

Der schnelle Zustand besitzt eine feste Slotkapazitaet. Ein Schritt fuehrt in
fester Reihenfolge aus:

1. faellige Slots verwerfen;
2. vollstaendige audiovisuelle Uebereinstimmung suchen;
3. passenden Slot aktualisieren oder einen freien beziehungsweise nach LRU
   bestimmten Slot belegen;
4. Teilassoziationskonflikte kennzeichnen, ohne einen bestehenden Slot
   einseitig umzuschreiben;
5. bei erreichter Unterstuetzung genau die beiden aktuellen Originalframes
   atomar an die unveraenderten PPB-1-Baenke uebergeben;
6. erst nach vollstaendiger Validierung Nachzustand, Receipt und terminalen
   Owner veroeffentlichen.

Scheitert ein Teil der Konsolidierung, entsteht weder ein teilweiser
Composite-Nachzustand noch ein Receipt. Der Owner wird terminal `FAILED` und
kann nicht erneut verbraucht werden.

## Read-only Probe

Die private Probe veraendert weder Fast-Zustand noch PPB-1-Baenke. Sie haelt
Fast-, auditive PPB-1- und visuelle PPB-1-Befunde getrennt. Ein vollstaendiger
langsamer PPB-1-Kontext hat Vorrang vor einem vollstaendigen schnellen Match;
anderenfalls wird der Fast-Kontext oder `NO_COMPLETE_CONTEXT` gemeldet.

Der Probe-Befund ist an Quell-, Konfigurations-, Vorzustands- und
Bankdigests gebunden. Es gibt keinen Nachzustand und keinen Feldhandoff.

## Synthetische Vertragspruefung

Elf neue S2-DH-Tests pruefen:

- Quellen- und Objektidentitaetsbindung der Expositions- und Probehuellen;
- Erzeugung, Match, Aktualisierung und getrennte Konsolidierung;
- Teilassoziationskonflikte ohne einseitige Slot-Aenderung;
- deterministische LRU-Verdraengung und Ablauf;
- atomaren Abbruch beim Fehlschlag des zweiten PPB-1-Schritts;
- terminales Fail-Closed-Verhalten bei stale Quelle und Retry;
- read-only Abruf und Unveraenderlichkeit aller drei Speicherachsen;
- private Paketgrenze und direkte Nutzung der Originalframes.

Alle 11 neuen Tests bestehen. Zusaetzlich bestehen 49 fokussierte
Regressionstests fuer PPB-1, die S1-WU-Probe und die aktive
Rezeptorbatchbindung. Damit bestehen im qualifizierenden Umfang 60 von 60
Tests.

Die vollstaendige historische Suite umfasst 7.056 Tests und wurde nicht als
S2-DH-Qualifikationslauf verwendet. Ein begonnener Gesamtlauf wurde wegen
dieses Umfangs beendet; dabei trat ein bereits ausserhalb von S2-DH liegender
Importfehler in `test_contact_reproduction_probe` auf. Dieser Befund veraendert
das fokussierte S2-DH-Ergebnis nicht.

## Entscheidung

`PASS_PRIVATE_TSPM1_FAST_CORE_AND_ATOMIC_COORDINATOR_CONTRACT_TESTS`

Der technische private Pfad fuer kurzfristige audiovisuelle Aufnahme,
Aktualisierung, Ablauf, Konfliktbehandlung, atomare Konsolidierung in zwei
unveraenderte PPB-1-Baenke und spaeteren read-only Abruf ist implementiert
und synthetisch abgesichert.

Dies ist ein Engineeringbefund ueber eine private technische
Memory-Komponente. Er ist kein Befund einer eigenstaendigen MCM-Feldmechanik
und keine Feldwirkung.

## Naechster Schritt

Der fachlich naechste Schritt ist S2-DI als statischer Abschlussaudit der
S2-DH-Implementierung. Er sollte Quellenbindung, Zustandsinvarianten,
Atomaritaet, PPB-1-Unveraendertheit, Testabdeckung und private Grenze anhand
des implementierten Codes abnehmen, ohne neue Funktion oder Ausfuehrung
hinzuzufuegen.
