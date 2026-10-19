# Publikationsplan: administrative Qualifikation

Status: **NOT_QUALIFIED**, 11/12 bestanden; genau ein Aufruf, 12 Prüfgruppen.
Kein historischer Test wiederholt. Keine Payload-, Decoder-, Rezeptor-, Memory- oder Medienausführung.

## Befund
Prüfdetails stehen vollständig in stderr.log und observations.json; Quellen und Prüfbestand sind vorab gebunden.
Der gespeicherte Fall wird mit 89.972 + 12.049 + 7.744 + 24.576 = 134.341 Byte gegen 131.072 geprüft.
Grenzgleichheit, Überschreitung, fehlende Positionen, alternative Fehlerpfade und Primärreserve sind getrennte Kontrollen.

### Konkreter Fehllauf

Prüfgruppe 12 scheitert in `tests/test_media_publication_plan.py:183`:
Die vollständige administrative Fehlerfixture umfasst **4.593 Byte**,
zulässig sind **4.096 Byte**, Differenz **497 Byte**. Diese Größe stammt
aus der neuen neutralen Fixture, nicht aus einer erneuten Medienverarbeitung.
Die folgende Fehlerpublikation und ihre Einmaligkeitskontrolle wurden daher
nicht erreicht. Ihr Bestehen wird nicht aus historischen Prüfungen übernommen.
Der vollständige Traceback bleibt in `stderr.log` erhalten (2.524 Byte).
Keine Kürzung, Grenzänderung, nachträgliche Codekorrektur oder Wiederholung.

Unabhängig bestanden: historischer Summenfall vor Medienbeginn und am
Schreibeinstieg, 131.072 Byte akzeptiert, 131.073 Byte abgewiesen, jede der
82 fehlenden Planpositionen einzeln abgewiesen, ungebundene Obergrenze
gesperrt, Verlustfreiheit administrativer Referenzen sowie blockierter
Haupteinstieg vor Manifest-/Medienverarbeitung. Die Fehlerpfadspitzen
126.597 / 130.469 / 134.341 Byte sind alternative Zeitpunkte; keine Addition
vollständiger Erfolgs- und Fehlerläufe.

### Bindung und Qualifikationsbilanz

Repositorybasis: `537109994cf777f8d36cda617aafe12226806c25`, Arbeitsbaum mit
bestehenden Änderungen. Die fünf neuen/geänderten aktiven Quelldateien
sind in `preregistration.json` einzeln gebunden; geerbte Abhängigkeiten
werden aus der vollständig verfügbaren Elternbindung aufgelöst.
Inventardigest: `e4a28f1d29d88deead64e115483c464869b8980ed5880e2ddc13e6e856218293`.
Alle gebundenen Quellhashes blieben beim Test unverändert.

Vor dem Test: 87.499 Byte Pflichtmetadaten, 8.513 Byte Vorregistrierung,
8.192 Byte Fixture- und 64 Byte Claimreserve, dazu je 8.192 Byte für Logs,
Abschluss und primäre Fehlerkopien: **128.844 Byte**. Der größte geplante
Abschlusstext einschließlich Fehlerstatus hatte 1.882 Byte; mit temporärer
Kopie ergibt das **130.726 / 131.072 Byte**. Die Vorregistrierungspublikation
lag bei 129.101 Byte. Quellen: **323.442 / 327.680 Byte**;
größte gemeinsame Vorbelegung damit **454.168 / 4.194.304 Byte**.
Die nachträgliche Beschreibung dieses Fehllaufs wird zusätzlich im aktuellen
Abschluss mitgezählt; sie verändert weder Vorregistrierung noch Testlog.
Die abschließenden Istwerte einschließlich dieser Dokumentation stehen in
`balance.json`. Die positive Gesamtbilanz ersetzt nicht die verletzte
4.096-Byte-Einzelgrenze der Fehlerform.

## Erfolgshülle
Die vollständige Rollenstruktur umfasst 82 Positionen: {'field': 3, 'formations': 59, 'generations': 59, 'metadata': 116, 'native': 180, 'nj': 59, 'verification': 1}. Mengen sind obere Instanzzahlen, keine neuen Messwerte.
Pro Position müssen finale Bytes und eine gleichzeitig bestehende temporäre Kopie gebunden werden. Log- und Abschlussreserven werden nur um vorhandene final publizierte Inhalte vermindert. Fehler vor, während und nach der Verlinkung sind Alternativen, keine addierten Laufabschlüsse. Eine vollständige obere Bytebilanz ist weiterhin nicht begründet; unbekannte Obergrenzen sperren den Start.

## Tragfähigkeit und Einsparungen
Bereits die historische Metadaten-Untergrenze überschreitet um 3.269 Byte. Neue Pflichtquellen, Plan- und Qualifikationsbindungen kommen hinzu. Keine behauptete Durchführbarkeit. Inhaltlich und kanonisch identische Objektdateien werden schon durch vollständigen Bytevergleich gemeinsam abgelegt. Die sechs bei DRAIN vorhandenen Verwaltungsobjekte sind nicht identisch. Für neue Einsparungen liegt kein belegter Bytebetrag vor; Quellenklassifikation, Historie und Reserven werden nicht passend geändert.

Historischer Lauf bleibt NOT_EVALUABLE. Keine neue Medienfreigabe. Gates False.

## Nächste Entscheidungsgrenze

Die gesamte Korrektur ist noch nicht qualifiziert. Zunächst wäre die neue
Diagnoseform innerhalb der unveränderten Einzelgrenze zu klären; keine
automatische Umsetzung freigegeben. Auch danach fehlen eine tragfähige
vollständige Medien-Erfolgshülle und belegte Einsparungsbeträge. Kein neuer
Medienlauf vorbereitet oder gestartet.
