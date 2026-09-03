# S2-KF - Uniforme PCM-Skalierung

## Ergebnis

Die einmalige Qualifikation `s2kf-qualification-20260903-01` bestand mit
`12/12` Tests, Exit-Code `0` und `OK`. Produkt- und Vertragsquellen waren
vor und nach dem Lauf digestgleich. Hauptgate und autorisierte Lauf-ID
blieben geschlossen; es gab keine Memoryoperation.

Das reale Startgate endete mit:

```text
S2KF_AUDIO_GEOMETRY_MATERIALIZED
```

Der feste Faktor `24/25` wurde genau einmal auf die drei Zielbeitraege
angewendet. U und V wurden je genau einmal ausgewertet und genau ein
Koeffizientensatz erzeugt. Eine Suche, Normalisierung, Begrenzung oder
Nachjustierung fand nicht statt.

## Reale Messwerte

```text
max |T_PLUS|               = 0.9883150458335876
d(H_AUDIO,T_PLUS)          = 0.02064000018821595
d(H_AUDIO,T_MINUS)         = 0.02063999929402905
d(T_PLUS,T_MINUS)          = 0.00959999972837876
d(H_AUDIO,P6)              = 0.018096882417946113
d(N_AUDIO,T_PLUS)          = 0.03023999967450985
d(N_AUDIO,T_MINUS)         = 0.020639999975482805
d(N_AUDIO,P6)              = 0.02769688190424002
```

Alle sechs adaptiven Vorabstaende liegen innerhalb `0,02`. Alle neun
Distraktoren liegen gegen Training und adaptiven Prototyp ausserhalb
`0,02`. Die zentralen Rollen besitzen denselben visuellen
Rezeptorwertedigest.

## Grenze

Dies qualifiziert die prospektive PCM-Fixture und das reale Startgate, noch
nicht die auditive Lern- und Generalisierungshypothese. Der Hauptumfang
`17/8/157` wurde nicht ausgefuehrt und benoetigt eine separate Freigabe.
S2-KE bleibt mit seinem urspruenglichen Geometriestopp unveraendert
dokumentiert.

Der vollstaendige maschinenlesbare Beleg liegt in `qualification.json`.
