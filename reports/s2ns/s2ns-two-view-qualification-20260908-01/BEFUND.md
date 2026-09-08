# S2-NS: private Zwei-Sichten-Logik neutral qualifiziert

Status: `S2NS_TWO_VIEW_LOGIC_QUALIFIED`, **24/24**, Exit-Code `0`.
ID: `s2ns-two-view-qualification-20260908-01`.

Genau ein vorab gebundener Qualifikationsaufruf aus dem workspace-Root:

```powershell
C:/Python314/python.exe -m reports.s2ns.qualify_two_view_once
```

Der Einstieg rief genau einmal `python -m unittest
tests.test_s2ns_private_two_view -v -f` auf. Alle 24 neuen Testkoerper wurden
erreicht, Laufzeit laut Testprotokoll 9.236 Sekunden. Kein Retry und keine
Wiederholung historischer Qualifikationen. Inventar, Grenzen, Umgebung und
Quellhashes sind in `preregistration.json` vor dem Aufruf gebunden.
Die Vor-/Nachhashes stimmen ueberein, einschliesslich der NS-Versiegelung.

## Implementierter Umfang

- Eigene unveraenderliche Endpoint-/Sichtformen fuer LOWER_24 und UPPER_24.
  Beide binden Originalindizes, gemeinsame Quelle/PCM, Rohzustand,
  NJ-Projektion, Profil, Konfiguration und native Audiozeit. Der Anschluss
  partitioniert einen vorhandenen NJ-Beleg, ohne erneut zu halbieren.
- Beide vollstaendigen 9/3/8-Scans mit A-Maximum <= 0.1 und jeweils eigenem
  historischen Slow-Mittelwert sum/24 <= 0.01. Keine Toleranz, Umordnung,
  automatische Sichtwahl oder gemeinsame 48er-Mittelung.
- Generationstreue Schnittmenge vor der A/B-Aufloesung. Gleiche Slot-ID
  und gleiche Werte genuegen nicht. Ein Ersetzungsbeleg mit geaenderter
  Generation wird auch nach Reparatur des aeusseren Inventoryhashes abgewiesen.
- Reine Zulassung/Enthaltung mit Bereich und Verweisen auf gebundene
  Kandidatenherkunft; keine ergaenzten Wahrnehmungswerte oder Hypothese mit
  Wertekomplement. Fehlende Sicht bleibt regulaere unzureichende Evidenz.
- Unabhaengige Direkttraversierung, Schnittmenge und Entscheidungstabelle.
  Die technische Verifikation rechnet separat nach und akzeptiert gueltige
  Enthaltungen unabhaengig von fachlichen Erwartungen.
- Auswertung gegen jeden Einzelarm getrennt: Zielbeziehungs- und
  oeffentliche N/D/R/L, A/B, Gewinne, Verluste, falsche Anwendbarkeit und
  neue/verhinderte Fehlzulassungen. Rezeptorvariation gegen originale
  Formationswerte; PPB-Drift separat, fehlende/uneindeutige Referenzen null.

Neutrale Kontrollen bestaetigen insbesondere disjunkte Treffer ohne
Bestaetigung, gemeinsame Eindeutigkeit trotz zweier Einzelmehrdeutigkeiten,
interne A-Konflikte, oeffentliche A/B-Mehrdeutigkeit und auswertbare Enthaltung.
Ein expliziter Kontrollfall verliert die Zielbeziehung und laesst dadurch
einen anderen Kandidaten neu falsch zu. Dieser Fall wird als neue
Fehlzulassung ausgewiesen, nicht als Selektivitaetsgewinn. Gewinne und Verluste
werden nicht verrechnet; D=0 bleibt ERHALTUNG_NICHT_GEPRUEFT.

## Getrennte Arbeit und Ausgabe

Die Zaehler umfassen alle neutralen Kontrollen einschliesslich Manipulationen,
nicht einen NS-Hauptlauf. 27 Verifikatoraufrufe innerhalb des einen Testsuite-
Aufrufs enthalten auch gezielt abzuweisende Belege. Fehlgeschlagene
Verifikationskontrollen werden nicht als neuer Korpusversuch wiederholt.

| Arbeit | Aufgezeichnet | Vorabgrenze |
| --- | ---: | ---: |
| Ausfuehrung: Sichtscans | 102 | 192 |
| Ausfuehrung: Slotzeilen | 2040 | 3840 |
| Ausfuehrung: Banddifferenzen | 21216 | 28800 |
| Ausfuehrung: Kandidatengleichheitsvergleiche | 864 | 4320 |
| Zusatzverifikation: Sichtscans | 52 | 96 |
| Zusatzverifikation: Slotzeilen | 1040 | 1920 |
| Zusatzverifikation: Banddifferenzen | 11472 | 28800 |
| Zusatzverifikation: Kandidatengleichheitsvergleiche | 432 | 4320 |

Zusaetzlich genau ein neutraler historischer LOWER-Referenzscan mit eigener
vorab gebundener Obergrenze 20 Zeilen/480 Banddifferenzen/48 Gleichheitsvergleichen.
Die Werte dieses Referenzscans wurden nicht als weitere NS-Korpusmessung verwendet.
Bindungs-/Formvalidierungen sind separat vorab budgetiert und in den
Verifikationsbelegen enthalten, nicht stillschweigend als Distanzarbeit gezaehlt.

| Kanonische Form | Groesster beobachteter Wert in Byte | Gebundene Grenze |
| --- | ---: | ---: |
| Sichtscan | 13983 | 32768 |
| Ergebnisarm | 28936 | 49152 |
| Inventory | 15102 | Teil der gemeinsamen Huelle |
| Inventory plus zwei Sichtbelege | 16806 | 32768 |
| Fallauswertung | 2290 | 65536 |

Die vorab definierte aeussere JSON-Oberhuelle mit maximalen Unterbelegplaetzen
serialisierte zu **3834608 Byte**, unter der unveraenderten Gesamtgrenze
4194304 Byte. Dies ist eine konservative Byteplatzbelegung, kein realer
31-Ereignis-Beleg und keine RSS-Peakmessung. Die Vollstaendigkeit und das
Einpassen der spaeteren realen Formations-/Quellenbelege sind am noch fehlenden
Gesamtlaufanschluss zu pruefen; sie werden hier nicht vorweggenommen.

`neutral-full-capacity.json` enthaelt die tatsaechliche neutrale Vollbelegung
mit Inventory, Sichten, Primaer, Direktbaseline und technischer Verifikation:
75469 Byte, SHA-256
`19727178f67842f30fa7c8bf7b77dc9510951f653fffad38e1f88739394118a2`.

## Quellbindungen

Ergebnisdigest:
`cf4f75d03a409b0a5801b8bb2835e4b68c61008d2ee6cf03bac72cfc9d9dae7f`.

| Neue Datei | SHA-256 vor und nach Qualifikation |
| --- | --- |
| tools/_s2ns_private_two_view.py | `e249c842e2cb6d344192186c6c39cda37f0db3f0484aed2605ef929f34300b52` |
| tools/_s2ns_private_direct.py | `b3f963adcfc600d9eaa2ce188d1803a91b002a00a4c022d68b48dba062ff8acc` |
| tools/_s2ns_private_evaluation.py | `ad66f589e5924e373a3c0c00b1c4d439015e9020ab4e3fe7970f4fb69d0f46b9` |
| tests/test_s2ns_private_two_view.py | `68183c61f3e25d2685d97bba106ebb1f6491383c9231a09226c2d4e44c270b04` |
| reports/s2ns/qualify_two_view_once.py | `d21ad86409422c1bd6c82f9ec0a19c9a36a10f1144296938d826c0b0da1924ea` |
| reports/s2ns/S2NS_ZWEI_SICHTEN_QUALIFIKATIONSBINDUNG.md | `d5495d118e3147f1f38f8a5e7dee0735abde243f2835e62853f24390c36c1d9f` |

## Verbleibende Laufanschluesse

Die neutrale Qualifikation benutzt synthetische native Zustandsformen und
synthetische Herkunftsbelege, keine erzeugte NS-Memorygeschichte. Der Join
prueft Identitaet und Integritaet gegen das gebundene Inventory. Er kann
allein nicht beweisen, dass eine beliebig eingereichte Generationsbehauptung
aus einer realen Formation stammt. Der spaetere Adapter muss die komplette,
verifizierte Transaktionskette daran anbinden: CREATED/REPLACED begruenden
eine Generation, MATCHED erhaelt sie, freie/ersetzte Slots verlieren die alte
Bindung. Das ist keine neue Memoryebene und kein neuer Herkunftsrecorder.

Ebenfalls noch nicht implementiert/qualifiziert: reale NS-Materialisierung,
31-Ereignis-Einmaleinstieg, atomarer Gesamtbeleg und unabhaengige Gesamtpruefung
einschliesslich Formationsherkunft und der originalen Evaluationsreferenzen.
Eine Quellen-ID oder ein Prototypdigest darf diese Referenzwerte nicht ersetzen.

Keine NS-Payloads, Rezeptoranalysen, NJ-Projektionen, Memoryformationen,
Feld-/Runtimeausfuehrung oder reale Auswertung. Hauptgate bleibt False.
Versiegelung, historische Komponenten/Belege, fremde Aenderungen und Bootstrap
blieben unveraendert. Kein realer Nutzen, keine Objektidentitaet oder allgemeine
Fehlzulassungsfreiheit nachgewiesen.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser neutralen
Zwei-Sichten-Qualifikation und der Entscheidung ueber die verbleibende kleine
Quellen-/Formationsketten- und Gesamtlaufanbindung weiter.
