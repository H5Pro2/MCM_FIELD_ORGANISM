# S2-OB: Konsolidierte Qualifikation des privaten Aufruferanschlusses

## Freigegebene Korrektur und neue Bindung

Neue Lauf-ID: `s2ob-caller-qualification-20260910-02`. Genau ein vollständiger
unittest-Aufruf mit 30 Prüfgruppen, keine historische Passzahl und keine
Delta-Kette. Der erste Fehlbefund bleibt unverändert NOT_QUALIFIED.

Nur die lokale Ergebnisbenennung im Verifikator, die Zustandsserialisierung,
der Zeitpunkt ihrer Größenprüfung und die konsolidierte Test-/Belegbindung
ändern sich. Neue Hülle `s2ob.caller.v2`; Profil, Wahrnehmungswerte,
Memoryzustände, Regeln und native Zustandsdigests bleiben unverändert.
Die 13-Ereignis-Fixture mit ihren bisherigen Farben und PCM-Werten bleibt
inhaltlich identisch; keine Ersatzquelle oder leichtere Belegung.

## Verlustfreie Darstellung

`s2ob.state.binary64-be.v1` erhält sämtliche nativen Metadaten und ersetzt
ausschließlich die 27 bekannten Wertevektorfelder durch Base64-kodierte
IEEE-754-Binary64-Bytes in Big-Endian-Reihenfolge. Kein Clipping, keine Rundung,
keine Prototypänderung oder numerische Delta-Bildung. Auch Minusnull und
Subnormalwerte bleiben bitgenau. Leere Vektoren bleiben leer.

Die maximalen Vektorlängen stammen aus den unveränderten Kapazitäten:
9 × 336 + 3 × (48 + 288) + 8 × 48 + 4 × 288 = 5.568 Werte,
44.544 Binärbytes und 59.392 Base64-Zeichen. Für die 27 Marker werden
je 16 Byte angesetzt. Die festen Feldnamen, Schema-/Profil-/Bank-/Slotkennungen,
Digestfelder, begrenzten Ereigniszähler und nativen Zeiten erhalten konservativ
32.768 Byte; hinzu kommen 256 Byte Hülle. Damit beträgt die Vorabbelegung
92.848 Byte je maximal belegtem Zustand, unter 98.304 Byte.
Die tatsächliche Serialisierung wird dennoch für jeden einzelnen Zustand
geprüft. Dies behauptet keine Größenfreigabe für andere Profile oder Formate.

Die Hülle bindet zusätzlich den SHA-256 der vollständigen ursprünglichen
kanonischen Zustandsdarstellung. Dekodierung prüft Schema, Feldzahl,
Vektorlängen, kanonisches Base64, Endlichkeit und den nativen Bytehash.
Danach gelten unverändert die nativen Memoryvalidatoren samt Digestketten.
Der Schreibpfad kontrolliert die exakte kanonische Rekonstruktion sofort.
Im Test werden die tatsächlichen nativen Zustände rekonstruiert und die
Binary64-Grenzfälle zusätzlich unabhängig mit Byte-/Hexvergleichen geprüft.

## Frühe Grenze und Fehlerisolation

Ein eigener Zustandsbelegpool kodiert beim bestehenden Zustandszuweisungs-
punkt der OA-Transaktionsaufzeichnung, vor dem nächsten Ereignis und vor
close. Der native Memoryzustand bleibt in seinem ursprünglichen Owner.
Ein Größenfehler nennt Belegklasse, native/serialisierte Größe und Zustand;
der Fehlabschluss bindet Ereignis, tatsächlichen Runtimefortschritt und
unveränderten bereits fortgeschriebenen Feldzustand. Kein Rückrollen.

Die Verifikatorkontrollen verwenden eine eigene neu erzeugte Fünferfolge
(V, AV, AV, A, V), nicht einen Ausschnitt oder Replay der größeren Geschichte.
Jede negative Mutation erhält eine frische Kopie; bei den zentralen
Manipulationen wird der gültige Ausgangsbeleg vorher unabhängig akzeptiert.
Die größere Fixture darf scheitern, ohne diese Prüfungen zu verdecken.

## Vollständiges Prüfinventar und Arbeit

Die bisherigen 24 Ziele bleiben erhalten. Sechs zusätzliche Gruppen prüfen
native Rekonstruktion einschließlich des zuvor zu großen Zustands, besondere
Binary64-Werte, beschädigte Encodings, den früh ausgelösten Größenfehler,
veraltete Generationen und den separaten Einmal-Verifikatoreinstieg.

Neutrale Obergrenzen: sieben Verarbeitungspfade, 23 Runtimeereignisse,
16 Formationsversuche, 19 Audioanalysen/NJ-Projektionen, 20 visuelle Analysen
und 18 technische Verifikationsaufrufe einschließlich typisierter Abweisungen.
Kein OA-Payload, keine reale Geschichte. Test-Payloads werden einzeln erzeugt
und nach den neutralen Prüfungen vollständig entfernt.

Je Verifikationsaufruf bleiben die bisherigen Obergrenzen unverändert:
116 Zustandsvalidierungen, 20 Formationsprüfungen, 20.160 Fast-Rangterme,
30.720 PPB-Auswahlterme, 13.440 Updatekomponenten, 11.712 Scanvergleiche.
Codec-Roundtrips sind zusätzliche reine Serialisierungsarbeit: höchstens
5.568 Werte pro Zustand; maximal 23 Zuweisungen plus sieben Nullzustände
im Schreibpfad und je Prüfer höchstens 21 Zustände. Kein Rezeptor-, NJ-,
Memory- oder Feldaufruf durch die read-only Prüfung.

## Aktive Belege und Vorabbilanz

Vor Ausführung werden aktuelle Test-/Aufrufdateien und Codec in das vollständige
Codeinventar aufgenommen. Es enthält die konservative lokale Importhülle und
die bestehenden NG-/NN-Dokumentbindungen. Keine historischen Laufarchive als
aktive Voraussetzung. Softwaredateien bleiben vollständig gehashte installierte
Abhängigkeiten; das Inventar selbst wird als Quellenbeilage mitgezählt.

Die bestehende 4.096-Byte-Qualifikationsreserve wird vorab aufgeteilt:
Vorregistrierung 1.024, Ergebnis 1.280, Ledger 1.152, Log 256,
Metriken 128, Zustandsgrößentabelle 256 Byte. Bericht weiterhin 512 Byte.
Es gibt keine neue Reserve. Bei einem Fehllauf werden Logs vollständig erhalten;
tatsächliche Überschreitungen ergeben NOT_QUALIFIED, niemals eine Kürzung.

Der Aufruf bilanziert vor dem Test zusätzlich die gesamte neutrale Hülle:
21 Zustandsbelege à 98.304, je 23 Eingaben und Schritte à 16.384,
13 Scans à 32.767, 60.000 Byte Runtime-Metadaten, das tatsächliche vollständige
Inventar, 19 NJ-Belege à 1.024, je 16 Formations-/Generationsbelege à 1.536
und 262.144 Byte gesamte Verifikation. Metadaten einschließlich Reserve/Bericht
bleiben damit bei höchstens 64.608 Byte. Gemeinsame Zusatzhülle 262.144,
Gesamthülle 4.194.304 Byte; lokale Maxima sind keine allgemeine Gesamtfreigabe.

Vorregistrierung enthält alle konkreten Summen. Überschreitung bedeutet
Stopp vor unittest. Nach Ausführung werden alle geschriebenen Dateien sowie
Ergebnis und abschließender Ledger selbst mit tatsächlichen Bytezahlen
bilanziert. Istwerte ersetzen keine Reserveprüfung: Beide bleiben sichtbar.

## Grenzen

Der spätere Aufrufer benötigt diesen konsolidierten Nachweis mit aktuellem
Inventar, Vorregistrierung, Ergebnis, vollständigem Log, Metriken,
Zustandsgrößentabelle und Abschlussbilanz. Historische Fehlbelege werden weder
gelöscht noch als bestandene Qualifikation übernommen.

Offline werden keine Rohwerte aus halbierten Werten rekonstruiert. Rezeptor-/NJ-
und visuelle Rohherkunft sowie Feldtrajektorie behalten ihre dokumentierte
Nachprüfgrenze. Die native Zustandsrekonstruktion ist davon getrennt vollständig.

Kein realer Aufruferlauf, keine OA-Wiederholung, keine neuen Quellenformate,
Taktungen oder Memorymechanik. Hauptgates außerhalb neutraler Prüfungen False,
ME/MI gesperrt, Prognosezweig ruhend.
