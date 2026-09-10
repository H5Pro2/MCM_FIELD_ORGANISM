# S2-OA: korrigierte administrative Bindung

Status **ADMINISTRATIVE_BINDINGS_VALID**, Exit-Code 0.
ID `s2oa-administrative-binding-20260910-01`. Ein administrativer
Bindungsaufruf, danach genau eine unabhaengige read-only Pruefung.
**Keine erneute numerische Versiegelung und keine Payloadregeneration.**

Grundlage: unveraenderte historische OA-Quellenbelege vom 2026-09-09 und
die neue [20/20-Qualifikation](../s2oa-admin-binding-qualification-20260910-01/BEFUND.md).
Der alte [Budgetabweichungsbefund](../s2oa-source-preseal-20260909-01/BEFUND.md)
bleibt unveraendert gueltig; die alten Artefakte werden nicht rueckwirkend
budgetkonform genannt. Neue v2-Geltung ausschliesslich administrativ.

## Kompakte Bindung und Herkunft

[binding.json](binding.json) enthaelt eine kompakte Ausfuehrungswurzel mit
48 getrennten Quellenreferenzen und 28 Ereignisreferenzen. Referenzen binden
Archivdatei, Originalfeld, Originalindex und Digest des vollstaendigen Wertes.
Quellen-/Ereignisidentitaet, originale Rezepte, Payloadhashes und Zeitfenster
bleiben erhalten; Profil, Generator, Umgebung und Code werden einmal aus
derselben historischen Wurzel referenziert. Keine Duplikation dieser Werte
in der neuen [Vorregistrierung](preregistration.json).

Die getrennte Evaluationswurzel verweist unveraendert auf alle historischen
Erwartungen. Historische budgets sind Archivaussagen, keine aktiven v2-Limits.
Die [vorab festgelegte Klassenzuordnung](../ADMINISTRATIVE_BUDGETBINDUNG.md)
zaehlt die sechs benoetigten historischen Datenartefakte mit ihrer vollen
Dateilaenge. Mehrfache Referenzen erzeugen keinen mehrfachen Freibetrag;
Referenzierung entfernt keine notwendigen Artefaktbytes aus der Bilanz.

## Vollstaendige administrative Bytebilanz

| Metadatenbestandteil | Byte |
| --- | ---: |
| Neuer Bindungsbeleg | 15.594 |
| Neue administrative Vorregistrierung | 2.977 |
| Neue Qualifikationsvorregistrierung | 2.082 |
| Neues Qualifikationsergebnis | 2.167 |
| Qualifikation stderr / stdout | 2.618 / 0 |
| **Metadaten gemeinsam** | **25.438 / 65.536** |
| **Verbleibend fuer Metadaten** | **40.098** |

| Historische Quellenherkunft, voll mitgezaehlt | Byte |
| --- | ---: |
| Ausfuehrungsplan | 78.644 |
| Vorregistrierung | 69.553 |
| Evaluationsplan | 1.665 |
| Siegel | 6.683 |
| Read-only Verifikation | 1.421 |
| Historisches 18/18-Ergebnis | 4.355 |
| **Referenzierte Quellenherkunft** | **162.321 / 174.080** |

| Gemeinsame Zusatzhulle mit Zukunftsreserven | Byte |
| --- | ---: |
| Quellenherkunft aktuell | 162.321 |
| NJ: 22 * 1.024 reserviert | 22.528 |
| Formation: 20 * 1.536 reserviert | 30.720 |
| Generationsdelta-Bloecke: 20 * 1.536 reserviert | 30.720 |
| **Gemeinsam belegt oder reserviert** | **246.289 / 262.144** |
| **Verbleibend insgesamt** | **15.855** |

Die 15.855 Byte bestehen aus 11.759 noch freier Quellenherkunftsbelegung und
4.096 nicht zugewiesener Reserve. Kein Einzelbestandteil bekommt diese
Summe zusaetzlich; die festen Teildeckel bleiben verbindlich.

Fuer die vorhandenen 21 Zustands-, 56 Eingabe-/Schritt- und 16 Scanbelege
sind ausserdem 3.506.160 Byte vorgesehen. Mit den aktuellen Metadaten und
der gesamten obigen Zusatzreservierung: **3.777.887 / 4.194.304 Byte**;
verbleibend **416.417 Byte**, darunter die noch freien Metadaten-/Quellen-
Anteile. Mit voll ausgeschoepften urspruenglichen Metadaten- und Zusatz-
deckeln waeren es 3.833.840 Byte; kein zusaetzlicher Rahmen ausserhalb der
Klassen erlaubt. Die funktionalen Belege existieren noch nicht.

Neue Verifikationsklasse separat: Pruefbeleg 1.580 + Einmal-Claim 24 =
**1.604 / 262.144 Byte**. Keine fachliche Auswertung erzeugt.

## Unabhaengige Pruefung und Aussagegrenze

[verification.json](verification.json) bestaetigt Quellenabschluss, alle
Referenzziele, vollstaendige referenzierte Werte, getrennte Evaluationsbindung,
historische und neue Codehashes, tatsaechliche Dateigroessen und unabhaengige
Summenbildung. Neue Belegdateien bleiben vor/nach der Pruefung hashgleich.
Alle sechs historischen Dateihashes stimmen mit den vorab gepinnten Werten
ueberein. Die vier neuen Qualifikationsdateien sind ebenfalls voll gebunden.

Bindungsdigest:
`7497f8346bcdcd8a04615a093bcb8794c63c8e9ecfad31c2eccbfb2d4cde4228`.
Verifikationsdigest:
`42d1a4d26fa6f4eb619c56a7fc0a88a4ba1a598449943b01c63d12dca029f795`.

Keine PCM-/RGB-, Rezeptor-, NJ-, Memory-, Feld- oder Runtimeaufrufe. Keine
numerische Gueltigkeits-, Zustands- oder Funktionsaussage hinzugefuegt.
Insbesondere muessen NJ-/Formations-/Generationsbelege bei einer spaeter
freigegebenen Anschlussqualifikation ihre reservierten Einzel- und Gesamt-
limits tatsaechlich einhalten. Dieser administrative Beleg ersetzt diese
Qualifikation nicht und behauptet keine bereits vorhandene Generationserfassung.

Gates False. Eininstanz-/Generationsimplementierung und Hauptlauf bleiben
gesperrt. Historische Belege, fremde Aenderungen und Bootstrap unveraendert;
ME/MI gesperrt, Prognosezweig ruht.

RUECKMELDUNG ERFORDERLICH: separate Analystenentscheidung ueber den
funktionalen Eininstanz-/Generationsanschluss. WEITER: Am besten geht es
jetzt mit der Pruefung dieser korrigierten administrativen Bindung weiter.
