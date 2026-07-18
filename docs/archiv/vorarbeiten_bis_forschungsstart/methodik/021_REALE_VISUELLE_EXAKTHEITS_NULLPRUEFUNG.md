# Methodik 021: Reale visuelle Exaktheits-Nullprüfung

## 1. Forschungsfrage

Bleibt die in synthetischen Folgen klar getrennte lokale Raum-Zeit-Struktur in
einer realen Bildfolge bereits durch exakten Vergleich beobachtbar, ohne
Schwelle, Glättung, Normalisierung oder Bewegungsregel?

## 2. Unveränderte Mechanik

Der reale Pfad verwendet ausschließlich:

```text
Kameraadapter
-> lokales 12-x-8-x-3-Rezeptorraster
-> saubere visuelle MCM-Schnittstelle
-> receptor_projection_baseline
-> passiver lokaler Raum-Zeit-Beobachter
```

Es werden keine Pixel oder Frames gespeichert. Jeder Frame wird gelesen,
reduziert und vor dem nächsten Frame freigegeben.

## 3. Reale Zeit

Anfang und Ende jedes tatsächlichen Frame-Lesevorgangs werden mit der
monotonen Organismusuhr gemessen. Die Prüfung endet nach einer expliziten
endlichen Framezahl.

Eine geplante menschliche Phaseneinteilung darf nur ausgewertet werden, wenn
die tatsächliche Laufdauer und die Phasengrenzen ebenfalls gemessen wurden.
Verbale Zeitangaben vor dem Lauf genügen dafür nicht.

## 4. Exakte Nullmessungen

Ohne Toleranz werden je Folgetakt gezählt:

1. Neuronen, deren aktueller Rezeptorkontakt nicht exakt ihrer eigenen
   Aktivierung des vorherigen Takts entspricht.
2. Lokale Nachbarpaare mit einem Aktivierungsunterschied ungleich null.
3. Positive und negative lokale Nachbarunterschiede getrennt.

Diese Zähler sind äußere Forschungsmaße. Sie werden nicht in das Feld
zurückgegeben und stellen keine Bewegungsmerkmale dar.

## 5. Entscheidung

Der exakte Beobachter ist für natürliche visuelle Variation nicht ausreichend,
wenn die Zähler unabhängig von der beabsichtigten kontrollierten Veränderung
nahezu oder vollständig gesättigt sind.

Ein solcher Negativbefund gibt nicht automatisch frei:

- eine feste Rauschschwelle,
- Bildnormalisierung,
- Hintergrundsubtraktion,
- zeitliche Glättung,
- Kanten- oder Bewegungsdetektion,
- trainierte Merkmale.

## 6. Evidenzgrenze

Maximal E2 für die reale Scheitergrenze des exakten passiven Beobachters.

Nicht gezeigt sind visuelle Feldreaktion, natürliche Invarianz,
Bewegungswahrnehmung, Beziehung, Lernen oder Semantik.
