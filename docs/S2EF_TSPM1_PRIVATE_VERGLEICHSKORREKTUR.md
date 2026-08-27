# S2-EF: Private Umsetzung der S2-EE-Vergleichsbindung

## Status und Umfang

`PRIVATE_IMPLEMENTATION_RECORDED_STATIC_AUDIT_REQUIRED_MATRIX_LOCKED`.

Ausgangsstand: `0e7e1a2a75e85b50ff96c959bd3d7e54de1f279f`.
Grundlage sind der S2-EE-Vertrag und der S2-ED-Wiederholungsaudit.
Die ausdrueckliche S2-EF-Freigabe erlaubt die private Umsetzung der fuenf
Korrekturen, nicht deren Ausfuehrung oder fachliche Abnahme.

Geaendert wurde ausschliesslich
`mcm_field_organism/_tspm1_s2dr_private_comparison.py`.
Hinzu kommen dieses Protokoll und sein JSON-Beleg. PPB-1, TSPM-1-Grundkern,
S1-WU-Probe, Tests, oeffentliche API, Snapshot und Feldpfad bleiben unveraendert.
Die unabhaengigen generischen R0-Zustaende und ihre Operatoren bleiben erhalten.

## Umgesetzte Bindungen

1. **Neutrale Auswertung:** Alle Arme erhalten dieselben 18 Sollproben und
   P1-P5-Kriterien. Verwendet werden native Wiedererkennung und tatsaechlich
   ausgewaehlte Werte mit Herkunft im beobachteten Zustand. Zielabweichungen
   werden erst im getrennten Evaluator berechnet. Zustandszahl, Fast-/Slow-Rolle,
   Stabilisierung und Digestwechsel sind keine Erfolgskriterien. Die numerische
   AX-Erhaltung gehoert zu P3; H6 ist Bestandteil von P4.
2. **Einheitliche Zaehler:** Ein privater Thread-Profiler beobachtet Aufrufe
   des bestehenden L1-Evaluators, einschliesslich transitiver Validierungen.
   Er ersetzt weder Core-Funktionen noch Modulreferenzen. Herkunft, Aufrufstelle,
   Dimension und Zweck werden versiegelt. Schreibaktionen folgen den festen
   S2-EE-Wortbreiten; tatsaechliche PPB-Aufrufe binden Vor-/Nachzustand und
   Readout. Ueberschreitungen werden ausschliesslich relational in
   `validate_s2dr_cell_result` abgelehnt. Die bisherigen Grenzen bleiben gleich.
3. **Entscheidung und Gleichstand:** Methodische Gueltigkeit einschliesslich
   vollstaendiger R0-Projektion hat Vorrang. Erst danach folgen Funktionsgueltigkeit
   und Vergleich mit einfachen Baselines. Rangfolgen verwenden Zahl erfuellter
   Kriterien, funktionale Fehler, beobachtete Aufnahmelatenz, Schreibaufwand und
   abschliessend ASCII-Arm-ID. Dieser letzte Gleichstandsentscheid ist keine
   funktionale Ueberlegenheit.
4. **Beweiskette:** Die neue private Schemafassung bindet S2-EE, Quellenmanifest,
   Interpreter, Abhaengigkeiten, vollstaendige Registry, Ausfuehrungsplan,
   separate Autorisierung, Reservierung, Zellstart, Owner, Receipts, Kosten und
   Probeherkunft. Der Comparator akzeptiert keine allein uebergebenen Rohresultate.
   Er verlangt die Originalresultate des einen Versuchs und dessen persistierte
   Start- und Abschlussbelege. Kanonische Wertkopien werden erneut geprueft;
   Belege werden nicht zur Wiederherstellung fehlender Zustandsresultate verwendet.
5. **Einmaligkeit und Veroeffentlichung:** Die private Versuchshuelle reserviert
   einen festen Schluessel unter dem gemeinsamen Git-Verzeichnis exklusiv.
   Auch leere oder beschaedigte bestehende Reservierungen sperren einen neuen
   Versuch. Zellstarts werden vor dem jeweiligen Aufruf dauerhaft protokolliert.
   Nach allen 56 Zellen sind erneute Quellenpruefung, vollstaendiges Staging,
   `SEALED`-Journal und atomare Veroeffentlichung ohne Ersetzen vorgesehen.
   Fehler erlauben weder Retry noch Fortsetzung oder nachtraegliche Rekonstruktion.

Die Ergebnisart `NOT_ASSESSED_BY_BOUND_FIXTURES` haelt die Frage der strukturierten
Wahrnehmungsrepraesentation offen. Ein moeglicher Vorteil waere auf die gebundenen
Aufgaben und einfachen Baselines begrenzt; R0 bleibt zwingende Reduktionsbaseline.

## Ausfuehrung bleibt gesperrt

`_EXECUTION_RELEASE_ENABLED = False` wird nicht geoeffnet.
Der private Versuchskonstruktor stoppt damit vor Reservierung und Zustandsaufruf.
Es wurden keine Autorisierung, kein Ausfuehrungsplan, kein Versuchsjournal,
keine Reservierung und keine Ergebnisdatei materialisiert.

Eine spaetere Freigabe muss zuerst die gepruefte Codefassung binden; erst danach
koennen ein Quellenmanifest und ein konkreter Plan erstellt und separat
autorisiert werden. Ein Plandigest wird nicht in seine eigene Quellfassung
eingetragen. Die Autorisierung muss vor einem Versuch als unveraenderlicher
Beleg im gebundenen Ledger vorliegen und zum vollstaendigen Plan passen.
Dies ist eine private Vertrauensgrenze, kein Schutz gegen absichtliche
Manipulation von Prozess, Code oder Ledger durch einen privilegierten Benutzer.

## Dateisystemgrenze

Der implementierte Backendpfad ist auf ein lokales festes NTFS-Volume unter
Windows beschraenkt. Er verlangt einen geoeffneten Volume-Handle fuer
`FlushFileBuffers`; fehlen die notwendigen Rechte, wird vor der Reservierung
abgebrochen. Es wird keine Rechteerhoehung angefordert. Reparse-Punkte,
abweichende Pfade und volumeuebergreifendes Staging werden abgelehnt.

Dateien werden exklusiv angelegt und geflusht. Zur endgueltigen Veroeffentlichung
ist `MoveFileExW` mit `MOVEFILE_WRITE_THROUGH`, ohne `REPLACE_EXISTING` und ohne
`COPY_ALLOWED`, mit anschliessendem Volume-Flush vorgesehen. Die Anforderungen
folgen der Microsoft-Dokumentation zu
[FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers)
und [MoveFileExW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-movefileexw).

**Die Plattformfaehigkeit wurde nicht ausgefuehrt oder bestaetigt.** Dateisystem-
und Absturzgarantien muessen vor einer Matrixfreigabe separat geprueft werden.
Eine Reservierung ohne vollstaendigen finalen Beleg bleibt verbraucht; ein
vollstaendiger bereits veroeffentlichter Beleg darf nicht durch einen spaeteren
Fehlerstatus oder erneuten Lauf ersetzt werden. Manipulierte, geloeschte oder
zurueckgerollte Ledger sind kein unterstuetzter Neustartmechanismus.

## Ausschliesslich statische Eigenpruefung

- Python-AST, Compile-only ohne Auswertung des Codeobjekts und Symbolauflosung.
- Git-Diff, Hashvergleich geschuetzter Dateien und Quelltextabgleich der Datentraeger.
- Literale Registry, Kapazitaeten, native Parameter und R0-Operatoren erhalten.
- Null Projektimporte, Zustands-/Probe-/Comparatoraufrufe und Registryaufrufe.
- Null Tests, Test-Collection, Vergleichszellen und Dateisystem-Versuchsaufrufe.

Die historischen 51 Testdefinitionen wurden weder veraendert noch ausgefuehrt.
Ihr frueherer Erfolg gilt nicht fuer die neue Schema-, Beleg- und
Comparatorgrenze. Insbesondere benoetigen kuenftige Comparatorpruefungen die
neue attestierte Eingabe. Es wird weder deren Kompatibilitaet noch eine bereits
vollstaendige neue Testabdeckung behauptet.

Die nun vollstaendige Operationszaehlung kann bisher verdeckte Ueberschreitungen
sichtbar machen. Die Budgeteinhaltung aller Arme ist deshalb nicht angenommen.
Ein entsprechender Befund muss zum Stopp fuehren, nicht zu hoeheren Grenzwerten,
Validierungsrabatten oder einer stillen Aenderung der nativen Operatoren.

## Naechster Schritt

**S2-EG: separater statischer Implementierungs- und Testaudit.** Zu pruefen sind
die fuenf Umsetzungen, transitive Zaehlerabdeckung, Budgetmaterialisierbarkeit,
Quellen-/Owner-/Belegidentitaet, Absturz- und Veroeffentlichungsgrenzen sowie die
Eignung beziehungsweise die Luecken der vorhandenen Testdefinitionen.
Keine Testausfuehrung und keine Vergleichszelle ohne eigene Freigabe.
S2-EF trifft kein Vergleichsurteil und keine Memory- oder MCM-Feldbehauptung.
