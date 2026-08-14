# S1-CO: E1 Teilhinweis-Rekonstruktionsvertrag

## Status

S1-CO registriert den ersten Teilhinweiskorridor statisch. Es wurde kein
Feld fortgeschrieben, kein Runner implementiert oder ausgefuehrt und keine
Entscheidung erzeugt.

Der Begriff Rekonstruktion bezeichnet hier nur die Forschungsfrage. Ein
spaeterer positiver Lauf darf zunaechst hoechstens als
`HISTORY_SPECIFIC_PARTIAL_CUE_EFFECT` bezeichnet werden.

```text
Vertragsdigest: a69eb30b91fb3cb69bb319b8a514be761eb4c2700e3ad720b2042dc7c63a7528
```

## Forschungsfrage

Erzeugt ein schwaecherer Teilkontakt nach einer passenden wiederholten
Geschichte und vier Sekunden Nullkontakt eine history-spezifische spaetere
S/H-Feldwirkung, die weder P0, ein einzelner statischer H8-Gain noch die
nichtpassende gespiegelte Geschichte erklaeren?

## Welt und Zeit

```text
Linke Geschichte:  8 * (1.0, 0.0, 0.0), je 1.0 s
Rechte Geschichte: 8 * (0.0, 0.0, 1.0), je 1.0 s
Danach:             4.0 s uniforme Nullkontaktentwicklung

Vollhinweise:       (1.0, 0.0, 0.0) / (0.0, 0.0, 1.0)
Teilhinweise:       (0.25, 0.0, 0.0) / (0.0, 0.0, 0.25)
Hinweisdauer:       1.0 s bei 20 Hz
```

Linker und rechter Teilhinweis besitzen exakt dieselbe Energie und sind
Spiegelbilder. Jeder Hinweis startet auf einer frischen, wertidentischen
S/H-Feldkopie. Nur der jeweilige langsame Zustand wird uebertragen. Dadurch
werden Rohbild-Replay und schneller Nachhall ausgeschlossen.

## Arme und Gegenbaselines

```text
Geschichten: left-g4, right-g4, neutral
Modelle:     E1, P0, B1-static-H8
```

Jede linke und rechte Geschichte wird sowohl mit passendem als auch mit
gekreuztem Teilhinweis geprueft. Die Vollhinweise liefern nur die gerichtete
Referenz. P0 kontrolliert direkte Hinweiswirkung. B1 verwendet denselben
statischen H8-Gain fuer alle Geschichten und kontrolliert unspezifische
Verstaerkung ohne entwickelten Historyzustand.

## Beobachtung

Beobachtet werden ausschliesslich vorzeichenbehaftete `Delta_S`- und
`Delta_H`-Vektoren gegen P0 desselben Hinweises. Rechte Resultate werden nur
fuer den Vergleich geometrisch gespiegelt; es gibt keine Labels oder
Runtime-Auswahl.

Primaer ist die gespiegelte History-Hinweis-Interaktion. Sie subtrahiert
fuer jeden Hinweis die Wirkung der nichtpassenden von der passenden
Geschichte und mittelt beide Seiten nach Spiegelung. Zusaetzlich werden
Vollkontaktinteraktion, gerichtetes Skalarprodukt, P0- und B1-Interaktion,
gekreuzter Historyrest, Spiegelungsfehler und n=2/n=4-Verfeinerung berichtet.

## Entscheidungsreihenfolge

```text
INVALID_S1_CO_RUN
NO_MEASURABLE_PARTIAL_CUE_EFFECT
PARTIAL_CUE_EXPLAINED_BY_P0_OR_STATIC_GAIN
HISTORY_SPECIFIC_PARTIAL_CUE_EFFECT
```

Ein history-spezifischer technischer Effekt ist nur zulaessig, wenn:

1. Zeitplan, Spiegelung, Invarianten und n=2/n=4 bestehen;
2. der Teilhinweiseffekt oberhalb des gemeinsamen Numerik-, P0- und B1-Bodens liegt;
3. passende und gekreuzte Geschichte messbar verschieden sind;
4. Teil- und Vollkontaktinteraktion dieselbe gerichtete Orientierung besitzen;
5. keine Entscheidung aus einer einzelnen Endkomponente abgeleitet wird.

## Aussagegrenze

Auch `HISTORY_SPECIFIC_PARTIAL_CUE_EFFECT` waere noch kein Nachweis fuer
Memory, Rekonstruktion, Bedeutung, Organisation, Selbstregulation oder KI.
Er wuerde nur zeigen, dass ein schwacher Hinweis nach passender Geschichte
eine kontrolliert unterscheidbare substratvermittelte Feldwirkung besitzt.
Fuer einen Memorybefund fehlen danach weiterhin Robustheit ueber mehrere
Hinweisstaerken sowie Funktionsverlust durch Freigabe oder Umpraegung.

## Technische Abnahme

Sieben fokussierte Vertragstests und 37 relevante Verbundtests mit den
bestehenden Spiegelgeschichten, G4-Zustandsarmen und Einmallaufgrenzen
bestehen. Kein Test hat den abgeschlossenen S1-CN-Lauf wiederholt.

## Bester naechster Schritt

S1-CP implementiert nur Weltarme, gespiegelte Teil-/Vollhinweise,
P0/B1-Kontrollen und den interpretationsfreien Ergebniscontainer. Vor einer
Ausfuehrung muessen die Interaktionsformel, der gemeinsame technische Boden
und das Fehlerverhalten durch synthetische Tests abgenommen werden.
