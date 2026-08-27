# S2-EH: Enger statischer Korrekturvertrag

## Geltung und Freigabegrenze

Ausgangsstand: `45f4057ecb3a214058f6970ff6c92e0afa342aab`.
Grundlagen sind S2-EE, S2-EF und die Befunde EG-B01, EG-B02 und EG-T01.

`STATIC_CORRECTION_CONTRACT_BOUND_IMPLEMENTATION_PENDING`.

S2-EH legt ausschliesslich die Korrekturregeln und die betroffenen
Testdefinitionen auf Vertragsebene fest. Implementierungs- und Testdateien
werden nicht geaendert. Keine Tests, Zustandsfunktionen, Registrybuilder,
Comparatoren, Dateisystem-Versuche oder Vergleichszellen werden aufgerufen.
Die nachfolgende S2-EG-Wiederholung darf Vertragsbindung und vorhandenen Code
nicht gleichsetzen: Ein unveraenderter fehlerhafter Code bleibt blockiert.

Unveraendert bleiben alle H1-H7-Literale, Arme, P1-P5-Kriterien, nativen
Schwellen, Budgets, Operationsbreiten, Gleichstands- und Entscheidungsregeln,
die R0-Projektion sowie die kanonischen Hashverfahren und historischen
Hashbelege. Eine spaetere autorisierte Codekorrektur erhaelt eigene neue
Quellhashes; alte Belege werden weder umgeschrieben noch als Nachweis fuer
geaenderte Bytes ausgegeben. `_EXECUTION_RELEASE_ENABLED` bleibt `False`.

## K1: Eindeutige Generator-Aufrufstellen

Die Ausnahme gilt nur fuer den vorhandenen L1-Generator in der unveraenderten
S1-WU-Quelle. Seine statisch ermittelte Identitaet lautet:

- Quelle: `mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py`.
- Rohbyte-SHA256: `8739a5cf630ca8bbfb6c0c801d4d17b81dd25ae66d1bb7eef2d36bb45e17ca27`.
- Codeobjektname: `<genexpr>`.
- Qualifizierter Name: `probe_s1wu_perceptual_state.<locals>.<genexpr>`.
- Erste Codezeile: 209; L1-Call-Ausdruck: Zeilen 211-214.
- Callee: der unveraenderte `normalized_mean_l1_distance`.
- Operandenlaenge: jeweils gleich und genau 8 oder 18.

Vor der Aufnahme eines Distanzbelegs muss der private Quellmatcher die
Quelldatei gegen das gebundene Manifest pruefen und das tatsaechliche
Caller-Codeobjekt eindeutig dem aus diesen Bytes kompilierten Generator
zuordnen. Kompilieren dient nur der Codeobjektanalyse, niemals `exec`, `eval`
oder einem Import der erneut gelesenen Quelle. Compilerfassung und Optionen
muessen zur gebundenen Interpreteridentitaet passen. Mehrdeutige oder nicht
zuordenbare Codeobjekte werden verworfen.

Die spaetere relationale Kostenpruefung muss die aufgezeichnete Kombination
aus Quellpfad, Git-Blob, `<genexpr>` und Call-Zeile gegen dieselbe eindeutige
Quellstelle akzeptieren. Die bereits gebundenen Belegfelder werden dabei
nicht erweitert. Die staerkere Codeobjektpruefung findet am tatsaechlichen
Erfassungsort statt; die bestehende Owner-Attestation bindet diesen Ursprung.

Benannte Funktionen behalten ihre bisherige Quellpruefung. Eine generelle
Freigabe fuer `<genexpr>`, unbekannte Comprehensions, fremde Dateien oder
beliebige Zeilen innerhalb einer Elternfunktion ist ausgeschlossen. Ein
extrahierter Helfer darf nur ein privater reiner Quellmatcher sein, kein
neuer Runtime-, API- oder Test-Bypass.

Die Zaehleinheit bleibt die vollstaendige Dimension jedes tatsaechlichen
L1-Aufrufs, auch bei Validierungsarbeit und identischen Operanden. Keine
Rabatte, neuen Limits oder nachtraeglichen Receiptkorrekturen. Schema- oder
Quellabweichungen bleiben fail-closed; Ueberschreitungen bleiben allein bei
`validate_s2dr_cell_result` und dessen bestehendem Limitfehler.

## K2: Sichtbarkeit ist keine Abschlussbestaetigung

Das Feld `MatrixArtifact.status=COMPLETED` beschreibt den zum Abschluss
vorbereiteten Gesamtbefund. Allein das Lesen dieses Feldes oder eines
passenden Digests darf keinen operativen Abschluss bestaetigen.

Verbindliche Reihenfolge der spaeteren privaten Veroeffentlichung:

1. Vollstaendiger, methodisch gueltiger Befund und unveraenderte Quellen.
2. Exklusives Staging, dessen Flush und vollstaendige Inhaltspruefung.
3. Dauerhaftes `SEALED`-Journal mit dem Artefaktdigest.
4. Genau eine atomare No-Replace-Veroeffentlichung.
5. Erfolgreiche Rueckkehr des zugehoerigen Volume-Flush.
6. Vollstaendige erneute Pruefung der finalen Datei und ihrer Beweiskette.
7. Exklusive terminale `COMPLETED`-Journalzeile, die erst nach 5 und 6
   geschrieben werden darf; anschliessend deren Flush und Ruecklesen.

Es wird kein neuer Recordtyp und kein neues Hashverfahren eingefuehrt.
Schritt 7 verwendet `AttemptJournalEntry` mit dem bestehenden Status
`COMPLETED`, demselben Reservierungsdigest, der vorangehenden
`SEALED`-Journalidentitaet und demselben `sealed_artifact_digest_or_null`.
Zellstart-, Zellevidenz- und Fehlerfelder sind dort null. Im unveraenderten
56-Zellen-Ablauf folgen auf 112 Zelljournalzeilen genau `SEALED` als 113 und
die terminale Zeile als 114. Das Artefakt referenziert diese spaetere Zeile
nicht; die Digestkette bleibt azyklisch.

Ein privates, pro Versuch anfangs falsches Bestaetigungsmerkmal darf nur
nach erfolgreichem Schritt 5 gesetzt werden. Es darf nicht aus einer
lesbaren Datei, einem JSON-Status, einem externen Parameter oder dem
Vorhandensein eines Pfades abgeleitet werden. Eine Rueckgabe als abgeschlossen
benoetigt zusaetzlich die vollstaendige Finalpruefung und den terminalen Beleg.

Fehlerregeln:

- Ein Fehler vor erfolgreichem Schritt 5 darf nie zu `COMPLETED` fuehren,
  auch wenn die finale Datei vollstaendig lesbar ist.
- Unvollstaendige, fremde oder widerspruechliche Ergebnisbelege sind keine
  abgeschlossene Veroeffentlichung, auch nach einem erfolgreichen Flush.
- Ist die Veroeffentlichung sichtbar, aber nicht bestaetigt, bleibt der
  Versuch verbraucht und unvollstaendig (`ABORTED_INCOMPLETE`). Ein vor der
  Veroeffentlichung eindeutig fehlgeschlagener Versuch kann `FAILED` bleiben.
- Ein Fehler nach einem bereits belegten Abschluss darf diesen nicht durch
  einen widerspruechlichen Fehlerabschluss ersetzen. Im laufenden Prozess
  sind dafuer mindestens das intern gesetzte Flush-Merkmal, der vollstaendige
  Finalbeleg und die gueltige nachgelagerte Terminalzeile erforderlich.
- Scheitert nur der Flush der Terminalzeile, ist ein vorhandener vollstaendiger
  Terminalbeleg ausschliesslich zusammen mit dem bereits erfolgreich
  bestaetigten Final-Flush aus Schritt 5 und der Finalpruefung verwertbar.
  Eine teilweise Terminalzeile reicht nicht. Es erfolgt kein Flush-Retry.
- Nach Prozessverlust darf eine rein lesende Pruefung einen Abschluss nur
  aus vollstaendigem Finalbeleg und gueltiger Terminalzeile mit passender
  Reservierungs-/SEALED-Kette einordnen. Diese Zeile bezeugt aufgrund der
  gebundenen Schreibreihenfolge den vorausgehenden Final-Flush. Fehlt sie,
  bleibt der Abschluss unbestaetigt, selbst wenn der Flush stattgefunden haben
  koennte. Es gibt keine nachtraegliche Belegerzeugung.

Damit wird allein die mehrdeutige Abschluss-/Crash-Auslegung aus S2-EE fuer
EG-B02 praezisiert. Speicherfunktion, Vergleichsurteil und Erfolgskriterien
aendern sich nicht. Jede bestehende Reservierung bleibt dauerhaft verbraucht.
Kein Retry, Resume, Ersatz-Owner, Ueberschreiben, Loeschen oder zweiter Versuch.
Ein Ledger-Rollback oder eine absichtliche Belegfaelschung liegt weiterhin
ausserhalb der bestehenden Vertrauensgrenze.

## K3: Anpassung der betroffenen Testdefinitionen

Die Definitionen T01-T51 bleiben als Bestand erhalten. Nur die neun bereits
betroffenen Definitionen und ihre notwendigen privaten Testhelfer erhalten
neue Vorgaben. Es werden jetzt keine Python-Tests materialisiert und keine
neue Matrix-, Feld- oder Speicherfunktion eingefuehrt.

| Definition | Verbindliche Anpassung |
| --- | --- |
| T01 | Statt drei Hashes den expliziten, sortierten 18-Dateien-Importbestand aus dem JSON-Anhang pruefen. Pfade, Git-Blobs und Rohbytehashes unabhaengig aus den gelesenen Dateien ermitteln, nicht dieselbe Inventarfunktion zweimal als Soll und Ist verwenden. Generator-Unterfaelle G1-G5 aufnehmen. |
| T34 | Alle fuenf neuen Pflichtfelder des Vergleichsresultats, den S2-EE-gebundenen Registryinhalt und den eigenen Resultatdigest pruefen. Veroeffentlichungs-Unterfaelle P1-P9 mit isolierten In-Memory-Doubles aufnehmen. |
| T35 | Alle 18 neutralen Beobachtungen einschliesslich H2/1 und H6 liefern; P1-P5 aus fest vorgegebenen Sollwerten pruefen, nicht aus vorgegebenen Erfolgsvektoren rueckwaerts erzeugen. |
| T36 | Methodische Ungueltigkeit hat auch bei sonst erfolgreichen Funktionswerten Vorrang. |
| T37 | Technischer Armfehler ergibt `METHOD_INVALID`; davon getrennt ergibt methodisch gueltiges funktionales Scheitern `TSPM1_FUNCTION_NOT_VALID`. |
| T38 | Fehler, Latenz, Schreibarbeit und ASCII-Gleichstand in der bestehenden Reihenfolge pruefen. ASCII-Auswahl begruendet keine funktionale Ueberlegenheit. |
| T39 | Den unveraenderten begrenzten Engineeringentscheid nur bei fuenf erfuellten TSPM-Kriterien, exaktem R0 und keiner voll erfolgreichen einfachen Baseline erwarten. |
| T46 | Ohne Attestation zuerst Autorisierungsablehnung erwarten. Den getrennten Duplikatfehler erst hinter der kontrollierten Test-Attestationsgrenze pruefen. |
| T51 | Die vollstaendige bestehende R0-Projektion bei abweichender Bank-, Konfigurations- oder Slotidentitaet sowie Funktionsbeobachtung pruefen; der Comparator muss die Abweichung als methodisch ungueltig behandeln. |

Generator-Unterfaelle in T01:

- G1: exakte gebundene Generatorstelle, auditiver und visueller Fall, gueltig.
- G2: gleicher Generatorname, aber fremde Quelle oder falscher Blob, ungueltig.
- G3: richtige Datei, aber falsche Call-Zeile oder anderes Generator-Codeobjekt,
  ungueltig; keine pauschale `<genexpr>`-Freigabe.
- G4: fehlende oder mehrdeutige Codezuordnung, ungueltig.
- G5: unveraenderte benannte Call-Stelle bleibt gueltig; ungueltige Dimension
  oder ungleiche Operandenlaenge wird nicht durch die Generatorregel zugelassen.

Veroeffentlichungs-Unterfaelle in T34, ohne echtes Dateisystem:

- P1: Staging unvollstaendig oder Flush fehlgeschlagen; kein Rename/Abschluss.
- P2: No-Replace scheitert, etwa wegen bestehender Zieldatei; kein Abschluss.
- P3: Rename erfolgreich, Final-Flush fehlgeschlagen, Finaldatei lesbar und
  vollstaendig; trotzdem kein `COMPLETED` und keine Terminalzeile.
- P4: Final-Flush erfolgreich, finale Kette unvollstaendig oder fremd;
  kein Abschluss und keine Terminalzeile.
- P5: vollstaendige Reihenfolge bis Terminalbeleg; genau ein Abschluss.
- P6: spaeterer Fehler nach bestaetigtem Abschluss; keine Herabstufung und
  kein widerspruechlicher Fehlerbeleg.
- P7: Prozessverlust zwischen Rename und Terminalbeleg; lesbarer Inhalt
  allein bleibt unbestaetigt und dauerhaft verbraucht.
- P8: Terminalbeleg fehlt, ist beschaedigt oder gehoert zu einem anderen
  Versuch/Artefakt; kein bestaetigter Abschluss und kein Retry.
- P9: Fehler beim Terminal-Flush: nur vollstaendiger Terminalbeleg plus
  bereits bestaetigter Final-Flush und Finalpruefung kann den Abschluss tragen;
  ein Teilbeleg nicht. Keine zweite Flush- oder Publish-Ausfuehrung.

Die Comparator-Unterfaelle bleiben Einheitenpruefungen am echten
`compare_s2dr_results`, keine Produktionsevidenz. Ausschliesslich innerhalb
der Testdatei darf dessen Attestationspruefung mit einem eng begrenzten Mock
kontrolliert werden; Produktionscode erhaelt dafuer keinen Schalter oder
alternativen Erfolgsweg. Aufruf und Argumente der Attestation sind zu pruefen.
Die synthetischen Daten sind reine Resultat-Datentraeger mit Testidentitaeten,
keine durch Bildung erzeugten Armzustaende. Nach Entfernen des Mocks muss die
echte Grenze diese Daten weiterhin verwerfen. Keine Freigabe des Matrixgates.

Diese Pruefungen sichern die nachgelagerte Auswertungslogik, nicht die echte
Erzeugungs- oder Persistenzkette. Fuer diese darf aus einem Mock-Erfolg kein
Integrationsbefund abgeleitet werden. Veroeffentlichungsdoubles duerfen keine
Windows-API, Ledgerdatei, `run_once`, `consume_once` oder Zustandserzeugung
aufrufen. Ein dazu isolierter privater Abschlusshelfer darf ausschliesslich
die bereits gebundene Veroeffentlichungssequenz enthalten.

## Abnahme und naechste Grenze

S2-EG muss nach diesem Vertrag erneut statisch pruefen. Solange K1-K3 nur
dokumentiert, aber nicht separat freigegeben umgesetzt sind, bleiben EG-B01,
EG-B02 und EG-T01 im Code offen. Ein bestandener Vertragsabgleich ist keine
Implementierungsabnahme und keine Testfreigabe.

Fuer eine anschliessende Umsetzung ist eine gesonderte Freigabe erforderlich:
nur das private Vergleichsmodul und die bestehende private Testdatei, keine
Testausfuehrung. Danach erneut S2-EG. Die 56-Zellen-Matrix, Feldintegration,
oeffentliche API und Snapshot bleiben in jeder dieser Stufen gesperrt.
