# S2-GS: Abschliessender statischer Audit der S2-GR-Laufhuelle

## Auftrag und Grenze

S2-GS prueft die in S2-GR materialisierte Lauf- und Beleginfrastruktur rein
statisch auf Vollstaendigkeit, Nichtzirkularitaet, terminale Exklusivitaet
und exakte Pfadbudgets.

Es wurden keine Projektmodule importiert, keine Tests ausgefuehrt und keine
Rezeptor-, Speicher-, Projektions-, Verbraucher-, Runner- oder Dateifunktion
aufgerufen.

Gepruefter Stand:

- S2-GR-Vertrag:
  `a402cfe2b74baa46ee5aae3432292158f6471c99b53e5024369702e2dd2835fc`
- Erfolgsregistry:
  `8b900da51f6a8921c5231679570f0aa3e188d56b9bd5507f989038a354787d05`
- Fehleroperationsregistry:
  `f6d201e3c1f5bd91f244a065ef8e97129f39a829c3c50b74b0a697460793c721`
- Fehlercode-Registry:
  `a6db907bf9065fd6a7afcf631441c5eda5b8993db01972bb533a8cefa5ac2e09`
- Fehlerpfad-Budgetregistry:
  `fcebc195aeb3ebc51879d9b5eb3657fe59e3f9df6339892ffff1375325597024`

## Operationsregistry

Die Registry enthaelt exakt und eindeutig:

```text
op-0001 bis op-0139
```

Alle 139 Zeilen besitzen nichtleere Bindungen fuer:

- Owner;
- Reservierungsdigest;
- Pfadrolle;
- Zugriffsart;
- Artefakttyp;
- Zielpfad;
- Fehlernachfolger;
- erforderlichen Zustand;
- Erfolgszustand;
- maximales Ausgabevolumen.

Operations-IDs, Indizes, Zielpfade und Ressourcenrollen sind eindeutig. Die
lineare Nachfolgerkette ist lueckenlos; nur `op-0139` endet bei `END`.

Alle expliziten Operationseltern besitzen einen kleineren Index als ihr Kind.
Es existiert keine rueckwaertsgerichtete Operationskante.

Jede Erfolgsoperation erzeugt genau ein START- und ein RESULT-Ereignis:

```text
139 * 2 = 278
```

## Fehlerpfade

### Vollstaendige Zuordnung

Die Fehlerpfadregistry enthaelt exakt 140 Varianten:

- `fp-0000`: `op-0001` vor Reservierung;
- `fp-0001`: `op-0001` nach Reservierung;
- `fp-0002..fp-0139`: je eine Variante fuer die entsprechende
  Erfolgsoperation.

Die Abbildung ist eindeutig:

```text
op-0001 pre-reservation  -> fp-0000 -> START_BLOCKED
op-0001 post-reservation -> fp-0001 -> err-0001
op-0002..op-0139         -> fp-0002..fp-0139 -> err-0001
```

Es fehlt keine registrierte Erfolgsoperation und keine Erfolgsoperation
besitzt mehr als einen aktiven Fehlerpfad fuer dieselbe Phase.

### Vorreservierungsgrenze

`fp-0000` besitzt:

```text
0 Erfolgsoperationen
0 Laufereignisse
0 Laufbytes
0 Laufartefakte
Terminal = START_BLOCKED
```

Damit entstehen vor bestaetigter Reservierung weder Laufverzeichnis,
`ReservationReceipt`, `NOT_EVALUABLE` noch Completion-Marker. Fuer
`START_BLOCKED` existiert keine ausgehende Registryoperation.

### Fehlerabschluss

Nach bestaetigter Reservierung verweist jede Erfolgsfehlerkante eindeutig auf
`err-0001`. Die Fehleroperationsregistry ist lueckenlos:

```text
err-0001 -> err-0002 -> err-0003 -> END
```

Alle drei Operationen erfordern `FAILING`. Nur `err-0003` erzeugt
`NOT_EVALUABLE`. Es existiert keine Rueckkante in den Erfolgs- oder
Evaluationsgraphen.

Scheitert der Fehlerabschluss selbst, ist nur
`HARD_STOP_UNCONFIRMED` zulaessig. Dieser Zustand erzeugt keinen
Erfolgsmarker und keine weitere Operation.

## Fehlercodes

Die Fehlercode-Registry enthaelt exakt 16 eindeutige Codes.

- `E001` ist ausschliesslich der Vorreservierungsphase und
  `START_BLOCKED` zugeordnet.
- `E002..E016` sind ausschliesslich zulaessigen nichtterminalen
  Laufphasen zugeordnet und fuehren zu `err-0001`.
- Jeder Code besitzt eine feste ASCII-Message-ID und einen festen
  ASCII-Nachrichtentext.
- Jeder Nachrichtentext liegt unter seiner Grenze von 64 Bytes.
- Kein Code, keine Message-ID und kein Text enthaelt Fallrolle, Bildrolle,
  Zielwert oder Sollentscheidung.

Die spezialisierten Codes fuer ExecutionEvidence, Regelbindung und reine
Auswertung sind nur in ihren jeweils passenden Zustaenden zugelassen. Die
allgemeinen Registry-, Owner-, Pfad-, Digest-, Ressourcen-, Journal- und
Publikationsfehler decken die uebrigen aktiven Phasen ab.

## Evaluationstrennung

In `op-0001..op-0131` existiert keine Eltern-, Pfad-, Owner- oder
Reservierungskante zum `EvaluationPlanSeal`.

Insbesondere enthalten weder `RUN_PREPARE`, `ExecutionPlan`,
`ReservationReceipt`, Reservierungsdigest noch
`ExecutionEvidencePackage` den Evaluationsplandigest.

Die erste direkte Beruehrung lautet ausschliesslich:

```text
op-0132 EVALUATION_RUN_BIND
  result:op-0131
  + external-evaluation-plan-seal
```

Alle spaeteren Evaluationsergebnisse haengen von dieser Bindung ab. Es
existiert keine zweite direkte Verbindung der beiden Wurzeln und keine
Kante zurueck in den Ausfuehrungspfad.

## Terminale Zustandsmaschine

Die Registry materialisiert genau:

```text
UNRESERVED
-> ACTIVE
-> EXECUTION_SEALED
-> EVALUATING
-> COMPLETING
-> COMPLETE
```

Aus jedem nichtterminalen Laufzustand ist alternativ nur der Wechsel nach
`FAILING` und weiter nach `NOT_EVALUABLE` zulaessig.

Die beiden exklusiven Zielpfade sind:

```text
terminal/complete/COMPLETE
terminal/failure/NOT_EVALUABLE
```

Nur `op-0139` darf den ersten, nur `err-0003` den zweiten Pfad anlegen.
Beide verwenden `CREATE_EXCLUSIVE_TERMINAL`. Keine Registryoperation
akzeptiert `COMPLETE`, `NOT_EVALUABLE` oder `START_BLOCKED` als
Vorzustand.

Damit gilt statisch:

- genau ein terminaler Abschluss;
- kein Error-Return in den Erfolgsgraphen;
- keine Evaluation nach Fehlerwechsel;
- keine Operation nach einem terminalen Zustand.

## Azyklizitaet

Der Erfolgsgraph ist streng nach steigender Operationsordinalzahl geordnet.
Der Fehlergraph ist streng nach `err-0001..err-0003` geordnet. Der
Evaluationsgraph beginnt erst nach `op-0131`. Die terminalen Knoten besitzen
keine Nachfolger.

Es wurde keine Selbstkante, Rueckkante oder zyklische Digestbeziehung
gefunden.

## Budgets

### Erfolgspfad

Die Summe aller `output_max_bytes` der 139 Erfolgsoperationen plus aller
278 Eventobergrenzen ergibt exakt:

`2.009.088 Bytes`

Enthalten sind Manifest, Reservierung, Journalereignisse, alle Funktions- und
Projektionsreceipts, ExecutionEvidence, EvaluationRunBinding,
EvaluationReceipts, FinalEvidence, CompletionCandidate und CompletionMarker.

Der externe `EvaluationPlanSeal` ist kein per-run Ausgabeartefakt und wird
nicht doppelt gezaehlt.

### Fehlerpfade

Jede Fehlerpfadzeile wurde aus ihrem tatsaechlich bestaetigten
Erfolgspraefix, dem fehlgeschlagenen START-/RESULT-Paar und dem festen
Fehlerabschluss von 38.912 Bytes neu berechnet.

Der groesste zulaessige Einzelpfad ist:

```text
fp-0139
1.998.848 Bytes bestaetigtes Praefix bis op-0138
+ 8.192 Bytes fehlgeschlagenes START/RESULT
+ 38.912 Bytes Fehlerabschluss
= 2.045.952 Bytes
```

Der Pfad enthaelt keinen CompletionMarker, weil die Ausgabe der
fehlgeschlagenen `op-0139` nicht publiziert wird. Der Erfolgspfad enthaelt
umgekehrt keine Fehlerartefakte.

Damit ist `2.045.952` das Maximum eines tatsaechlich zulaessigen
Einzelpfads und keine Summe gegenseitig ausgeschlossener Abschluesse.

## Auditentscheidung

Alle S2-GS-Pruefpunkte sind statisch erfuellt. Es wurde keine fehlende
Registryzeile, Fehlerkante, Pfadrolle, Terminalbindung, Rueckkante oder
Budgetposition gefunden.

Status:

`PASS_S2GS_STATIC_COMPLETE_RUN_ENVELOPE_ACCEPTED`

Dieser Befund nimmt ausschliesslich die statische Lauf- und Beleginfrastruktur
ab. Er implementiert und bestaetigt weder Runner noch Recorder, Fixtures,
Speicherfunktion oder Kontextvergleich.

S2-GK, Bilder, Schwellen, Speicherkerne und Funktionsvertrag bleiben
unveraendert.

## Naechster enger Schritt

Nach S2-GS darf eine separate Freigabe die private Fixture-, Runner-,
Recorder- und Verifikatorimplementierung exakt nach S2-GR zulassen.

Auch dieser spaetere Schritt darf noch keine Hauptausfuehrung starten. Vor
einem Funktionslauf bleibt eine neutrale technische Qualifikation der
implementierten Laufhuelle erforderlich.
