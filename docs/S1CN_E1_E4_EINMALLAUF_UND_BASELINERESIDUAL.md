# S1-CN: E1 E4 Einmallauf und Baselineresidual

## Status

Der in S1-CM registrierte E4-Gesamtlauf wurde nach bestandener Vorpruefung
genau einmal ausgefuehrt und atomar gespeichert. Der Versuch endete
vollstaendig; es existiert kein verbliebener Versuchsnachweis und keine
Sperrdatei. Eine Wiederholung ist durch die vorhandene Ergebnisdatei
gesperrt.

## Technische Entscheidung

```text
E4_RESIDUAL_AFTER_REGISTERED_BASELINES
```

Alle neun Modelllaeufe waren kontrollgueltig. Alle sechs entscheidenden
Baselines B1 bis B6 waren technisch kompatibel. Die S1-CD-
Kontinuitaetsanker bestanden, B0 war exakt null und ORACLE-G reproduzierte
E1 innerhalb der absoluten Kontrolltoleranz.

Keine registrierte enge Baseline erreichte die vorab gebundene relative
Profilgrenze `0.05`.

## Profilresiduen

```text
Baseline  relativ L-inf   absolut L-inf   Release L-inf   Konkurrenz L-inf
B1        0.9774918513    0.0058266138    0.0051301279    0.0058266138
B2        3.6481944922    0.0217460844    0.0217460844    0.0209059659
B3       10.5002607089    0.0625897430    0.0625897430    0.0487757539
B4        7.5435864623    0.0449656586    0.0285117545    0.0449656586
B5        6.5257580343    0.0388986074    0.0251225714    0.0388986074
B6        3.5418140821    0.0211119742    0.0146982659    0.0211119742
```

B1 ist mit `0.9774918513` die naechste registrierte Baseline, liegt aber
weiterhin weit oberhalb der Erklaerungsgrenze. Der Befund ist daher kein
numerischer Grenzfall.

## Numerik und Bilanz

Der groesste relative n=2/n=4-Verfeinerungsrest aller Modelle betraegt
`5.510657447103238e-05` bei B6 und bleibt unter der Grenze `0.01`. Der
groesste Massen- oder Budgetfehler betraegt `1.0624834345662748e-13` bei B4.
Alle modellbezogenen Invarianten, Ablationen, festen Reader und
Beobachtungszeitplaene bestanden.

## Ergebnisartefakt

```text
reports/e1_e4_s1cn_once_v1.json
Bericht SHA-256: 692be2cca1759e818ecee0ec683756060267b7b1efd21b955ab526f4a38e2327
Ergebnis SHA-256: 11793db814a696d621f9aaf8423efaae53d7ac874881aa6260bb729eedd22bf4
Vertrag SHA-256:  f4b225564f3d085ac61a99453b2415b14b294a67d3b92b3609ca2887269f6cf1
```

## Technische Abnahme

Vor dem realen Start bestanden 12 fokussierte Einmallauf- und
Vertragstests sowie 77 relevante Verbundtests. Die abgeschlossenen
S1-BZ- und S1-CD-Einmallaufsuiten wurden nicht wiederholt.

## Aussagegrenze

E4 zeigt ausschliesslich: Die registrierten statischen, linearen, leaky,
S2-, F3- und CONST-V-Baselines reproduzieren den vollstaendigen technischen
E1-Verlauf in diesem Korridor nicht innerhalb der festgelegten Grenze.

Das ist kein Nachweis fuer Memory, Lernen, Rekonstruktion, Bedeutung,
Organisation, Selbstregulation oder KI. Insbesondere wurde noch nicht
geprueft, ob ein Teilhinweis einen zuvor durch wiederholten Weltkontakt
veraenderten Zustand spezifisch reaktiviert.

## Bester naechster Schritt

S1-CO registriert vor jeder weiteren Ausfuehrung einen statischen
Teilhinweis-Rekonstruktionsvertrag. Er muss E1 gegen mindestens P0, B1 und
eine nichtpassende Geschichte vergleichen, die Hinweise wert- und
energiekontrollieren und eine Gegenprognose festlegen. Erst danach darf ein
getrennter Lauf pruefen, ob der E1-Zustand mehr als unspezifischen Nachhall
oder allgemeinen Gain zeigt.
