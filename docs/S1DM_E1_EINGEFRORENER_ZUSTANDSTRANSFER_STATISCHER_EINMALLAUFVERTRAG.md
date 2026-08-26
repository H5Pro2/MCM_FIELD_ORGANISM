# S1-DM: E1-Zustandstransfer statischer Einmallaufvertrag

## Status

Genau ein spaeterer kanonischer Transfer der veroeffentlichten `b_AB`- und
`b_BA`-Zustaende ist statisch registriert. Es wurde kein Zustand geladen,
keine AV-Probe konstruiert, kein Feld erzeugt und keine Ziel-, Versuch- oder
Sperrdatei angelegt.

## Implementierung

```text
mcm_field_organism/e1_frozen_state_transfer_one_shot_contract.py
tests/test_e1_frozen_state_transfer_one_shot_contract.py
```

Die Vorbereitung liest nur die vorhandene Evidenz, prueft normalisierte
Quellcodedigests und kontrolliert freie Pfade. Sie bleibt privat.

## Digestbindung

Fuer das Projektverzeichnis `reports` gelten:

```text
S1-DM Einmallaufvertrag  3b98967f3922f8f06fdf0576be5e09043e7f230858f2e9f45bf5e5b02dc93d9c
S1-DM Konfiguration      c9d9505b241f4074bb16fde5e6ebdd04f13daaec666dd83871ee6b0a7cfc0629
S1-DK Transfervertrag    4574cf1caae3792a3721249dac73b4a589062051bb944fcf2f43f317b4e347f8
S1-DL Implementierung    86dced5ddda7634d455fcbc50aca75eb6f64ef9b04f7f690c611edb997f2bdb6
b_AB                     bf93d871f6352f82bf0b4d1a0f2cbdc0a577d0f27d03cbc34cbd57ccc2754f86
b_BA                     354d65d02435c31fcad31b182ae78fb3cce0c88180c3f0d9a847cc8e368eb014
Probequelle              c0a9a59fb93996bdfd95247a1f6feec19723aeb36c84bd8bc8a423e677fbea7d
```

Jede Aenderung an Evidenz, S1-DL-Implementierung oder Konfiguration macht
die Registrierung ungueltig.

## Einmalpfade

```text
Ergebnis reports/e1_frozen_state_transfer_s1dn_once_v1.json
Versuch  reports/e1_frozen_state_transfer_s1dn_once_v1.attempt.json
Sperre   reports/e1_frozen_state_transfer_s1dn_once_v1.lock
```

Alle drei Pfade fehlen zum Abschluss von S1-DM. Sie muessen vor einem
spaeteren Start erneut gemeinsam fehlen. Nach einem gestarteten Fehler
bleibt der Versuchsnachweis bestehen; eine automatische Wiederholung ist
verboten. Ein Ergebnis darf nur gleichverzeichnisig und exklusiv atomar
veroeffentlicht werden.

## Gebundene Ausfuehrung

Der spaetere Executor muss dieselben sieben Arme fuer beide registrierten
Proposal-Partitionen ausfuehren:

```text
coarse  (0, 1_000_000)
split   (0, 500_000, 1_000_000)

p0, ab0, ba0, ab1, ba1, abf, baf
```

Erlaubt sind nur die in S1-DK gebundenen technischen Metriken. Der eigene
Probe-Partitionsrest darf den fehlenden S1-DC-History-Verfeinerungsrest
nicht ersetzen.

## Zulaessige Statuswerte

```text
TECHNICALLY_UNDECIDABLE
NO_REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE
REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE
```

Auch der dritte Status bezeichnet nur einen technischen Unterschied in der
Fortsetzung zweier gegebener eingefrorener Zustandsinputs. Er ist keine
nachtraegliche Aussage ueber deren History-Ursache.

## Gesperrte Rollen

S1-DM verbietet weiterhin:

- jede Wiederholung von S1-DI;
- den vollen S1-DC-Befund;
- weitere Quellen-, Parameter-, Gap- oder Wiederholungsarme;
- Memory-, Semantik-, Organisations-, Topologie-, Selbstregulations- oder
  KI-Claims.

## Technische Abnahme

```text
9 fokussierte Tests
155 relevante Verbundtests
OK
```

Geprueft sind Evidenz-, Implementierungs-, Konfigurations-, Partitions-,
Arm-, Metrik- und Pfadbindung, Nebenwirkungsfreiheit, Wiederholungsschutz,
Claim-Sperren, Fehlereinkapselung und private API-Grenze.

## Aussagegrenze

S1-DM ist nur eine statische Registrierung. Es existiert noch kein
kanonischer Transferexecutor und kein Transferergebnis. Der volle S1-DC-
Zweig bleibt gestoppt.

## Bester naechster Schritt

S1-DN implementiert den privaten Einmalexecutor. Erfolg, gestarteter Fehler,
falscher Digest, benutzte Pfade, unvollstaendige Kontrollarme, atomare
Veroeffentlichung und Wiederholungsverbot werden zuerst mit einem
synthetischen Ergebnisproduzenten geprueft. Die kanonische Probe bleibt bis
zu einer danach erneut bestaetigten finalen Vorpruefung unaufgerufen.

## Anschlussstatus

S1-DN hat den Einmalexecutor und seine Ergebniscontainer implementiert und
ausschliesslich synthetisch abgenommen. Die kanonischen Einmalpfade bleiben
unbenutzt. S1-DO implementiert als naechstes die getrennte kanonische
Produzentenbruecke, noch ohne Ausfuehrung.
