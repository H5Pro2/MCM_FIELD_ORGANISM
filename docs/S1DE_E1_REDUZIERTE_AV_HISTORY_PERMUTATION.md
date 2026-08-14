# S1-DE: Reduzierte AV-History-Permutation

## Status

S1-DE ist implementiert und technisch abgenommen. Die Stufe erzeugt nur eine
kontrollierte reduzierte AB-Rezeptorquelle und deren BA-Permutation. Sie fuehrt
weder E1 noch ein MCM-Feld oder eine Probe aus.

## Implementierung

- `mcm_field_organism/e1_av_history_permutation.py`
- `tests/test_e1_av_history_permutation.py`

Die kanonische Quelle verwendet zwei je eine Sekunde lange AV-Phasen aus der
bestehenden kontrollierten Reentry-Welt:

```text
A = erster Kontakt der unveraenderten Welt
B = dritter Kontakt der veraenderten Welt
```

Vor A liegt eine fuer beide Arme identische neutrale Aufwaermphase. Sie ist
nur fuer die vollstaendige Initialisierung des bestehenden fensterbasierten
Audiorezeptors erforderlich. Ihre reduzierten Frames werden verworfen; A und
B beginnen danach auf Organismuszeit null. Die Aufwaermphase gelangt weder in
die AB-/BA-Historie noch in E1 oder ein Feld.

AB wird genau einmal auf Rezeptorebene reduziert. BA entsteht danach, indem
die vollstaendigen reduzierten B- und A-Framebloecke auf die unveraenderten
Organismus-Zeitslots gesetzt werden. Es werden dieselben Frameobjekte
wiederverwendet; Payload, Carrier und Source-Supports werden nicht neu
berechnet.

## Gebundene Identitaeten

| Modalitaet | Frames | A | B | absolute Masse | quadratische Energie |
|---|---:|---:|---:|---:|---:|
| auditory | 200 | 100 | 100 | 63.13146521424816 | 14.616248432339066 |
| visual | 20 | 10 | 10 | 136.97058823529412 | 31.471202181853133 |

Fuer jede Modalitaet sind zwischen AB und BA exakt identisch:

- Payload-Multiset einschliesslich Carrier und Werte;
- Source-Support-Multiset;
- Organismus-Zeitslot-Multiset;
- Framezahl und Blockgroesse;
- absolute Eingangsmasse und quadratische Energie.

Die geordnete Folge ist dagegen verschieden. Die gebundenen Digests lauten:

```text
AB          a48d3d1620afa82d12dda855bb2ec03de3a57e7a69488d46edba6ec99cbef6d6
BA          bb1d887f1ff5809964ae8175c7fa661430e8fbc8502f0522a7003d6c6fc3c011
Permutation ad509ef23a9394009baddc8185edc5a13f76882ee79e7c31d3b0ec111bfbcc78
```

Ungueltige Modalitaetsreihenfolge, fremde Uhr, ungueltiger Trennzeitpunkt,
ueberlappende Bloecke oder ungleiche Blockgroessen brechen hart ab.

## Abnahme

Der fokussierte Testlauf besteht mit:

```text
7 tests
OK
```

Der relevante AV-/E1-Verbund besteht mit:

```text
107 tests
OK
```

Der begrenzte Befund lautet:

```text
REDUCED_AV_AB_BA_SOURCE_READY
```

## Aussagegrenze

S1-DE zeigt ausschliesslich eine faire, reproduzierbare Quellenpermutation.
Es wurde keine E1-Historie gebildet und keine Feld- oder Probeantwort
verglichen. Die Stufe belegt weder Einpraegung noch Vergessen,
Rekonstruktion, MCM-Memory, inneren Kontext, Semantik, Organisation,
Topologie, Selbstregulation oder KI.

## Bester naechster Schritt

S1-DF bindet vor jeder Ausfuehrung statisch den privaten A0-History-Produzenten:
AB und BA werden auf frischen, geometrie- und zustandsidentischen Feldern mit
ablatierter E1-Rueckwirkung verarbeitet. Festzulegen sind Eingangsbindung,
Frischeidentitaeten, erlaubte Ergebnisrollen, Abbruchbedingungen und die
vollstaendige Trennung von der spaeteren eingefrorenen Probe. S1-DF erzeugt
noch keine E1-Historie und startet keinen Forschungsrunner.

S1-DF ist inzwischen statisch gebunden. Siehe
`S1DF_E1_A0_AV_HISTORY_PRODUKTIONSVERTRAG.md`.
