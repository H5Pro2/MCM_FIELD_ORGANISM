# S2-GX: Statischer Receipt-, Groessen-, Budget- und Fehlercodeaudit

Stand: 2026-08-30

## Grenze und Ergebnis

Der Audit verwendet ausschliesslich die versionierten Quellen und die
gespeicherten S2-GW-Belege. Es wurden keine Rezeptor-, Speicher-, Runner- oder
sonstigen Zustandsfunktionen ausgefuehrt. S2-GW bleibt dauerhaft
`NOT_EVALUABLE`.

```text
S2GX_STATIC_AUDIT_COMPLETE
CORRECTION_REQUIRED_BEFORE_ANY_NEW_RUN
```

Die funktionale Kontextpruefung wurde in S2-GW nicht erreicht. Der gefundene
Fehler liegt vollstaendig in der Aufzeichnungsgrenze.

## Kanonische Anatomie von op-0002

`op-0002` gibt `_BoundSource` an den generischen `_record`-Pfad zurueck. Der
kanonische Nutzinhalt umfasst:

- Rolle, neutrale Quell-ID, visuelle und auditive Fixture-ID sowie Zeitfenster;
- den visuellen Rohbyte-SHA-256, aber keine Rohbildbytes;
- das vollstaendige `PPB1ActiveReceptorBatchEnvelope`;
- den vollstaendigen `B4TSPM1BoundInput`;
- den abschliessenden `source_digest`.

Die Vollserialisierung dupliziert dabei dieselbe bereits digestgebundene
Provenienz. Das Envelope erscheint dreimal. Auditive und visuelle Timed-Frame-
Bindings erscheinen jeweils fuenfmal. Die 26 reduzierten AV-Werte erscheinen
insgesamt in sieben Kopien mit zusammen 182 Zahlenwerten. Die 26 Carrier-IDs
erscheinen in acht Kopien mit zusammen 208 Eintraegen. Diese Wiederholungen
entstehen durch `dataclasses.asdict`; sie sind keine zusaetzliche
Wahrnehmungsinformation.

## Bytebefund

Die Groessen wurden aus den konkreten Datentraegerfeldern, den literalen
S2-GT-IDs, den 25 Bildfixtures, den 14 auditiven Fixtures und der exakt im Code
verwendeten kanonischen ASCII-JSON-Form rekonstruiert. SHA-256-Werte duerfen
inhaltlich variieren, besitzen aber stets 64 ASCII-Zeichen und aendern deshalb
die Bytezahl nicht.

| Bestandteil | Kanonische Groesse |
| --- | ---: |
| `_BoundSource` von `op-0002` | 21.344 Bytes |
| an `finish` uebergebenes `{"result": ...}` | 21.355 Bytes |
| vollstaendige Artefakthuelle vor Dateischreiben | 21.645 Bytes |
| hypothetisches erfolgreiches RESULT-Ereignis | 585 Bytes |
| tatsaechlich gespeichertes fehlgeschlagenes RESULT-Ereignis | 658 Bytes |

Die Artefakthuelle fuegt dem `_BoundSource` bei diesem Lauf 301 Bytes hinzu.
Die 4.096-Byte-Pruefung schlug in `_exclusive_json` fuer diese Huelle fehl.
Sie schlug vor Verzeichnisanlage und Dateischreiben fehl. Deshalb existiert
kein `receipts/op-0002.json`. Die unabhaengige 4.096-Byte-Grenze des
RESULT-Journaleintrags wurde nicht erreicht und war nicht die Fehlerursache.

## Alle 57 Rezeptoroperationen

Die 25 Bildfixtures enthalten ausschliesslich 18 Werte aus `0.0` und `1.0`.
Ihre Wertebelegung aendert die JSON-Laenge nicht. Ueber die tatsaechlichen 52
Formations-, vier Kontextabruf- und eine Verbraucheranalyse ergeben sich:

| Statische Groesse | Minimum | Maximum |
| --- | ---: | ---: |
| `_BoundSource` | 21.342 | 21.467 |
| vollstaendige Artefakthuelle | 21.643 | 21.768 |

Das Minimum entsteht bei einer Formationsquelle mit kurzer Fixture-ID. Das
Maximum entsteht bei der laengeren gemeinsamen read-only Verbraucherquelle.
Damit wuerden alle 57 Rezeptoroperationen mit der aktuellen Vollserialisierung
dieselbe registrierte 4.096-Byte-Grenze ueberschreiten.

## Kleinste Korrekturrichtung

Die fachlich und technisch kleinste Korrektur ist kein groesseres Receipt,
sondern eine kanonische, digestgebundene Projektion fuer die Aufzeichnung. Sie
soll genau einmal enthalten:

- Quell-ID, Rolle, Fixture-IDs und Zeitfenster;
- Rohbyte-Digest und die Aussage, dass keine Rohdaten gespeichert werden;
- Envelope-, auditive Timed-Frame-, visuelle Timed-Frame- und Bound-Digest;
- genau eine auditive und eine visuelle reduzierte Wertefolge;
- Werte- und Quelldigest.

Envelope, Timed Frames, Carrierinventar und gebundener Koordinatoreingang
bleiben waehrend der Operation als validierte Objekte vorhanden. Im Receipt
werden ihre wiederholten Vollkopien durch ihre bereits kanonisch gebundenen
Digests ersetzt. Herkunft, Quellidentitaet, reduzierte Werte und spaetere
Pruefbarkeit bleiben damit erhalten.

Eine statische Musterprojektion dieser Form umfasst fuer `op-0002` 886 Bytes;
einschliesslich der bestehenden Artefakthuelle 1.187 Bytes. Die bestehende
4.096-Byte-Einzelgrenze reicht daher aus. Die Erfolgs- und
Maximalpfadbudgets muessen bei dieser bevorzugten Korrektur nicht erhoeht
werden. Die konkrete Datenform muss vor einer Codeaenderung verbindlich
festgelegt werden.

## Alternative ohne Kompaktierung

Soll die derzeitige Vollserialisierung unveraendert bleiben, ist 21.768 Bytes
die kleinste gemeinsame Einzelgrenze fuer alle 57 gebundenen
Rezeptoroperationen. Daraus folgen bei derselben Grenze fuer jede Operation:

| Budget | Bisher | Vollserialisierungsalternative |
| --- | ---: | ---: |
| 57 Rezeptorreceipts | 233.472 | 1.240.776 |
| Erfolgsmaximum | 2.009.088 | 3.016.392 |
| maximales Einzelpfadbudget | 2.045.952 | 3.053.256 |

Die Erhoehung betraegt jeweils 1.007.304 Bytes. Die Summe der konkret
rekonstruierten 57 Huellen waere mit 1.235.388 Bytes geringfuegig kleiner;
eine gemeinsame Einzelgrenze muss jedoch den groessten zulaessigen Datensatz
abdecken. Diese Alternative konserviert technisch unnoetige Redundanz und ist
daher nicht die bevorzugte Korrektur.

## Fehlercodeweitergabe

`_exclusive_json` erzeugte korrekt den registrierten
`S2GTRecordingError("E008", ...)`. Der aeussere Ausnahmehandler in
`run_main_once` faengt jedoch jede Ausnahme und ruft ohne Typ- oder
Codepruefung `recorder.fail("E009", ...)` auf. Dadurch wurde der unmittelbare
Ressourcenfehler im terminalen Fehlerpfad als `operation-result-invalid`
klassifiziert.

Verbindliche kuenftige Regel:

1. Ein registrierter `S2GTRecordingError` behaelt seinen vorhandenen `.code`
   beim Fehlerabschluss unveraendert.
2. `E009` ist nur fuer nicht klassifizierte Ausnahmen beziehungsweise einen
   tatsaechlich ungueltigen Operationsresultatpfad zulaessig.
3. Ein bereits registrierter Fehlercode darf weder ueberschrieben noch aus
   einem nachgelagerten generischen Handler neu klassifiziert werden.
4. Der originale Ausnahmebeleg und der terminale Fehlerreceipt muessen
   denselben registrierten Fehlercode tragen.

Sowohl `E008` als auch `E009` sind fuer die aktive Phase registriert. Die
Korrektur benoetigt daher keinen neuen Fehlercode, sondern nur korrekte
Weitergabe.

## Entscheidung und naechster Schritt

S2-GX begruendet einen engen Korrekturvertrag, aber noch keine Codeaenderung
und keinen neuen Lauf. Der naechste Schritt soll ausschliesslich binden:

- die kompakte digestgebundene `ReceptorReceipt`-Datenform;
- deren maximale kanonische Groesse innerhalb der bestehenden 4.096 Bytes;
- die codeerhaltende Weitergabe registrierter `S2GTRecordingError`-Werte;
- fokussierte spaetere Negativtests fuer Groessengrenze und E008/E009-Trennung.

S2-GW wird nicht wiederholt oder repariert. Eine neue Hauptausfuehrung bleibt
bis zu Implementierung, neutraler Qualifikation und eigener Freigabe gesperrt.
