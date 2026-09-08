# S2-NR: administrative Verbundqualifikation

Keine erneute Gesamtqualifikation und kein Hauptlauf. Der neue Verbundbeleg
`reports/s2nr/combined-qualification-v1/qualification.json` bindet drei
unveraenderte Belegteile mit Datei-SHA-256, Ergebnisdigest, Testnamen,
Pruefbereichen, Protokoll- und Vorregistrierungsbindung:

- 16/16 der Typ-/Maskenanbindung;
- ausschliesslich die elf bestandenen Gruppen des 11/12-Laufs;
- drei nachtraeglich unabhaengig erreichte Fehlerbindungskontrollen.

Der 11/12-Gesamtstatus bleibt `NOT_QUALIFIED`. Der Verbundstatus bezeichnet
zusammengefuehrte Testdeckung, keinen neu ausgefuehrten Komplettlauf.

## Explizite Versionsfolge

Die beiden NR-Kompositionsmodule wurden zwischen der 16-Test-Pruefung und
der Laufanbindung erweitert. Diese Erweiterung wird dem spaeteren Beleg
zugeordnet, nicht als bereits im 16-Test-Lauf qualifiziert dargestellt.
Zwischen 11/12 und fokussierter Qualifikation ist ausschliesslich die
dokumentierte Testdatei geaendert. Sonstige Produktquellen sind gleich.

Jetzt neu: ausschliesslich der administrative Qualifikationsanschluss im
privaten `run_main_once` sowie seine Quellenliste. Der neue private Helfer,
die vier neutralen Tests und dieser Aufrufer sind separat hashgebunden.
Kein weiterer Funktionscode darf von den zuletzt gebundenen Quellen abweichen.
Der alte `QUAL_ID` bleibt als historischer Bezeichner erhalten; er wird weder
auf den Drei-Test-Lauf gesetzt noch als gescheiterter Gesamtbeleg akzeptiert.

## Einmalige Anschlusspruefung

ID: `s2nr-qualification-connection-20260908-01`.
Genau ein unittest-Aufruf mit vier neuen Testkoerpern, keine historischen Tests:

1. Vollstaendiger Verbund akzeptiert, historischer Fehlerstatus erhalten.
2. Fehlender Teilbeleg: `S2NRRunError / QUALIFICATION_PART_MISSING`.
3. Falscher Teilbelegdigest: `S2NRRunError / QUALIFICATION_PART_DIGEST_INVALID`.
4. Nicht erlaubte Quellabweichung: `S2NRRunError / QUALIFICATION_SOURCE_MISMATCH`.

Die Tests verwenden den tatsaechlichen Lade-/Pruefhelfer des Haupteinstiegs.
Lediglich dessen noch nicht vorhandener eigener Anschlusspruefbeleg wird als
synthetische neutrale Metadatenfixture bereitgestellt. Alle drei historischen
Teilbelege werden unveraendert von Platte gelesen und gepinnt geprueft.
Der spaetere Haupteinstieg verlangt den echten bestandenen Anschlussbeleg mit
passendem Verbunddigest und identischen Vor-/Nachquellhashes. Eine synthetische
Testfixture ist keine reale Freigabe und wird nicht als Qualifikation abgelegt.

Vor dem Test wird per AST gegen `519e1db2` gebunden, dass am Hauptrunner nur
Qualifikationspruefung und administrative Quellenliste veraendert wurden.
Verbundbeleg maximal 65536 Byte, Einzelkontrollbelege maximal 65536 Byte;
bestehende Gesamtartefaktgrenze 4194304 Byte unveraendert. Alle Gates bleiben
False; Generator, Materialisierung, Quellenplanladung und Runtime erhalten
Aufrufsperren. Keine Payloads, Rezeptoren, NJ, Memory, Feld, Abrufe oder Distanzarbeit.

Die neue administrative Anschlusspruefung wird separat ausgewiesen. Sie ist
nicht Teil der historischen 16/16-, 11/12- oder 3/3-Messungen. Erst ein
bestandener Anschlussbeleg vervollstaendigt die maschinenpruefbare
Qualifikationsvorbedingung; die Benutzerfreigabe des Einmallaufs bleibt separat.
