# S2-NB: Einmaliger read-only Selektivitaetsvergleich

## Abschluss

- Diagnose-ID: `s2nb-auditory-selectivity-20260906-01`.
- Technischer Status: `READ_ONLY_TABLES_COMPLETE`, Exit-Code `0`.
- Genau ein Aufruf des eigenstaendigen Rechenskripts, kein Retry.
- Exakt 120 Distanzen und 4.320 absolute Wertdifferenzen.
- Keine Projektimporte, Tests, Rezeptor-, Memory-, Scanner-, Kontext-,
  Feld- oder Runtimeaufrufe. Keine PCM-Erzeugung oder Skalierung.
- S2-MT Lauf 05 bleibt `S2MT_FUNCTION_FALSIFIED`; Lauf 04 bleibt
  `NOT_EVALUABLE`. Historische Belege und Produktcode bleiben unveraendert.

## Gebundene Methode

Der unveraenderte S2-NB-Plan vergleicht `OBSERVED_24` (Baender 0 bis 23)
mit `FULL_48_DIAGNOSTIC` (Baender 0 bis 47). Grundlage sind ausschliesslich
die 13 bereits gespeicherten, skalierten Rezeptorvektoren des S2-MW-Belegs
und die Quellen-/Slotbindungen von S2-MT Lauf 05.

Beide Datei- und Recorddigests, alle 13 Binary64-Vektorbytedigests,
PCM-Bindungen, Rezeptdigests und der Quellenplandigest wurden vor der
Distanzberechnung geprueft. Alle 14 im Lauf gebundenen Quellhashes stimmen.
Die Profilparameter wurden nur statisch aus dem Quell-AST gelesen;
Fast-Konfigurations- und PPB-Parameterdigest wurden nachgerechnet.
Die Schwellen bleiben exakt `0.2` fuer A und `0.02` fuer Lernreferenzen.

B4 wird ueber den unveraenderten Eintragsbeleg aus seiner Formation,
den neuen Fast-Geschwisterslot und den gemeinsamen AV-Eingang gebunden.
Die finalen Fast-Werte stimmen direkt mit den kanonischen Vektordigests
ueberein. Es wurde kein Vektor aus einem Digest rekonstruiert.

Die Rechnung verwendet die gebundene Python-Form
`sum(abs(float(x[i]) - float(q[i])) for i in range(n)) / n`.
Bandreihenfolge, Python-Version und Skripthash stehen im Ergebnisbeleg.
Vergleiche erfolgen ohne Rundung oder Toleranz per `distance <= threshold`.
Die Tabellen unten sind ausschliesslich fuer die Darstellung gekuerzt;
JSON und CSV enthalten die ungerundeten Rechenwerte und Reserven.

## A-Treffermengen

Die fachlichen Rollen werden erst hier den fertigen labelblinden Tabellen
zugeordnet. Alle neun B4-Rollen und alle drei Fast-Rollen bleiben getrennt;
es findet keine Zusammenfassung gleicher oder aehnlicher Slotwerte statt.

| Hinweis | Rolle | B4 24 -> 48 | Fast 24 -> 48 | Entfernte / neue A-Treffer |
| --- | --- | ---: | ---: | ---: |
| e21 / n00 | A | 9 -> 9 | 3 -> 3 | 0 / 0 |
| e23 / n01 | B | 9 -> 9 | 3 -> 3 | 0 / 0 |
| e25 / n02 | C | 9 -> 9 | 3 -> 3 | 0 / 0 |
| e27 / n12 | unbekannt | 9 -> 9 | 3 -> 3 | 0 / 0 |

Damit bleiben beide internen A-Banken in beiden Armen bei jedem Hinweis
mehrdeutig. Es entsteht keine einzige neue Eindeutigkeit.

| Hinweis | B4-Distanzbereich, 24 Baender | B4-Distanzbereich, 48 Baender |
| --- | --- | --- |
| e21 | 0.0591329255 bis 0.1024846237 | 0.0510523227 bis 0.0515132793 |
| e23 | 0.0489846348 bis 0.0923362816 | 0.0459781802 bis 0.0464391292 |
| e25 | 0.0441341018 bis 0.0874855860 | 0.0435529225 bis 0.0440138568 |
| e27 | 0.0000016468 bis 0.0433533896 | 0.0214866821 bis 0.0219476453 |

Die oberen Baender sind nicht wirkungslos: Beispielsweise vergroessert sich
der Abstand des unbekannten Hinweises zu den finalen Fast-Slots von etwa
`0.000001647` auf `0.0214866821` bis `0.0214950757`. Diese Distanzen bleiben
jedoch klar unter dem fuer A gebundenen Wert `0.2`. Bei anderen Beziehungen
verringert sich die mittlere Distanz. Der 48er-Mittelwert benutzt auch einen
anderen Nenner; mehr Eingabeinformation garantiert keinen groesseren L1-Wert.

## Urspruengliche Lernreferenzen

Bei `0.02` bleiben die Referenztreffermengen ebenfalls unveraendert:

| Hinweis | OBSERVED_24 | FULL_48_DIAGNOSTIC |
| --- | --- | --- |
| e21 / n00 | n00 | n00 |
| e23 / n01 | n01 | n01 |
| e25 / n02 | n02 | n02 |
| e27 / n12 | keine | keine |

Das sind ausschliesslich Vergleiche mit den urspruenglichen Rezeptorwerten
n00/n01/n02, nicht mit finalen Slow-Prototypen. Die fehlenden Slow-Werte
wurden nicht nachgebildet. Aus dieser Tabelle folgen keine finalen
Slow-Treffermengen, Stabilitaetsaussagen oder neuen A/B-Zulassungsentscheide.

## Interpretation und Grenze

Auf diesen bekannten Quellen loest die vollstaendige 48-Band-Information
die A-Konkurrenz bei unveraenderter mittlerer L1-Bewertung und Schwelle
`0.2` nicht. Der Engpass ist damit nicht allein das Weglassen der oberen
24 Baender. Der Vergleich qualifiziert weder eine neue Maske noch eine
andere Distanzregel oder Schwelle.

Die Vollsicht bleibt eine informationsreichere Diagnosekontrolle; der
reale Teilhinweis wurde nicht erweitert. Das Ergebnis ist keine unabhaengige
Transferbestaetigung und kein negativer Befund zu jeder denkbaren auditiven
Repraesentation. Es begruendet auch keine automatische B_STABLE-Praeferenz.

STOPP: Der Zwei-Arm-Diagnosezweig ist abgeschlossen. Eine Wiederholung mit
denselben Quellen und Regeln besitzt keine neue Gegenprognose.
Eine Fortsetzung muss einen eigenstaendigen prospektiven Vergleich der
auditiven A-Anwendbarkeit unter Konkurrenz begruenden, mit unbekannten
Hinweisen und Enthaltung als regulaeren Ergebnissen. Keine Schwelle wird
aus den vorliegenden Tabellen nachtraeglich ausgewaehlt.

## Artefakte

- `../calculate_tables.py`: eigenstaendige Standardbibliotheksrechnung.
- `result.json`: Quellen-/Slotbindungen, 120 Zeilen, indexgeordnete
  Treffermengen, Kardinalitaeten und Armveraenderungen.
- `tables.csv`: vollstaendige 120-Zeilen-Tabelle.
- Ergebnis-Recorddigest:
  `3f28c93abf25458b79920d631a17f966afda50d68d939a79a46ff4f47d741c7d`.

Alle Eingabe- und gebundenen Quellhashes wurden am Ende unveraendert geprueft.
Die historische interne S2-MW-Audit-ID bleibt unveraendert; die Zuordnung
verwendet die konkreten Datei-, Record- und PCM-Bindungen.
