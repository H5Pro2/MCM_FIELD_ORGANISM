# S2-NU: einmaliger realer Verlaufvergleich

## Technischer Abschluss

Lauf-ID: `s2nu-temporal-comparison-20260909-01`.
Genau ein Hauptaufruf, anschliessend genau eine unabhaengige read-only
Verifikation und erst danach eine getrennte Auswertung. Exit-Code `0`.
**RECORDING_COMPLETE**, **S2NU_COMPARISON_VERIFIED**, **FUNCTION_EVALUATED**.
Keine Wiederholung oder nachtraegliche Aenderung.

Nur das gespeicherte, bereits verifizierte NU-Materialisat wurde verwendet.
Der Haupteinstieg pruefte vor der Vergleichsrechnung die 22/22-Qualifikation,
Quell-/Codebindungen, Versiegelung, Profile, native Fenster sowie die
Materialisierungs- und Verifikationsdigests. Qualifizierte Module unveraendert;
der neue `reports/s2nu/compare_once.py` bindet nur den autorisierten Einmalaufruf.

Sechs getrennte Fuenferfolgen; je Folge vier vorzeichenbehaftete Uebergaenge,
48 Einzelterme je Uebergang, vier step-Werte und T. Keine Uebergaenge zwischen
Verlaeufen. Alle numerischen Terme samt Originalindizes sind in
[result.json](result.json) unter `primary` und `direct` erhalten.

## Primaerbefund und Kontrollgleichheiten

Die vorab gebundene Primaerbedingung ist **CONFIRMED**:

| Bedingung fuer s02/s03 | Beobachteter Befund |
| --- | --- |
| Erster und letzter Halbvektor bitgleich | Ja, 96/96 Komponenten je Implementierung |
| Vollstaendiges Multiset bitgleich, Multiplizitaet erhalten | Ja, 240/240 Komponenten je Implementierung |
| `T(s02) < T(s03)` | `0.0018286359991568396 < 0.003657297305254732` |

Die Kontrollgleichheiten wurden anhand der tatsaechlich gespeicherten
Rezeptorhalbwerte berechnet, nicht aus den PCM-Hashentsprechungen abgeleitet.
Primaere und direkte Messbelege sind kanonisch gleich, einschliesslich
Einzeltermen, Summen, Multisetdarstellung und Kontrollbefunden.

Der Randarm erhielt ausschliesslich die beiden Randvektoren und Profilbindung.
Der ungeordnete Arm erhielt ausschliesslich Profilbindung und fuenf nach
kanonischen `<48d`-Bytes sortierte Vektoren; keine Zeit-, Quellen-, Ordinal-,
Rezept- oder Zustandsdigestfelder. Herkunftsbelege liegen ausserhalb dieser
funktionalen Eingaben. Keine Zeitinformation durch eine Nebenkennung.

## Getrennte Ordnungsbefunde

| Kriterium | Rolle | Linkes T | Rechtes T | Strikte Ordnung |
| --- | --- | --- | --- | --- |
| o01: s02 < s03 | PRIMARY | 0.0018286359991568396 | 0.003657297305254732 | LT, bestanden |
| o02: s01 < s02 | DESCRIPTIVE | 0.0 | 0.0018286359991568396 | LT, bestanden |
| o03: s01 < s04 | DESCRIPTIVE | 0.0 | 0.0021080942194405157 | LT, bestanden |
| o04: s01 < s05 | DESCRIPTIVE | 0.0 | 0.0012767674201762723 | LT, bestanden |
| o05: s01 < s06 | DESCRIPTIVE | 0.0 | 0.009108703113076402 | LT, bestanden |

Primaer: 1/1 unter beiden zusaetzlichen Kontrollgleichheiten.
Beschreibend: getrennt 4/4. Die vier Kontrollen ersetzen keine der drei
Primaerbedingungen und belegen keine Erkennung ihrer Erzeugungskategorien.

## Gespeicherte Summen

Die folgenden Zahlen sind aus den gespeicherten Belegen uebernommen,
nicht fuer den Bericht erneut berechnet. Alle Summen nutzen die gebundene
aufsteigende Python-Builtin-Reihenfolge ohne Toleranz.

| Strom | step 0 | step 1 | step 2 | step 3 |
| --- | --- | --- | --- | --- |
| s01 | 0.0 | 0.0 | 0.0 | 0.0 |
| s02 | 0.0004571044624586471 | 0.0004571503635454602 | 0.00045718029302795326 | 0.00045720088012477915 |
| s03 | 0.001371435116768057 | 0.00091433065430941 | 0.0004571503635454602 | 0.0009143811706318048 |
| s04 | 0.000490854045869418 | 0.0005471720212874861 | 0.0005398720507330771 | 0.0005301961015505344 |
| s05 | 0.0003316841828554027 | 0.00030669964563882567 | 0.00030657155568549664 | 0.0003318120359965473 |
| s06 | 0.0 | 0.004544573232344131 | 0.00456412988073227 | 0.0 |

| Strom | T | Randabstand E |
| --- | --- | --- |
| s01 | 0.0 | 0.0 |
| s02 | 0.0018286359991568396 | 0.0018286359966359121 |
| s03 | 0.003657297305254732 | 0.0018286359966359121 |
| s04 | 0.0021080942194405157 | 0.002098660484150141 |
| s05 | 0.0012767674201762723 | 0.0 |
| s06 | 0.009108703113076402 | 0.009079378645561251 |

## Arbeit und Groessen

| Arbeit | Tatsaechlich / gebundene Grenze |
| --- | --- |
| Primaere Differenzen, inklusive Randarm | 1.440 / 1.440 |
| Direkte Differenzen, inklusive Randarm | 1.440 / 1.440 |
| Primaere / direkte Kontrollkomponenten | 336 / 336 je Implementierung |
| Read-only Vorwaertshalbierungen | 1.440 / 1.440 |
| Read-only Termpruefungen | 2.880 / 2.880 |
| Read-only Summenpruefungen | 72 / 72 |
| Read-only Kontrollkomponenten | 672 / 672 |
| Nachgelagerte Ordnungskriterien | 5 / 5 |

Die Verifikationsarbeit ist zusaetzlich und separat ausgewiesen, nicht in
den 2.880 Vergleichsdifferenzen verborgen. Der Verifikator prueft gespeicherte
Roh-zu-Halb-Beziehungen mit eigener Vorwaertsmultiplikation, ruft NJ aber
nicht auf. Keine Quellenregeneration, FFT-/Rezeptorwiederholung oder weitere
Quellpaare. Keine Schwellenableitung oder Maskenwahl.

Gesamtbeleg **564.684 Byte**, unter 2.097.152 Byte.
Vorregistrierung **2.540 Byte**, unter 65.536 Byte.
Verifikationsbeleg **615 Byte**, Auswertung **1.531 Byte**, jeweils unter
262.144 Byte. Atomare Publikation mit exklusiven Einmalbelegen fuer
Verifikation und Auswertung; keine Rohpayloadablage.

## Digestbindungen

- [Vorregistrierung](preregistration.json): Qualifikations-/Code- und Arbeitsbindungen vor Vergleich.
- Vergleichsdigest: `e7157e436b973ce305b66cc54b43b9a0283150b9ca62bccf8e6bb5f40ace3af5`.
- Ergebnisdatei-SHA-256 vor/nach Verifikation: `f90047242aeba6c57c47756336a9b83b7c70d5cc83a66faee1388f38190155ff`.
- [Verifikationsdigest](verification.json): `8106e6f3a7520e3a3ad1e53e6b872eb79caf114ddd8b3d8da5136ecfcdcb8ff2`.
- [Auswertungsdigest](evaluation.json): `91c94200bb294797b38bec040294333c7b14d24ddbdd0b835518906c4d8de96c`.
- Verwendetes Materialisat: `4785e577139ff597564b1e0ceae63d3793e00a47188d5574af445025f4b37c13`.
- Ausfuehrungsplan: `1d2787da42fe01e6bb960ad545bcfbf96a3e4abd036ce91033b325c450d7f2c7`.
- Evaluationsplan: `7556d0f0c7807817468f840347ca5d139477fffb18e1b24c67ecbba00d716847`.

## Interpretation und Nichtnachweise

Die festen Rand- und ungeordneten Kontrolleingaenge sind auf dem Gegenpaar
bitgleich, die geordnete Kennzahl ist es nicht. Das bestaetigt den begrenzten
Einfluss der Reihenfolge bei identischem beobachtetem Wertebestand. Der
Unterschied stammt hier nicht lediglich aus mehr Messwerten.

Dies bleibt eine kontrollierte Permutationsgegenprobe. Weder fortgesetzte
Quellenkorrespondenz noch Bestandteilerkennung, Erzeugungskategorie oder
tragfaehige Lernbindung sind nachgewiesen. Vorzeichenbehaftete Banddifferenzen
sind keine zerlegten Klangkomponenten; andere Verlaeufe koennen dieselbe
Kennzahl ergeben. Keine neue Zulassungs- oder Memoryregel folgt daraus.

Gates nach dem Lauf `False`; keine Memory-, Feld-, Kontext- oder
Runtimeintegration. ME/MI bleiben gesperrt. Historische Fehlbefunde,
Versiegelung, fremde Aenderungen und Bootstrap bleiben unveraendert.

Naechster Vorschlag: diesen engen Befund durch den Analysten einordnen und
erst danach die naechste fachliche Gegenprognose bestimmen. Kein weiterer
NU-Lauf, keine Quellenoptimierung und keine automatische Lernintegration.
