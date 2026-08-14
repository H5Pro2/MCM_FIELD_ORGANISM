# S1-EC96: Autorisierter r4/r8-Einmallauf und atomarer Rohbefund

## Ausfuehrungsgrenze

Die ausdrueckliche Besitzerfreigabe wurde als In-Memory-Exactly-once-Token
gebunden. Unmittelbar vor dem ersten Adapteraufruf bestand die erneute
Ressourcenpruefung:

- freier physischer Arbeitsspeicher: 5.223.333.888 Bytes;
- freier Datentraeger: 234.722.398.208 Bytes;
- Ressourcen-Digest:
  `d05a1cae21a479ec7a7100f675daacb4d6d1e259204d8fd0201f58892b6e3923`.

Der Token wurde danach genau einmal verbraucht. Der gemeinsame r4/r8-Lauf
endete erfolgreich nach exakt 19.248 Feldschritten. Es gab keinen Retry,
keine Nachparametrierung und keine Zwischenpersistenz.

Atomarer Ergebnis-Digest:
`bc3c4dce150a4a1d363906728c99a37441183671caafb423247b34f4f063a6c7`.

## Messung

### r4

Ergebnis-Digest:
`06c1a81cca6dbf639a809cab2f91560467c0b76adcf6abde9944bfc292ff8857`.

| Kontrast | Aktivierung | Nachhall |
|---|---:|---:|
| P0 Reset Reihenfolge | 0 | 0 |
| E1 aktive Reihenfolge | 1,3059210545174338e-06 | 7,880146558336687e-07 |
| E1 Probe-Rueckwirkung ablatiert, Reihenfolge | 0 | 0 |
| E1 Bildung ablatiert, Reihenfolge | 0 | 0 |
| AB aktiv gegen Probe-Rueckwirkung ablatiert | 1,5595721751193725e-05 | 9,397665304750058e-06 |
| BA aktiv gegen Probe-Rueckwirkung ablatiert | 1,690164280571116e-05 | 1,0185679960583727e-05 |

### r8

Ergebnis-Digest:
`0a9f4e356c991945f389b3efb6845442b9c9fc1452904ddf479fd5cf1bf053cd`.

| Kontrast | Aktivierung | Nachhall |
|---|---:|---:|
| P0 Reset Reihenfolge | 0 | 0 |
| E1 aktive Reihenfolge | 1,1897795942905631e-06 | 7,193309551900562e-07 |
| E1 Probe-Rueckwirkung ablatiert, Reihenfolge | 0 | 0 |
| E1 Bildung ablatiert, Reihenfolge | 0 | 0 |
| AB aktiv gegen Probe-Rueckwirkung ablatiert | 1,0563465350499346e-05 | 6,368259147182531e-06 |
| BA aktiv gegen Probe-Rueckwirkung ablatiert | 1,1753244944789909e-05 | 7,087590102372587e-06 |

## Technische Interpretation

Die drei vorregistrierten Nullkontrollen sind in beiden neuen
Verfeinerungen exakt null. Der aktive AB/BA-Reihenfolgekontrast bleibt bei
`r4` und `r8` deutlich oberhalb der absoluten Toleranz von `1e-12`.
Auch die beiden aktiven Gegen-Rueckwirkungsablationskontraste bleiben in
beiden Verfeinerungen positiv.

Damit liegt der zuvor fehlende reale r4/r8-Ergaenzungsrohbefund fuer die
EC46-Konvergenz- und Kontrollauswertung vor. Die Werte nehmen von r4 zu r8
ab, verschwinden aber nicht. Ob Grob-/Feinabstand und r8-Zielwerte den
vorregistrierten EC46-Vertrag insgesamt erfuellen, ist noch separat und
rein statisch zu berechnen.

## Nichtnachweis und offene Annahmen

S1-EC96 trifft keine EC46- oder Forschungsentscheidung. Der Befund zeigt
kontrollierte zustandsabhaengige spaetere Feldantworten im E1-Pfad, beweist
aber kein MCM-Memory, keine Feldzeit, Organisation, Topologie, Semantik,
Selbstregulation oder KI. Insbesondere sind Rekonstruktion,
Vergessensverlauf, Kapazitaetswiederverwendung und laengerfristige
Weltkontaktentwicklung damit nicht nachgewiesen.

Die Autorisierung ist verbraucht. Jede Wiederholung oder weitere reale
Ausfuehrung erfordert einen neuen Vertrag und eine neue ausdrueckliche
Besitzerfreigabe.

Am besten geht es mit S1-EC97 weiter: r2, r4 und r8 statisch in den bereits
vorregistrierten EC46-Vertrag einsetzen, Grob-/Feinabstaende und maximale
Nullkontrollen berechnen und erst danach eine begrenzte technische
Entscheidung treffen. Keine weitere Feldberechnung.
