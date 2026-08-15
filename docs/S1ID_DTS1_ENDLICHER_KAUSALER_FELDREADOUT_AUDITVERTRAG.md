# S1-ID: Endlicher kausaler DTS-1 Feldreadout-Auditvertrag

## Status

S1-ID bindet das feste synthetische Fixture und den Ausfuehrungsvertrag fuer
den S1-IC-Zweischritt-Readout. Es wird noch kein Harness implementiert und
kein Feldschritt ausgefuehrt.

Entscheidung:

```text
DTS1_FINITE_CAUSAL_FIELD_READOUT_AUDIT_CONTRACT_BOUND
```

Vertragsdigest:

```text
aeadd736c2d8a1982a2b37d874494542603b67586852c78d081eca69ae187750
```

Quelle ist der S1-IC-Vertragsdigest
`98a376eee3bb141d4a058202cd8759bd34324b80ecaa19a333491148a18ca5e9`.

## Festes Fixture

```text
Geometrie:          offene Zweiknotenlinie mit einer Kante
Kapazitaeten:       (1.0, 1.0)
S0:                 (-1.0, 1.0)
H0 Hauptfall:       (-0.2, 0.2)
H0 Nullkontrolle:   (0.0, 0.0)
Rezeptorkontakt:    (0.0, 0.0), konstant
Antwortzeit:        1.0
Nachhallzeit:       0.5
Leckrate:           0.0
Subschrittdauer:    0.5
Subschritte:        2
DTS-1-Raten:        bind=0.4, turn=0.3, rec=0.2
b0 beide Arme:      0.4
F_HIGH refraktaer:  0.2, frei je Knoten 0.7
R_HIGH refraktaer:  0.8, frei je Knoten 0.3999999999999999
```

Alle Werte sind synthetische Algebrafixtures und keine Materialparameter oder
physische Zeitskala.

## Analytische Vorpruefung

Der Zweiknotenfall liegt vollstaendig im antisymmetrischen Feldmodus. Ohne
Aufruf des gekoppelten Schritts wurden vorregistriert:

```text
Subschritt 1 Beteiligung       = 1.0
Subschritt 1 Adapterrate       = 1.2 in beiden Armen
Engagement F_HIGH              = 0.2537769456908254
Engagement R_HIGH              = 0.14501539753761447
Umsatz beide Arme              = 0.05571680942997688
b1 F_HIGH                      = 0.5980601362608484
b1 R_HIGH                      = 0.48929858810763766
Feldkontrast C1                = 0.3653670481054693 in beiden Armen
H-Kontrast C1 Hauptfall        = 0.6762829682363132 in beiden Armen
H-Kontrast C1 Null-H-Kontrolle = 0.5291311917677363

Subschritt 2 Adapter F_HIGH    = 1.299030068130424
Subschritt 2 Adapter R_HIGH    = 1.2446492940538187
C2 F_HIGH                      = 0.06045337407166922
C2 R_HIGH                      = 0.06383190638930979
C2-Marge R minus F             = 0.0033785323176405632
vollstaendige S/H-Trennung     = 0.0016892661588202816
Float64-Grenze                 = 1.1368683772161603e-13
```

Die Null-H-Kontrolle hat dieselbe C2-Marge und dieselbe vollstaendige
S/H-Maximumstrennung. Damit sind Vorzeichen und Nichtnullmarge vor der
Ausfuehrung festgelegt.

## Fallmatrix

| Fall | Beschreibung | technische Feldaufrufe |
| --- | --- | ---: |
| C01 | aktives F_HIGH/R_HIGH-Paar mit Haupt-H | 4 |
| N01 | zwei wertidentische F_HIGH-Arme | 4 |
| N02 | F_HIGH/R_HIGH mit A0 in beiden Subschritten | 4 |
| N03 | F_HIGH/R_HIGH mit fuer Subschritt 2 eingefrorenem urspruenglichem b0 | 4 |
| N04 | aktives F_HIGH/R_HIGH-Paar mit H0 exakt null | 4 |

Ein Audit umfasst exakt 20 gekoppelte technische Feldaufrufe. Eine zweite
identische Gesamtausfuehrung muss denselben Receipt liefern. Der Doppelaudit
ist auf hoechstens `40` technische Feldaufrufe begrenzt. Forschungsfeldschritte
bleiben null.

N03 uebernimmt fuer Subschritt 2 den bitgenauen Feldoutput aus Subschritt 1,
setzt aber die Anatomie kontrolliert auf den urspruenglichen gueltigen Arm mit
dem gemeinsamen `b0` zurueck. Ressourcenoutputs dieses Kontrollfalls sind nur
Diagnostik. Das ist keine Runtimeoption und darf den aktiven Fall nicht
beeinflussen.

## Entscheidung

C01 muss in Subschritt 1 bitgenaue Adapter und vollstaendige S/H-Vektoren
liefern. `b1`, die Adapterraten in Subschritt 2, beide C2-Werte und die
vollstaendige S/H-Trennung muessen innerhalb der vorregistrierten Grenze bei
ihren Erwartungen liegen. Zusaetzlich gelten strikt
`b1_F>b1_R`, `r2_F>r2_R` und `C2_F<C2_R`.

N01 verlangt bitgenaue vollstaendige Paaroutputs. N02 verlangt bitgenaue
Feldvektoren im A0-Pfad. N03 verlangt bitgenaue Feldvektoren und b0-Adapter.
N04 wiederholt Richtung und Trennung bei H0 null. Alle Feldwerte und
Ressourcenbilanzen muessen gueltig bleiben.

Die fuenf S1-IC-Gegenbaselines bleiben statische Zustandsraumrecords. Nur A0
und der vorregistrierte Frozen-b0-Kontrollpfad werden als technische
Feldgegenkontrollen ausgefuehrt; kein weiteres Baselinemodell wird gestartet.

## STOPP

Jede Fixture-, Reihenfolge-, Subschritt- oder Aufrufzahldrift, fehlerhafte
Erstschrittidentitaet, falsche b1-/Adapter-/Kontrastrichtung, unzureichende
Trennung, Kontrollfehler, Poststateeinfluss, dritter Erklaerungsschritt,
Bilanz- oder Feldbereichsfehler, Baselineerweiterung, Nachjustierung, Retry,
Teiloutput oder mehr als 40 Feldaufrufe ergibt atomar STOPP.

## Aussagegrenze

S1-ID hat nur Fixture und Ausfuehrungsentscheidung vorregistriert. Eine
Feldwirkung wurde noch nicht gemessen. Selbst ein spaeterer PASS waere nur
der kausale technische Feldreadout einer bekannten Ressourcenintervention im
festen synthetischen Zweiknotenfall. Abschwaechung, Interferenz, Freigabe,
Wiederbeanspruchung und Materialeignung blieben offen.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1id_causal_field_readout_audit_contract.py
tests/test_dynamic_substrate_s1id_causal_field_readout_audit_contract.py
```

Zehn Tests pruefen Quellenbindung, Fixture, unabhaengige Ressourcen-,
Eigenmodus- und Nachhallanalytik, Fallbudget, Kausalkriterien, Frozen-Kontrolle,
Baselinegrenzen, Ausfuehrungssperren und Manipulationsschutz.

## Bester naechster Schritt

S1-IE darf genau das private Auditharness implementieren und den
vorregistrierten Doppelaudit genau einmal mit hoechstens 40 technischen
Feldaufrufen ausfuehren. Keine Runtimeintegration, kein weiteres
Baselinemodell und keine Forschungsprobe. STOPP beendet den Feldreadoutpfad;
PASS belegt noch keine Abschwaechungs- oder Interferenzfunktion.
