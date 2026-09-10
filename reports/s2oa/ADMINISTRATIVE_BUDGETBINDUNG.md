# S2-OA: administrative Budgetbindung v2

Vor dem einzigen neutralen Qualifikationsaufruf vom 2026-09-10 festgelegt.
Keine neue numerische Versiegelung. Historische v1-Dateien und ihre belegte
Budgetabweichung bleiben unveraendert. Neue Geltung nur fuer administrative
Quellen-/Ereignisreferenzen, nicht fuer den noch gesperrten Funktionsanschluss.

## Artefaktklassen und Referenzabschluss

1. **Metadaten gemeinsam maximal 65.536 Byte:** neuer Bindungsbeleg samt
   kompakter Ausfuehrungs- und getrennter Evaluationswurzel, neue administrative
   Vorregistrierung sowie maschinenlesbare neue Qualifikationsbelege
   (Vorregistrierung, Ergebnis, stdout, stderr). Jeder Bestandteil muss
   zusaetzlich einzeln unter diesem Deckel liegen. Keine volle Kopie der
   Quellenrezepte in der neuen Vorregistrierung.
2. **Zusatzhulle gemeinsam maximal 262.144 Byte**, prospektiv aufgeteilt:
   Quellenherkunft maximal 174.080 Byte; 22 NJ-Belege zu maximal 1.024 Byte
   = 22.528; 20 Formationszusatzbelege zu maximal 1.536 = 30.720;
   20 Generationsdelta-Bloecke zu maximal 1.536 = 30.720. Summe der
   Teildeckel 258.048; nicht zugewiesene Reserve 4.096 Byte. Keine Teilklasse
   darf Rest anderer Klassen automatisch beanspruchen.
3. **Spaeterer vollstaendiger Gesamtbeleg maximal 4.194.304 Byte:** einschliesslich
   Metadaten und aller referenzierten Zusatzbelege. Extern gespeicherte Bytes
   zaehlen genauso wie eingebettete. Vorhandene Zustands-/Eingabe-/Schritt-/Scan-
   Einzelgrenzen bleiben zusaetzlich bestehen; die Summe muss ebenfalls passen.
   Fuer 21 Zustaende, 56 Eingabe-/Schrittbelege und 16 Scans werden schon
   jetzt 21*98.304 + 56*16.384 + 16*32.767 = 3.506.160 Byte reserviert.
   Mit den vollen urspruenglichen Metadaten-/Zusatzhuellendeckeln sind dies
   3.833.840 Byte. JSON-Rahmen und kuenftige Verwaltungsfelder muessen in
   der Metadatenklasse bleiben; kein zusaetzlicher unbegrenzter Rahmen.
4. Getrennte Verifikation und spaetere Auswertung je maximal 262.144 Byte
   gemaess OA-Plan. Der neue Pruefbeleg und seine Einmal-Claimdatei werden
   gemeinsam in der Verifikationsklasse gezaehlt, nicht im Metadatenbudget.

Quellenherkunft umfasst **die vollen Dateibytes** der historischen OA-
Ausfuehrungswurzel, Evaluationswurzel, Vorregistrierung und Versiegelung,
der alten read-only Verifikation und des historischen 18/18-Ergebnisses.
Keine dieser Dateien wird durch einen blossen 64-Zeichen-Hash aus der Bilanz
entfernt. Jede dieser sechs Dateien wird einmal gezaehlt, auch wenn mehrere
Referenzen auf sie zeigen. Die alte Metadatenzuordnung wird dadurch nicht
rueckwirkend korrigiert: v2 zaehlt diese Dateien jetzt als historische
Quellenherkunft fuer den neuen, kleineren administrativen Beleg.

Der ausfuehrbare Daten-Referenzabschluss ist genau diese Liste sowie die vier
neuen Qualifikationsdateien. Historische Code-/Profil-/Dokument- und NP-
Elternidentitaeten sind unveraenderte Provenienzaussagen, keine nachzuladenden
funktionalen Artefaktpayloads. Rezeptinhalt, Zeit, Profil, Generatoridentitaet,
Payloadhash und Erwartung liegen vollstaendig in den mitgezaehlten OA-Wurzeln.
Die Verwaltungspruefung liest historische Code-/Elterndateien nur zur
SHA-Bestaetigung, fuehrt sie nicht aus und importiert keine Quellenmodule.
Erlaeuternde Markdown-Berichte und Programmdateien sind keine serialisierten
Laufdaten; ihre Hashbindungen sind dagegen in den Metadaten enthalten.

Referenzen binden Datei-Alias, Feld, gegebenenfalls Originalindex und Digest
des vollstaendigen referenzierten Wertes. Quellen-ID und Ereignis-ID werden
gegen den Originaleintrag geprueft. Ausfuehrung verweist nicht auf Sollwerte;
die separate Evaluationswurzel bindet unveraenderte historische Erwartungen.
Historische budgets sind nur Archivaussagen. Aktiv ist ausschliesslich v2.

## Reserven sind keine erfundenen Funktionsbelege

NJ reserviert kompakte Rohzustands-/Projektions-/Zeitdigests und Marker,
nicht rekonstruierte Rohspektren. Formationen reservieren Transaktions- und
Eingangsreferenzen, keine zweiten Memoryvollkopien. Generationsbloecke
reservieren referenzgebundene Deltas pro Formation fuer zusammen maximal
480 Slotuebergaenge. Diese Inhalte werden jetzt **nicht implementiert**.
Die Reserven sind Obergrenzen und spaetere Anschlussbedingungen, kein
Nachweis, dass ein noch nicht gebauter vollstaendiger Funktionsbeleg passt.
Eine Ueberschreitung muss dann stoppen, nicht die Reserven vergroessern.

## Einmalige neutrale Qualifikation

ID: `s2oa-admin-binding-qualification-20260910-01`.
Genau 20 unabhaengige Tests in einem unittest-Aufruf, kein Retry.
Synthetische 48 Quellen/28 Ereignisse, keine echten Quellenrezepte oder
Payloads. Quellen-/Rezeptor-/Systemimporte sowie historische Datenlesezugriffe
im Testprozess gesperrt. Vorher Testinventar, Code-/Dokumenthashes und diese
Budgettabelle festschreiben; nachher Hashgleichheit sichern.

Pruefgruppen: gueltige Referenzen; fehlende Referenz; falscher Digest;
vertauschte Quellen; vertauschte Ereignisse; Profilmanipulation;
Zeitmanipulation; Evaluationsmanipulation; unvollstaendiger Archivabschluss;
Archivhashfehler; Metadateneinzellimit; Metadatengesamtlimit;
Quelleneinzellimit; Quellengesamtlimit; NJ-Reserve; Formationsreserve;
Generationsreserve; gemeinsame Zusatzhulle; vollstaendige Gesamthuelle;
Unveraenderlichkeit, geschlossene Gates und Schreibkonflikt.
Grenzen synthetisch inklusive exakt am Deckel und ein Byte darueber pruefen.
Keine PCM-/RGB-Produktion, NJ-, Rezeptor-, Memory-, Feld- oder Runtimeaufrufe.

Nach Bestehen einmal `s2oa-administrative-binding-20260910-01` aus vorhandenen
Belegen erstellen, anschliessend genau eine unabhaengige read-only Pruefung.
Bei Fehler typisierter Abschluss, kein Retry. Die Verwaltungspruefung darf
Referenzen, Originalwerte, Codehashes und Bytegroessen vergleichen, aber keine
Payloads oder Rezeptorwerte neu berechnen. Gates bleiben False. Eininstanz-
und Generationsimplementierung sowie Hauptlauf benoetigen eigene Freigabe.
