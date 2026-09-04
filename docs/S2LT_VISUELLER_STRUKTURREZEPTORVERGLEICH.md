# S2-LT visueller Struktur-Rezeptorvergleich

## Umfang

S2-LT vergleicht die bestehende visuelle Blockmittelung mit zwei privaten
read-only Alternativen. Es wurden keine Produktionsrezeptoren, Schwellen,
Memory-, Kontext- oder Feldfunktionen geaendert.

Der Korpus wurde vor jeder Rezeptoranalyse versiegelt:

- zwei Formfamilien aus je zwei gleich grossen hellen Quadraten;
- horizontale gegen vertikale Anordnung;
- je vier Trainings- und zwei zurueckgehaltene Positionsvarianten;
- exakt gleiche RGB-Histogramme und Helligkeitssummen fuer alle zwoelf Frames;
- zwoelf eindeutige RGB8-Payloaddigests.

Plan-Digest:
`c72853f8bcf08441f438acb885129f1a5beb1d15dd487ba78ddac216ccb24176`

## Repräsentationen

1. `BLOCK_MEAN_12X8_RGB`: bestehender unveraenderter 288-Werte-Rezeptor;
2. `SUBBLOCK_MEAN_24X24_RGB`: private 1728-Werte-Teilblockmittel;
3. `LOCAL_GRADIENT_12X8_RGB_XY`: private 576-Werte-X/Y-Gradienten.

Die vorab gebundenen Kriterien waren:

- kleinste Cross-Family-Trainingsdistanz groesser als die groesste
  Within-Family-Trainingsdistanz;
- alle vier Holdouts liegen naeher am eigenen Trainingszentroid;
- kein Ergebnis beeinflusst Quellenauswahl oder Korpuszugehoerigkeit.

## Ergebnis

| Repräsentation | Dimension | Max. innerhalb | Min. zwischen | Marge | Holdouts |
|---|---:|---:|---:|---:|---:|
| Blockmittel `12x8` | 288 | `0.017257806826` | `0.027774872912` | `0.010517066086` | `4/4` |
| Teilblockmittel `24x24` | 1728 | `0.019247639797` | `0.028334059550` | `0.009086419753` | `4/4` |
| lokale X/Y-Gradienten | 576 | `0.000219415794` | `0.000389361376` | `0.000169945582` | `4/4` |

Alle drei Repräsentationen erfuellen beide Kriterien. Die Cross/Within-Relation
betraegt ungefaehr `1.61` fuer die bestehende Blockmittelung, `1.47` fuer die
feineren Teilblockmittel und `1.77` fuer die Gradienten. Diese Relationen sind
eine nachgelagerte dimensionslose Beschreibung, keine neue Schwelle.

Die bestehende Blockmittelung trennt die klaren geometrischen Anordnungen auf
diesem Korpus bereits stabil und erreicht die groesste absolute Marge. Die
Gradienten verbessern die relative Trennung, liefern hier aber keinen
funktionalen Vorteil bei der Holdout-Zuordnung. Die feineren Teilblockmittel
sind ebenfalls korrekt, jedoch weder absolut noch relativ besser als die
bestehende Baseline.

## Einordnung

S2-LT widerlegt die pauschale Aussage, dass Blockmittel erkennbare geometrische
Struktur grundsaetzlich nicht tragen. Der S2-LS-Verlust bleibt zugleich gueltig:
hochfrequente Zufallstexturen mit nahezu identischen lokalen Mittelwerten werden
vom bestehenden Rezeptor stark komprimiert.

Auf diesem kleinen Korpus ist keine Produktionsintegration einer Alternative
begruendet. Vor einer erneuten Memoryanbindung muesste eine neue, unabhaengig
versiegelte Formensammlung mehr Kantenlagen, Groessen, Kontraste und
Anordnungen abdecken. Rezeptorvarianten duerfen dabei weiterhin weder Quellen
auswaehlen noch Schwellen nach dem Ergebnis anpassen.

## Technische Bindungen

- Qualifikation: `8/8`, Exit-Code `0`, `OK`;
- Vergleichsstatus: `S2LT_VISUAL_STRUCTURE_COMPARISON_EVALUATED`;
- Verifikation: `RECORDING_COMPLETE`;
- Vergleichsdigest:
  `ad4b8e6748b5eb226f4f4a9d03f9f08ce6961cabcde362bad14efc9b438d9771`;
- Ergebnisdatei SHA-256:
  `0e4e546f593fe62cfa2a0c8eaae2a1ceafb04eee076d60f2f182c9d9d5659fca`;
- Aufrufe: visueller Baseline-Rezeptor `12`, Memory `0`, Kontext `0`, Feld `0`;
- Rohpayloads im Ergebnis: `0`;
- Produktionsintegration: `False`.
