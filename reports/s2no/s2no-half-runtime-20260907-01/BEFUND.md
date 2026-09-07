# S2-NO: realer Halbprofil-Funktionslauf

## Abschluss und Einordnung

Lauf-ID: `s2no-half-runtime-20260907-01`, Quellenstand `7a3022a`.
Genau ein Aufruf aus dem workspace-Root:

```powershell
C:/Python314/python.exe -B -m reports.s2no.run_half_profile_once
```

Exit-Code **0**. Ein `run_main_once`, eine unabhaengige read-only
Dateiverifikation und anschliessend eine getrennte Funktionsauswertung.
Keine Tests, Rezeptorvorpruefung, Wiederholung oder Parameteranpassung.

**Technik: RECORDING_COMPLETE, evidence_valid=true.**
**Funktion: auswertbarer gemischter Befund mit zwei neuen richtigen auditiven
Abrufen.** Nicht alle Treffervorhersagen sind bestaetigt: Die bekannte
Frequenzvariante e25 bleibt auch unter ALL_BANDS_24 mehrdeutig.
Das ist eine regulaere Funktionsabweichung, kein technischer Abbruch.

Der neue Versuch verwendet ausschliesslich das getrennt versionierte
Halbprofil. Er repariert oder ersetzt keinen historischen NH-Lauf.

## Quellen und technischer Umfang

Unveraenderte NH-Vorversiegelung vom 2026-09-06:

- Ausfuehrungswurzel:
  `47ac97a175e37d45f576479ba82c906e4b36c47ae3708fca7d8e6ced885298a4`.
- Evaluationswurzel:
  `03bb9a881d5f03935104788f2a98083d2790c8dc0565c5a9664c5d5ba13e8cb2`.
- Neues Koordinatorprofil:
  `55f1de8602c945749728ce17c74cdff8320d1b5fc72c800f239bc86737db1a1e`.

Quellen-/Generator-/Interpreterbindungen und die 109 qualifizierten
Dateihashes wurden geprueft und blieben unveraendert. Nur die vorab benannten
vier versionierten Profil-/Memorymodule verwenden ihre neue qualifizierte
Hashbindung. Die historischen Quellenhashes wurden nicht pauschal ausgenommen.

Alle Payloadhashes wurden vor Verarbeitung geprueft. Keine Neuversiegelung,
zusaetzliche Eingangsabschwachung, Normalisierung, Saettigung oder Ersatzquelle.
Der bereits versiegelte PCM-Faktor blieb unveraendert. S2-NJ lag genau einmal
vor jeder neuen Audiokontaktbildung; beide Arme erhielten dieselben neuen
Wahrnehmungen. Rohpayloads wurden nach Reduktion verworfen.

| Gespeicherte Zaehler | Ergebnis |
| --- | ---: |
| Gemeinsame Audiofenster | 24 |
| Hops eines fortgefuehrten HearingPath | 240 |
| Rollende Audioabschluesse | 231 |
| Gebundene Audioendpunkte / NJ-Projektionen | 24 / 24 |
| Visuelle Analysen | 24 |
| Ereignisse je Runtimearm | 28 |
| Formationen je Runtimearm | 20 |
| Teilhinweise je Runtimearm | 8 |
| Feldkontakte, beide Arme | 16128 |
| Scanbelege einschliesslich Direktbaselines | 32 |
| Aufgezeichnete Scan-Wertvergleiche | 11552 |

Die 11552 Vergleiche liegen unter 21248; Verifikation mit eigener gebundener
Reserve. Recording **1469774 Byte** unter 4194304, Auswertung **674458 Byte**.
Auch die kompakte NO-Aussenbeleggrenze wurde erfolgreich verifiziert.
Alle Bankscans waren vollstaendig; Direktbaselines stimmen ueberein.

Korrespondierende Feld- und Memoryzustaende beider neuen Regelarme waren
gleich. Beide Runtimes endeten `CLOSED`, mit jeweils 28 verarbeiteten Ereignissen
und 20 Formationsversuchen. Alle Hinweise blieben read-only; die fruehen
Hinweise setzten die Geschichte nicht zurueck. Keine Hypothesenanwendung.

## Tatsaechliche Bildung und Herkunft

Bezeichnungen A/B/C und Druckrollen werden nur hier im Auswerter verwendet:
A=`p00`, B=`p01`, C=`p02`, Druck=`p03..p11`.

Fast legte bei e01/e02/e05 drei getrennte Slots 000/001/002 an. Die folgenden
Wiederholungen trafen jeweils den eigenen Slot. Bei e14 wurde Fast-002 durch
p03 ersetzt, bei e15 Fast-000 durch p04, bei e16 Fast-001 durch p05. Die
weiteren Druckereignisse belegten die Slots im gleichen dreistufigen Wechsel.
Final: Fast-000=p10, Fast-001=p11, Fast-002=p09. Keine gemischte Fast-Herkunft
in den gespeicherten Formationsinventaren.

Die folgende PPB-Kette gilt getrennt fuer Audio und Visual:

| Inhalt | Slotendung | Tatsaechliche Uebergaenge | Final |
| --- | --- | --- | --- |
| A/p00 | 000 | e06 CREATED(1), e09 MATCHED(2), e12 MATCHED(3) | stabil, reine p00-Herkunft |
| B/p01 | 001 | e07 CREATED(1), e10 MATCHED(2), e13 MATCHED(3) | stabil, reine p01-Herkunft |
| C/p02 | 002 | e08 CREATED(1), e11 MATCHED(2) | instabil, reine p02-Herkunft |

Bei e01/e02/e05 sowie e14..e22 ist fuer beide PPB-Banken `NO_UPDATE`
aufgezeichnet. Keine Slow-Ersetzung, keine Vermischung und keine nachtraegliche
Slow-Mitaktualisierung durch Druckquellen. Final sind je drei Slots belegt;
fuenf auditive und ein visueller Slow-Slot bleiben frei.

Die neun B4-Eintraege enthalten final ausschliesslich die Formationen 12..20
(p03..p11). A, B und C sind aus B4 und Fast vollstaendig verdraengt. Support
3/3/2 wurde in beiden Slow-Banken erreicht; es war kein technisches Startgate.
Alle 20 Inventare und 40 modalitaetsgetrennten PPB-Uebergangsbelege samt
Pre-/Postdigests und Herkunft stehen unveraendert in `evaluation.json`.

## Alle acht Hinweise

Referenz: `HISTORICAL_SUM_L1_24` mit historischer `sum(...)/24`-Rechenfolge
innerhalb des neuen Profils. Alternative: `ALL_BANDS_24` nur fuer auditives A.
Audio-A-Grenze 0.1, Audio-Slow-Grenze 0.01; feste Rangumrechnung unveraendert.

| Ereignis | Hinweis | Referenz | Alternative | Fachlicher Befund |
| --- | --- | --- | --- | --- |
| e03 | A auditiv, fruehe Exaktkontrolle | interne Mehrdeutigkeit | A_RECENT | neuer richtiger Abruf |
| e04 | A visuell, frueh | A_RECENT | A_RECENT | richtig erhalten |
| e23 | A auditiv, Pegelvariante | interne Mehrdeutigkeit | B_STABLE_AUDITORY | neuer richtiger Abruf |
| e24 | A visuell, spaet | B_STABLE | B_STABLE | richtig erhalten |
| e25 | B auditiv, Frequenzvariante | interne Mehrdeutigkeit | interne Mehrdeutigkeit | erwarteter Treffer fehlt |
| e26 | B visuell, spaet | B_STABLE | B_STABLE | richtig erhalten |
| e27 | unbekannt auditiv | interne Mehrdeutigkeit | interne Mehrdeutigkeit | korrekte Enthaltung, keine Unbekanntheitserkennung |
| e28 | unbekannt visuell | kein anwendbarer Kontext | kein anwendbarer Kontext | korrekte Enthaltung |

Die zwei neuen auditiven Hypothesen besitzen eindeutige reine Zielherkunft:
e03 aus p00 in B4-000/Fast-000, e23 aus p00 in Auditory-Slow-000.
Reine Wertegleichheit wurde nicht als hinreichender Herkunftsnachweis gewertet.

Gespeicherte auditive Treffermengen, Anzahl B4/Fast/Slow:

| Ereignis | Referenz | Alternative |
| --- | --- | --- |
| e03 | 2 / 2 / 0 | 1 / 1 / 0 |
| e23 | 9 / 3 / 1 | 0 / 0 / 1 |
| e25 | 9 / 3 / 1 | 5 / 2 / 1 |
| e27 | 9 / 3 / 1 | 5 / 2 / 1 |

Bei e25 ist der richtige B-Slot vorhanden, aber verbleibende A-Treffer
erzwingen weiterhin Enthaltung. Auch e27 passt zu B-Slot 001 und mehreren
A-Inhalten. Seine Enthaltung beweist deshalb keine Erkennung von Unbekanntheit.
Keine B-Bevorzugung oder nachtraegliche Schwellenkorrektur.

## Getrennte Erhaltung, Gewinn und Verlust

N zaehlt bekannte positive Hinweise; D deren richtige Referenzabrufe,
R erhaltene richtige Abrufe und L Verluste. In allen folgenden Gruppen liegt
tatsaechliche Konkurrenz vor; D=R+L.

| Gruppe | N / D / R / L | Neue richtige Abrufe |
| --- | --- | --- |
| Audio gesamt | 3 / 0 / 0 / 0 | 2: e03, e23 |
| Audio frueh, exakt | 1 / 0 / 0 / 0 | 1: e03 |
| Audio spaet, Varianten | 2 / 0 / 0 / 0 | 1: e23 |
| Audio Pegel | 1 / 0 / 0 / 0 | 1 |
| Audio Frequenz | 1 / 0 / 0 / 0 | 0 |
| Visual gesamt, beobachtete Werte exakt | 3 / 3 / 3 / 0 | 0 |
| Visual frueh | 1 / 1 / 1 / 0 | 0 |
| Visual spaet | 2 / 2 / 2 / 0 | 0 |

**Auditiv bleibt Erhaltung nicht geprueft.** L=0 bei D=0 ist kein Nachweis von
Verlustfreiheit und wird nicht durch die drei visuellen Referenztreffer ersetzt.
e03 ist auch rezeptorseitig exakt; e23/e25 sind sowohl im vollen Rezeptorvektor
als auch auf den beobachteten Baendern veraendert. Die visuellen Teilbilder
haben andere Payloads und volle reduzierte Vektoren wegen der Okklusion,
aber unveraenderte beobachtete Positionen. Diese Achsen bleiben getrennt.

Fehlzulassungen: **0/4 Audio und 0/4 Visual je Arm**, also 0/8 je Arm.
Keine verhinderte Fehlzulassung gegenueber der Referenz in diesem Versuch.
Verworfene zuvor anwendbare Zielkandidaten: keine in allen acht gepaarten
Hinweisbelegen. Gewinne werden nicht mit Verlusten verrechnet.

Enthaltungen: Referenz 4/4 Audio, 1/4 Visual; Alternative 2/4 Audio,
1/4 Visual. Davon sind je Arm zwei Enthaltungen bei den zwei unbekannten
Hinweisen korrekt. Die auditive Enthaltung bei e25 ist dagegen ein verfehlter
bekannter Abruf und bleibt sichtbar.

## Belegbindungen und Grenzen

- Gesamtbelegdigest:
  `c4095c283efa12cdfb28f650c625f1850e2ae619946f2d7bbdbfd097b0a30aad`.
- Recording-Datei-SHA-256, durch die einmalige Pruefung gebunden:
  `f55d0273189a57d5111fe521fe3dd932bb759134be999a3aa22ba259613d39c5`.
- Auswertungsdigest:
  `be8ec235d881b4e7ce4953f690984bac7d86f802f7e697b0a21ba18e9f99fa18`.
- Abschlussdigest:
  `a155b3828f24521c7336949d42c9f407c2046f90c9fa3fe043449434043be47a`.

Der Korpus war urspruenglich unabhaengig vorversiegelt, war vor diesem Lauf
jedoch bereits teilweise untersucht, insbesondere e01/e02. Dies ist **kein
vollstaendig unberuehrter Bestaetigungskorpus** und keine allgemeine Robustheit.

Die S2-NM-Abweichung bleibt akzeptierte Grenze der neuen Forschungsvariante:
Halbierung kann Subnormalunterschiede und damit historische Konflikte verlieren.
In den 24 gespeicherten NJ-Belegen sind hier keine Subnormal-/Unterlaufbaender
markiert. Daraus folgt weder ein universeller Binary64-Nachweis noch eine
allgemeine semantische Gleichheit der Profile. Keine Alt-/Neu-Feldgleichheit
wurde gefordert oder gemessen; kein kompensierender Feldgain.

Die Offline-Pruefung bestaetigt Quellen-/Plan-/Zeitbindungen, Digestlinks,
NJ-Ausgabeobjekte, neue gerundete Werte und Runtime-/Scanbelege. Sie wiederholt
weder Rezeptor noch Multiplikation und rekonstruiert keine Rohenergien.
Ohne Rohwerte bleibt die numerische Herkunft von Halbierung und Unterlauf
nicht unabhaengig nachrechenbar. Diese Einschraenkung steht explizit im
Verifikationsbeleg, nicht nur in diesem Bericht.

NO, NG, NN, NH, NL und Source-Gate sind nach dem Aufruf **False**.
Historischer NH-Abbruch, NM-Befund, andere historische Belege, fremde
Aenderungen und Bootstrap bleiben unveraendert. Keine Produktumstellung.

WEITER: Am besten geht es jetzt mit der Analystenbewertung dieses begrenzten
Halbprofil-Transfergewinns und der weiterhin offenen Abrufkonkurrenz bei e25
weiter, ohne Wiederholung oder Schwellenanpassung.
