# S2-OA: konsolidierter administrativer Anschluss, Vorbereitung

Stand 2026-09-10. **PREPARED_NOT_QUALIFIED; RUECKMELDUNG ERFORDERLICH.**
Keine neue Qualifikations-ID, kein Testaufruf, kein Hauptlauf. Keine
Payload-, Rezeptor-, NJ-, Memory- oder Feldausfuehrung; kein Replay.
Die vorliegende Bearbeitung erzeugt nur einen administrativen Manifestentwurf,
ein Pruefinventar und eine Serialisierungsbilanz. Die Ausfuehrung des
administrativen Bilanzprogramms ist keine Funktionsqualifikation.

## Prospektive Entscheidung und aktiver Anschluss

Der private Haupteinstieg verwendet jetzt `s2oa.bound-main.v4` und verlangt
genau eine aktuelle, vollstaendige administrative Qualifikationsbindung.
`load_bound()` laedt nicht mehr die Kette aus 20/20, 14/14, 13/14 und 13/16.
Die bestehenden Delta-Pruefhelfer verbleiben unbenutzt; ihr Vorhandensein ist
keine aktive Ladeabhaengigkeit. Die neue Aenderung ist **noch nicht getestet**.

Die neue Ausgabe ist eine direkte kanonische JSON-Huelle. Sie braucht weder
die v3-Referenzkompaktierung noch deren historische Manifest-Rekonstruktion.
Die 28 ID-Zuordnungen stehen vollstaendig im Beleg. Keine funktionale
ID-Ableitung, Ereignisverarbeitung oder Memoryregel wurde geaendert.
Historische v3-Dateien werden nicht durch Umetikettierung zu v4-Dateien.

Der aktive Entwurf steht in `manifest.json`: alle 73 derzeit gebundenen
Code-/Dokumentidentitaeten vollstaendig, nicht als Hashdelta. `inventory.json`
bindet 30 vorgesehene Kontrollen fuer **diesen administrativen Anschluss**.
Eine spaetere `qualification.json` muss genau diesen Manifestdigest, gleiche
Vor-/Nachquellhashes, einen Testaufruf und alle 30 einzeln bestandenen
Kontrollen belegen. Sie existiert nicht. Ihr Fehlen sperrt den Einstieg.

Das Inventar ist noch keine ausgefuehrte oder bereits fertig implementierte
Testsuite. Vor einem freigegebenen Aufruf muessen die tatsaechlichen Test- und
Aufrufdateien ebenfalls in der vollstaendigen aktuellen Codebindung stehen;
deren Referenzbytes muessen innerhalb der hier ausgewiesenen Restbelegung
bleiben. Kein zusaetzlicher Delta-Nachweis und keine weitere 4-KiB-Reserve.

Die spaetere administrative Qualifikation behauptet keine neue vollstaendige
Funktionsqualifikation. Die bisherigen funktionalen Pruefungen bleiben
historische, versionsbezogene Evidenz. Ihre Passzahlen werden weder addiert
noch in das neue Ergebnis uebertragen. Der neue Nachweis prueft die aktuelle
Anschlussgrenze eigenstaendig, nicht nachtraeglich die reale OA-Geschichte.

## Aktive Abhaengigkeiten und Archiv

| Aktive Artefakte | Klasse | Byte |
| --- | --- | ---: |
| administrative-binding: binding.json | Metadaten | 15.594 |
| administrative-binding: preregistration.json | Metadaten | 2.977 |
| admin-binding-qualification: preregistration.json | Metadaten | 2.082 |
| admin-binding-qualification: result.json | Metadaten | 2.167 |
| admin-binding-qualification: stderr.txt | Metadaten | 2.618 |
| admin-binding-qualification: stdout.txt | Metadaten | 0 |
| aktuelles inventory.json | Metadaten | 4.523 |
| aktuelles manifest.json | Metadaten | 11.260 |
| neuer Qualifikationsabschluss, unveraenderte volle Reserve | Metadaten | 4.096 |
| administrative-binding: verification.json | Verifikation, innerhalb 262.144 | 1.580 |
| source-preseal: execution-plan.json | Quellenzusatzhuelle | 78.644 |
| source-preseal: evaluation-plan.json | Quellenzusatzhuelle | 1.665 |
| source-preseal: preregistration.json | Quellenzusatzhuelle | 69.553 |
| source-preseal: seal.json | Quellenzusatzhuelle | 6.683 |
| source-preseal: verification.json | Quellenzusatzhuelle | 1.421 |
| source-binding-qualification: result.json | Quellenzusatzhuelle | 4.355 |

Alle vollstaendigen Pfade, SHA-256-Werte und Dateigroessen stehen im Manifest.
Die sechs historischen Quellenartefakte bleiben voll mitgezaehlt:
**162.321 Byte**, keine nur als Digest berechnete Einsparung. Die vollstaendige
bestehende administrative Herkunftskette bleibt ebenfalls geladen und gezahlt.
Die alten Abweichungen werden dadurch nicht rueckwirkend budgetkonform.

Nicht mehr operative Qualifikationsvoraussetzungen sind die Laufprotokolle
der Single-Runtime-, Main-Binding-, Event-ID- und Compact-Reference-Pruefungen
sowie der fehlgeschlagene reale OA-Lauf. Diese Dateien bleiben vollstaendig
im Archiv, einschliesslich aller Fehlertexte und der 22.867-Byte-Ablage der
letzten Fehlqualifikation. Der neue Loader braucht sie nicht zur
Statusaggregation, Hashrekonstruktion oder Decodierung.

Historische Test-/Hilfsdateien koennen weiterhin als Codeidentitaet im
Manifest stehen. Das ist weder ein Import ihrer Ergebnisdateien noch eine
Uebernahme ihrer Passzahlen. Repository-Quelltext ist wie bisher keine zweite
Kopie im Laufartefakt; seine Identitaet wird vollstaendig gebunden.

`balance.json`, dieser Vorbereitungsbericht und die gespeicherte neutrale
Formvorlage sind **Vorbereitungs-/Archivevidenz**, nicht Eingaben des neuen
Hauptloaders. Der Loader misst die tatsaechlichen Laufartefakte neu. Diese
Trennung ist prospektiv; sie ist keine Umklassifikation alter Fehlbelege.
Eine zukuenftige Qualifikation muss ihre gesamte eigene Ausgabe ebenfalls
bilanzieren. Ausgelagerte, fuer ihre Akzeptanz notwendige Belege duerfen nicht
unter Berufung auf diesen Absatz verschwinden.

## Tatsaechliche IDs und Formbilanz

`s2oa-event-e01` bis `s2oa-event-e28` haben **14 Zeichen**. Die historischen
neutralen `neutral-oa-01`-IDs haben 13. Es wird keine Laengengleichheit behauptet.

Statisch erfasste Verwendungen im unveraenderten Runtimeanschluss:

- `bind_input`, Zeilen 62-64: AV-`pair_id` ist die technische Ereignis-ID, 14.
- `formation_context`, Zeilen 126-132: Owner-ID 20, Consume-ID 22 Zeichen.
- `MemoryBranch.__call__`, Zeilen 167-170: dieselben Owner-/Consume-Ableitungen.
- `pack_formation`/`unpack_formation`, Zeilen 133-157: diese IDs sind bereits
  als Kontextreferenzen serialisiert; die Rekonstruktion benutzt die technische
  ID. Sie verschwinden nicht semantisch und werden nicht auf 13 gekuerzt.

Die rein administrative Formabbildung durchlaeuft rekursiv alle Schluessel
und Werte des gespeicherten neutralen Gesamtbelegs. 48 ausgeschriebene
Ereignis-ID-Vorkommen erhalten jeweils ein zusaetzliches Byte. Weitere
Owner-/Consume-Zeichenfolgen sind dort nicht ausgeschrieben, sondern durch
die bestehenden Kontextreferenzen vertreten. Ihre neuen Laengen sind oben
explizit gebunden und im Inventar separat zu pruefen.

Core: **809.384 -> 809.432 Byte**. ID-Tabelle vollstaendig **1.041/2.048 Byte**.
Neue aeussere Form: **813.321 Byte**, Shell 3.889 Byte. Die alten Digests bleiben
hier ausschliesslich feste 64-Zeichen-Platzhalter fuer die Groessenbetrachtung.
Es wird kein funktional gueltiger neuer Laufbeleg erzeugt oder behauptet.

## Vollstaendige Bilanz vor Ablehnung

Metadaten:
25.438 historische Administration + 4.523 Inventar + 11.260 Manifest
+ 4.096 Qualifikationsreserve + 9.399 Runtime-Metadaten + 3.889 Shell
+ **512 Berichtreserve = 59.117/65.536 Byte**. Rest: **6.419 Byte**.
Kleinere kuenftige Ergebnisdateien reduzieren die gebundene Reserve nicht.

| Zusatzklasse | Tatsaechliche neutrale Form | Unveraenderte Reserve |
| --- | ---: | ---: |
| Quellen, vollstaendig | 162.321 | 162.321 |
| NJ | 12.482 | 22.528 |
| Formationen | 21.932 | 30.720 |
| Generationen | 11.623 | 30.720 |
| Gemeinsam | 208.358 | **246.289/262.144** |

Verbleibende gemeinsame Reserve: **15.855 Byte**. Sie ist kein separater
Freiraum fuer jeden Bestandteil. Die gemessenen Einzelgroessen aller
21 Zustaende, 28 Eingaben/Schritte, 16 Scans und Zusatzbelege stehen in
`balance.json`; keine Funktionspruefung dieser Form wurde wiederholt.

Konkrete Form mit den **vollen** NJ-/Formations-/Generationsreserven,
4.096 Qualifikations- und 512 Berichtbyte, beiden Abschlussgrenzen von je
262.144 Byte sowie 4 Byte Verifikationsclaim:
**1.583.694/4.194.304 Byte**, Rest **2.610.610 Byte**.
Die administrative Verifikation ist innerhalb der Verifikationsgrenze
enthalten, nicht nochmals zusaetzlich reserviert.

Auch die Ueberschreitung ist voll sichtbar: Wuerden alle lokalen Obergrenzen
fuer Zustaende, Eingaben, Schritte und Scans gleichzeitig ausgeschoepft,
ergibt sich inklusive Abschluss **4.335.858 Byte**, also **141.554 Byte zu viel**.
Diese Summe ist keine zulaessige gemeinsame Reserve. Die unveraenderte globale
Grenze verbietet diese gleichzeitige Ausschoepfung. Die konkrete Form ist
tragfaehig; eine allgemeine Groessengarantie fuer beliebige Werte ist damit
nicht erbracht. Es wird keine Grenze angehoben oder neue Datenreserve erfunden.

Der neue lokale Bilanzierer trennt `measure`/`inspect_envelope` von `enforce`.
Auch bei Ueberlauf liefert er zuerst alle Einzelbeitraege, Klassensummen,
Gesamtsumme und Verletzungen. Ein typisierter Budgetfehler traegt dieselbe
vollstaendige Bilanz. Der administrative Haupteinstieg kann diese im
Fehlerbeleg erhalten. Historische interne Einzelvalidatoren bleiben unveraendert;
dies ist keine globale Lockerung oder allgemeine Fehlerdiagnoseplattform.

## Isoliertes, zusammengefuehrtes Pruefinventar

30 konkrete Kontrollen stehen in `inventory.json`, nicht 30 bestandene Tests:
28-ID-Rekonstruktion und alle Ableitungen; e01-LM-Grenze; aktuelle Manifest-/
Qualifikationsbindung; Quellen-/Archivabschluss; unabhaengige ID-Pruefung;
alle Byteklassen; reservierte Abschlussbelege; vollstaendige Fehlerbilanz.
Keine Addition historischer 20/20-, 14/14- oder Teilpasszahlen.

Jede Negativprobe beginnt mit einer frischen synthetischen Bilanz. Beispiele:

- Metadaten-Einzelgrenze: ein Eintrag 65.537, Quellen/Reserven/sonstige Byte 0.
- Metadaten-Gesamtgrenze: zwei einzeln gueltige Eintraege 32.768 und 32.769.
- Quellen-Einzelgrenze: 174.081 Quellenbyte, 100 Metadatenbyte, Reserven 0.
  Metadaten, gemeinsame Huelle und Gesamtgrenze bleiben gueltig.
- Quellen-Gesamtgrenze: zwei einzeln gueltige Eintraege 87.040 und 87.041.
- Globale Grenze: kleine gueltige Klassen, nur `other_total` loest Ueberlauf aus.

Die jeweils logisch mitverletzte **eigene** Klassensumme bei einer
Einzelueberschreitung wird ebenfalls berichtet; sie ist kein vorgelagerter
Fehler einer anderen Klasse. Die Tests pruefen diese erwartete Verletzungsmenge
und alle nicht untersuchten Grenzen vor der eigentlichen Fehlerassertion.

Eine wichtige Unmoeglichkeit wird nicht ueberdeckt: alle gueltigen
Quellen-/Zusatzklassen zusammen sind maximal 258.048 Byte. Ein isoliertes
`SHARED_LIMIT` im vollstaendigen Ledger mit zugleich gueltigen Einzelklassen
ist daher unerreichbar. Statt einer ungueltigen Fixture prueft a24 den
vorhandenen direkten Summeneinstieg separat; das ist ausdruecklich keine
behauptete vollstaendige Ledger-Erreichbarkeit.

## Grenze und naechste Entscheidung

Kein Test, keine erneute Versiegelung, keine neue Laufnummer. Beide alten
Fehlqualifikationen bleiben NOT_QUALIFIED, der reale OA-Lauf NOT_EVALUABLE.
Gates False; ME/MI gesperrt, Prognosezweig ruhend. Die Quelle, ihre Payloadhashes,
Ereignisfolge und Funktionsprognosen sind unveraendert.

RUECKMELDUNG ERFORDERLICH: Analystenentscheidung ueber diese prospektive aktive
Abhaengigkeitsgrenze und das zusammengefuehrte administrative Pruefinventar.
Danach kann genau dessen Testimplementierung vorab mitgebunden und ein
separat freigegebener Qualifikationsaufruf vorbereitet werden. Kein Hauptlauf.

WEITER: Am besten geht es jetzt mit der Pruefung dieses konsolidierten aktiven
Anschlusses und seiner vollstaendigen Bytebilanz durch den Analysten weiter.
