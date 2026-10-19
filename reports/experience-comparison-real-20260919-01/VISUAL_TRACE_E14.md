# Erfahrungsvergleich: Visuelle Spurentabelle e14 bei 1,0 Sekunden

Status: read-only Befund. Grundlage sind ausschließlich die gespeicherten
Lauf-, Verifikations- und Auswertungsbelege von
`experience-comparison-real-20260919-01` sowie die statische Bankzuordnung im
laufgebundenen Code. Es wurden keine Scans, Distanzen oder Rezeptoraufrufe neu
berechnet.

Die Planbezeichnung `e14` entspricht `media-event-14`: visueller Teilhinweis
im zweiten Durchlauf bei Medienzeit `1,0 s`. Seine Zielbildung ist
`media-event-03`, die vollständige AV-Formation im ersten Durchlauf bei
derselben Medienzeit. Beide beziehen sich auf den Video-PTS `31031` mit
nächstem PTS `32032`; der Teilhinweis verwendet erwartungsgemäß seinen eigenen
okkludierten RGB-Payload und nicht den vollständigen Formations-Payload.

| Spur oder Prüfung | Gespeicherte Kette | Zustand unmittelbar vor e14 | Befund |
| --- | --- | --- | --- |
| Zielbildung | e03 bildete den Zielinhalt; die Formation erhielt `B4_APPENDED` in `b4.slot.002`. | Die e03-B4-Generation ist nicht mehr aktuell. | Die direkte B4-Zielspur wurde bei e12 in derselben Slot-ID durch eine neue Generation ersetzt. |
| Visuelle Slow-Spur | e03 erzeugte in der visuellen PPB-Komponente mit globalem Index 21 eine Generation. | Diese Generation ist nicht mehr aktuell. | e07 ersetzte Komponente 21 durch eine neue Generation; e04 bis e06 enthalten für diese Komponente keinen `MATCHED`-Übergang. |
| Fast-Spur | e03 protokolliert für Fast einen `MATCHED`-Übergang. | Der e14-Scan enthält einen aktuellen, prüfbaren Fast-Kandidaten; dieser besteht die beobachtete Prüfung nicht. | Eine visuelle Herkunft des aktuellen Fast-Prototyps aus der e03-Zielbildung ist im gespeicherten Scan nicht ausgewiesen. |
| B4-Scan | Neun aktuelle B4-Kandidaten, 288 beobachtete Vergleiche. | Kein Kandidat ist beobachtet anwendbar (`match_count = 0`). | Alle aktuellen B4-Spuren werden durch die bestehende Regel ausgeschlossen. |
| Fast-Scan | Ein aktueller Fast-Kandidat, 32 beobachtete Vergleiche. | Der Kandidat ist nicht beobachtet anwendbar (`match_count = 0`); zwei Slots sind frei. | Kein Fast-Kandidat trägt zur Zulassung bei. |
| Visueller Slow-Scan | Vier visuelle Slow-Slotcontainer werden im Scan geführt. | Keiner ist stabil und scanberechtigt: `eligible_count = 0`, `comparison_count = 0`, für jeden Platz fehlen Kandidatenwerte und Stabilitätssupport. | `B_STABLE_ABSENT_VALID` bedeutet hier keinen stabilen Slot, nicht den Nachweis, dass alle physischen Slotcontainer frei sind. Die visuelle stabile Bank liefert keinen alternativen Kontext. |
| Öffentliche Entscheidung | Primärscan und unabhängige Direktbaseline sind gespeichert. | Beide geben `ABSTAIN_NO_APPLICABLE_CONTEXT` ohne Hypothese aus. | Die Ablehnung ist kein Baselinekonflikt und keine Mehrdeutigkeitsauflösung. |

Die globale Bankreihenfolge ist statisch als B4, Fast, auditives PPB und
visuelles PPB belegt. Damit ist Index 21 der visuellen PPB-Bank zugeordnet;
die Zuordnung folgt nicht aus einer nachträglichen Rolleninterpretation.

## Einordnung

**Bestätigt:** Vor e14 sind sowohl die direkte B4-Zielgeneration aus e03 als
auch die zugehörige visuelle Slow-Generation nicht mehr verfügbar. Die noch
aktuellen B4- und Fast-Kandidaten werden vom unveränderten Scan regelkonform
ausgeschlossen. Die visuelle Slow-Bank ist im technischen Sinn
`ABSENT_VALID`: Es gibt keinen stabilen, scanberechtigten visuellen Slow-Slot.
Sie ist damit nicht als Nachweis einer vollständig freien physischen Bank zu
lesen. Der Teilhinweis bleibt read-only, der Vor- und Nachzustand sind gleich.

**Nicht belegt:** Aus dem gespeicherten `MATCHED`-Übergang bei e03 folgt nicht,
dass der aktuelle Fast-Prototyp noch einen unterscheidbaren visuellen Anteil
der Zielbildung enthält. Der e14-Scan enthält keine transaktionsgebundene
visuelle Herkunftskette für Fast-Updates. Deshalb lässt sich für Fast nicht
zwischen „Zielinhalt wurde erhalten, aber die Regel verwirft ihn“ und
„Zielinhalt wurde in Fast nicht erhalten“ entscheiden.

**Kleinste fehlende Evidenz:** Eine rein diagnostische, transaktionsgebundene
Herkunftskette je Fast-Prototyp-Update: beitragende Formationsgenerationen,
visuelle Komponente sowie Ersetzungs- oder Mischstatus. Sie könnte nur
belegen, ob e03 zu einem späteren Fast-Update beigetragen hat. Sie wäre
kein Erhaltungsnachweis, weil eine Beitragsherkunft nicht zeigt, ob der
visuelle e03-Inhalt im aktuellen Prototyp noch unterscheidbar erhalten ist.
Für diese zweite Frage wären zusätzlich wert- und updategebundene
Erhaltungsbelege nötig. Beides dürfte nur den Befund erklären und weder als
Cuewert noch als Eingabe der Abrufregel dienen.

Die vollständigen Primär- und Baselinebelege verbleiben unverändert in
[`record.json`](record.json), [`evaluation.json`](evaluation.json) und
[`REPORT.md`](REPORT.md). Dieser Nachtrag ersetzt keine historische Messung und
klassifiziert keine fehlende historische Zahl als Messwert.
