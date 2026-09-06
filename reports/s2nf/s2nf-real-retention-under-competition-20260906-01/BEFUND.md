# S2-NF: Einmaliger Erhaltungs- und Verlustvergleich unter Konkurrenz

Technischer Abschluss: **RECORDING_COMPLETE**, unabhaengige read-only
Verifikation: **RECORDING_COMPLETE**. Getrennte Funktionsauswertung:
**CONFIRMED** fuer den vorgebundenen Erhaltungsnenner, nicht fuer alle Hinweise.

Lauf-ID: `s2nf-real-retention-under-competition-20260906-01`.
Ausgangscommit: `a9ba17f7e11b9d7fcf4e21aaec39dea42cca8f62`.

## Ausfuehrung und Quellenbindung

```text
C:\Python314\python.exe -B -m reports.s2nf.run_real_retention_once
```

Arbeitsverzeichnis: `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`.
Exit-Code `0`. Genau ein `run_main_once`, genau ein `verify_main_once`, erst
nach erfolgreicher technischer Verifikation genau ein `evaluate_main_once`.
Keine Tests, Rezeptorvorlaeufe oder Wiederholungen. Die neue Zielablage war
vor dem Hauptaufruf nicht vorhanden. Preregistration und Outcome liegen
neben dem Ergebnisverzeichnis unter derselben Lauf-ID.

Nur ein archivierter Aufrufer wurde ergaenzt. Alle qualifizierten Produkt-
und Testdateien blieben unveraendert. Das Gate wurde nur im Prozess fuer
den einen Hauptaufruf geoeffnet und im `finally` wieder auf **False** gesetzt.
Auch die historischen NE-Gates blieben geschlossen.

Die unveraenderte Vorversiegelung wurde verwendet. Sieben getrennte
Quellenrollen, darunter die bytegleichen nf-a01/nf-a03, wurden gemaess der
literalen Ereignisfolge verarbeitet. Jeder Payloadhash wurde vor der
jeweiligen Rezeptoranalyse geprueft; Rohpayloads wurden danach freigegeben,
nicht gespeichert. Keine Skalierung, Normalisierung, Ersetzung oder Suche.

Tatsaechlich ausgefuehrt: zwei frische Geschichten, drei Formationen,
zehn Teilhinweise, **13 Ereignisse und 40 Abrufbelege**. Innerhalb dieses
Laufs erfolgten **13 Audio- und drei Videoanalysen**, insgesamt **1.488
Rezeptorwerte**. Wiederholte Quellen blieben wert- und payloadgleich,
ihre Ereigniszeitbindungen jeweils getrennt.

Die Vor-/Nachhashes aller **82** im Aufrufer gebundenen Dateien sind identisch.
Diese umfassen die qualifizierten Quellen, Regeln, Kerne, Quellenversiegelung,
historischen Fehlbelege, Qualifikation und den neuen Aufrufer. Vollstaendige
Hashes stehen in Preregistration und Outcome. Die einmalige Verifikation
bestaetigt den unveraenderten atomaren Gesamtbeleg.

| Bindung | Digest |
| --- | --- |
| Ausfuehrungswurzel | 83da38c8ba7dfb7b2eb6c615d9f646a89eda60a83e3898a177fd08fe632d8cbe |
| Konfiguration | 72c74a8298d98013ef7d1552f764e46c4df1935703f0e4188f11a6eca0479beb |
| Ereignisplan | 5a0264fe43f4cc97a9ab4782b83266904e06a614a63a2c6139ad73f76a8db77a |
| Gesamtbeleg, kanonischer Digest | b8e434c39beda9b665efaf6f9b189d3a13708541f049542c2e17e376632c2272 |
| recording.json, Datei-SHA-256 | 18ae89f1a7ece3100b4f1cccba8a2f276b3fac5358d7a679c927b50b50a169a2 |
| Verifikation, interner Digest | 5e3c648b799777fb03191ce59db0d4190da0c66673a04c36bb685dc5a24bd810 |
| Auswertung, kanonischer Digest | 5a4149d0e90eecfaa44f5e5aef7a4fa8c281d8802065382b55cda3c7d304fe4a |

## Tatsaechlich gebildete Konkurrenz

Keine manuell eingesetzten Kandidaten. In h01 erzeugten die zwei
AV-Formationen Ziel und Konkurrent in B4[0]/Fast[0] beziehungsweise
B4[1]/Fast[1]. In h02 erzeugte eine frische Formation nur den Konkurrenten
in B4[0]/Fast[0]. Alle Fast-Supportwerte sind `1`, alle uebrigen Slots frei.
Beide Slow-Banken bleiben in beiden Geschichten leer.

Die drei Formationsbelege zeigen je Modalitaet **NO_UPDATE** fuer PPB:
insgesamt sechs unveraenderte PPB-Uebergaenge, keine Slotneubildung oder
Stabilisierung. Die vollstaendigen Pre-/Postdigests stehen in
`verification.json`. Alle vier Inventarpruefungen pro Geschichte sind wahr.

Alle zehn Hinweise bleiben read-only, einschliesslich ihrer vier Arme.
In h01 bleibt der Zustandsdigest durch alle fuenf Hinweise
`5a18284c04cb345da6ae4d2d2c46fd7d1bae914fe447eeef8c926fb1879943f4`,
in h02
`a89b6806f6901027eb3a74c9d233b9c0673bf769ced69fb1da9390ff246f8918`.
Nur die drei Formationen waren bestimmungsgemaess schreibend.

## Alle zehn Entscheidungen

Referenz: historisches `sum(delta_i)/24 <= 0.2`, NICHT `statistics.mean`.
Alternative: ausschliesslich B4/Fast `max(delta_i) <= 0.2`.
Beide Slow-Arme behalten historisches `sum(delta_i)/24 <= 0.02`.
Die vollen 48 Kandidatenwerte bleiben fuer interne Gleichheit gebunden.
Keine B-Bevorzugung, Hypothesenanwendung oder Vervollstaendigung.

Tabellenkuerzel: Z = `ADMIT_SINGLE_CONTEXT` mit richtigem Ziel;
K = derselbe Status mit falschem Konkurrenten;
M = `ABSTAIN_INTERNAL_AMBIGUITY`;
E = `ABSTAIN_NO_APPLICABLE_CONTEXT`.
Trefferzahlen jeweils B4/Fast/Slow. Jede Bank wurde vollstaendig gescannt.

| Fall / Ereignis | Quelle / Variante | Belegung | Referenz | Treffer | Alternative | Treffer |
| --- | --- | --- | --- | --- | --- | --- |
| c01 / h01-e03 | nf-a03 / Exakt | Ziel + Konkurrent | Z | 1/1/0 | Z | 1/1/0 |
| c02 / h01-e04 | nf-a04 / Pegel | Ziel + Konkurrent | Z | 1/1/0 | Z | 1/1/0 |
| c03 / h01-e05 | nf-a05 / Frequenz | Ziel + Konkurrent | Z | 1/1/0 | Z | 1/1/0 |
| c04 / h01-e06 | nf-a06 / spektrale Umgewichtung | Ziel + Konkurrent | Z | 1/1/0 | Z | 1/1/0 |
| c05 / h01-e07 | nf-a07 / Partialaddition | Ziel + Konkurrent | M | 2/2/0 | E | 0/0/0 |
| c06 / h02-e02 | nf-a03 / Exakt | nur Konkurrent | E | 0/0/0 | E | 0/0/0 |
| c07 / h02-e03 | nf-a04 / Pegel | nur Konkurrent | E | 0/0/0 | E | 0/0/0 |
| c08 / h02-e04 | nf-a05 / Frequenz | nur Konkurrent | E | 0/0/0 | E | 0/0/0 |
| c09 / h02-e05 | nf-a06 / spektrale Umgewichtung | nur Konkurrent | E | 0/0/0 | E | 0/0/0 |
| c10 / h02-e06 | nf-a07 / Partialaddition | nur Konkurrent | K | 1/1/0 | E | 0/0/0 |

Beide unabhaengigen Direktbaselines stimmen jeweils bei **10/10** Hinweisen
mit ihrem Primaerarm ueberein, insgesamt 20/20 Arm-Baseline-Paare.
Die Hypothesenwerte und Kandidatendigests der richtigen Zulassungen
entsprechen dem tatsaechlich gebildeten Ziel, nicht dem Cue-Zielwert.

## Erhaltung unter Konkurrenz: N/D/R/L

N = alle gebundenen positiven Faelle; D = richtige eindeutige
Referenztreffer bei tatsaechlich vorhandenem Konkurrenten;
R = davon richtig erhalten; L = nicht erhalten. Stets `D = R + L`.

| Gruppe | N | D | R | L | Befund |
| --- | ---: | ---: | ---: | ---: | --- |
| Alle Konkurrenzfaelle | 5 | 4 | 4 | 0 | CONFIRMED auf D=4 |
| Exaktkontrolle | 1 | 1 | 1 | 0 | CONFIRMED |
| Alle Varianten | 4 | 3 | 3 | 0 | CONFIRMED auf D=3 |
| Pegelvariation | 1 | 1 | 1 | 0 | CONFIRMED |
| Frequenzvariation | 1 | 1 | 1 | 0 | CONFIRMED |
| Spektrale Umgewichtung | 1 | 1 | 1 | 0 | CONFIRMED |
| Lokale Partialaddition | 1 | 0 | 0 | 0 | ERHALTUNG_NICHT_GEPRUEFT |

Die Trennung nach tatsaechlicher Variation ergibt auf allen drei Achsen
(PCM, volle 48 Rezeptorwerte, beobachtete 24 Werte) dieselben Nenner:
unveraendert `N=1,D=1,R=1,L=0`, veraendert `N=4,D=3,R=3,L=0`.
Damit sind die drei erhaltenen Varianten tatsaechlich auch im beobachteten
Rezeptorteil nicht bitidentisch. Die Exaktkopie bleibt eine getrennte Quelle.

**Verlustliste: leer. Neue richtige Treffer: keine.** Das heisst nicht,
dass alle Zielanwendbarkeiten erhalten bleiben. c05 ist in der Referenz
bereits mehrdeutig und deshalb kein D-Fall; die Alternative weist dort
sowohl das Ziel als auch den Konkurrenten ab. Keine der beiden Regeln
loest diese vorgegebene Partialaddition als richtigen Zielabruf.

Die bereits aufgezeichneten B4-/Fast-Statistiken fuer c05:

| Kandidat | Historischer Mittelwert | Maximum |
| --- | ---: | ---: |
| Ziel | 0.021060939979353908 | 0.3055088549715709 |
| Konkurrent | 0.18247290888296894 | 0.42355335368604025 |

Damit verliert der Zielkandidat selbst seine Anwendbarkeit unter der
Max-Regel, ohne dass hier ein zuvor richtiger eindeutiger Abruf verloren
geht. Das darf nicht als allgemeine Verlustausschliessung bezeichnet werden.
Die Zahlen sind aus bestehenden Abrufbelegen gelesen, nicht neu gemessen.

## Zielentfernung und Fehlzulassungen

| Bereich | Referenz | Alternative |
| --- | ---: | ---: |
| Richtiger Zielabruf bei Konkurrenz | 4/5 | 4/5 |
| Enthaltung bei vorhandenem Ziel | 1/5 | 1/5 |
| Mehrdeutigkeit bei vorhandenem Ziel | 1/5 | 0/5 |
| Fehlzulassung bei vorhandenem Ziel | 0/5 | 0/5 |
| Korrekte Enthaltung nach Zielentfernung | 4/5 | 5/5 |
| Fehlzulassung nach Zielentfernung | 1/5 | 0/5 |
| Fachlich korrekte Entscheidungen insgesamt | 8/10 | 9/10 |

Die einzige verhinderte Fehlzulassung ist **c10**: Die Referenz akzeptiert
den allein vorhandenen Konkurrenten fuer die Partialaddition; die
Alternative enthaelt sich. Diese Kontrolle hat dieselben oben aufgezeichneten
Konkurrentenabstaende wie c05. Die Verbesserung wird separat berichtet,
nicht gegen Verluste verrechnet. Die Kontrollen sind kein allgemeiner
Open-Set-Nachweis und behaupten keine akustische Identitaet der Partialaddition.

## Ressourcen und Aussagegrenze

Atomarer Gesamtbeleg: **707.838 Byte**, unter 4.194.304 Byte.
40 vollstaendige 9/3/8-Scans: **800 Slotbesuche**, **120 belegte Beziehungen**,
**2.880 Banddifferenzen**, **864 interne Gleichheitsvergleiche**, insgesamt
**3.744 Abrufwertvergleiche**, **560 logische Abrufoperationen**.
Die profilgebundene Formations-L1-Obergrenze bleibt **10.656**.
Abruf- und Gesamtgroessenlimits bestanden die einmalige Verifikation.

Dieser Lauf belegt begrenzte Erhaltung korrekter exakter und variierter
A-Treffer unter einem real gespeicherten Konkurrenten sowie eine vermiedene
Fehlzulassung nach Zielentfernung. Er prueft weder allgemeine Robustheit noch
neue Lernmechanik oder Speicherkapazitaet. Slow blieb leer; B-Abruf und
A/B-Konkurrenz sind hier nicht neu untersucht. Die Direktbaselines erklaeren
den Effekt vollstaendig.

Historische Versiegelungen, Qualifikationen und Fehlbelege bleiben
unveraendert. Feld, Runtime und Hypothesenanwendung wurden nicht aufgerufen.
Keine Produktumstellung oder Erweiterung auf Sequenz-/Praegungsfragen.

WEITER: Am besten geht es jetzt mit der Analystenbewertung dieses begrenzten
Erhaltungsbefunds und einer getrennten Entscheidung ueber die weitere
Verwendung der privaten A-Regel weiter, ohne erneuten NF-Lauf.
