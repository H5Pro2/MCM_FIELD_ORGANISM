# Reale Erfolgshülle: NICHT_PASSEND

Nur administrative Größenrechnung, keine Qualifikation und keine Medienausführung.
Bezug: unveränderte Referenz bis EOF, Suspend nach Ereignis 19, einmalige
Wiederaufnahme bis Ereignis 20. Historischer Lauf bleibt NOT_EVALUABLE.
Repositorybasis: `537109994cf777f8d36cda617aafe12226806c25`.

## Ergebnis und Aussagegrenze

**NICHT_PASSEND ist der Status der vollständig konservativen Vorbindung.**
Der reservierte Spitzenstand beträgt **17.798.455 Byte**
gegen **4.194.304 Byte**, Überdeckung **13.604.151 Byte**.
Der kontrollierte Fehlerpfad erreicht dieselbe obere Belegung, nicht zusätzlich
einen zweiten vollständigen Erfolgsabschluss.

Dies ist **kein gemessener künftiger Spitzenstand und kein Beweis, dass ein
konkretes neues Ergebnis so groß werden müsste**. Die bereits geltenden
Einzelobergrenzen sind teilweise nur grobe Reserven. Ein engerer, belegter
PASSEND-Nachweis folgt daraus nicht. Mehrere Einzelmaxima sind wegen der
übergeordneten Grenzen nicht gemeinsam erreichbar: Der reale Pfad würde
vorher stoppen. Sie werden nicht als gleichzeitig beobachtete Werte ausgegeben.

## Vollständige Bilanz

| Grenze | Größter reservierter Stand | Grenze | Verbleibend |
|---|---:|---:|---:|
| total | 17.798.455 | 4.194.304 | -13.604.151 |
| metadata | 2.292.966 | 131.072 | -2.161.894 |
| sources | 340.429 | 327.680 | -12.749 |
| shared | 588.735 | 393.216 | -195.519 |
| verification | 262.144 | 262.144 | 0 |

Die Spaltenmaxima können an unterschiedlichen Publikationen liegen.
Die größte Gesamtbelegung entsteht beim temporären Feldobjekt der Referenz
(gleich groß ist die entsprechende Restore-Obergrenze). Im JSON stehen
**82 konkrete Publikationsrollen**, ihre Instanzzahlen,
Größenherleitungen, Messbezüge und die Spitzenrollen je Grenze.
471 Publikationspositionen einschließlich der beiden
gemeinsamen Log-/Abschlussgruppen wurden administrativ bilanziert.
Ergebnisdateien dieses Nachweises: 93.779 Byte,
vollständig zusätzlich gezählt.

## Belegte Größen und reservierte Inhalte

Die historische Referenz enthält tatsächlich 21 Zustandsobjekte mit zusammen
**924.708 Byte**, 20 Eingangsobjekte mit **183.114 Byte** und 20 Schrittobjekte
mit **59.874 Byte**. NJ: **11.920**, Formationen: **22.552**, Generationen:
**12.388 Byte**. Die sechs Verwaltungsobjekte belegen **11.819 Byte**.
Dateien, Bytes und SHA-256 sind im JSON aufgeführt. Keine Vektorprüfung,
Zustandsrekonstruktion oder neue Reizverarbeitung.

Diese Größen bleiben Messbezüge, keine garantierten Obergrenzen eines
unabhängig neu erzeugten Zustands. Deshalb werden für neue Zustandsobjekte
die bestehenden 98.304 Byte plus 27 Byte native Objektumhüllung angesetzt:
**62 Objekte, 6.096.522 Byte**. Bereits dieser Reservierungsteil liegt
**1.902.218 Byte** über der gesamten Laufgrenze, ohne sonstige Belege.
Es wird weder Zustandsgleichheit zwischen Armen noch Wiederverwendung der
historischen Wahrnehmungswerte als neue Erfahrung vorausgesetzt.

Eingänge, Schritte, NJ, Formationen, Generationen und Selektionsbelege verwenden
die vorhandenen Einzelgrenzen mit ihrer JSON-Umhüllung. Referenzindizes sind
aus Anzahl, Originalschlüsseln und vollständigen Objektreferenzen begrenzt.
Für noch nicht enger gebundene administrative Formen und normale Feldabschlüsse
gelten die vorhandenen Publikationsobergrenzen, nicht passend gewählte Schätzwerte.
Checkpoint-Feld: bestehende 524.288-Byte-Grenze plus Hülle.
Die beiden künftigen Eingangsbindungen werden jeweils gegen die bestehende
65.536-Byte-Lesegrenze reserviert; keine Autorisierung oder Lauf-ID erzeugt.

## Konkrete Hindernisse

1. Der vollständig weitergeführte Quellensatz umfasst **340.429 Byte** bei
   **327.680 Byte** Grenze: **12.749 Byte** zu viel. Alle 37 Dateien sind
   einzeln gelistet. Die kleinere Klassifikation des fokussierten Tests wird
   ausdrücklich nicht automatisch auf den realen Haupteinstieg übertragen.
2. Die noch nicht enger begrenzten Zustandsbelege überschreiten in ihrer
   reservierten Summe bereits allein die Gesamtgrenze.
3. Verwaltungs-/Indexbelege und Feldabschlüsse sind vollständig enthalten,
   ihre teils groben Obergrenzen erlauben ebenfalls keinen PASSEND-Nachweis.
   Der historische Summenfall bleibt zusätzlich **134.341 / 131.072 Byte**;
   seine 3.269 Byte Abweichung wird nicht durch Reservenwegfall umgedeutet.

## Ledger, Übergänge und Mehrfachablagen

Die Rechnung benutzt unverändert `publication.transaction`,
`reservations.assess` und dieselben Klassensummen wie die Veröffentlichung.
Alle finalen Obergrößen plus jeweils eine temporäre Kopie bilden eine
reihenfolgeunabhängige Oberhülle für Zwischenstände. Fehler vor und nach der
temporären Publikation enthalten die bereits belegten Inhalte und zwei
geschützte 4.096-Byte-Fehlerkopien. Diese ersetzen die Fehlerreserve.

Logs und Abschluss haben jeweils **gemeinsam 8.192 Byte**, nicht je Datei.
Die Katalogmitglieder dieser Gruppen werden nicht zusätzlich als volle
Einzelreserven addiert. Physisch mehrfache Dateien bleiben mehrfach gezählt.
Beide neuen Verwaltungsdateien werden zusätzlich mitgerechnet; Berechnung
und Herkunft sind im JSON vollständig verfügbar.

Das vorhandene Interning kann identische vollständige kanonische Inhalte
schon gemeinsam referenzieren. Die sechs beobachteten Verwaltungsobjekte sind
unterschiedlich; dafür wird kein Einsparungsbetrag erfunden. Gleichartige
Strukturen sind keine Bytegleichheit. Insbesondere keine vorausgesetzte
Gleichheit unabhängig erzeugter Zustands- oder Feldbelege.

## Abschluss

Die vier Fehlerformprüfungen und elf früheren Kontrollen werden nicht wiederholt.
Kein Produktcode geändert, keine Quellenregeneration, kein Medienlauf.
**Gates False. Kein PASSEND-Nachweis und keine Laufvorbereitung freigegeben.**
