# Einmalvergleich visueller B-Anwendbarkeit

## Technischer Abschluss

visual-b-frozen-comparison-20260912-01: RECORDING_COMPLETE.
Sieben Hinweise einmal analysiert, Payloadhash jeweils vorher bestätigt.
112 gespeicherte B-Slotbelege und 448 Abstandsterme einschließlich Direktarm.
Ein unabhängiger Verifikationsdurchgang: VERIFIED, evaluation_allowed=true;
56 zusätzliche B-Slotprüfungen und 224 Abstandsterme im Verifikator.
Danach einmal getrennt ausgewertet. Keine Qualifikation wiederholt.

Record-Digest:
`a722aef38847a999358e9c7fda4544c0ceaad52676df4a71cd9babab7f3ba86f`.
Freigabedatei admission-authorized.json, SHA-256:
`40909585a8a60e8da83556648c3347e20f72a486e584f37fc1c6dc8fb7639380`.
Die vorherige admission-final.json bleibt unverändert erhalten und mitgezählt.

## Alle sieben Entscheidungen

EX = historische Exaktgleichheit; MAX = Maximumabstand <= 1/255.
I = ABSTAIN_INTERNAL_AMBIGUITY; N = ABSTAIN_NO_APPLICABLE_CONTEXT;
B = ADMIT_SINGLE_CONTEXT im Bereich B_STABLE.

| Hinweis | Rolle | B-Treffer EX | B-Treffer MAX | Öffentlich EX / MAX |
| --- | --- | --- | --- | --- |
| vb-01 q04 | gelernter Eingang | keiner | Slot 000 | I / I |
| vb-02 q05 | gelernter Eingang | keiner | Slot 000 | I / I |
| vb-03 q06 | gelernter Eingang | keiner | Slot 000 | I / I |
| vb-04 q06 +1 | positive Pegelvariante | keiner | keiner | N / N |
| vb-05 q06 -1 | negative Pegelvariante | keiner | Slot 000 | N / B |
| vb-06 q01 | verdeckte Strukturkontrolle | keiner | Slot 000, fachlich falsch | I / I |
| vb-07 Rechteck | sichtbare Strukturkontrolle | keiner | keiner | N / N |

Alle MAX-Treffer betreffen dieselbe eingefrorene Generation 2 von
ppb1.visual.default-live.v1.slot.000. Keine Ersetzung oder Aktualisierung.
Bei vb-01/02/03/06 treffen weiterhin B4 000/001/002/003 und Fast 000;
die unveränderte A-Auflösung bleibt intern mehrdeutig. Bei vb-04/05/07
ist A nicht anwendbar. Primär- und unabhängige Direktrechnung stimmen überein.

## Getrennte Funktionsbefunde

Vier neue richtige B-Anwendbarkeiten gemäß vorgebundener Bewertung:
drei gelernte Eingänge und die negative Pegelvariante. Zusätzlich eine
neue falsche B-Anwendbarkeit bei vb-06. Keine Verrechnung dieser Befunde.
Öffentlich entsteht genau ein neuer richtiger B-Zielabruf, bei vb-05.
Keine neue öffentliche Fehlzulassung: Bei vb-06 verhindert A-Mehrdeutigkeit
die öffentliche Zulassung. Das macht seine B-Fehlanwendbarkeit nicht richtig.

| Gruppe | N | B: D/R/L | B-Gewinne | neue falsche B-Anwendbarkeit | öffentliche Gewinne |
| --- | ---: | --- | ---: | ---: | ---: |
| gelernte Eingänge | 3 | 0/0/0 | 3 | 0 | 0 |
| neue Pegelvarianten | 2 | 0/0/0 | 1 | 0 | 1 |
| verdeckte Struktur | 1 | 0/0/0 | 0 | 1 | 0 |
| sichtbare Struktur | 1 | 0/0/0 | 0 | 0 | 0 |

Öffentlich ebenfalls in jeder Gruppe D/R/L=0/0/0. **D=0 bedeutet Erhaltung
nicht geprüft**, nicht bestätigte Verlustfreiheit. Die positive Pegelvariante
besteht die Alternative nicht; ihre numerische Ursache wurde nicht zusätzlich
zerlegt. Exakte Quellenwiederholung war kein exakter Prototyptreffer.

## Bilanz und Aussagegrenzen

Abschluss mit verbleibender Berichts-/Bilanzreserve: 2.219.538 Byte,
davon 80.889 Metadaten; keine Verletzung, keine temporären Reste.
Referenzen 2.113.594 Byte vollständig enthalten. Datei-Istwerte: balance.json.
Dieser Bericht bleibt innerhalb seiner 4.096-Byte-Reserve.

vb-01/02/03/06 sind nach Okklusion bytegleich, bei getrennten Quellenrollen.
Sie sind keine unabhängigen Replikate. Quellenrollen gehen nicht in die
Scanrechnung ein; die verdeckte Struktur liefert dort keine Zusatzinformation.
Der Bestand wurde wiederverwendet und war bereits untersucht. Offline-Prüfung
rekonstruiert weder RGB-Erzeugung noch Rezeptoranalyse. Keine Memoryfortschreibung,
Feld-/Runtimeausführung, Hypothesenanwendung oder Produktumstellung. Gates False.
Einmallauffreigabe verbraucht; keine automatische Folgeausführung.
