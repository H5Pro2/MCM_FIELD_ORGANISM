# Vertragsprüfung: visueller Prototyp und Teilhinweis

Read-only-Nachtrag zum unverändert geschlossenen Lauf
`structure-av-system-20260912-01`. Stabilisierung und Abruf sind getrennte
Befunde. Keine neue Auswertung, Distanzberechnung oder Verifikation.

## A: unmittelbarer Grund ist Trefferzahl, nicht Vollvektorvergleich

Der gespeicherte Primärscan enthält vier B4-Treffer und einen Fast-Treffer.
`tools/_s2kq_private_partial_cue_retrieval_336.py:663–665` weist bereits
`BANK_MULTIPLE_OBSERVED_MATCHES` in einer Bank als interne A-Mehrdeutigkeit
aus. Der gespeicherte `internal_equality_comparison_count` ist **0**.
Die Frage, welche Vollvektorunterschiede die Mehrdeutigkeit auslösen, enthält
deshalb eine zu starke Voraussetzung: Dieser konkrete Zweig benötigt sie
nicht. Auch gleiche Vollwerte mehrerer Slots werden hier nicht zusammengeführt.

Gespeicherte vollständige visuelle Kandidatendigests (288 Werte, nicht das
gesamte AV-Tupel; Extraktion `entry.values[48:]` in Zeile 574):

| Slot | Herkunft | Digestanfang |
| --- | --- | --- |
| B4 000 | erste q04 | aa3dba7736e3e1d7 |
| B4 001 | zweite q04 | aa3dba7736e3e1d7 |
| B4 002 | q05 | 8e6b4671c1172621 |
| B4 003 | q06 | 58a69dc6bad57751 |
| Fast 000 | fortgeschriebener AV-Slot | 28ae0007b765e170 |

Die beiden q04-Präsentationen tragen denselben visuellen Wertedigest.
q05 und q06 haben andere vollständige visuelle Werte; ihre gebundenen
Rezepte verschieben den Vordergrund gegenüber q04 um 80 Pixel horizontal
beziehungsweise 60 Pixel vertikal. Fast enthält fortgeschriebene Werte,
nicht bloß eine weitere q06-Kopie. Diese Herkunft erklärt unterschiedliche
vollständige Kandidaten, nicht aber eine ausgeführte Konfliktdistanzrechnung.
Alle fünf Kandidaten erfüllen laut gespeicherten Scans die sichtbare Gleichheit.
Ihre Unterschiede sind daher nicht durch die 32 beobachteten Komponenten
unterschieden worden. Keine numerische Differenzliste wurde neu erzeugt.

Nur falls jede Bank genau einen Treffer liefert, vergleicht `_resolve_a`
in Zeilen 672–676 die beiden vollständigen visuellen Kandidaten (Digest und
Wertetupel). Dieser andere Zweig wurde hier nicht erreicht.

## B: Stabilität und Anwendbarkeit sind unterschiedliche Bedingungen

`_scan_slow`, Zeilen 611–623: belegter Slot mit Support mindestens 3 wird
prüfbar. Anschließend gilt dieselbe `_slot_record`-Prüfung wie für A:
Zeilen 489–492 verlangen für jede sichtbare Position
`values[index] == float(cue.values[index])`.

Das ist exakte numerische Gleichheit ohne Toleranz, keine Distanzprüfung
gegen 0,01. Sie ist nicht allgemein identisch mit einer Binary64-Byteprüfung
(beispielsweise vergleicht Python +0.0 und -0.0 numerisch gleich).
Die zusätzliche Auswertungsprojektion prüft kanonische Wertdarstellung;
für die operative Entscheidung ist der gespeicherte produktive Scan maßgeblich.

Hier: visueller Slow-Slot 000, Support 3, prüfbar, `observed_match=false`;
Bereich `B_STABLE_NOT_APPLICABLE`. Der Scan speichert den aggregierten
Gleichheitsbefund und 32 Vergleiche, aber keine Liste einzelner ungleicher
Indizes oder Differenzbeträge. Native Prototyp- und Cuewerte liegen in den
Zustands-/Eingangsbelegen; eine neue numerische Gegenüberstellung wurde nicht
vorgenommen. Eine konkrete Größe oder Rundungsursache wird daher nicht behauptet.

## Verhältnis zur Prototypbildung

`mcm_field_organism/_ppb1_reference.py:619–627` aktualisiert bei Match jede
Komponente nach `(1.0-update_rate)*previous + update_rate*current` und sättigt
Support. Gebundene visuelle Rate: 0,05. Die Produktionszuordnung verwendet
den mittleren L1-Abstand; der spätere visuelle Teilabruf übernimmt diese
Anwendbarkeit ausdrücklich nicht.

Ein gemittelter stabiler Prototyp kann nach bestehendem Vertrag genau solche
gültigen Hinweise annehmen, deren 32 sichtbare Werte numerisch mit seinen
tatsächlich gespeicherten Werten übereinstimmen. Die verdeckten Werte sind
kein Cueeingang. Ob ein realer Rezeptorhinweis diese Werte erzeugt, ist eine
weitere Frage; synthetische Existenz eines Wertetupels beweist das nicht.

Keine pauschale Unvereinbarkeit: Mittelung kann sichtbare Werte erhalten
oder einen späteren Hinweis exakt treffen. Sie garantiert jedoch weder die
Wiederannahme eines früheren Eingangs noch des zuletzt eingemischten Eingangs.
Auch unveränderte Eingabekomponenten sind ohne Prüfung der konkreten
Gleitkommakette kein allgemeiner Bitgleichheitsnachweis.

Der Lauf bestätigt somit reguläre visuelle Stabilisierung, aber nicht
Abrufbarkeit dieses stabilen Prototyps mit dem festgelegten Hinweis. Die
öffentliche Enthaltung folgt bereits der internen A-Mehrdeutigkeit; B-Vorrang,
Maskenänderung oder neue Schwelle werden daraus nicht abgeleitet.
