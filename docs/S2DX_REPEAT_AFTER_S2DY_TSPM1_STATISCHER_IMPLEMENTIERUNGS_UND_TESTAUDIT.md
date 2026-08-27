# S2-DX: Statischer Wiederholungsaudit nach S2-DY

## Auftrag und Quellen

Gepruefter Commit: `164e6625d1654c8fb2f5cbfd211d6e4a133cf8af`.
Dieser Audit ergaenzt den ersten S2-DX-Befund; er ersetzt dessen historischen
Quellstand nicht. Massgeblich sind die aktuelle Benutzerfreigabe sowie
S2-DQ, S2-DR, S2-DT, S2-DU, S2-DV und der S2-DS-Preflight nach S2-DV.

Geprueft wurden ausschliesslich Quelltext, AST, Aufruf-/Rueckgabepfade,
Git-Differenzen und kanonische Dokumentdigests. Keine Projektmodule wurden
importiert. Keine Tests, Zustandsfunktionen, Comparatoren oder
Vergleichszellen wurden ausgefuehrt. Es entsteht keine Laufnummer.

Die beiden privaten Dateien sind:

- `mcm_field_organism/_tspm1_s2dr_private_comparison.py`
- `tests/test_tspm1_s2dr_private_comparison_contract.py`

Zeilenangaben unten beziehen sich auf den geprueften Commit. Rohbyte-SHA256
des lokalen Quellstands und Git-Blob-IDs stehen im zugehoerigen JSON-Beleg.
Die sieben herangezogenen Vertrags-/Audit-JSONs besitzen gueltige kanonische
Eigendigests.

## Sechs beauftragte Pruefpunkte

| Punkt | Statischer Befund |
| --- | --- |
| Eigene generische R0-Zustaende | Bestanden. `_GenericFastSlot`, `_GenericFastState` und `_GenericTwoLevelState` enthalten keine TSPM-Typen. Die langsame Ebene verwendet unveraendertes PPB-1. |
| Keine TSPM-Operatoren im R0-Pfad | Bestanden. R0-Initialisierung, Fortschreibung, Projektion und Probe zweigen vor TSPM-Konfiguration/-Operatoren ab. `_advance_r0` implementiert die generische Fortschreibung selbst. |
| Vollstaendige R0-Projektion | Nicht bestanden. Die Projektion ist breiter als die bisherigen fuenf Bits, verwirft aber weiterhin gebundene Zustandsidentitaet; siehe DX-RB01. |
| T35-T39 und T51 erreichen den Comparator | Statisch bestanden. Alle sechs Definitionen rufen `synthetic_comparison` auf; dessen erreichbarer Rueckgabepfad ruft `compare_s2dr_results` auf. Kein Testbestehen wird daraus abgeleitet. |
| Kanonischer Plandigest in T44 | Bestanden. Der geaenderte Autorisierungsdigest wird in die Payload ohne Eigendigest eingesetzt und diese neu gehasht. Die Autorisierungsformel bleibt absichtlich falsch. |
| Slow-Prototypen an S1WU-Findings gebunden | Bestanden fuer den regulaeren Quellpfad. Slot, Distanz und Prototypdigest stammen aus dem S1WU-Finding; im TSPM-Arm werden beide Findingdigests und Status gegen die TSPM-Slow-Rollen abgeglichen. |

Das gemeinsame Vergleichsmodul importiert TSPM-1 weiterhin fuer den
TSPM1-Vergleichsarm. Die bestaetigte Trennung gilt fuer R0-Datentypen und
R0-Operatorpfade, nicht fuer einen TSPM-freien Import des gesamten Moduls.

Die S1WU-Quellfunktion validiert Bank und Probe, prueft die unveraenderte
Bankidentitaet und erzeugt ein selbst-digestvalidiertes Finding. Der neue
Helper `_s1wu_evidence` verwendet diese Quelle und ordnet erkannte
Prototypwerte dem ausgewaehlten belegten Slot zu. Die TSPM-Zuordnung in
Zeilen 1494-1512 vergleicht dieselben Probe-IDs und Findingdigests. Die
B1- und R0-Arme uebernehmen die jeweiligen S1WU-Findings direkt.

## Verbleibende Blocker

### DX-RB01: Die exakte Projektion verliert weiterhin Zustandsidentitaet

Quellen: Vergleichsmodul Zeilen 764-807 und 1950-2018;
`_ppb1_reference.py` Zeilen 229-316; S2-DQ `r0_projection`.

S2-DQ bindet die beiden PPB-Zustaende modalitaetserhaltend und unveraendert.
`_ppb_projection` uebernimmt jedoch nur Schrittzahl, Quelluhr, Endtick und
vier Werte je Slot. `bank_id`, `config_digest` und die PPB-`slot_id` fehlen.
Diese Rollen gehoeren zum unveraenderten PPB-Zustand und sind keine
TSPM-spezifischen Typ- oder Schemanamen. Unterschiedliche Bank- oder
Konfigurationsidentitaeten koennen dadurch dieselbe Projektion erhalten.

Zusaetzlich nimmt `_two_level_payload` die auditiven und visuellen
Quelluhr-/Endtick-Rollen des Fast-Zustands nicht entgegen. Die spaetere
Gleichheitspruefung kann diese Informationen folglich nicht vergleichen.
Der Comparator erhaelt nur das bereits verkuerzte `poststate_payload`,
nicht die urspruenglichen Zustandsobjekte.

Auch die Ereignis- und Findingprojektion filtert Nicht-`Mapping`-Eintraege
stillschweigend heraus. Es gibt im Comparator davor keine entsprechende
Formpruefung. Damit ist die geforderte indexerhaltende, fail-closed
Projektionspruefung nicht vollstaendig abgesichert: Weglassen ist kein
gueltiger Ersatz fuer die Ablehnung ungueltiger Eintraege.

Die Befunde sind aus dem Quelltext abgeleitet. Es wurden keine manipulierten
Ergebnisse gebaut und keine Comparatorausfuehrungen vorgenommen.

Erforderliche enge Korrektur: die gebundenen Zustands- und Quellrollen
verlustfrei erhalten oder vor der generischen Normalisierung ausdruecklich
gegen ihre identische Quelle pruefen; ungueltige Projektionsformen ablehnen.
Keine neue Vergleichsregel und keine Lockerung der Exaktheit.

### DX-RB02: Verrutschter Rueckgabeblock zerstoert T48-T50

Quellen: Testdatei Zeilen 67-85, 234-253 und 463-491;
Vergleichsmodul Zeilen 1617-1619.

`rebuilt_result` baut nur noch einen Receipt und endet ohne `return`.
Der bisherige Aufbau samt Rueckgabe des `S2DRCellResult` steht jetzt hinter
dem unbedingten Comparator-`return` in `synthetic_comparison` und ist dort
unerreichbar.

Damit liefert `rebuilt_result` bei normaler Rueckkehr `None`. T48, T49 und
T50 verwenden diesen Wert als Ergebnis fuer `validate_s2dr_cell_result`.
Sofern die jeweilige Vorbereitung erfolgreich ist, wuerde bereits dessen
Typpruefung mit `S2DR_INVALID_TYPE_OR_SCHEMA` abbrechen. Die vorgesehenen
Relations- bzw. Budgetfehler werden dann nicht erreicht. Dies ist eine
statisch festgestellte Regression, kein ausgefuehrter Testfehler.

Erforderliche enge Korrektur: den bestehenden Ergebnisaufbau in
`rebuilt_result` zurueckversetzen. Die sechs neuen Comparator-Aufrufpfade,
die 51 Testidentitaeten und die zwoelf Fail-Closed-Faelle bleiben erhalten.

## Inventar und Unveraendertheit

Die AST-Auswertung bestaetigt genau 51 Definitionen T01-T51 und zwoelf
Fail-Closed-Definitionen T40-T51. Beide Dateien sind syntaktisch parsebar.
Das allein bestaetigt weder die Ausfuehrbarkeit aller Testvorbereitungen
noch die Ergebnisrichtigkeit.

S2-DY aendert genau die beiden privaten S2-DW-Dateien. Gegenueber dem
S2-DS-Quellstand sind ausser diesen Dateien nur die beiden ersten
S2-DX-Auditdokumente hinzugekommen. PPB-1, TSPM-1-Grundkern, oeffentliche
API, Snapshot und Feldpfad sind unveraendert. Die Korrektur fuegt keinen
Matrixrunner hinzu. Die 56 Vergleichszellen bleiben gesperrt.

## Entscheidung und naechster Schritt

`BLOCK_TSPM1_PRIVATE_COMPARISON_TEST_EXECUTION_TWO_STATIC_GAPS`

S2-DX ist erneut nicht bestanden. DX-B01, DX-B03 und die regulaere
S1WU-Quellbindung aus DX-B04 sind statisch geschlossen. DX-B02 ist nur
teilweise geschlossen: die echten Comparator-Aufrufpfade sind vorhanden,
die vollstaendige R0-Projektion noch nicht. Hinzu kommt DX-RB02.

Die 51 Tests bleiben ebenso gesperrt wie alle 56 Vergleichszellen.
Es entsteht kein Funktions-, Vergleichs- oder Memory-Befund.

Naechster vorgeschlagener Schritt ist S2-DZ: nach gesonderter Freigabe nur
DX-RB01 und DX-RB02 in den zwei privaten Dateien korrigieren, ohne Tests
oder Vergleichszellen auszufuehren. Danach S2-DX erneut statisch pruefen.
Dieser Audit erteilt weder eine Korrektur- noch eine Ausfuehrungsfreigabe.
