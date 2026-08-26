# S1-HY: DTS-1 Verfeinerungs- und Kausalitaetsaudit

## Status

S1-HY implementiert das in S1-HX vorregistrierte private Auditharness und
fuehrt den deterministischen Doppelaudit genau einmal aus. Beide
Gesamtausfuehrungen liefern denselben Receipt. Es wurden exakt `140`
technische Feldschritte und `0` Forschungsfeldschritte ausgefuehrt.

Entscheidung:

```text
PASS_DTS1_SYNTHETIC_REFINEMENT_AND_CAUSALITY
```

## Unveraenderter Umfang

- Quelle: S1-HX-Digest
  `168ab2c291fa6e0dca658e3b308c8c1879a988a652d60d19c29a98fefad2938e`
- Partitionsstufen: `2,4,8`
- gemeinsames physisches Intervall: `2` synthetische Zeiteinheiten
- Leserlatzenzen: `1.0,0.5,0.25`
- Fixture, Raten und Akzeptanzregeln wurden nach der Ausfuehrung nicht
  veraendert.
- Das Modul ist privat und nicht an Runtime, `current_api` oder
  Forschungslaeufe angebunden.

## C01: P0/A0-Exaktheitskontrolle

`P0_A0_every_substep_bit_exact=true`. Alle Ressourcenbilanzen sind gueltig.
Die kanonischen Endvektoren `(S,H,b_norm,u_norm)` lauten:

```text
p2 = (0.49681034371806093, 0.17545813294831816, 0.278862711773346,
      0.40376883430563587, 0.1375782207690846, 0.28838878013783226,
      0.08403232515577444, 0.1235674469648571,
      0.08345333385120854, 0.15210296852933752)
p4 = (0.49681034371806093, 0.17545813294831816, 0.27886271177334604,
      0.4037688343056357, 0.13757822076908446, 0.28838878013783215,
      0.07094222840664638, 0.11910078417329002,
      0.0786082401032485, 0.14757333846737933)
p8 = (0.4968103437180606, 0.1754581329483179, 0.2788627117733458,
      0.40376883430563537, 0.1375782207690842, 0.28838878013783187,
      0.06592016719711384, 0.11742861359286368,
      0.07540533181729722, 0.14525890071088776)
```

Technische Feldschritte: `28`.

## C02: Nullbindungs-Kausallatenz

Die Flags `first_field_exact`, `first_resource_exact`,
`positive_new_binding`, `later_field_separation_above_floor` und
`latency_bounds_halve` sind alle wahr. Die finalen A1/A0-Feldtrennungen sind:

```text
p2 = 0.006262946127444546
p4 = 0.002782247502185864
p8 = 0.001803916584304649
```

Die kanonischen A1-Endvektoren lauten:

```text
p2 = (0.4905473975906164, 0.1811442301587554, 0.27943956069035425,
      0.39954875878104534, 0.14178060141456278, 0.28840647501694505,
      0.0528182181974135, 0.024938406691593213,
      0.017303025007495598, 0.00769023333666471)
p4 = (0.49402809621587507, 0.17819862722224805, 0.27890446500160265,
      0.4016873742022977, 0.1399889622823248, 0.2880594987279306,
      0.028579317909582392, 0.016631413239723423,
      0.01222810730795541, 0.006913164771814862)
p8 = (0.4951948432843581, 0.17726204953262256, 0.2786742956227455,
      0.40272502250816317, 0.1391568935210197, 0.2878539191833704,
      0.019320990428852818, 0.013540166373636945,
      0.008124304388102611, 0.0061899307154302165)
```

Alle Ressourcenbilanzen sind gueltig. Technische Feldschritte: `28`.

## C03: Aktive Paarverfeinerung

`all_active_pair_states_valid=true`. Die kanonischen Endvektoren lauten:

```text
p2 = (0.4892760650218576, 0.18751171825258522, 0.27434340516528366,
      0.4010989131909815, 0.14973768522903644, 0.2788992367925358,
      0.08387071879212896, 0.12305185765431532,
      0.08345333385120854, 0.15210296852933752)
p4 = (0.49172635260737596, 0.18496357960908705, 0.274441256223263,
      0.4024499222642352, 0.1480549076497151, 0.2792310052986028,
      0.07067412650658743, 0.11827195784584266,
      0.07859580626868068, 0.14738119461461766)
p8 = (0.49255445322905633, 0.1840924120017728, 0.2744843232088967,
      0.4030397486925377, 0.14731147510330317, 0.27938461141671245,
      0.06561479307238033, 0.11652510426659743,
      0.07536880997654202, 0.14496235164548318)
```

Die vorregistrierte Entscheidung ist eindeutig:

```text
R_n_2n  = 0.013196592285541528
R_2n_4n = 0.0050593334342071
floor   = 1.1368683772161603e-13
```

Damit gilt `R_n_2n > floor` und `R_2n_4n < R_n_2n`. Das ist ein endlicher
Verfeinerungsbefund ueber drei Stufen, keine Behauptung einer asymptotischen
Konvergenzordnung. Technische Feldschritte: `14`.

## Reproduzierbarkeit

```text
erster Receipt  = 7e0cb59afe7bbd88d66b5eba48b5bdefb07de858f88a5b35a74b78001732de05
zweiter Receipt = 7e0cb59afe7bbd88d66b5eba48b5bdefb07de858f88a5b35a74b78001732de05
Audit-Receipt   = c6f75a0a1009c51dd03ad546ae04c4aded34ecf7ccd0b687bcbac4d715f24de2
```

Die 161 Tests des dynamischen Substratpfads bestehen, darunter sieben neue
S1-HY-Strukturtests. Diese Tests fuehren den Audit-Einstieg nicht erneut aus.

## Aussagegrenze

PASS bestaetigt nur fuer das feste synthetische Fixture:

- bitgenaue Neutraldelegation;
- die vorregistrierte Ein-Subschritt-Kausalitaet;
- gueltige Ressourcenbilanzen;
- einen sinkenden vollstaendigen Paarrest unter `2/4/8`-Verfeinerung;
- deterministische Wiederholung.

Nicht nachgewiesen sind Funktion, Abschwaechung, Interferenz,
Kapazitaetsfreigabe, Wiederbeanspruchung, Materialeignung oder eine
Projektfaehigkeit. Insbesondere entstehen keine Memory- oder KI-Claims.

## Bester naechster Schritt

S1-HZ darf ausschliesslich einen statischen Interventionsvertrag fuer die
kleinste eigene DTS-1-Gegenprognose binden: identisches `S`, `H`, leitend
gebundenes Budget und identische Gesamtressource, aber unterschiedliche
Aufteilung frei/refraktaer, muessen eine unterschiedliche naechste
Bindungskapazitaet vorhersagen. Vor jeder Ausfuehrung sind Paarbildung,
Messzeitpunkt, Nullkontrolle, Fixed-Adapter-, zweistufige E1- und
Nachhallgegenbaseline sowie atomare STOPP-Kriterien festzulegen. Noch keine
Parameterwahl, Implementierung, Runtime oder Ausfuehrung.
