# S1-IN: DTS-1 Kapazitaetsfreigabe- und Wiederverwendungsbefund

## Status

S1-IN implementiert das private Auditharness und vollzieht den in S1-IM
vorregistrierten Doppelaudit genau einmal. Beide Durchgaenge liefern denselben
Receipt. Insgesamt wurden exakt `36` direkte Ressourcenaufrufe, `20`
technische Feldaufrufe und `0` Forschungsfeldschritte ausgefuehrt.

Entscheidung:

```text
PASS_DTS1_LOCAL_CAPACITY_RELEASE_AND_ADJACENT_REUSE
```

## Direkte Freigabe

Im kontaktfreien Recovery-on-Fenster werden auf A und B jeweils
`0.011261744217875269` direkt von refraktaer nach frei uebertragen.
Recovery-off liefert auf beiden Kanten exakt `0.0`. Die leitenden
Bindungswerte bleiben nach dem Fenster bitgenau armgleich.

Direkt vor der identischen B-Probe gilt am gemeinsamen Endpunkt:

```text
freie Ressource Recovery-on  = 0.5938895295688665
freie Ressource Recovery-off = 0.5826277853509914
Freigabemarge                 = 0.01126174421787518
```

## Direkte Wiederverwendung

Die nichtsaturierende benachbarte B-Probe bindet:

```text
Recovery-on  = 0.2153078155596401
Recovery-off = 0.21122499977283485
Marge        = 0.0040828157868052495
```

Freigabemarge und zusaetzliche B-Bindung wurden getrennt geprueft. Alle
Knotenzulassungen bleiben `1.0`; Clipping oder Saettigung erzeugt die
Richtung nicht.

## Gemeinsamer Feldreadout

Der getrennte Readout aus den Postprobe-Anatomien ergibt:

```text
C_B(Recovery-on)  = 0.3367717320392176
C_B(Recovery-off) = 0.33724837238920485
Marge off - on    = 0.00047664034998723404
```

Die maximale vollstaendige S/H-Armtrennung betraegt mit Haupt-H und H null
jeweils `0.000273420770841859`. Kein Feldreadout-Poststate wurde in eine
Ressourcenfolge zurueckgeschrieben. Der Feldreadout ist kein Ersatz fuer die
direkten Freigabe- und Wiederbindungsledger.

## Kontrollen

- N01: wertidentische vollstaendige Folgen und Readouts sind bitgenau;
- N02: Recoveryrate null ist bitgenau zur expliziten Recovery-off-Kontrolle;
- N03: ohne refraktaere Ressource und Turnoverquelle sind alle Transfers null;
- N04: B-Beteiligung null erzeugt exakt null B-Bindung;
- N05: A0 erzeugt bitgenau gleiche neutrale Feldausgaben und Basisraten `1.0`;
- N06: ein gemeinsamer vor Freigabe fixierter Adapter erzeugt bitgenau gleiche
  Feldausgaben;
- N07: bei H null bleiben S-Ausgaben und vorregistrierte Armtrennung erhalten.

Alle lokalen und globalen Bilanzreste bleiben unter der Float64-Grenze
`1.1368683772161603e-13`.

## Gegenbaselines

Fixed Adapter/Frozen-E1, Leaky/Integrator, F3/CONST-V und schneller Nachhall
wurden nur als statische Gegenprognoserecords gefuehrt. Kein Baselinemodell
wurde ausgefuehrt oder angepasst.

Fuer dynamisches zweistufiges E1 lautet der Record
`RELEASE_REUSE_ALONE_NOT_DISTINCT_NO_EXECUTION`. Freigabe und
Wiederverwendung allein grenzen DTS-1 daher nicht von E1 ab. Die direkte
Frei/Refraktaer-Intervention aus S1-IB und ihr kausaler Feldreadout aus S1-IE
bleiben fuer eine spaetere Gesamteinordnung gemeinsam erforderlich.

## Reproduzierbarkeit

```text
erster Receipt  = 1399b0750307208f83b5bb2082fe02eb84a970200766276b8b7c5f45796691bc
zweiter Receipt = 1399b0750307208f83b5bb2082fe02eb84a970200766276b8b7c5f45796691bc
Audit-Receipt   = 521dcb2750b87315550552979c4d1fe4ab7cd045fef4f3218265c3a32959a245
```

Die Strukturtests rufen den offiziellen Audit-Einstieg nicht auf.

## Aussagegrenze

PASS bestaetigt nur fuer das feste synthetische Fixture direkte lokale
Recovery, vergroesserte freie Kapazitaet und zusaetzliche Bindung auf einer
benachbarten Kante. Er bestaetigt keine Materialeignung, Runtimebereitschaft,
alleinige E1-Nichtreduzierbarkeit oder weitergehende Projektfaehigkeit.
Memory bleibt eine offene Forschungsrichtung; KI, Lernen, Vergessen,
Semantik, Organisation und Selbstregulation werden nicht behauptet.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_dts1_release_reuse_audit.py
tests/test_dynamic_substrate_dts1_release_reuse_audit.py
```

## Bester naechster Schritt

S1-IO darf ausschliesslich einen statischen Evidenz- und Falsifikationsaudit
ueber S1-IB, S1-IE, S1-IH, S1-IK und S1-IN gegen den urspruenglichen
S1-HH-Vertrag binden. Jedes Mindestkriterium und jede Gegenbaseline muss
einzeln als belegt, offen oder nicht unterscheidend klassifiziert werden.
Keine neue Gleichung, kein Fixture, keine Runtime und keine Ausfuehrung.
