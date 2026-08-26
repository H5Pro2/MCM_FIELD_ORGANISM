# S1-IW: DTS-1-Kausalexpositions-Zeitordnungs-STOPP

## Status

S1-IW sollte endliche A/B/Gap-Werte und Dauern fuer S1-IV binden. Die
Vorpruefung der vorhandenen gekoppelten Schrittordnung zeigt jedoch, dass der
aktuelle Ereignisvertrag die Rezeptorbezeichnung und die tatsaechlich von
DTS-1 gelesene Beteiligung um ein Intervall verschiebt. Deshalb wurde vor
jeder Wertwahl gestoppt.

Entscheidung:

```text
STOPP_S1IV_EVENT_LABEL_DTS1_PARTICIPATION_TEMPORAL_MISALIGNMENT
```

Auditdigest:

```text
c3cb4826421b34129af5b3d412be853f23a67bac7dd2e3a88ae434f1c8a88c89
```

## Gebundene Schrittordnung

Der vorhandene DTS-1-Koppelschritt arbeitet atomar in dieser Reihenfolge:

1. abgeschlossenen Feld-, Anatomie- und Zeitvorzustand pruefen,
2. Kantenraten aus der abgeschlossenen Anatomie ableiten,
3. S1-HK-Beteiligung aus dem abgeschlossenen S-Vorzustand ableiten,
4. DTS-1-Ressourcenschritt fuer das Intervall buchen,
5. erst danach S/H mit dem aktuellen Rezeptorkontakt fortschreiben.

Damit kann ein im aktuellen Intervall eingespeister B-Rezeptorpayload die
DTS-1-Beteiligung desselben Intervalls nicht beeinflussen.

## Auswirkung

- In P_IK wirkt das mittlere B- beziehungsweise Gap-Ereignis auf DTS-1 erst
  im folgenden, als A bezeichneten Intervall.
- In P_IN erreicht das abschliessende B-Ereignis die DTS-1-Ressource vor dem
  unmittelbar folgenden S/H-Reset und Readout gar nicht.

Kontaktamplitude, Dauer oder Toleranz koennen diese fest gebundene
Vorzustandsreihenfolge nicht umkehren. Eine stillschweigende Verschiebung der
Ereignislabels waere kein Formadapter und ist unzulaessig.

## Begrenzte Korrektur

Vor jedem ressourcenaktiven A-, B- oder Gap-Intervall muss ein gemeinsamer
modellneutraler S/H-Grenzzustand fuer DTS-1 und B1 bis B6 gesetzt werden.
Dabei bleiben die jeweiligen modelleigenen Zustaende unveraendert erhalten.
DTS-1 darf seine Beteiligung erst nach diesem gemeinsamen Grenzschritt aus S
ableiten.

Der separate gemeinsame S/H-Reset vor dem Nullkontakt-Readout, die
kandidatenspezifische Recoveryintervention, die Profilquarantaene und alle
Informationssperren aus S1-IV bleiben bestehen. Nur die Regel, S/H innerhalb
der Vorgeschichte durchgehend zu tragen, muss ersetzt werden.

## Aussagegrenze

Der STOPP betrifft die zeitliche Expositionsdefinition, nicht die
Kernelkompatibilitaet, S1-HK-Observable oder vorhandenen direkten Ledger. Es
wurde kein Wert, Digest, Fixture oder Modell gebunden oder ausgefuehrt.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1iw_exposure_ordering_precheck.py
tests/test_dynamic_substrate_s1iw_exposure_ordering_precheck.py
```

Acht Tests pruefen Quellenbindung, atomare Schrittordnung, beide
Fehlzuordnungen, Nichtreparierbarkeit durch Werte, erforderliche gemeinsame
Grenzzustaende, erhaltene Regeln, Ausfuehrungsfreiheit und
Manipulationsschutz.

## Bester naechster Schritt

S1-IX darf ausschliesslich den korrigierten statischen
Ereignisgrenzenvertrag binden. Er legt gemeinsame S/H-Grenzrollen vor A, B und
Gap, die Erhaltung modelleigener Zustaende und die Ableitungsreihenfolge fest.
Noch keine Grenzwerte, Dauern, Fixtureimplementierung, Baselinekonfiguration,
Modellausfuehrung, Runtime oder Forschungsprobe.
