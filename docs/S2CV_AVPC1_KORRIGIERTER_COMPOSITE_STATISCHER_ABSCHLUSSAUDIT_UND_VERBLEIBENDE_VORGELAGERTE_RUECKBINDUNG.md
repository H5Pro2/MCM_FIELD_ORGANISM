# S2-CV: Statischer Composite-Abschlussaudit

## Ergebnis

Die drei in S2-CT gefundenen Kindausgabenblocker sind durch S2-CU korrekt
geschlossen. Formation, einzelner Relationsschritt und atomarer Endabruf
werden vollstaendig an ihren jeweiligen Composite-Aufruf zurueckgebunden.

Der weitergefuehrte statische Audit findet jedoch drei vorgelagerte
Rueckbindungsgrenzen, die bisher nur durch nachfolgende Kindvalidierung
abgesichert sind. Der Composite ist deshalb noch nicht abschliessend
geschlossen.

In S2-CV wurden keine Projektmodule importiert und keine Tests oder
Zustandsfunktionen ausgefuehrt.

## Geschlossene S2-CT-Blocker

Das Formationsergebnis bindet jetzt Frischzustaende und Owneridentitaeten.
Jeder Relationsbildungsbefund bindet den exakten Frame-, Partitions-,
Vorzustands- und Ownerumfang. Jeder atomare Abruf bindet den konkreten
Umschlag, Finding, Relationszustand, visuellen Bankzustand und seine
Kindaufruf-IDs. Die drei adversarialen S2-CU-Substitutionen decken diese
Grenzen direkt ab.

## Blocker 1: Initialer Relationszustand

Der Rueckgabewert von `initial_avpc1_bounded_relation_state` wird direkt als
Spurvorzustand verwendet. Der Composite prueft danach nicht selbst, ob
Tabellen-ID, Profil, auditive und visuelle Bankidentitaeten und -digests,
Prototypinventare, Relationspartition, freie Slots und Nullverbrauch exakt
dem vorgesehenen Spuraufruf entsprechen.

Ein intern gueltiger fremder Initialzustand koennte damit die deterministisch
vorgesehene Tabellenidentitaet ersetzen.

## Blocker 2: Audio-only-Probenhuelle

Die von `bind_avpc1_private_auditory_only_probe_envelope` gelieferte Huelle
wird nicht unmittelbar gegen die beabsichtigte Binding-ID, Quellbindung,
Sequenz, Profil-, Bank- und Partitionsdigests, Snapshotprovenienz und die
Eingabeanzahlen eins auditiv und null visuell zurueckgebunden.

Der atomare Leseconsumer prueft spaeter nur die ihm tatsaechlich uebergebene
Huelle. Er kann deshalb nicht erkennen, ob der Composite statt der
beabsichtigten Probe eine andere intern gueltige Huelle erhalten hat.

## Blocker 3: Auditiver read-only Prototypbefund

Der von `probe_s1wu_perceptual_state` gelieferte Befund wird vor dem Abruf
nicht unmittelbar gegen Probe-ID, auditive Modalitaet, Bank-, Konfigurations-
und Zustandsidentitaet sowie den exakten Eingabeprojektionsdigest der
beabsichtigten Probesequenz gebunden.

Werden Huelle und Befund gemeinsam konsistent substituiert, kann der atomare
Leseconsumer beide als zueinander passend akzeptieren. Die S2-CU-
Endabrufrueckbindung bindet dann korrekt an die substituierten lokalen Werte,
nicht an die urspruenglich beabsichtigte Probe.

## Erforderliche Korrektur

S2-CW darf ausschliesslich diese drei vorgelagerten Rueckbindungen ergaenzen:

1. exakter Initialrelationszustand gegen Spur-ID und alle Quellen;
2. exakte Audio-only-Huelle gegen die beabsichtigte Probe;
3. exakter auditiver Finding gegen Probe, Bank und Eingabeprojektion.

Je Grenze ist eine digestkonsistente fremde Ausgabe zu testen. Gemeinsam
substituierte Huelle und Finding muessen vor dem atomaren Endabruf scheitern.
Danach ist der fokussierte Integrationsumfang erneut auszufuehren.

Neue Mechanik, Parameter, Fixturewerte, Comparatoren, oeffentliche API,
Feld-, Produktions-, Live- oder Semantikpfade bleiben ausgeschlossen.

## Einordnung

Die verbliebenen Blocker betreffen ausschliesslich die Beweiskraft der
Composite-Quellkette. Die technische Funktion und ihre Erklaerung durch die
generische Baseline bleiben unveraendert.
