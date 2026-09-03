# S2-LA - Statischer Erreichbarkeitsaudit fuer auditive Memorygeschichten

## Status und Aussagegrenze

`S2LA_STATIC_AUDITORY_MEMORY_REACHABILITY_PARTIAL_ONLY`

S2-LA prueft ausschliesslich, welche der acht in S2-KY geometrisch
materialisierten Beziehungsklassen durch die unveraenderten B4-, TSPM-Fast-
und auditory-PPB-1-Uebergaenge tatsaechlich erreichbar sind.

Der Audit verwendet keine Memoryausfuehrung, keine neue PCM-Suche, keine
Schwellenanpassung und keine Rezeptor-, Slotscan-, Kontext- oder Feldfunktion.
Er leitet die Zustaende aus den eingefrorenen S2-KY-Messwerten und dem
vorliegenden Quellcode ab. S2-KZ bleibt als neutrale Funktionsqualifikation
gueltig; sie ist kein Nachweis der realen Erreichbarkeit ihrer synthetischen
Slotinventare.

Der reale Acht-Faelle-Hauptlauf bleibt gesperrt. Mit der vorhandenen
S2-KY-Geometrie sind nur `UNIQUE_A`, `A_BANK_AMBIGUITY` und `NO_CONTEXT`
natuerlich erreichbar. Die zentralen realen Faelle `UNIQUE_B`,
`PUBLIC_AMBIGUITY` und `NO_APPLICABLE_CONTEXT` sind nicht isolierbar.

## Gebundener Ausgangsstand

Technischer Ausgangsstand ist Commit
`edbaff3ae99202e1338b6bb575e84aa51a45ee90`.

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| S2-KX-Vertrag | `docs/S2KX_AUDITIVER_TEILHINWEISABRUF_336_VERTRAG.md` | `a7652d029e938fc09038285f63c1107603ced906638a60369dcb67ae9b33d2c0` |
| S2-KY-Plan | `docs/S2KY_AUDITORY_PARTIAL_CUE_GEOMETRY_PLAN.json` | `99a71c96fe00620a6f1ebe27fbe5bd88cd8b79e46311a9b80425e52becfd8755` |
| S2-KY-Materialisierung | `reports/s2kx/s2ky-auditory-partial-cue-geometry-20260903-01/materialization.json` | `87ac9aed39e6f3cd63f4d3cee24873a7e67357ce5cd9e5ed1ccc353d407d1dc3` |
| S2-KZ-Slotscan | `tools/_s2kz_private_auditory_partial_cue_retrieval_336.py` | `58bb0f7e9265278ced70d38bfe2858081b2e2eb134753c3457e4e03ba01eb04b` |
| TSPM-1 | `mcm_field_organism/_tspm1_private.py` | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| PPB-1 | `mcm_field_organism/_ppb1_reference.py` | `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0` |
| Default-Live-Profil | `tools/_s2jw_default_live_profile.py` | `ad5c8f607bc375daa8a6ed70134f6ed716780658a2a5e88bddb77a980da1af6f` |
| vorhandene visuelle D1-D9-Fixtures | `tools/_s2jx_default_live_memory_fixtures.py` | `5313888d81b946c7ca87f6cf140a04d7810fdb0ecd1eaa0650e9fc1bb1854936` |

Verbindliche Mechanik:

| Bestandteil | Bindung |
| --- | ---: |
| B4-Kapazitaet | 9 FIFO-Eintraege |
| Fast-Kapazitaet | 3 Slots |
| Fast-Match | Audio `<= 0.2` UND Visual `<= 0.2` |
| Fast-Update | Faktor `0.5` |
| Fast-Konsolidierung | ab Support 2 |
| Fast-Ablauf | 8 Expositionen seit letzter Auswahl |
| auditory Slow-Kapazitaet | 8 Slots |
| auditory Slow-Match | volle 48-Werte-L1-Distanz `<= 0.02` |
| auditory Slow-Update | Faktor `0.05` |
| auditory Slow-Stabilitaet | Support 3 |
| auditory Slow-Ablauf | 256 PPB-Schritte |
| Teilhinweisscan A | beobachtete Baender `0..23`, Schwelle `0.2` |
| Teilhinweisscan B | beobachtete Baender `0..23`, Schwelle `0.02` |

PPB-1 erhaelt bei einer Fast-Konsolidierung die aktuelle reale Exposition,
nicht den gemittelten Fast-Prototyp. B4 speichert jede akzeptierte Formation
als eigenen FIFO-Eintrag, auch bei identischen Werten.

## Notation und erlaubte Druckformationen

```text
L = CUE_LOW
P = CANDIDATE_PLUS
M = CANDIDATE_MINUS
H = CANDIDATE_HIGH
```

Jede L-, P-, M- oder H-Formation traegt als visuellen Begleiter den bereits
materialisierten S2-JV-X-Rezeptorzustand. Dadurch entscheidet innerhalb
dieser Gruppe allein die auditive Distanz ueber den gemeinsamen Fast-Match;
es wird kein handgeschriebener visueller Vektor eingesetzt.

Soweit eine Geschichte Kapazitaetsdruck benoetigt, bezeichnet

```text
E_i = auditory H + visual S2-JV-D_i, i = 1..9
```

keine neue auditive Fixture. Der auditive Anteil ist stets die bereits
materialisierte S2-KY-H-Fixture. Die visuellen Anteile sind die bestehenden
S2-JV-D1-D9-Fixtures. Ihr Abstand untereinander und zum visuellen
Ausgangszustand betraegt mindestens `13/24 > 0.2`. Deshalb ist jedes `E_i`
gegen den Ziel-Fast-Slot und gegen jedes andere `E_j` ein gemeinsamer
Fast-Nichttreffer. Jedes `E_i` wird nur einmal gebildet und loest daher
keinen PPB-Schritt aus.

Diese Kombination ist nur eine statische obere Erreichbarkeitspruefung. Sie
fuehrt keine neue PCM-Geometrie ein und wird in S2-LA nicht ausgefuehrt.

## Vollstaendige Distanzgrenze der vorhandenen Audioformen

Die sechs vorhandenen S2-KY-Rezeptorrollen wurden paarweise aus den bereits
gespeicherten 48-Werte-Messungen verglichen. Es wurde kein Rezeptor erneut
aufgerufen.

| Paar | beobachtete L1 `0..23` | volle L1 `0..47` |
| --- | ---: | ---: |
| H - M | `0.03167999721135169` | `0.02063999929402905` |
| H - P | `0.03167999726488322` | `0.02064000018821595` |
| H - L | `0.03167999722647929` | `0.025439998230849664` |
| H - U_UNIT | `0.06339938590143676` | `0.041299693422612097` |
| H - V_UNIT | `2.8998836705220724e-10` | `0.015919888266807267` |
| M - P | `9.817018673792375e-11` | `0.00959999972837876` |
| M - L | `1.2327556304197705e-10` | `0.004799999442841757` |
| M - U_UNIT | `0.03171938869008508` | `0.020659694213218973` |
| M - V_UNIT | `0.031679996921363335` | `0.036559886332546136` |
| P - L | `7.036867813356767e-11` | `0.014399999088649598` |
| P - U_UNIT | `0.031719388636553554` | `0.030259693610902996` |
| P - V_UNIT | `0.03167999697489486` | `0.026959886951289813` |
| L - U_UNIT | `0.0317193886749575` | `0.01585969562254678` |
| L - V_UNIT | `0.03167999693649092` | `0.04135988546288812` |
| U_UNIT - V_UNIT | `0.06339938561144845` | `0.05721958040707891` |

Damit gilt fuer die gesamte vorhandene S2-KY-Audiofamilie:

```text
max d_observed = 0.06339938590143676 < 0.2
```

Jeder B4- oder Fast-Slot mit einer dieser Audioformen ist beim auditiven
Teilscan fuer jeden S2-KY-Cue ein A-Treffer. Visuelle Trennung kann seine
Fast-Bildung oder -Ersetzung erzwingen, kann ihn aber aus einem spaeteren
rein auditiven Scan nicht entfernen.

Zugleich gilt:

```text
d_full(P,M) = 0.00959999972837876 <= 0.02
```

`P` und `M` koennen daher keine zwei auditory-Slow-Slots bilden. Sie
aktualisieren denselben PPB-Prototyp.

## Referenztrajektorie T-P: stabiler P-Slot unter Druck

Die Trajektorie

```text
P P P P E1 E2 E3 E4 E5 E6 E7 E8 E9
```

materialisiert den staerksten Versuch, einen eindeutigen stabilen P-Slot bei
gleichzeitigem Verlust der P-Spur aus B4 und Fast zu erhalten.

| Schritt | Formation | B4-Fenster | Fast-Ereignis und Bestand | auditory Slow |
| ---: | --- | --- | --- | --- |
| 1 | P | `P` | `F0=P/s1`, `CREATED` | leer |
| 2 | P | `P P` | `F0=P/s2`, `UPDATED`, PPB 1 | `S0=P/s1`, instabil |
| 3 | P | `P P P` | `F0=P/s2`, `UPDATED`, PPB 2 | `S0=P/s2`, instabil |
| 4 | P | `P P P P` | `F0=P/s2`, `UPDATED`, PPB 3 | `S0=P/s3`, stabil |
| 5 | E1 | `P P P P E1` | `F1=E1/s1`, `CREATED` | unveraendert |
| 6 | E2 | `P P P P E1 E2` | `F2=E2/s1`, `CREATED` | unveraendert |
| 7 | E3 | `P P P P E1 E2 E3` | `F0=P` durch `E3` ersetzt | unveraendert |
| 8 | E4 | `P P P P E1 E2 E3 E4` | `F1=E1` durch `E4` ersetzt | unveraendert |
| 9 | E5 | `P P P P E1 E2 E3 E4 E5` | `F2=E2` durch `E5` ersetzt | unveraendert |
| 10 | E6 | `P P P E1 E2 E3 E4 E5 E6` | `F0=E3` durch `E6` ersetzt | unveraendert |
| 11 | E7 | `P P E1 E2 E3 E4 E5 E6 E7` | `F1=E4` durch `E7` ersetzt | unveraendert |
| 12 | E8 | `P E1 E2 E3 E4 E5 E6 E7 E8` | `F2=E5` durch `E8` ersetzt | unveraendert |
| 13 | E9 | `E1 E2 E3 E4 E5 E6 E7 E8 E9` | `F0=E6` durch `E9` ersetzt | `S0=P/s3`, stabil |

Final sind alle P-Eintraege aus B4 und Fast entfernt. Es tritt kein
Fast-Ablauf ein; die drei Fast-Slots werden in eindeutiger LRU-Reihenfolge
ersetzt. Der finale Fast-Bestand ist:

```text
F0=E9/s1, F1=E7/s1, F2=E8/s1
```

Trotz dieses mechanisch korrekten Zielverlusts findet der Cue L im
auditiven Teilscan alle neun B4- und alle drei Fast-Slots, weil jeder
`E_i` den Audioanteil H traegt und `d_observed(L,H) < 0.2` gilt. Der
stabile P-Slot ist ebenfalls ein B-Treffer. Das Resultat ist daher eine
A-interne Mehrdeutigkeit, nicht `UNIQUE_B`.

## Referenztrajektorie T-PM: P und M verdichten gemeinsam

```text
P P P P M M M M E1 E2 E3 E4 E5 E6 E7 E8 E9
```

| Schritt | Formation | Fast | auditory Slow | B4 |
| ---: | --- | --- | --- | --- |
| 1 | P | `F0=P/s1` | leer | Index 1 |
| 2 | P | `F0=P/s2`, PPB | `S0=P/s1` | Indizes 1-2 |
| 3 | P | `F0=P/s2`, PPB | `S0=P/s2` | Indizes 1-3 |
| 4 | P | `F0=P/s2`, PPB | `S0=P/s3` | Indizes 1-4 |
| 5 | M | `F0=.5P+.5M/s2`, PPB | `S0=.95P+.05M/s3` | Indizes 1-5 |
| 6 | M | `F0=.25P+.75M/s2`, PPB | `S0=.9025P+.0975M/s3` | Indizes 1-6 |
| 7 | M | `F0=.125P+.875M/s2`, PPB | `S0=.857375P+.142625M/s3` | Indizes 1-7 |
| 8 | M | `F0=.0625P+.9375M/s2`, PPB | `S0=.81450625P+.18549375M/s3` | Indizes 1-8 |
| 9 | E1 | `F1=E1/s1`, created | unveraendert | Indizes 1-9 |
| 10 | E2 | `F2=E2/s1`, created | unveraendert | Indizes 2-10 |
| 11 | E3 | `F0` ersetzt | unveraendert | Indizes 3-11 |
| 12 | E4 | `F1` ersetzt | unveraendert | Indizes 4-12 |
| 13 | E5 | `F2` ersetzt | unveraendert | Indizes 5-13 |
| 14 | E6 | `F0` ersetzt | unveraendert | Indizes 6-14 |
| 15 | E7 | `F1` ersetzt | unveraendert | Indizes 7-15 |
| 16 | E8 | `F2` ersetzt | unveraendert | Indizes 8-16 |
| 17 | E9 | `F0` ersetzt | ein stabiler Mischprototyp | `E1..E9` |

PPB-1 sieht bei den Schritten 5 bis 8 die aktuellen M-Expositionen.
Aufgrund `d_full(P,M) <= 0.02` waehlt es stets S0. Es entstehen weder ein
zweiter Slot noch Slow-Mehrdeutigkeit. Der Support bleibt nach Erreichen von
3 gekappt; der Prototyp wird mit Faktor 0.05 weiter aktualisiert.

## Diagnosealternativen fuer die internen Konfliktfaelle

### B4/Fast-Konflikt

Die kleinste Geschichte, die verschiedene B4- und Fast-Werte erzeugt, ist:

```text
P M
```

Nach Schritt 2 gilt:

```text
B4   = [P, M]
Fast = [0.5P + 0.5M] mit Support 2
Slow = [M] mit Support 1, nicht oeffentlich stabil
```

Der Cue L trifft P und M in B4. Deshalb entsteht bereits
`A_BANK_AMBIGUITY`; der verschiedene Fast-Prototyp kann nicht als isolierter
`A_INTERNAL_CONFLICT` ausgewertet werden. Druck mit E1-E9 entfernt P und M,
ersetzt sie aber durch neun beziehungsweise drei neue auditive A-Treffer.

### Zwei getrennte Slow-Slots

Mit `P P P P H H H H` koennen zwar zwei Slow-Slots entstehen, weil
`d_full(P,H) = 0.02064000018821595 > 0.02` gilt. Nach Schritt 8 sind P und H
jeweils stabil mit Support 3. Keine vorhandene Cue-Rolle trifft jedoch beide
Slots auf den beobachteten Baendern:

- L, P und M treffen P, aber H liegt rund `0.03168 > 0.02` entfernt;
- H und V_UNIT treffen H, aber P liegt rund `0.03168 > 0.02` entfernt;
- U_UNIT liegt von P und H jeweils oberhalb `0.02` entfernt.

Die in S2-KY synthetisch angesetzte Slow-Mehrdeutigkeit mit P und M ist noch
strenger ausgeschlossen: Beide Werte landen wegen ihrer vollen Distanz von
nur `0.0096` im selben Slow-Slot.

## Acht Fallentscheidungen mit finalem 9/3/8-Bestand

`-` bezeichnet einen freien Slot. Instabile Slow-Slots werden ausgewiesen,
sind aber kein oeffentlicher B-Kandidat.

| Fall | statisch gepruefte Geschichte / Cue | final B4, max. 9 | final Fast, max. 3 | final auditory Slow, max. 8 | tatsaechlicher Befund | Sollklasse erreichbar |
| --- | --- | --- | --- | --- | --- | --- |
| KY-R01 `UNIQUE_A` | `L` / L | `L` | `L/s1` | `-` | B4 und Fast liefern denselben eindeutigen A-Wert | ja |
| KY-R02 `UNIQUE_B` | T-P / L | `E1..E9` | `E9,E7,E8` | `P/s3`, 7 frei | A mehrfach, B eindeutig | nein |
| KY-R03 `PUBLIC_AMBIGUITY` | T-P danach `L` / L | `E2..E9,L` | `E9,L,E8` | `P/s3`, 7 frei | A intern mehrfach, B eindeutig | nein |
| KY-R04 `A_BANK_AMBIGUITY` | `P M` / L | `P,M` | `.5P+.5M/s2` | `M/s1` instabil | zwei B4-Treffer | ja |
| KY-R05 `A_INTERNAL_CONFLICT` | `P M E1..E9` / L | `E1..E9` | `E9,E7,E8` | `M/s1` instabil | B4 und Fast jeweils mehrfach | nein |
| KY-R06 `B_INTERNAL_AMBIGUITY` | T-PM / L | `E1..E9` | `E9,E7,E8` | ein stabiler P/M-Mischslot | nur ein B-Slot; A mehrfach | nein |
| KY-R07 `NO_CONTEXT` | frischer Nullzustand / L | `-` | `-` | `-` | beide Bereiche gueltig leer | ja |
| KY-R08 `NO_APPLICABLE_CONTEXT` | T-P / H | `E1..E9` | `E9,E7,E8` | `P/s3`, 7 frei | A mehrfach anwendbar; B unpassend | nein |

Fuer KY-R03 ersetzt die zusaetzliche L-Formation den aeltesten Fast-Slot.
Sie beseitigt die acht uebrigen B4-Treffer nicht. Fuer KY-R05 erzeugt die
zweite Formation zwar verschiedene volle B4-/Fast-Werte, aber B4 ist bereits
mehrdeutig und bleibt es nach dem Druck durch die E-Slots.

## Erreichbarkeitsentscheidung

### Natuerlich erreichbar

1. `UNIQUE_A`: eine einzelne reale Formation aus frischem Zustand.
2. `A_BANK_AMBIGUITY`: mindestens zwei passende B4-Eintraege, insbesondere
   P und M.
3. `NO_CONTEXT`: ein vollstaendig frischer Nullzustand.

### Mit der vorhandenen Geometrie nicht isolierbar

1. `UNIQUE_B`: Die neun Druckformationen entfernen den Zielinhalt aus A,
   sind wegen der breiten A-Scanschwelle aber selbst A-Treffer.
2. `PUBLIC_AMBIGUITY`: Ein stabiler B-Slot erfordert mehrere Formationen;
   die verbleibenden beziehungsweise nachrueckenden B4-/Fast-Slots erzeugen
   A-interne Mehrdeutigkeit statt genau eines A-Kandidaten.
3. `A_INTERNAL_CONFLICT`: Verschiedene B4-/Fast-Werte sind erreichbar, aber
   nicht bei je genau einem passenden internen Banktreffer.
4. `B_INTERNAL_AMBIGUITY`: P und M koaleszieren; trennbare P/H-Slots besitzen
   keinen gemeinsamen vorhandenen Cue innerhalb der Slow-Schwelle.
5. `NO_APPLICABLE_CONTEXT`: Jeder nichtleere A-Bestand aus der vorhandenen
   Audiofamilie ist fuer jeden vorhandenen Cue unter der A-Schwelle
   anwendbar.

Diese Nichterreichbarkeit ist kein Fehler von S2-KZ und kein negativer
Memorybefund. Sie zeigt, dass eine geometrische Slotbelegung nicht mit einer
durch die reale Updatefolge erreichbaren Belegung gleichgesetzt werden darf.

## Stopp- und Falsifikationsregeln

Der geplante reale Acht-Faelle-Lauf darf auf Basis von S2-KY nicht gebaut
oder ausgefuehrt werden. Insbesondere sind unzulaessig:

- synthetisches Einsetzen der S2-KY-Inventare in einen Memoryzustand;
- neue PCM-Suche oder nachtraegliche Koeffizientenanpassung in S2-LA;
- A-freie Behauptung allein aufgrund visueller Fast-Trennung;
- zwei P/M-Slow-Slots trotz `d_full(P,M) <= 0.02`;
- Umdeutung einer internen Bankmehrdeutigkeit als oeffentliche
  A/B-Mehrdeutigkeit;
- Auslassen einzelner B4-, Fast- oder Slow-Slots beim Scan.

Der statische Befund waere widerlegt, wenn eine unveraenderte Kernregel einen
anderen der hier abgeleiteten Slotuebergaenge erzwingt oder ein bereits
vorhandener, prospektiv gebundener S2-KY-Audiowert einen beobachteten Abstand
ueber `0.2` beziehungsweise die benoetigte Slow-Doppelgeometrie belegt.

## Abschluss

S2-LA entscheidet gegen einen realen Acht-Faelle-Hauptlauf mit der aktuellen
PCM-Geometrie. Die vorhandene Geometrie traegt einen eindeutigen A-Fall, eine
A-Bankmehrdeutigkeit und echte Abwesenheit, aber nicht die fuer den zentralen
Funktionsvergleich benoetigten isolierten B-, oeffentlichen A/B- und
Nichtanwendbarkeitsfaelle.

Interne B4/Fast-Konflikte und Bankmehrdeutigkeiten bleiben durch S2-KZ als
neutrale Fail-Closed-Sicherheitsfaelle qualifiziert. Sie werden nicht durch
weitere PCM-Konstruktionen erzwungen.

Ein spaeterer realer auditiver Teilhinweislauf benoetigt vorab eine neue,
separat freizugebende PCM-Geometrie mit mindestens einem prospektiv
rezeptorerzeugten Druckinhalt, dessen beobachteter Abstand zur Ziel-Cue
`> 0.2` ist. Das ist eine neue Materialisierungsfrage und nicht Bestandteil
von S2-LA.
