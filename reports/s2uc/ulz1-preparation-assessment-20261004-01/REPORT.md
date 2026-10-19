# ULZ1: Implementierung und neutrale Qualifikation

Stand: 2026-10-04. **PASS – ULZ1 implementiert, vollständig neutral qualifiziert
und vorstartgebunden.** Genau ein vollständiger neutraler Größenablauf.
Keine Forschungsquelle materialisiert oder abgespielt; separate Einmalfreigabe offen.

## Umsetzung

U verwendet den unveränderten MultiErrorAdapter. Der neue LastErrorAdapter
überschreibt ausschließlich consume_feedback: vorhandene Fehlerpaare werden
durch die aktuelle gültige Rückmeldung ersetzt. Die vollständige Methode wurde
statisch mit U verglichen; einzig der EMA-Zweig entfällt. L besitzt keine neuen
Instanzfelder, Beobachtungshistorien, Zusatzvarianten oder ungenutzte Speicherpolster.

Beide Arme werden unabhängig gegen ein separates Bestandsmodell und separat
fortgeschriebene Fehlerwerte geprüft. Ein ereignisweiser Vergleich kontrolliert
Originale, Bestandsreihenfolge, Berechtigungen, warme/kalte Zellen und Feedback.
Veränderte Werte oder Ausgaben sind zulässig; abweichender Lebenszyklus nicht.
Fehlerwerte des Beobachters werden niemals in die Produktionsbank geschrieben.

Neue Dateien: tools/_s2uc_ulz1_last.py, _s2uc_ulz1_replay.py,
_s2uc_ulz1_resources.py, _s2uc_ulz1_sources.py, _s2uc_ulz1_engine.py,
_s2uc_ulz1_stats.py, tools/s2uc_ulz1.py und tests/test_s2uc_ulz1.py.
Bestehende U-, A1-, K1- und LZ1-Dateien wurden nicht geändert.

## Gezielte Prüfungen vor dem Größenablauf

Acht Prüfgruppen bestanden:

- Q1: U-Hash unverändert; exakter Methodenvergleich; L ersetzt auch ein
  vorhandenes Fehlerpaar, statt es zu glätten.
- Q2: je elf Unterprüfungen für U/L: kalt, Gleichstand, eigene EP-Werte,
  sechs Zellen/neun Treffer, verlorene Generationen, Promotion bei offenem
  Ticket, Originalhalter, ungültiges Feedback, 44 atomare Unterbrechungspunkte
  je Arm, Reentranz/Endzensur und Ressourcen. Alle bestanden.
- Q3: neues kleines technisches Verlaufsmuster mit warmer Z-Konkurrenz,
  Promotion/Verdrängung, unabhängigen Referenzen und Bereinigung; eingespeiste
  Abweichungen von Bestand oder Feedback werden abgelehnt.
- Q4a: 10.000 Bootstrap-Ziehungen unabhängig über explizite Wiederholungsindizes
  nachgerechnet; Quantile und beide gerichteten Primärurteile geprüft.
  Gegengerichtete Handtabellen ergeben WIDERLEGT; alleiniger sekundärer
  Gerüstgewinn erzeugt keinen Primärerfolg.
- Q4b: fehlende Fälle, falsche Cluster, fehlende Ziele, falsche Maskenmetriken
  und nichtendliche Fehler verhindern die Auswertung.
- Q5a: Forschungsgate und vollständige Zielzahlen; neutrale Materialisierung
  ruft den Forschungsquellengenerator nicht auf.
- Q5b: ungültiger Start, Workerabsturz/-fehler, Exportüberlauf, unvollständige
  Auswertung, Abbruch, Timeout, Vorbereitungs-/Vorstartgrenze und Kollision
  enden geschlossen ohne nutzbares fachliches Urteil oder automatischen Neustart.
- Q5c: Einzelfile-/Expansionsgrenzen und Ablehnung der nicht freigegebenen
  Autorisierung. Alle Quellen würden vor erster Policy versiegelt.

Die zuvor abgenommenen vier 28-Frame-Beispiele wurden nicht erneut ausgeführt.
Entwicklungskorrekturen an der Testanbindung und Runtime-Erfassung stehen in
[Entwicklungsnotizen](development-notes.json). Kein fachliches Beispiel wurde
passend verändert. Die gebundene Qualifikation verwendet die korrigierte Fassung.

## Aussagegrenze

Neutrale Quellen folgen dem festen technischen Periodenmuster, nicht der
Forschungsziehung. Ihre numerischen U/L-Kontraste sind Funktionsprüfungen der
Auswertung und kein Nutzenbefund für die stabile oder wechselnde Verteilung.
Die erwartete Abwägung bleibt offen. A1/K1 bleiben aus, historische negative
T1/F-Ergebnisse und die präzisierte LZ1-Einordnung bleiben unverändert.

## Vollständiger neutraler Größenablauf

64 Geschichten,128 Arme,66.560 Quellenframes und133.120 Produktionsarm-Aufnahmen.
Je Arm66.560 unabhängige Referenzfortschreibungen,33.216 bewertete Ziele,
davon16.384 Y-Ziele. Alle Fälle vollständig, Referenzgleichheit und gepaarte
Lebenszyklen geprüft; vollständige Bereinigung und Zensur bei1041. Kein Neustart.
Worker686,759s, Supervisor687,893s; Gesamtqualifikation einschließlich gezielter
Prüfungen715,341s. Worker beendet, kein laufender Hintergrundprozess.

| Ressource, Maximum im Größenablauf | U | L |
| --- | ---: | ---: |
| zusätzlicher Python-Heap einschließlich Operationstransienten | 6.080 Byte | 5.980 Byte |
| Bank-Nutzdaten | 416 Byte | 416 Byte |
| Originalunion an beobachteten Operationsgrenzen | 15 | 15 |
| konservative Originalobergrenze einschließlich Aufnahme | 16 | 16 |
| kombinierte konservative Obergrenze mit Ausgaben | 18 | 18 |
| gültige Zellen im Quellenmuster | 3 | 3 |
| Ausgabeslots | 2 | 2 |
| zusätzliche Vektorpayloads durch Ausgabekopie | 0 | 0 |
| ganze erreichbare Systemobjekte an Operationsgrenzen | 19.938 Byte | 19.866 Byte |
| davon separat ausgewiesener Basisarm | 16.023 Byte | 16.007 Byte |
| logische Originalpayload | 5.760 Byte | 5.760 Byte |
| Receipt-Peak | 989 Byte | 926 Byte |
| transiente UTF-8-Obergrenze | 1.978 Byte | 1.852 Byte |

Die Originalunion und gültige Zellbelegung wurden auch ereignisweise verglichen,
nicht nur ihre Maxima. Die kleine Differenz der tatsächlichen Python-Nutzung
wird nicht künstlich ausgeglichen. Die sechs möglichen Zellen sind separat in
Q2 qualifiziert, nicht durch einen Dreizellenbefund als Vollbelegung behauptet.

Die ganze erreichbare Systemgröße ist eine Objektzählung an Operationsgrenzen,
kein Peak des gesamten Prozesses. Die Zusatzheap-Messung erfasst zusätzlich
die kurzzeitigen Allokationen der Operation. Diese überlappenden Kategorien
nicht addieren. Frame-Tracing-Zähler0 im Rohbeleg bedeuten nicht Nullbelegung;
hierfür gelten der neue Grenzstellenzensus und die konservativen Obergrenzen.
Originalobjektzählung im Rohbeleg umfasst auch die temporäre Aufzählungsliste;
die ganze Systemzählung traversiert dagegen die tatsächlich erreichbaren
Objekte ohne diese Hilfsliste. Gleiche Einheiten und Traversierung für beide Arme.
Eingangsobjekte und externe Referenz-/Belegobjekte werden je Fall separat als
Objektzählung ausgewiesen; sie stehen den Armen nicht als Speicher zur Verfügung.
Die installierte Python-Runtime ist hashgebunden, kein exportierter Paketbestand.

Maximaler Fall:2.157.348Byte expandiert (Grenze4MiB),111.317Byte gzip
(Grenze512KiB). Vollständiger neutraler Laufexport einschließlich Abschluss:
7.509.298Byte. Normalisiertes Qualifikationsarchiv:3.543.043Byte.
Die normalisierten gzip-Inhalte wurden vollständig bytegenau rekonstruiert
und gegen die ursprünglichen SHA256-Werte geprüft; keine Belege weggelassen.
Gebundene Vorbereitung einschließlich Vorstart, Vorlage und der Größe einer
späteren exakten operativen Autorisierung: 4,635,399 Byte (Grenze8MiB).
Separate Übergabedokumente sind kein Policy-Eingang und werden zusätzlich
aufgeführt; auch mit ihnen bleibt die Vorbereitung deutlich innerhalb8MiB.
Die vorberechnete operative Autorisierung wurde nicht geschrieben.

## Bindung und Start

131 Dateien in der Codebindung; Python3.14.4, ausführbare Datei, Python-DLL,
LZMA-Modul und zlib-Laufzeit gebunden. Plan enthält festes Quellenrezept,
Masken, zwei Primärrichtungen und Bootstrap-Rezept. U-Quelldatei stimmt weiterhin
mit der vorherigen LZ1-Bindung überein.

Codebindung-SHA256: `fe50d6600dc6cfc7f0cf22bd943a558984896cf519dfd4857c378617d2efea19`.
Vorstart-SHA256: `58f6009f7b5609e3993983bafe554f9029bdca31f82addf9c79fa5eec2120537`.
Reine Vorstartprüfung: PASS_ULZ1_PRESTART_NO_RESEARCH.

[Prüf- und Ressourcenbilanz](verification.json),
[gezielte Qualifikation](../ulz1-neutral-20261004-01/tests.json),
[vollständige Größenbilanz](../ulz1-neutral-20261004-01/full-size-facts.json),
[Vorstartbindung](../../../docs/S2UC_ULZ1_V1_20261004_VORSTARTBINDUNG.json),
[Startanleitung](../../../docs/S2UC_ULZ1_V1_20261004_START.md).

Nach separater ausdrücklicher Einmalbeauftragung, aus dem workspace:

```powershell
C:/Python314/python.exe -m tools.s2uc_ulz1 run --authorization docs/S2UC_ULZ1_V1_20261004_AUTORISIERUNG.json
```

Die Vorlage steht auf PENDING_SEPARATE_AUTHORIZATION. Operative Autorisierung
und Forschungszielordner existieren nicht. Der Befehl wurde nicht ausgeführt.
Nächster sinnvoller Schritt beim Projektleiter: dieses gebundene Paket technisch
abnehmen und anschließend über genau einen Forschungsdurchlauf entscheiden.
Keine neue Regeländerung vorgeschlagen; die wissenschaftliche Abwägung ist offen.
