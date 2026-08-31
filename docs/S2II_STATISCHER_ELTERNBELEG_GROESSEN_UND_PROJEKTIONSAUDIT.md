# S2-II statischer Elternbeleg-Groessen- und Projektionsaudit

## Umfang und Grenze

S2-II prueft ausschliesslich die kanonischen Aufzeichnungsformen der privaten
S2-IG-Laufhuelle. Es wurden keine Projektmodule importiert, keine Tests
ausgefuehrt und keine Zustands-, Speicher- oder Funktionspfade aufgerufen.
S2-IH bleibt `QUALIFICATION_FAILED_EVENT_LIMIT`; der reale Funktionslauf bleibt
gesperrt.

## Befund zu `ie-op-171`

Ein START-Ereignis enthaelt derzeit:

- Ereignisschema, Index, Phase, Operations-ID und Operationsklasse;
- Owner-ID, Reservierungsdigest und vorherigen Ereignisdigest;
- `internal_parent_result_digests` als vollstaendige geordnete Liste;
- externen Elterndigest oder `null`;
- operationsspezifischen Input;
- Ereignisdigest und kanonischen Zeilenabschluss.

`ie-op-171` besitzt sechs History- und acht Case-Eltern, insgesamt also 14
interne Eltern. Im S2-IH-Qualifikationsbeleg ergibt diese Form exakt `1.550`
Byte. Mit dem tatsaechlichen Runner-Input und einer maximal gueltigen
96-Zeichen-Owner-ID ergibt sie `1.607` Byte. Beide Werte ueberschreiten
`MAX_EVENT_BYTES = 1.536`.

Die Liste der 14 Artefaktdigests ist fuer die Offline-Pruefung inhaltlich
notwendig, aber nicht als erneute vollstaendige Serialisierung im Ereignis.
Registry und veroeffentlichte Elternartefakte liefern Operations-IDs,
Reihenfolge und Artefaktdigests bereits unabhaengig.

## Gebundene Korrekturrichtung

Die Ereignisgrenze wird nicht erhoeht. Stattdessen ist fuer jeden START mit
mindestens zwei internen Eltern folgende kompakte Aufzeichnungsprojektion zu
verwenden:

```text
ParentSetV1 = canonical(
  schema,
  aktuelle operation_id,
  geordnete parent_operation_ids aus der Registry,
  geordnete parent_artifact_digests aus den validierten Artefakten
)

START speichert:
  internal_parent_count
  internal_parent_set_digest = sha256(ParentSetV1)
```

Bei null oder genau einem internen Elternbeleg bleibt die bestehende
`internal_parent_result_digests`-Form unveraendert. Der externe
Evaluationsplandigest von `ie-op-172` bleibt separat und unveraendert erhalten.
Die beiden Formen sind anhand der Registry-Elternzahl exklusiv; ein Ereignis
mit der falschen Form ist fail-closed abzulehnen.

Diese Schwelle vergroessert kein bestehendes Ereignis:

| interne Eltern | Vorkommen | heutige Rollenbytes | kompakte Rollenbytes | Differenz |
|---:|---:|---:|---:|---:|
| 0 | 1 | 38 | unveraendert | 0 |
| 1 | 106 | 104 | unveraendert | 0 |
| 2 | 68 | 171 | 124 | -47 |
| 5 | 6 | 372 | 124 | -248 |
| 8 | 1 | 573 | 124 | -449 |
| 14 | 1 | 975 | 125 | -850 |

Es bestehen insgesamt 294 interne Elternreferenzen und genau eine externe
Elternreferenz. Fuer die kompakte Form entstehen 76 typisierte
Parent-Set-Digests. Das ist Aufzeichnungsarbeit und veraendert kein
funktionales Memory-Budget.

## Vorausberechnung `ie-op-171` bis `ie-op-183`

Alle Werte enthalten die kanonische vollstaendige Huelle einschliesslich
Zeilenabschluss und eine maximal gueltige 96-Zeichen-Owner-ID. Artefakte
verwenden den jeweils groessten gebundenen regulaeren Status.

| Operation | Eltern | START heute | START korrigiert | Artefakt | Artefaktgrenze | RESULT |
|---|---:|---:|---:|---:|---:|---:|
| `171` | 14 | 1.607 | 757 | 1.692 | 3.072 | 668 |
| `172` | 1 + extern | 955 | 955 | 708 | 1.024 | 663 |
| `173-180` | je 2 | 870 | 823 | je 709 | je 1.536 | je 657 |
| `181` | 8 | 1.186 | 737 | 1.064 | 1.280 | 665 |
| `182` | 1 | 790 | 790 | 630 | 1.024 | 660 |
| `183` | 1 | 798 | 798 | 578 | 1.024 | 669 |

Damit liegt nach der Projektion jedes START- und RESULT-Ereignis unter 1.536
Byte. Alle Artefakte bleiben unter ihren bestehenden Einzelgrenzen. Die
kleinste nachgelagerte Artefaktreserve betraegt 216 Byte bei `ie-op-181`.

## Offline-Verifikation und Digestgraph

Der Verifikator muss fuer jede kompakte Zeile den Parent-Set-Digest aus der
unabhaengig rekonstruierten Registryreihenfolge und den kanonischen
Elternartefaktdigests neu berechnen. Er muss Anzahl, Projektionstyp und Digest
vergleichen. Die vollstaendigen In-Memory-Elternbelege und Artefakte bleiben
unveraendert.

Die Reihenfolge bleibt azyklisch:

```text
fruehere Elternartefakte
-> typisierter Parent-Set-Digest
-> aktuelles START-Ereignis
-> aktuelles Artefakt
-> aktuelles RESULT-Ereignis
-> spaetere Nachfolger
```

Der externe Evaluationsplandigest beruehrt den Ausfuehrungspfad weiterhin
erst bei `ie-op-172`. Es entsteht keine Rueckkante und keine Abhaengigkeit von
Evaluationsergebnissen.

## Ledger und Budgets

Operations- und Ereignisanzahl bleiben `183/366`. Receiptgrenzen bleiben
unveraendert. Die bestehenden konservativen Bytebudgets bleiben ausreichend:

- Artefaktgrenzen gesamt: `475.290` Byte;
- maximaler Erfolgspfad: `1.037.466` Byte;
- maximaler einzelner Fehlerpfad: `1.044.634` Byte.

Da `MAX_EVENT_BYTES` bei 1.536 bleibt und keine Artefaktgrenze steigt, ist
keine Erhoehung eines Gesamtbudgets erforderlich. Der Ausfuehrungsvertrag muss
zusaetzlich die 76 Parent-Set-Digestoperationen und die 294 validierten
internen Elternreferenzen binden. Funktionale Eingabe-, Speicher-, Probe- und
Vergleichsbudgets bleiben unveraendert.

## Entscheidung

Status: `S2II_COMPACT_PARENT_SET_PROJECTION_MATERIALIZABLE`

Die 1.550-Byte-Huelle ist nicht die nicht weiter reduzierbare Mindestform.
Freigegeben werden kann daher ausschliesslich die beschriebene kompakte
Parent-Set-Aufzeichnungsprojektion in Recorder, Registryvertrag und
Verifikator. Danach ist eine neue gemeinsame Qualifikation unter neuer ID
erforderlich. Bis dahin sind S2-IG-Laufhuelle und realer Funktionslauf nicht
qualifiziert.
