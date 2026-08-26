# S1-BY: E1 E2-Laufkomposition und Ergebniscontainer

## Status

Statischer End-to-End-Kompositions- und Ergebnisvertrag fuer den ersten
eingefrorenen E2-Lauf. Die spaetere Implementierung und der einmalige Lauf
sind in S1-BZ dokumentiert. Dieses Dokument bleibt die unveraenderte
Vorregistrierung und enthaelt selbst keinen Memory-, Lern-, Organismus- oder
KI-Befund.

## Ziel

S1-BY verbindet ohne neue Mechanik:

```text
S1-BX  gespiegelte Achtkontakt-Geschichten
S1-BW  eingefrorener aktiver und ablatierter Probeoperator
P0     bestehender neutraler S/H-Pfad
G_L/R  exakt passende feste Kantenraten
```

Die Komposition darf keine Parameter, Kontakte oder Laufdauer anhand eines
Ergebnisses veraendern.

## Getrenntes Modul

Die spaetere Implementierung liegt in:

```text
mcm_field_organism/e1_frozen_e2_run.py
tests/test_e1_frozen_e2_run.py
```

Keine Rolle wird aus `__init__` oder `current_api` exportiert.

## Frisches kanonisches Probefeld

Das gemeinsame Probefeld `F*` wird nicht aus `left_field` oder `right_field`
des Geschichtsresultats abgeleitet. Stattdessen wird aus einer frischen
wertidentischen Kopie des urspruenglichen Anfangsfeldes genau ein neutraler
Vorbereitungsschritt ausgefuehrt.

Feste Vorbereitung:

```text
Vorbereitungskontakt Q = (0.30, -0.20, 0.60)
Dauer                   = 1.0 s
gemeinsame Uhr           = e1.probe.organism
Intervall                = Tick 0 bis 20
ticks_per_second         = 20.0
Runtime                  = advance_neutral_fast_shared_field(...)
```

Das resultierende `F*` besitzt einen gueltigen abgeschlossenen
Rezeptorzustand und Snapshot-Digest. Es enthaelt kein E1 und keine
Geschichtsreferenz.

Vor den Armen werden tiefe getrennte Kopien von `F*` erzeugt. Verbindlich
gilt:

```text
gleicher Snapshot-Digest
gleiche S- und H-Werte
gleiche Docks und Geometrie
gleicher Tick und gleiche Organismuszeit
keine gemeinsame veraenderliche Objektidentitaet
```

## Feste Probe

```text
Probe P                 = (0.75, -0.25, 0.25)
Hauptintervall          = Tick 20 bis 40
Dauer                   = 1.0 s
ticks_per_second        = 20.0
```

Alle Arme erhalten wertidentische, aber objektgetrennte
`ReceptorDistribution`- und `MCMFieldStepTime`-Objekte.

## Verbindliche Ausfuehrungsreihenfolge

```text
1. neutralen E1-Anfang und frisches Anfangsfeld validieren
2. S1-BX-Geschichten genau einmal erzeugen
3. Energie-, Spiegel- und Gesamtbindungskontrollen pruefen
4. historisches left_field und right_field fuer Probe sperren
5. F* durch den neutralen Vorbereitungsschritt genau einmal erzeugen
6. sieben objektgetrennte F*-Kopien bilden
7. P0 ausfuehren
8. L0 und R0 mit eingefrorenem E1 und Rueckwirkung aus ausfuehren
9. L1 und R1 mit eingefrorenem E1 und Rueckwirkung an ausfuehren
10. G_L und G_R aus den in L1/R1 angewendeten festen Adaptern ausfuehren
11. Eingabe-, E1- und Identitaetskontrollen pruefen
12. rohe Metriken bilden und unveraenderlichen Ergebniscontainer ausgeben
```

Kein Arm liest den Ausgang eines anderen Arms. Nur die unveraenderlichen
Geschichts-E1-Zustaende und vorab erzeugten Probeobjekte werden weitergereicht.

## Sieben Ergebnisarme

```text
P0   neutrales Feld ohne E1
L0   linker E1-Zustand, eingefroren, Rueckwirkung aus
R0   rechter E1-Zustand, eingefroren, Rueckwirkung aus
L1   linker E1-Zustand, eingefroren, Rueckwirkung an
R1   rechter E1-Zustand, eingefroren, Rueckwirkung an
G_L  fester Adapter aus L1, ohne E1-Zustandsentwicklung
G_R  fester Adapter aus R1, ohne E1-Zustandsentwicklung
```

## Zeitverfeinerungsarme

Die Probe P wird zusaetzlich mit exakt denselben festen Adaptern in zwei und
vier gleich langen Teilintervallen ausgefuehrt:

```text
n=1: 20 Ticks
n=2: 2 * 10 Ticks
n=4: 4 * 5 Ticks
```

P bleibt in jedem Teilintervall konstant. E1 bleibt eingefroren. Da die
Kantenraten und der Randkontakt konstant sind und S/H spektral exakt
integriert werden, muessen die drei Aufloesungen bis auf numerische Rundung
denselben Endzustand liefern.

Der Verfeinerungsrest wird getrennt fuer S und H gebildet:

```text
R_S = max(
    Linf(L1_n2.S - L1_n4.S),
    Linf(R1_n2.S - R1_n4.S)
)

R_H = max(
    Linf(L1_n2.H - L1_n4.H),
    Linf(R1_n2.H - R1_n4.H)
)
```

Die n=1-Ergebnisse bleiben die primaeren Hauptarme. n=2 und n=4 dienen nur
der Numerikkontrolle.

## Ergebniscontainer

```text
E1FrozenE2RunResult
    history_result
    pre_probe_snapshot_digest
    p0_field
    left_ablated_field
    right_ablated_field
    left_active_field
    right_active_field
    left_fixed_gain_field
    right_fixed_gain_field
    left_active_n2_field
    right_active_n2_field
    left_active_n4_field
    right_active_n4_field
    metrics
```

Der Container speichert keine Interpretation und keinen Erfolgsstatus.

## Unveraenderliche Rohmetrik

```text
E1FrozenE2Metrics
    pre_s_linf
    pre_h_linf
    state_linf
    total_binding_difference
    mirror_binding_error
    active_s_linf
    active_h_linf
    ablated_s_linf
    ablated_h_linf
    p0_a0_s_linf
    p0_a0_h_linf
    fixed_gain_s_linf
    fixed_gain_h_linf
    refinement_s_linf
    refinement_h_linf
```

Alle Werte sind endliche nichtnegative Floats. Keine Metrik darf eine
Bezeichnung wie Memory, Praegung oder Erfolg tragen.

## Exakte Identitaetskontrollen vor Ergebnisbildung

Die Implementierung bricht ohne Ergebniscontainer ab, wenn eine dieser
Kontrollen scheitert:

```text
pre_probe_snapshot_digest in allen sieben Armen gleich
P0 == L0 == R0 im Felddigest
L1 == G_L im Felddigest
R1 == G_R im Felddigest
left_e1_state nach L0 und L1 objektidentisch zum Geschichtszustand
right_e1_state nach R0 und R1 objektidentisch zum Geschichtszustand
historische S/H-Endfelder nicht als Probeobjekte verwendet
```

## Vorregistrierte numerische Toleranz

Fuer reine Spiegel- und Fixed-Gain-Floatkontrollen gilt vor Ausfuehrung:

```text
absolute_tolerance = 1e-12
relative_tolerance = 0
```

Bitgenau geforderte Digestidentitaeten bleiben davon unberuehrt.

Ein technischer aktiver Unterschied wird nur berichtet, wenn:

```text
active_s_linf > max(refinement_s_linf, 1e-12)
oder
active_h_linf > max(refinement_h_linf, 1e-12)
```

Diese Grenze ist vor dem Lauf fixiert und darf danach nicht angepasst werden.

## Ergebnisentscheidung ausserhalb des Containers

Nach erfolgreichem Lauf wird separat anhand der S1-BV-Regeln entschieden:

```text
E2_TECHNICAL_CAUSAL_EFFECT
NO_E2_EFFECT_IN_FIRST_CORRIDOR
INVALID_RUN
```

Diese Entscheidung ist Auswertungssprache, kein Zustand der E1-Mechanik.

## Aussagegrenze

Auch `E2_TECHNICAL_CAUSAL_EFFECT` bedeutet nur, dass eine kontrolliert
geschichtserzeugte E1-Konfiguration eine spaetere identische Feldprobe kausal
veraendert. Die erwartete Gleichheit mit festen Gainfeldern bleibt bestehen.
Memory, Rekonstruktion, Vergessen und neue MCM-Natur sind damit nicht
nachgewiesen.

## Bester naechster Schritt

S1-BZ hat diese Komposition implementiert und genau einmal ausgefuehrt. Der
gueltige begrenzte Befund lautet `E2_TECHNICAL_CAUSAL_EFFECT`. S1-CA bindet
als naechsten Schritt Nullkontaktfreigabe und konkurrierende
Ressourcenwiederverwendung statisch vor jeder E3-Ausfuehrung.
