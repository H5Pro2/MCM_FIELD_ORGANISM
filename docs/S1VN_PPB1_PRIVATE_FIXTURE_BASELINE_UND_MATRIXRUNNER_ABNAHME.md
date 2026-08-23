# S1-VN: PPB-1 private Fixture-, Baseline- und Matrixrunner-Abnahme

## Auftrag und Grenze

S1-VN implementiert die in S1-VM vorregistrierte private
Ausfuehrungsinfrastruktur. Der Schritt umfasst:

- drei feste Parameterrecords;
- acht labelfreie Fixturegeneratoren;
- sieben reine Vergleichsadapter;
- den kanonischen 384-Fall-Plan;
- typisierte Fall- und Schrittbeobachtungen;
- den vollstaendigen internen Ausfuehrungskorper;
- ein hartes Gate vor der Vollmatrix.

Die 384 registrierten Faelle wurden nicht ausgefuehrt. Nur nicht registrierte
Miniaturfixtures mit hoechstens vier reduzierten Rezeptorframes duerfen die
private Verkabelung in Tests pruefen.

## Private Implementierung

Das Modul
[`_ppb1_s1vn_matrix.py`](../mcm_field_organism/_ppb1_s1vn_matrix.py)
importiert nur:

- den privaten PPB-1-Kern;
- den privaten Rezeptorprofilbinder;
- `ReceptorContactFrame`.

Es importiert keinen Feldkern, keine Medienruntime, keine historische
Kandidatenruntime und keine oeffentliche Ausfuehrungsoberflaeche.

## Fixturegeneratoren

F01 bis F08 werden fuer jede der sechs Kombinationen aus P0/P1/P2 und
Audio/Video direkt in der gebundenen Rezeptordimension erzeugt. Jeder Frame
besitzt:

- korrekte Modalitaet, Geometrie und Traegerreihenfolge;
- eine streng steigende technische Quellgrenze;
- ausschliesslich endliche Werte im normalisierten Bereich;
- eine technische Snapshot-ID ohne Medien- oder Semantikinformation.

F06 verwendet deterministische 12-Bit-Codewoerter mit mindestens drei
verschiedenen Bits. Das Muster wird dimensionsgerecht wiederholt. Dadurch
liegen alle Fuellvektoren in jeder gebundenen Konfiguration strikt ausserhalb
der jeweiligen Matchschwelle.

F07 und F08 verwenden eine getrennte inaktive Fuellspur. Sie waehlt den
geprueften niedrigen Zustand nicht erneut aus und erlaubt damit die exakte
Pruefung an sowie einen Schritt vor der Ablaufgrenze.

## Vergleichsadapter

Implementiert sind:

| ID | Private technische Form |
|---|---|
| B01 | begrenztes Replay reduzierter Vektoren |
| B02 | Mittelwert eines auf Slotkapazitaet begrenzten Fensters |
| B03 | feste Prototypliste ohne Update oder Ablauf |
| B04 | einzelne exponentiell fortgeschriebene Spur |
| B05 | begrenzte Leaky-Spur |
| B06 | geklammerter Integrator |
| B07 | zustandsloser PPB-OFF-Arm |

B02 wurde vor der Abnahme gegen B04 praezisiert: B02 fuehrt ein echtes
endliches Fenster, B04 genau eine exponentielle Spur. Damit sind die beiden
Adapter strukturell verschieden. Zustands- und Readoutdigests sind
kanonisch; Historien und Traces werden als getrennte logische Speicherrollen
gezaehlt.

## Plan und Budget

`s1vn_matrix_plan()` materialisiert ohne Zustandsaufruf exakt:

```text
8 Familien * 3 Parameterrecords * 2 Modalitaeten * 8 Fixtures
= 384 eindeutige Pfade
```

Der vorbereitete Plan bestaetigt:

```text
PPB-Aufrufe:       9.296
Baselineaufrufe:  65.072
Gesamt:           74.368
ausgefuehrt:           0
```

Plan-Digest:

```text
35c1e589f749f1c1f1f24900f611fd43f8329d803a4b82ca94584d1925067ba3
```

## Typisierte Beobachtungen

Der interne Ausfuehrungskorper kann pro Schritt folgende Rollen erfassen:

- Ereignis und normalisierte Distanz;
- logische gespeicherte Vektorwerte;
- belegte und stabilisierte Slotzahl;
- ausgewaehlte Slot-ID;
- Verschiebung des ausgewaehlten PPB-Zustands gegen seinen aktuellen
  Bildungswert;
- Eingangsfolgen-, Endzustands- und Falldigest.

Jeder registrierte Pfad wird vor seiner Ausfuehrung erneut gegen
Config-Digest, erwartete Aufrufzahl und Fixture-ID geprueft. Der vollstaendige
interne Matrixkorper validiert anschliessend Fallreihenfolge, Fallzahl und
Gesamtaufrufzahl.

## Ausfuehrungsgate

`execute_s1vn_matrix()` bricht bedingungslos mit
`S1VN_MATRIX_EXECUTION_BLOCKED` ab. Der interne Ausfuehrungskorper ist
implementiert, aber ueber diesen vorgesehenen Einstieg nicht erreichbar.

Die Miniaturabnahme akzeptiert nur ein bis vier Frames, deren Snapshot-ID
mit `s1vn.contract.` beginnt. Registrierte F01-bis-F08-Frames werden dort
ausdruecklich abgelehnt. Damit kann die Verdrahtung getestet werden, ohne
einen Matrixfall vorwegzunehmen.

## Testergebnis

Die S1-VN-Abnahme besteht mit `19 von 19` neuen Tests. Zusammen mit
Profilbinder, PPB-Referenzkern und aktiven Architekturgrenzen bestehen
`81 von 81` fokussierte Tests. Die Paketkompilierung ist erfolgreich.

Beim ersten Test der neuen typisierten PPB-Beobachtung wurde eine falsche
Readout-Feldbezeichnung erkannt. Der Adapter wurde auf die bestehende
Kernrolle `slot_id` korrigiert; der PPB-Kern selbst blieb unveraendert. Der
abschliessende Testverbund besteht vollstaendig.

## Entscheidung

```text
S1_VN_THREE_PARAMETER_RECORDS_IMPLEMENTED
S1_VN_EIGHT_DIMENSIONED_FIXTURE_GENERATORS_IMPLEMENTED
S1_VN_SEVEN_DISTINCT_BASELINE_ADAPTERS_IMPLEMENTED
S1_VN_384_PATH_PLAN_AND_74368_CALL_BUDGET_ACCEPTED
S1_VN_TYPED_STEP_AND_CASE_RECEIPTS_IMPLEMENTED
S1_VN_INTERNAL_MATRIX_BODY_IMPLEMENTED
S1_VN_PUBLIC_EXECUTION_ENTRY_UNCONDITIONALLY_BLOCKED
S1_VN_19_OF_19_NEW_TESTS_PASS
S1_VN_81_OF_81_COMBINED_FOCUSED_TESTS_PASS
S1_VN_ZERO_REGISTERED_MATRIX_CALLS_EXECUTED
S1_VN_NO_FIELD_API_SNAPSHOT_OR_MEDIA_INTEGRATION
```

S1-VN bestaetigt die technische Ausfuehrbarkeit des vorregistrierten
Vergleichsaufbaus, aber kein Parameterergebnis und keinen Nutzen von PPB-1.

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-VO - privater reiner Ergebnisauswerter und abschliessender
        Vollmatrix-Preflight
```

S1-VO darf die in S1-VM gebundene Entscheidungsfolge als reinen Auswerter
implementieren und mit konstruierten, nicht aus der Matrix stammenden
Receipts testen. Der Preflight muss Plan-Digest, Fallregister, Aufrufbudget,
Ausfuehrungsgate, Frischstarts, Baselinehistorien und Resultatschema
vollstaendig pruefen.

Auch S1-VO darf die 384-Fall-Matrix noch nicht ausfuehren. Eine spaetere
Ausfuehrung benoetigt erst einen vollstaendig bestandenen Preflight und einen
eigenen klaren Ausfuehrungsschritt.

## Grundlagen

- [S1-VM statischer Auswahl- und Matrixvertrag](S1VM_PPB1_STATISCHER_PARAMETERWAHL_BASELINE_UND_AUSFUEHRUNGSMATRIXVERTRAG.md)
- [S1-VL privater Rezeptorprofilbinder](S1VL_PPB1_PRIVATER_REZEPTORPROFILBINDER_UND_DIMENSIONSSKALIERTE_SYNTHETISCHE_ABNAHME.md)
- [S1-VJ privater PPB-1-Referenzkern](S1VJ_PPB1_PRIVATER_REINER_REFERENZKERN_UND_SYNTHETISCHE_VERTRAGSABNAHME.md)
