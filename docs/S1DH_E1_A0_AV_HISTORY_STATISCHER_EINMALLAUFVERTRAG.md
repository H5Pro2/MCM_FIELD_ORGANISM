# S1-DH: E1-A0-AV-History statischer Einmallaufvertrag

## Status

Die kanonische AB/BA-History-Produktion ist als genau ein spaeterer Versuch
statisch registriert. Der S1-DG-Produzent wurde nicht aufgerufen. Es wurde
keine History erzeugt, keine Probe gebildet und keine Ziel-, Versuch- oder
Sperrdatei angelegt.

## Implementierung

```text
mcm_field_organism/e1_a0_av_history_one_shot_contract.py
tests/test_e1_a0_av_history_one_shot_contract.py
```

Der Vertrag bleibt privat und fuehrt bei Vorbereitung ausschliesslich
statische Pfad- und Digestpruefungen aus.

## Digestbindung

Fuer das vorhandene Projektverzeichnis `reports` gelten:

```text
S1-DH Einmallaufvertrag bce53a59cdc4afff5b88fe36ecd891a94b00167169e9b502abf0949eac9a1224
S1-DH Konfiguration     279a2557f943e224fcb12cb35259c4c97a53e536e2b56f2869770f634b5d34f3
S1-DG Produzent         25596d8280059c53c8c48a4d511e4e1b893d5f4bb848106076f56258d5d7d43c
S1-DE AB                a48d3d1620afa82d12dda855bb2ec03de3a57e7a69488d46edba6ec99cbef6d6
S1-DE BA                bb1d887f1ff5809964ae8175c7fa661430e8fbc8502f0522a7003d6c6fc3c011
S1-DE Permutation       ad509ef23a9394009baddc8185edc5a13f76882ee79e7c31d3b0ec111bfbcc78
```

Der Produzentendigest wird ueber den normalisierten UTF-8-Quelltext
gebildet. Die Vorbereitung importiert oder startet den Produzenten nicht.
Eine Aenderung am Produzenten oder an der festen Konfiguration sperrt den
Vertrag.

## Einmalpfade

```text
Ergebnis reports/e1_a0_av_history_s1di_once_v1.json
Versuch  reports/e1_a0_av_history_s1di_once_v1.attempt.json
Sperre   reports/e1_a0_av_history_s1di_once_v1.lock
```

Alle drei Pfade fehlen zum Abschluss von S1-DH. Vor einem spaeteren Start
muessen sie erneut gemeinsam fehlen. Der Versuchsnachweis muss unmittelbar
vor dem ersten Produzentenaufruf exklusiv angelegt werden. Nach einem
gestarteten Fehler bleibt er bestehen; es gibt keine automatische
Wiederholung.

Ein vollstaendiges Ergebnis darf erst nach erfolgreicher Produktion,
Kontrollpruefung, Metrikbildung und Resultatdigest atomar ueber einen
gleichverzeichnisigen exklusiven Link veroeffentlicht werden.

## Ergebnisfelder

```text
execution_id
one_shot_contract_digest
history_ab_digest
history_ba_digest
permutation_digest
producer_implementation_digest
configuration_digest
result_digest
technical_status
d_state
d_total_binding
result
```

`result` ist der reine S1-DG-Ergebniscontainer mit `b_ab`, `b_ba` und den
technischen Audits. Historische S/H-Felder und Probeobjekte bleiben
ausgeschlossen.

## Erlaubte Rohmetriken

S1-DH bindet genau zwei interpretationsfreie E1-Zustandsmetriken:

```text
D_state         Linf der paarweise identischen E1-Kanteninventare
D_total_binding abs(Summe Bindung b_AB - Summe Bindung b_BA)
```

Beide Werte werden ohne Schwelle berichtet. Weder ein positiver noch ein
verschwindender Wert ist in S1-DH eine Forschungsentscheidung. Der einzige
zulaessige Erfolgsstatus lautet:

```text
E1_A0_AV_HISTORY_STATES_PRODUCED
```

Er bedeutet nur, dass beide kontrollierten E1-Endzustaende und alle
Pflichtaudits vollstaendig erzeugt wurden.

## Gesperrte Rollen

Der Vertrag erteilt keine Freigabe fuer:

- eine eingefrorene AV-Probe;
- einen Memory-, Semantik-, Organisations-, Topologie-,
  Selbstregulations- oder KI-Claim;
- weitere Quellen-, Parameter-, Gap- oder Wiederholungsarme;
- eine Wiederholung nach angelegtem Versuchsnachweis.

## Technische Abnahme

Acht fokussierte Tests bestaetigen Pfadreinheit, Digestbindung,
Konfigurationsbindung, Quellcodebindung, Nebenwirkungsfreiheit,
Wiederholungsschutz, Claim-Sperren und private API-Grenze.

```text
8 fokussierte Tests
122 relevante Verbundtests
OK
```

## Aussagegrenze

S1-DH ist ausschliesslich ein Ausfuehrungs- und Persistenzvertrag. Es
existieren weiterhin keine kanonischen `b_AB`-/`b_BA`-Zustaende und kein
empirischer AV-History-Befund.

## Bester naechster Schritt

S1-DI implementiert den privaten Einmalexecutor und prueft Erfolg,
gestarteten Fehler, Digestabweichung, bereits verwendete Pfade, Metrikbildung
und atomare Veroeffentlichung zuerst mit einem synthetischen Produzenten.
Erst nach einer erneut sauberen finalen Pfad-, Quellcode- und Digestpruefung
darf der kanonische S1-DG-Produzent genau einmal aufgerufen werden. Eine
Probe bleibt auch danach eine getrennte spaetere Stufe.

S1-DI ist inzwischen implementiert, synthetisch abgenommen und nach finaler
Vorpruefung genau einmal kanonisch ausgefuehrt. Die Ergebnisdatei existiert
und sperrt jede Wiederholung. Siehe
`S1DI_E1_A0_AV_HISTORY_EINMALLAUF_UND_ZUSTANDSDIFFERENZ.md`.
