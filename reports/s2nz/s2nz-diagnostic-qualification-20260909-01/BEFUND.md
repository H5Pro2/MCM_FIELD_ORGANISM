# S2-NZ: diagnostische Laufanbindung neutral qualifiziert

ID `s2nz-diagnostic-qualification-20260909-01`.
Genau ein vorgebundener Testaufruf: **24/24 bestanden**, Exit-Code 0,
Status `S2NZ_DIAGNOSTIC_QUALIFIED`. Kein Retry. Alle Testgruppen wurden
erreicht; [Inventar und Vorbindung](preregistration.json),
[vollstaendiger Testoutput](stderr.txt) und [Ergebnis](result.json)
bleiben getrennte Belege. Keine NZ-Payloadverarbeitung oder Hauptausfuehrung.

## Anschluss

Der neue private Einstieg `tools/_s2nz_private_diagnostic_run.py` verbindet
die unveraenderte NZ-Vorversiegelung mit der vorhandenen NY-Komposition.
NY-Arithmetik, Direktrechnung, PrefixStream, FrozenInputs und der NW/NV-
AudioReader bleiben unveraendert. Kein historischer Haupteinstieg wird
aufgerufen oder umetikettiert. Der Original-NY-Kompositionsbeleg bleibt
mit eigenem Schema/Digest als `core` in der expliziten NZ-Huelle erhalten.

Eigene Quellen-/Versionsbindung, Gate, atomarer Gesamtabschluss und
Dateiverifikation verwenden die vorhandenen Belegwege. Der neue getrennte
NZ-Auswerter beschreibt absolute Fehler, Gewinne, Verluste und Abdeckung,
ohne die historischen NY-Erfolgskriterien zu uebernehmen. Keine neue
Vorhersagevorschrift, Lernmechanik oder Recorderplattform.

## Tatsaechlich gepruefte Grenzen

- Alle Prognosen beider Rechnungen, LOCAL und Empfehlung sind vor dem
  Ziel-Reader gebunden. Fehlende oder geaenderte Bindungen sperren den Zugriff.
- Fremde Folge, veraltete Zielstelle, falsche Freeze-Bindung und manipulierter
  vergangener Fehler werden unabhaengig typisiert abgewiesen. Identische
  funktionale Praefixe liefern trotz anderer Kennungen identische Prognosen.
- Saubere Gegenstuecke sind weder funktionaler Eingang noch Ersatz-Ziel.
  Fremde Zielbelege werden abgewiesen; gespeicherte Fehler beziehen sich
  auf den eigenen tatsaechlich beobachteten Zielvektor der jeweiligen Folge.
- Jede Folge beginnt mit frischem Praefix und leerer Fehlerhistorie.
  Freeze-Fixtures bleiben unveraendert; Manipulation wird vor dem Reader
  erkannt, die Lesebindung wird geschlossen. Keine Lernupdates oder Owner.
- Bei fehlender Evidenz und Gleichstand bleiben Empfehlung und zugehoeriger
  MAE aus; keine Ersatzprognose, Nullfehlerwertung oder Ersetzung durch LOCAL.
- Alle vier Schwerpunktstellen bleiben bei teilweiser Enthaltung mit
  **N=4/D=2** und bei vollstaendiger Enthaltung mit **N=4/D=0** erhalten.
  D=0 bleibt NUTZEN_NICHT_GEPRUEFT. Die festen Historien behalten eigene Nenner.
- Eine weitere vollstaendige synthetische Folge hat an allen zwoelf LOCAL-
  Stellen negative Unterschiede beider festen Historien und der Empfehlung
  gegen LOCAL. Sie wird technisch verifiziert und regulaer diagnostisch
  ausgewertet. NEXT_BEST trotz Verlust gegen LOCAL/PERSIST ist separat geprueft.
- Direkte Verifikation funktioniert mit gesperrten primaeren Prognose-,
  LOCAL-, Score- und Empfehlungshelfern. Fehlende oder fremde Zielbelege
  werden abgewiesen. Nullnenner und ungeclippte Extrapolation bleiben gleich.
- Quellenzeit-/Profilfehler, Materialisierungsabbruch, phasengenauer
  Fehlerbeleg ohne fachliche Teilresultate, atomarer Schreibkonflikt,
  Ressourcenlimits und Auswertungssperre vor technischer Pruefung sind erreicht.

Diese Zahlen bezeichnen ausschliesslich neutrale Kontrollfixtures, keine
NZ-Ergebnisse. Drei vollstaendige synthetische Gesamtfolgen und zwei
Fehlerabschluesse verwenden keine versiegelten Rezeptorwerte. Der echte
Adaptertest erzeugte ausschliesslich fuenf neutrale Null-PCM-Fenster:
**fuenf Analysen und fuenf NJ-Projektionen**, 96.000 PCM-Byte insgesamt,
hoechstens ein 19.200-Byte-Fenster gleichzeitig. Dabei lag die Prognosebindung
bereits vor dem neutralen Generatoraufruf. Keine Rohpayloadablage.

## Vollstaendige Huelle und Ressourcen

[neutral-envelope.json](neutral-envelope.json) umfasst **609.371 Byte** von
maximal 2.097.152 Byte: NZ-Bindung, Original-NY-Core, vollstaendige neutrale
Quellen-/Rezeptmetadaten, Roh-/Halbwerte, Prognosen, Fehler, Freeze-Fixtures
und Codehashes. Kein Platzhalter-Huellennachweis.
[neutral-evaluation.json](neutral-evaluation.json): **14.605 Byte** von
maximal 262.144 Byte. Die Verifikation wurde ebenfalls innerhalb ihrer
eigenen 262.144-Byte-Grenze geprueft. Quellen/NZ-Plan und Groessenlimits
wurden nicht veraendert.

Aktive NY-Rechnung und Offline-Nachrechnung behalten ihre getrennten
vorgebundenen Arbeitslimits. Die Diagnose ergaenzt 24 direkte feste
H1/H2-Gewinndifferenzen gegen LOCAL aus vorhandenen MAE; sonstige Gewinne
werden aus den NY-Belegen uebernommen. Hoechstens 96 verschiedene
WIN/TIE/LOSS-Beziehungen und 18 Empfehlungsurteile; der gespeicherte neutrale
Beleg nutzt 92 bzw. 18. Gruppensummen zaehlen bereits vorhandene Statusformen,
keine wiederholte numerische Klassifikation. Null Relevanzvergleiche,
keine praktische Schwelle, kein praktischer Erfolgs- oder Robustheitsstatus.

## Hashes und Grenzen

Alle Quellhashes vor/nach dem Testaufruf stimmen ueberein. Historische
NY-/NW-/NX-Komponenten, Freeze-Dateien und NZ-Versiegelung sind dateigebunden
und unveraendert. Keine historischen Tests oder Lernketten wiederholt.

| Beleg | Digest / SHA-256 |
| --- | --- |
| Qualifikation result_digest | 5246417a82e85008e443052ba5f6e1c671e7b9258dd5b4266fbc38cdf45c5486 |
| Neutrale Gesamtdatei SHA-256 | a639446f065e1dd22b8174c4ed1e27b383882cc4e0d9e5a21910546114ac5a07 |
| NZ-Laufanschluss SHA-256 | f69430ba65ad2d73282ee90341c16db65893493c1a82d0bf15a6932b349e91c5 |
| NZ-Auswerter SHA-256 | 7ddeb3f70511e12da37756e3d121f307445f070b94585d6e305a2dc883f56bab |
| NZ-Testdatei SHA-256 | 5b35a38b41d0580460656442c1ea33680e726920c1b039c9cdaf55866a5fbd02 |

Die kontrollierte Aufrufgrenze ist keine Sandbox gegen beliebigen fremden
Pythoncode. Offline werden gespeicherte Werte, Arithmetik, Halbierungen
und Bindungsketten geprueft, nicht allein durch Digests die historische
CPU-Aufrufordnung bewiesen. Die Quellen-/Zeitbindung im echten NZ-Strom
und dessen Rezeptorgueltigkeit bleiben erst im separat freizugebenden Lauf
zu pruefen. Die neutralen Ergebnisse belegen keinen Stoerungs- oder
Vorhersagenutzen und keine praktische Robustheit.

NZ-Payloads: **0**. NZ-Hauptlaeufe: **0**. Keine Owneroeffnung, Lernupdates,
Memory-, Feld- oder Runtimeintegration. Alle beteiligten Gates danach False;
ME/MI unveraendert gesperrt. Bootstrap und fremde Aenderungen unberuehrt.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses
Qualifikationsbefunds und der separaten Entscheidung ueber den einmaligen
NZ-Diagnoselauf weiter.
