# Struktur/Lage: Entscheidungsübersicht aus vorhandenen Werten

Der Einmalvergleich bleibt unverändert geschlossen. Nur Code und gespeicherte
Ergebnisse gelesen; keine Distanz-, Projektions- oder Memoryrechnung,
keine erneute Verifikation. Keine Formintegration, neue Variantenserie oder
Schwellenanpassung.

## Einzelwerte, ohne Neuberechnung

Quelle: `structure-location-comparison-20260912-01/record.json`, Bank
`primary`, Feld `mean`. Die folgenden Binary64-Hexwerte werden unverändert
wiedergegeben. Die Rohwerte sind für korrespondierende H0-/H1-Paare identisch;
die gemeinsame Spalte ersetzt keine Berechnung oder Mittelung.
Referenz ist jeweils A/P0 oder B/P0. L bezeichnet reine Lageänderung,
S andere Struktur an der genannten Position. H0 ist gleichmäßig, H1
feststehend strukturiert. Rollen sind ausschließlich Auswertungsherkunft.

| Paare H0/H1 | Beziehung | Roh288 beide | Form144 H0 | Form144 H1 |
| --- | --- | --- | --- | --- |
| 0/10 | A→A/P1 L | `0x1.cc7721cc7721cp-7` | `0x1.9bf86a314dbf8p-7` | `0x1.6a754c704b9b0p-9` |
| 1/11 | A→A/P2 L | `0x1.0bb6610bb6612p-7` | `0x1.4d1db5698f7c8p-7` | `0x1.a091479ee655fp-10` |
| 2/12 | A→B/P0 S | `0x1.0101010101010p-5` | `0x1.23456789abcdep-7` | `0x1.7b4652d4ea990p-8` |
| 3/13 | A→B/P1 S | `0x1.f74ca1f74ca20p-6` | `0x1.9bc7dea00c22ep-7` | `0x1.770f1a3884adfp-8` |
| 4/14 | A→B/P2 S | `0x1.13be6913be692p-5` | `0x1.af98d76b54933p-7` | `0x1.934b831a97655p-8` |
| 5/15 | B→B/P1 L | `0x1.d72c81d72c820p-8` | `0x1.3db15dee0c63cp-7` | `0x1.64c6863922ce7p-10` |
| 6/16 | B→B/P2 L | `0x1.0bb6610bb6613p-7` | `0x1.a3d70a3d70a3ep-7` | `0x1.8bd030ebb581ap-10` |
| 7/17 | B→A/P0 S | `0x1.0101010101010p-5` | `0x1.23456789abcdep-7` | `0x1.7b4652d4ea990p-8` |
| 8/18 | B→A/P1 S | `0x1.1e73c91e73c92p-5` | `0x1.b0bc1cd2de3efp-7` | `0x1.ad89f5cee4da7p-8` |
| 9/19 | B→A/P2 S | `0x1.be2ff713854c6p-6` | `0x1.9dc598153d0f9p-7` | `0x1.4a861982abe70p-8` |

Exaktpaare 20 (H0) und 21 (H1): in beiden Darstellungen `0x0.0p+0`.
Keine fehlende Projektion oder Gleichstände in den 24 Ordnungskriterien.

## Getrennte Entscheidung

Rohsicht: beide Lagevarianten liegen für jede Referenz vor sämtlichen drei
Strukturänderungen, unter H0 und H1. Alle vier globalen und acht gepaarten
Kriterien bestehen. Für diese konkrete relationale Unterscheidung ist keine
zusätzliche Darstellung erforderlich.

Form: unter H0 scheitern beide globalen Kriterien. A/P1 und B/P2 bestehen
auch ihre positionsgleiche Gegenprobe nicht. Unter H1 bestehen alle sechs
Kriterien. Gegenüber Rohsicht keine globalen Gewinne, zwei Verluste.
Der Hintergrund ändert die Formprojektion; die Ursache ist mit dieser
Tabelle nicht isoliert. Kein allgemeiner Hintergrundvorteil.

## Vergleichbarkeit mit produktiver visueller PPB

Der bestehende Rezeptor bildet die gleiche 12×8×3-RGB-Mittelwertskala /255
(`mcm_field_organism/finite_video_path.py:191`). Das Halbprofil halbiert nur
Audio, nicht Visual. Die private visuelle PPB-Konfiguration bindet 0,01
(`tools/_s2jw_default_live_profile.py:131`); die Entscheidung lautet
`distance <= config.match_threshold` (`mcm_field_organism/_ppb1_reference.py:611`).

**Die Rechenregel ist jedoch nicht identisch:**

- Vergleich: `sum(terms)/len(terms)` in `tools/_structure_comparison.py:40`;
  auch die unabhängige Direktrechnung verwendet `sum` (Zeile 48).
- PPB: `math.fsum(abs(left-right) ...)/len(first_values)` in
  `mcm_field_organism/_ppb1_reference.py:453`.

Damit sind Dimension und Eingangsskala gleich, aber nicht die konkrete
Binary64-Summation. Keine gespeicherte PPB-Nachrechnung für diese Paare
vorhanden. Gemäß Auftragsgrenze werden **keine Grenzbeziehungen zu 0,01 und
keine produktiven MATCHED-Entscheidungen** aus den Tabellenwerten abgeleitet.
Die Form144-Skala ist zusätzlich massennormalisiert und besitzt ohnehin
keine übertragbare visuelle PPB-Schwelle.

## Architekturentscheidung

Die Darstellung genügt hier für die vorgebundene Abstandsordnung. Nicht
belegt ist, dass die aktuelle Memory-Zuordnungsregel in dieser Gegenprobe
Erhaltung verhindert: Es fehlen ihre identische numerische Distanzrechnung
und tatsächlich gebundene Prototyp-/Zustandsverläufe. Paarabstände zwischen
Quellen sind keine Fortschreibung gegen einen schon aktualisierten Prototyp.
Auch Konkurrenz, Ablauf und Ersetzung wurden hier nicht ausgeführt.

Deshalb keine Erweiterung der Merkmalsverarbeitung auf Verdacht und keine
bevorzugte Formprojektion. Die offene Anschlussfrage liegt nun konkret bei
der regelidentischen Zuordnung der bereits ausreichend geordneten Rohwerte,
nicht bei einer schon nachgewiesenen Notwendigkeit neuer Merkmale.
Dies ist eine Eingrenzung, keine Ausführungsfreigabe oder neue Prüfserie.
Die separate reale e03/e04-PPB-Diagnose bleibt gültig, wird aber weder durch
diese synthetischen Bilder erklärt noch auf den gesamten Film verallgemeinert.
Keine Objektidentität, zeitliche Korrespondenz oder Lernbindung. Gates False.
