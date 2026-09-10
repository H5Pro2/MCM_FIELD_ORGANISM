# S2-OB: Begrenzter quellenentkoppelter Aufruferpfad

## Umfang der einmaligen neutralen Qualifikation

Keine neue Kernmechanik und kein realer Funktionslauf. Der neue Anschluss nimmt
eine unveränderliche, vorab vollständige Manifestliste mit lokalen Dateipayloads
entgegen. PCM: Little-Endian-Float32, 4.800 Samples bei 48 kHz; RGB: 1.920 × 1.080,
RGB8. Pro Ereignis bleiben die bisherigen OA-Zeitformen erhalten, aber mit der
eigenen Uhr `s2ob-caller-field-clock`. Keine Online-Nachlieferung oder freie Taktung.
Technische IDs sind 8 bis 80 Zeichen lang; die bestehenden Owner-/Consume-Suffixe
bleiben innerhalb ihrer historischen ID-Grenzen. Keine Inhaltsrollen im Manifest.

Bis zu 28 Ereignisse: höchstens 20 Formationen, zwei auditive und sechs visuelle
Hinweise. Jeder Dateipayload wird einmal mit begrenztem Leseumfang eingelesen,
gegen seinen Hash geprüft, analysiert und freigegeben. Keine Deduplizierung,
Generator- oder Sealeraufrufe im Verarbeitungspfad. Das Dateiformat ist ein
begrenzter privater Aufrufervertrag, kein beliebiger Medienimport.

## Wiederverwendung und Abhängigkeiten

MR/LM, LO-Feldadapter, NJ/NL-Halbprofil, JW-Owner und Speicherkerne bleiben
unverändert. Ebenso ALL_BANDS_24 auf 0..23, Slow-Mittelwert, visuelle Exaktregel,
Rangumrechnung, Supportregeln und Kapazitäten. Die qualifizierte OA-Transaktions-
und Generationsaufzeichnung wird als bestehende Funktion wiederverwendet;
Initialisierung, Materialisierung und Abschluss erhalten eine eigene Bindung.
Es gibt keine Ableitung des OA-Haupteinstiegs, keine Änderung seiner Validatoren
und keine Übernahme seines Quelleninventars, Qualifikationsarchivs oder Auswerters.

Der technische Gesamtprüfer übernimmt die vorhandene unabhängige Formations-
und Scan-Nachrechnung. Seine lokalen Unterschiede betreffen Manifest, variable
Ereignisanzahl, Felduhr und tatsächliche Belegbilanz. Er akzeptiert gültige
Enthaltungen; keine fachliche Auswertung ist Teil dieser Anbindung.

Das vor dem Test gespeicherte `code-inventory.json` inventarisiert konservativ
die statisch erreichbaren lokalen Imports sowie die bestehenden NG-/NN-Datei-
und Dokumentbindungen, jeweils mit vollständigem Pfad, SHA-256 und Dateigröße.
Auch nur transitiv importierte historische Helfer bleiben so sichtbar. Ihre
Generatoren oder Haupteinstiege werden nicht aufgerufen. Die Softwaredateien
sind installierte Voraussetzungen, keine kopierten Forschungsbelege. Das
vollständige Hashinventar selbst zählt als Quellen-/Bindungsbeilage; es gibt
keine ausgeblendeten referenzierten Datenarchive oder Rohpayloadbeilagen.

Aktiver Qualifikationsnachweis: aktuelles Inventar, Vorregistrierung, Ergebnis
und vollständige Testausgabe. Gespeicherte neutrale Laufbelege gehören zur
Prüfablage; der spätere Aufrufer führt sie nicht erneut aus. Es werden keine
historischen Passzahlen übernommen. Der reale Einstieg prüft diesen neuen
Nachweis, nicht frühere OA-Qualifikationen.

## Prüfgruppen und feste Arbeit

24 unabhängige Testgruppen gemäß Testdatei; Inventar und Hashes werden vor dem
einzigen unittest-Aufruf gebunden. Eine neue neutrale Folge umfasst 13 Ereignisse
mit zehn Formationen, einem auditiven und zwei visuellen Hinweisen. Dazu kommen
ein Payloadfehler vor Analyse und drei isolierte Memory-/Feld-/Scanfehlerfälle.
Keine OA-Quellen, gespeicherten Geschichten oder historischen JSON-Belege lesen.

- Höchstens fünf neutrale Verarbeitungsläufe, zusammen 17 Runtimeereignisse,
  13 Formationsversuche, 15 Audioanalysen/NJ-Projektionen und 15 visuelle Analysen.
- Zehn technische Belegprüfaufrufe einschließlich abgewiesener Manipulationen;
  je Aufruf bestehende Grenzen: 116 Zustandsprüfungen, 20 Formationsprüfungen,
  20.160 Fast-Rangterme, 30.720 PPB-Auswahlterme, 13.440 Updatekomponenten,
  11.712 Scanvergleiche. Maxima sind Prüfobergrenzen, keine behaupteten Istzahlen.
- Keine Feld-, Memory- oder Rezeptorwiederholung im Verifikator. Feldtrajektorie
  sowie Roh-zu-Halb- und RGB-zu-Rezeptor-Numerik bleiben dort Herkunfts-/Digest-
  bindungen, keine unabhängige numerische Rekonstruktion ohne Rohpayloads.
- Die neutrale Testhülle bindet Prognosen nur als Testassertions, nie als
  Startvoraussetzungen des Aufruferpfads. Alle Hauptgates am Ende False.

Abgedeckt werden kürzere Folgen, andere IDs/Inhalte, explizite Modalitätszeiten,
Hashprüfung vor Analyse, veränderte Payloads, Profilabweichung, read-only Hinweise,
vollständige Scans, tatsächliche Generationen mit MATCHED/REPLACED, Manipulationen,
Zweigfehlerisolation, reguläres close und Quellenfreigabe. Der unabhängige Prüfer
erhält ausschließlich Belege, keine Rohdateien oder Sollinventare.

## Unveränderte Bytegrenzen

Metadaten 65.536; Quellenbeilage 174.080; NJ gesamt 22.528 (22 × 1.024);
Formations- und Generationsbelege je 30.720 (20 × 1.536); gemeinsame Zusatzhülle
262.144; gesamte Laufhülle 4.194.304 Byte. Zustände einzeln 98.304, Eingaben und
Schritte 16.384, Scans strikt unter 32.768 Byte. Verifikation einschließlich
Abschlussanspruch höchstens 262.144; Qualifikationsreserve 4.096, Bericht 512 Byte.
Lokale Maxima sind keine gemeinsam garantierte Reservierung. Der vollständige
Ledger gibt Beiträge, Summen und alle Verletzungen vor der Ablehnung aus.

Die aktive Qualifikation zählt ihre tatsächlichen neutralen Gesamtbelege,
die Quelleninventarbeilage, alle Abschlussdateien und den vollständigen Log.
Vor dem Test werden 4.096 Byte für Vorregistrierung/Ergebnis/Log/Abschlussbilanz
und 512 Byte Bericht reserviert. Die tatsächliche Bilanz wird nach dem Test
vollständig gespeichert. Fehlerausgaben werden nicht abgeschnitten; ein
Überlauf bleibt NOT_QUALIFIED, kein Retry oder neue Reserve.

Der globale Summeneinstieg wird separat negativ geprüft. Diese künstliche
Summenprobe behauptet keinen erreichbaren vollständigen Lauf mit allen lokalen
Maxima. Die vollständige positive neutrale Hülle wird dagegen real erzeugt.

## Weiterhin gesperrt

Realer Aufrufer-Funktionslauf, OA-Payloads, Livequellen, neue Formate/Taktung,
Memory-/Feldänderung oder Hypothesenanwendung. ME/MI bleiben gesperrt,
der Prognosezweig ruht. Ein Bestehen qualifiziert nur diesen begrenzten
quellenentkoppelten Aufruferpfad, keinen allgemeinen Dauerbetrieb.
