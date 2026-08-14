# K2-B/F3: Vorregistrierung Funktionsverlust und Wiederverwendung

Stand: 2026-08-06

## 1. Forschungsfrage

Kann vier Sekunden normale kontrollierte B-Weltgeschichte die isolierte
spaetere Zusatzwirkung einer vorherigen viersekundigen A-Geschichte
funktional verdraengen, und entsteht gleichzeitig im selben endlichen
M-Zustandsraum eine andere B-bedingte Wirkung?

Der Lauf charakterisiert ausschliesslich die bekannte F3-Baseline. Er ist
kein E4-Test und kein Memory-, Organisations- oder Feldzeitnachweis.

## 2. Unveraenderte Mechanik

```text
response_time_seconds:          1.0
afterimage_time_constant:       0.5
lambda_sm_per_second:           1.0
kappa:                          0.5
eta:                            1.0
dissipation:                    keine
refinement:                     4n
F3-Gleichung:                   unveraendert
lineare Feldbaseline:           analytische Form aus Lauf 192
```

## 3. Kontrollierte Quellen

Alle Quellen stammen aus den bereits vorhandenen prozeduralen
Audio-/Video-Welten. A, B und Unterbrechung dauern jeweils eine Sekunde pro
Wiederholung. A wird viermal, B beziehungsweise Unterbrechung werden danach
bis zu viermal angewendet. Die gemeinsame Probe dauert eine Sekunde.

```text
A x4 digest:
d1ca7803a6fa8ec93992933f8320252a6e0eb64ea2cab98784abadfa5e538953

B step digests:
5d38f7e13d996b1276484969c8dd05461bf1bc41cee2501c58199d4814184856
2df447f0811c2ea471b12fc7e9dc3c0b23d2c18c6c9ffecb5498ac698b0e8a8b
8f18e1eaf72fff07827ff255e1a521ecc45c4f73b012e4fa8740441bf983fea9
3dd23501e0dd604712b8df5202ff36980e430fce79682080655469771c0aeee2

interruption step digests:
209446fbd5c2652cc3aab3bfbe46739ebdd46baf27e248aca38cd6b5701a714c
de950779d3674dc1dcaa6a2513bcbbe73b07ce9e2cfad297fcbfdb63f185c092
70dcf7a43b787564312f3753ed4f07268fa8aae93bc6e9864d37f6f1ef3f2483
1337395e1a8258899110db320afad12cd662775330ea7d5536ae5ff998f93436

probe checkpoint digests 0..4:
b975e8dc428c5ec93991b050c4949dc5dbaf08c5401c756b22a8aeca34579161
1f50ee4bf57c374a85ddb2dc22238ba2fe59bc02771b2a375cffa33f5ed38574
15c65c4610ce2070ba828e40e3f3ef14243f15d405f2760f43266d5133a0f192
0ecac3d52c1a9c29088ee9c13255e2cdd836708bb46b4207124458054793bd4a
783b9e29f0b16c482af54e8616a59ffb2b8bb3f7bce5fa6d3775e2845c64de43
```

## 4. Vier kausale Hauptpfade

Nach A werden S und H einmal exakt auf Null angeglichen. Danach laufen alle
Fortsetzungen ohne weitere Eingriffe kontinuierlich. Nur fuer die passive
Probe wird an jedem Checkpoint eine Kopie des jeweiligen Zustands in S und H
angeglichen; der Hauptpfad wird dadurch nicht veraendert.

```text
AB: A x4 -> B x0..4
UB: uniformes M -> B x0..4
AG: A x4 -> interruption x0..4
UG: uniformes M -> interruption x0..4
```

`U` ist der gleichfoermige technische M-Referenzzustand. Jeder Pfad wird
sowohl mit F3 als auch mit der festen linearen gekoppelten Feldbaseline aus
Lauf 192 fortgesetzt.

## 5. Messungen

Nach Checkpoint `k = 0..4` wird dieselbe technische Probe an den jeweiligen
Zeitpunkt gebunden. Gemessen werden ueber die vollstaendige Probe-Trajektorie:

- `old_b_contrast[k]`: S/H-Linf zwischen AB und UB;
- `old_gap_contrast[k]`: S/H-Linf zwischen AG und UG;
- `new_b_contrast[k]`: S/H-Linf zwischen UB und UG;
- zugehoerige M-Linf-Werte vor der Probe;
- `old_b_retention[k]` relativ zum A-Ausgangskontrast bei `k=0`;
- `old_gap_retention[k]` relativ zum selben Ausgangskontrast;
- Abweichung der gesamten F3-Kontrastkurven von der linearen Feldbaseline;
- Beobachtungstakte, Gesamtmasse, Nichtnegativitaet und S/H-Grenzen.

## 6. Vorregistrierte Schwellen und Entscheidungen

```text
functional_loss_limit:          0.05
competitive_advantage_factor:   0.50
```

Die Entscheidung fuer den F3-Pfad lautet:

1. `COMPETITIVE_DISPLACEMENT_AND_REUSE`, wenn
   `old_b_retention[4] <= 0.05`, zugleich
   `old_b_retention[4] <= 0.5 * old_gap_retention[4]` und ein positiver
   `new_b_contrast[4]` besteht.
2. `PASSIVE_LOSS_AND_REUSE`, wenn die alte Wirkung unter B auf hoechstens
   `0.05` faellt und eine B-Wirkung besteht, aber B keinen zweifachen Vorteil
   gegen die gleich lange Unterbrechung zeigt.
3. `SUPERPOSITION_WITHOUT_FUNCTIONAL_LOSS`, wenn die alte Wirkung nach B x4
   ueber `0.05` bleibt und gleichzeitig eine B-Wirkung besteht.
4. `NO_REUSABLE_B_EFFECT`, wenn keine B-bedingte Wirkung entsteht.
5. `TECHNICALLY_UNDECIDABLE`, wenn Quelle, Takte oder Invarianten verletzt
   werden.

Ein exakt positiver Fließkommawert allein genuegt fuer die B-Wirkung nicht.
Sie muss oberhalb des maximalen n/2n/4n-Integrationsfehlers aus Lauf 188
liegen. Die dort vorab bekannte Grenze lautet
`4.2090677451738585e-09`.

## 7. Aussagegrenze

Keine Entscheidung dieses Laufs belegt organisches Vergessen, Loesung,
Rekonfiguration, Wiederpraegung, Memory, Feldzeitverdichtung, inneren Kontext,
Organisation, Topologie, Semantik oder KI. Der Lauf sagt nur, welche
Ueberschreibungs- und Wiederverwendungsfunktion die bekannte F3-Baseline unter
diesem festen Weltkorridor technisch besitzt.

## 8. Laufnummer

Der letzte ausgefuehrte Forschungsdurchlauf ist Lauf 192. Erst die einmalige
Ausfuehrung dieses unveraenderten Vertrags erzeugt Lauf 193.
