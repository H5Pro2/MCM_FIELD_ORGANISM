# S2-NF: Laufanbindung, neutrale Qualifikation nicht bestanden

Status: **NOT_QUALIFIED**. Genau ein Qualifikationsaufruf,
15 erfolgreiche Testmethoden von 16, ein ERROR, Exit-Code `1`.
Kein Retry, keine nachtraegliche Code- oder Fixturekorrektur.
Ausgangscommit `6407fc9`.

Qualifikations-ID: `s2nf-run-binding-qualification-20260906-01`.

```text
C:\Python314\python.exe -m reports.s2nf.qualify_run_once
```

Workspace-Root als Arbeitsverzeichnis. Der archivierte Aufrufer schrieb
vorab alle 16 eindeutigen Test-IDs, Quellenbindungen und Grenzen und startete
genau einmal:

```text
C:\Python314\python.exe -m unittest tests.test_s2nf_private_run -v
```

`stdout.txt` und `stderr.txt` sind die unveraenderten Prozessausgaben.
`result.json` bindet Testprotokolle und neutrale Artefakte. Ergebnisdigest:
`f3ae961e47491fb5f0803271e7ef53841beb1eba82868e4b68837cbec3e8365a`.

## Implementierter, weiterhin geschlossener Umfang

Vier kleine private Anbindungen fuer Quellen, Einmaleinstieg,
Gesamtverifikation und getrennte Auswertung. Die NF-Planpositionen bleiben
zwei frische Zustaende, drei Formationen und zehn Hinweise, insgesamt
13 Ereignisse und 40 Abrufbelege. Sie wurden nicht ausgefuehrt.

Wiederverwendet werden unveraendert die NE-Arme, beide Direktbaselines,
Paarung, Koordinatortypen, atomare Dateipublikation, Zustands-/Armdekodierung,
Formations-/PPB-Receiptpruefung und `verify_arm`. Kein historischer
Haupteinstieg wurde umetikettiert oder durch Monkeypatching veraendert.

Die spaetere Materialisierung liegt im Funktionslauf: Payloadhash vor
`analyze`, je Ereignis ein Audioaufruf, Video nur bei Formation, Rohdaten
anschliessend freigeben. Wiederholte Quellen muessen erneut denselben
Wertdigest ergeben. Keine separate Rezeptormessreihe implementiert.

Referenz bleibt historisches `sum(...)/24`; Alternative `ALL_BANDS_24`
ausschliesslich fuer B4/Fast. Slow-Regel und vollstaendige 9/3/8-Scans
bleiben unveraendert. NF-Grenzen: 800 Slotbesuche, hoechstens 19.200
Banddifferenzen plus 1.920 Gleichheitsvergleiche, 10.656 Formations-L1-Terme,
Abrufbeleg unter 32.768 und Gesamtbeleg maximal 4.194.304 Byte.

## Beobachteter Fehler

Test `test_06_missing_swapped_and_foreign_events` setzt absichtlich einen
visuellen Formations-Quellenbeleg in ein auditives Cue-Ereignis ein.
Die fehlenden/vertauschten Ereignisse wurden zuvor abgewiesen. Bei der
dritten Manipulation, dem fremden Quellenbeleg, endet die Pruefung jedoch
mit `KeyError: 'None'`, nicht mit dem erwarteten typisierten Bindungsfehler.
Die vierte Manipulation dieses Testkoerpers wurde deshalb nicht erreicht.

Aufrufpfad laut gespeichertem Trace:

```text
NF verify_record
-> unveraendertes NE _source
-> NE materialized_from_frames
-> NE source_record
-> catalog["visual"][str(spec.visual_ordinal)]
-> KeyError: 'None'
```

Der Cue hat keine visuelle Ordinalzahl, der absichtlich fremde Beleg aber
einen visuellen Frame. Die NF-Pruefung delegiert vor ausreichender
Ereignis-/Belegformpruefung. Der bestehende aeussere Dateiverifikator faengt
solche Exceptions technisch als `NOT_EVALUABLE`; eine Annahme dieses
beschaedigten Belegs wurde nicht beobachtet. Die fokussierte Qualifikation
ist dennoch fehlgeschlagen und wird nicht umgedeutet.

Keine der sieben NF-Quellen und keine reale NF-Geschichte war beteiligt.
Das ist kein Erhaltungs-, Rezeptor- oder Memoryfunktionsbefund.

## Neutrale Teilbeobachtungen, keine Gesamtqualifikation

Der separate neutrale Kompositionsbeleg und seine lesende Gesamtpruefung
sind beide `RECORDING_COMPLETE`: sechs Ereignisse, zwei tatsaechliche
neutrale Formationen, vier Hinweise, 16 Abrufbelege. Die beiden neutralen
AV-Inhalte belegen tatsaechlich je zwei B4-/Fast-Slots, Slow bleibt leer.
Beide Direktbaselines stimmen mit ihren jeweiligen Primaerarmen ueberein.

Der gebundene synthetische Auswertertest meldet unter Konkurrenz korrekt
`N=2, D=2, R=1, L=1`, also **FALSIFIED** fuer die absichtlich verletzte
neutrale Erhaltungsprognose. Der erhaltene Treffer verdeckt den Verlust
nicht. Leere Nenner bleiben `ERHALTUNG_NICHT_GEPRUEFT`.
Dies ist ausdruecklich kein Ergebnis der versiegelten NF-Quellen.

Weitere bestandene Testmethoden: geschlossenes Gate, native Audiozeit,
PPB-NO_UPDATE-Digests, Quellen-/Wertebindung, Armvollstaendigkeit,
Read-only-Dateipruefung, historische Mittelwertarithmetik und inklusive
Max-Grenze, unveraenderte Slow-Regel, kein B-Vorrang, Schreibkonflikte,
Groessenfehler und kompakter Quellenfehlerabschluss.

Neutraler Gesamtbeleg: 300.477 Byte. Darin 320 Slotbesuche, 1.152
Banddifferenzen, 288 Gleichheitsvergleiche, 1.440 Abrufwertvergleiche,
224 logische Abrufoperationen und 7.104 Formations-L1-Terme als Obergrenze.
Zusaetzliche kleine synthetische Regel-/Fehlerpruefungen bleiben separat
vom neutralen Kompositionsbeleg; es gab insgesamt nur zwei Formationen.

## Quellenbindung und verbleibende Grenze

Die 60 vorab gebundenen Code-, Quellen- und Belegdateien haben identische
Vor-/Nachhashes, vollstaendig in `result.json` dokumentiert.

| Neue Datei | SHA-256 |
| --- | --- |
| tools/_s2nf_private_run_sources.py | 92e96c0312f4718d02719d99cb1f528dce86aa836a4092105947e3ac79cc53a7 |
| tools/_s2nf_private_run.py | 6a14bbbbe29cb41f04b4a47dfe132bc679cb2044cc56f931af178836f25e385c |
| tools/_s2nf_private_run_verification.py | 2886d2c7a22decfbc1bc1bf4e396118f6afc51cc0a3fc1edbea208625722ace9 |
| tools/_s2nf_private_run_evaluation.py | 8a62e956f4966301b9f907aee6aae5bb76b62bdc5285175b5158e7975c66a01e |
| tests/test_s2nf_private_run.py | 80d711c270778e41c071883b76754e91154c70f8bb15d81bb1232c0965db96f9 |

Rezeptoranalysen, NF-PCM-Erzeugungen, Hauptgeschichten, Feld- und
Runtimeaufrufe jeweils **0**. Hauptgate bleibt **False**.
Historische NF-Vorversiegelung, S2-NE, Schwellen und Kerne unveraendert.
Fremde AGENTS-Aenderung, Konzeptnotiz und Bootstrap werden nicht versioniert.

Vorschlag an den Analysten: ausschliesslich im NF-Verifikator vor der
Delegation Quellenbeleg-Ereignisbindung und visuelle Form gegen den
Ereignistyp pruefen. Keine Aenderung des historischen NE-Pfads und kein
blosses Erweitern der Test-Erwartung um `KeyError`. Dies ist ein Vorschlag,
keine ausgefuehrte Korrektur und keine Freigabe fuer einen erneuten Test.

RUECKMELDUNG ERFORDERLICH: Der Hauptlauf bleibt gesperrt. Korrektur und neue
Qualifikation benoetigen eine eigene Freigabe.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses engen
Quellenbeleg-Typfehlers und einer begrenzten Korrekturfreigabe weiter.
