# S2-C8: c1.a-Identitaetskontrolle D_pair(1)

Stand: 2026-08-07

Status: `S2C8_C1_IDENTITY_CONTROL_D_PAIR_1_BOUND`

Forschungsentscheidung: nein

Vollmatrix: gesperrt

Forschungslauf: nein

## Zweck

S2-C8 bindet `c1.a` als kanonische Identitaetskontrolle zu `r1.a`. Bei n=1
besitzen beide Welten dieselbe physikalische und zeitliche Struktur:

```text
neutral 3.8 s
-> Kontakt A 0.4 s
-> neutral 3.8 s
```

Die Welt- und Sequenzidentitaeten bleiben getrennt. Werte, Zeitabschluesse,
B0/B2-Fortschreibung, S/H-Abgleich, Probe P und Beobachtungssupport muessen
jedoch identisch sein.

## Getrennter C1-Plan

`S2PreparedC1Plan` und `prepare_s2c8_c1_receptor_plan` akzeptieren
ausschliesslich `c1.a`. Der Plan bindet:

- den eigenen kanonischen C1-Weltdigest;
- eigene auditive und visuelle Sequenzdigests;
- drei lueckenlose Phasenschritte von 0.0 bis 8.0 s;
- denselben Organismustakt und dieselbe Rezeptoranatomie wie r1.a;
- die vollstaendige Zuordnung aller Quellenstuetzpunkte.

Der C1-Weltdigest unterscheidet sich absichtlich vom R1-Weltdigest. Eine
Identitaetskontrolle darf getrennte Versuchsadressen nicht zusammenlegen.

## C1-Bildung und Probe

`advance_s2c8_c1_world` fuehrt nur C1 durch B0 oder B2. B2 verwendet
unveraendert `rho=8` und regulaer `g=0.25/s`; der technische Nullarm `g=0`
bleibt zulaessig.

`observe_s2c8_c1_probe` setzt S/H extern mit derselben Funktion wie C4 bis C7
auf null und beobachtet dieselbe Probe P an denselben 31 echten
Rezeptorabschluessen. Das Ergebnis ist eine fluechtige `S2ProbeTrace` mit der
eigenen Weltkennung `c1.a`.

## D_pair(1)

`measure_s2c8_c1_identity` berechnet direkt zwischen den synchronen R1- und
C1-Spuren:

```text
D_S_pair(1) = max_t ||S_R1(t) - S_C1(t)||_inf
D_H_pair(1) = max_t ||H_R1(t) - H_C1(t)||_inf
D_pair(1)   = max(D_S_pair(1), D_H_pair(1))
```

Das Ergebnis `S2C1IdentityControl` enthaelt ausschliesslich die zugehoerigen
Formation- und Probe-Digests, Modellkennung, Supportzahl und die skalare
`d_pair`-Metrik. Der Vertrag akzeptiert nur:

```text
D_pair(1) = 0.0 exakt
```

Eine Abweichung wird als technischer Identitaetsfehler verworfen.

## Technische Pruefung

`tests/test_s2c8_c1_identity_control.py` bindet:

1. getrennte Identitaeten bei identischen Werten und Zeitabschluessen;
2. exakte C1-B0-Gleichheit zum bestehenden kontrollierten Phasenpfad;
3. B2-Nullpfadgleichheit und aktive B2-Reproduktion;
4. `D_pair(1)=0` exakt fuer B0 und B2;
5. wertidentische R1/C1-Spuren auf allen 31 Probe-Ticks;
6. Abweisung unterschiedlich modellierter Identitaetspaare.

```text
neue S2-C8-Suite:                  6 passed
gesamter relevanter Testverbund:  117 passed, 13 subtests passed
Python-Kompilation:               bestanden
```

Die bekannte Pytest-Cachewarnung hat keinen Einfluss auf die Ergebnisse.

## Aussagegrenze

S2-C8 ist ausschliesslich eine technische Identitaetskontrolle. Der Nullwert
ist durch die kanonisch identischen n=1-Weltwerte gefordert und kein Befund
ueber Praegung, Memory oder Feldzeit.

Noch wurde keine unterschiedliche R/C-Zeitstruktur untersucht. Ebenso fehlen
weitere Modellbaselines, Interventionen, Toleranzbindung und Entscheidung.

## Entscheidung

```text
c1.a-Plan:                        gebunden
c1.a B0/B2:                      gebunden
R1/C1-Wert- und Zeitidentitaet:   bestanden
gemeinsamer Probe-Support:        bestanden
D_pair(1):                        0.0 exakt
n=2-Kontrast:                     nein
Entscheidungslogik:               nein
Vollmatrix:                       gesperrt
Forschungslauf:                   nein
```

## Bester naechster Schritt

S2-C9 bis S2-C16 schliessen die A/B-Referenz durch denselben B0/B2-, S/H-,
Probe- und Observerpfad bis zur kanonischen End-to-End-Komposition. Der
S2-Zwischenentscheid verweist als naechsten Schritt auf den statischen
S1-C-Kandidatenvertrag. Noch keine Entscheidung, Vollmatrix, Persistenz oder
Laufnummer.
