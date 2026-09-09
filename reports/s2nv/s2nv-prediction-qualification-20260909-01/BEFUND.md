# S2-NV: praefixgebundener Prognoseanschluss neutral qualifiziert

Genau ein Aufruf unter `s2nv-prediction-qualification-20260909-01`:
**20/20**, Exit-Code `0`, `S2NV_PREDICTION_QUALIFIED`. Kein Retry.
Die historische Quellenqualifikation und Vorversiegelung wurden nicht wiederholt.

```text
C:/Python314/python.exe -m reports.s2nv.qualify_prediction_once
```

Der [Vorabbeleg](preregistration.json) bindet das vollstaendige Testinventar,
Codehashes, Umgebung und getrennte Arbeits-/Verifikationsbudgets vor dem
Aufruf. Das [Protokoll](stderr.txt) weist alle 20 erreichten Testkoerper aus.
[Ergebnisbeleg](result.json), Digest:
`1f9b87baeb68cf8b4092b1007b13ed30f1832c09516dfcea40dbcdda15b189f8`.
Alle gebundenen Quellhashes sind vor/nach dem Aufruf identisch.

## Implementierter Anschluss

- LINEAR: Profil und zwei Halbvektoren, Subtraktion vor Addition.
- PERSIST: Profil und letzter Halbvektor, Bitkopie einschliesslich
  Subnormalwerten und negativem Nullwert.
- Fensterweiser Controller: beide Prognosen und die Direktnachrechnung
  zuerst unveraenderlich binden; erst dann das jeweilige Zielfenster erzeugen,
  hashen, analysieren und einmal mit NJ projizieren.
- Frischer Controller je Strom, keine Zielcache- oder Historienuebernahme.
  Das naechste Praefix verwendet reale Ergebnisse, keine Prognoseersatzwerte.
- Unabhaengige Direktarithmetik, atomarer Gesamtbeleg, read-only Gesamtpruefung
  und erst danach getrennte Auswertung. Bestehender NU-Dateihelfer unveraendert
  wiederverwendet; kein historischer Haupteinstieg aufgerufen.

Private Einstiegspunkte sind `run_main_once`, `verify_file_once` und
`evaluate_file_once` in
[prediction_run](../../../tools/_s2nv_private_prediction_run.py).
Der reale Einstieg erfordert explizite Freigabe, eine neue unbenutzte ID,
unveraenderte Quellen-/Qualifikationsbindungen und geoeffnetes Gate nur fuer
diesen Aufruf. Derzeit bleibt das Gate `False`; keine reale Lauf-ID wurde vergeben.

## Tatsaechlich erreichte neutrale Kontrollen

Vorzeitiger Zielzugriff sowie fehlende/doppelte Prognosebindung wurden vor
Adapteraufruf abgewiesen. Aenderung gebundener Prognosen wurde auch bei neuem
Digest erkannt; Aenderung waehrend Zielverarbeitung veroeffentlichte keinen
Fall. Gleiche funktionale Praefixe mit anderen administrativen Quellen-IDs
lieferten identische Prognosen.

Der echte neutrale Adapterpfad verarbeitete fuenf konstante, nicht aus NV
stammende Fenster: **fuenf direkte Analysen und fuenf NJ-Projektionen**.
Die Bindung lag jeweils vor Zielfenstererzeugung. Zeit-/Payloadfehler wurden
vor Analyse abgewiesen; gespeicherte Roh-/Halbwerte wurden anschliessend
neutral vorwaerts geprueft. Synthetische reduzierte Belege prueften zusaetzlich
die vollstaendige Vier-Strom-Huelle und die getrennten Arbeitszaehler.

Prognosen -1 und 2 blieben ungeclippt und gingen voll in den Fehler ein.
Neutrale Fortsetzungsgewinne, Wechselverluste und Gleichstaende wurden getrennt
bewertet. Eine durch Gleichstand falsifizierte Primaerprognose blieb technisch
gueltig. Quellen-/Prognosemanipulation, fehlende Belege, Auswertung vor
Verifikation, Schreibkonflikt und Uebergroesse wurden abgewiesen.

Der neutrale Dateieinstieg erzeugte einen atomaren Gesamtbeleg, genau eine
Dateiverifikation und eine nachgelagerte Bewertung im temporaeren Verzeichnis.
Die synthetische 2099-ID ist kein realer NV-Lauf. Ein phasengenauer neutraler
Generierungsfehler wurde mit abgeschlossenen Zaehlern, ohne fachliche
Teilauswertung und ohne Wiederholung abgeschlossen.

## Grenzen und Belege

Die gespeicherte [vollstaendige neutrale Huelle](neutral-envelope.json)
enthaelt 20 Fenster, zwoelf Prognosestellen, beide Implementierungen,
Roh-/Halbwerte, Prognosen, Einzelbandfehler und Codebindungen:
**265.017 Byte** bei unveraendertem Limit 2.097.152 Byte.
Huellendateihash:
`c95a8ad276c755b5f1cc6ce35eebac076951c5f4730253f37442b7530b046948`.
Vorabbeleg 12.074 Byte und Qualifikationsbeleg 7.059 Byte liegen jeweils
unter 65.536 Byte. Die Artefaktgrenze wird im echten Einstieg erneut erzwungen;
der neutrale Umfang ersetzt keine Annahme ueber konkrete NV-Ausgabewerte.

Prognosearithmetik, Fehlerarithmetik und Offline-Verifikation sind getrennt
budgetiert. Spaeter unveraendert hoechstens 2.304 Fehlerterme einschliesslich
Direktnachrechnung; Offline separat 960 Halbierungen, je 1.152 Prognose-
Subtraktionen/Additionen, 2.304 Fehlerterme, 48 Summen und 24 Gains.

Die Offline-Pruefung berechnet gespeicherte Halbierungen und Prognosen vorwaerts
nach. Sie regeneriert kein PCM, fuehrt keine FFT/NJ aus und rekonstruiert
keine Rohwerte aus Halbwerten. Die historische CPU-Reihenfolge folgt nicht
aus einem finalen Digest allein. Qualifiziert ist die programmatische Sperre
des konkreten Aufrufpfads, keine Sicherheitsgrenze gegen beliebige fremde
Codeausfuehrung im selben Pythonprozess.

**Keine NV-Payloads, kein NV-Zielmaterialisat und kein realer NV-Lauf.**
Kein Memory-, Feld- oder Runtimeaufruf. Ein Hauptlauf benoetigt weiterhin
separate Freigabe; eine separate Vorabmaterialisierung seiner Ziele bleibt
ausgeschlossen. Es liegt noch kein realer Prognosenutzen vor. Das Verfahren
ist feste Extrapolation, kein Lernen. NU bleibt geschlossen, ME/MI gesperrt;
Versiegelung, historische Belege, fremde Aenderungen und Bootstrap unveraendert.
