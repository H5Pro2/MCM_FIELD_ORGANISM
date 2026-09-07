# S2-NP: neutrale Abdeckungsvergleichsqualifikation nicht bestanden

## Ergebnis und einmaliger Umfang

Lauf-ID: `s2np-coverage-comparison-qualification-20260907-01`.
Status **NOT_QUALIFIED**, Exit-Code **1**. Genau ein Qualifikationsaufruf und
ein unittest-Unterprozess, kein Retry und keine nachtraegliche Codekorrektur.

Kommando aus dem workspace-Root:

```powershell
C:/Python314/python.exe -m reports.s2np.qualify_coverage_once
```

Der vorregistrierte Unteraufruf war:

```powershell
C:/Python314/python.exe -m unittest tests.test_s2np_private_coverage_comparison -v
```

22 Testgruppen ausgefuehrt; **21 bestanden**, Gruppe 22 mit einem Fehler im
Inf-Unterfall. `result.json` setzt deshalb `passed_tests=null`, nicht 22.
Die genaue Aufschluesselung steht unveraendert in `stderr.txt`.

## Lokalisierter Fehler, kein NP-Korpusbefund

`test_22_domains_subnormal_and_numeric_terms` ruft den neutralen Helper
`view(3, (inf,) * 48)` auf. Der Helper versucht zunaechst, fuer diesen
synthetischen Wert einen Payload-Digest zu bilden:

`payload_digest=c.digest(["synthetic-payload", tuple(values)])`

Die bestehende kanonische JSON-Serialisierung verwendet korrekt
`allow_nan=False` und lehnt `inf` mit `ValueError` ab. Damit wird in diesem
Unterfall weder `project_values` noch dessen erwartete typisierte
`VALUE_DOMAIN_INVALID`-Pruefung erreicht. Der Fehler liegt im Aufbau der
neutralen Pruefeingabe vor dem getesteten Produkteinstieg. Daraus folgt
keine Akzeptanz ungueltiger Rezeptorwerte und kein Abdeckungsbefund.

Die NaN-Pruefung an einem bestehenden `ViewValues`-Objekt in Gruppe 9 bestand.
Sie ersetzt nicht den fehlgeschlagenen Inf-Unterfall. Die gesamte
Qualifikation bleibt nicht bestanden. Keine Lockerung der JSON-Kanonisierung,
keine pauschale Exception-Akzeptanz und keine Produktkorrektur ausgefuehrt.

## Vorbereitete Komponenten und beobachtete Grenzen

Drei private Module trennen Teilwertvergleich, unabhaengige Direktnachrechnung
und nachgelagerte Auswertung. Drei feste Sichten und Bedingungen, historische
`sum(...)/len(I)`-Arithmetik, numerische Termwerte mit Originalindizes und
getrennte N/D/R/L-Nenner sind implementiert. Keine Memory- oder A/B-Entscheidung
wird daraus abgeleitet; die Panelbefunde sind reine Anwendbarkeitsdiagnosen.

Der neutrale Vollinventartest bestaetigte je Implementierung 360 Panelbefunde,
360 regelgebundene Beziehungszeilen und 3840 Banddifferenzen. Mit den kleinen
Einzelkontrollen wurden im gesamten Testaufruf **8736** synthetische
Banddifferenzen berechnet, unter dem vorab gebundenen Qualifikationslimit 16384.
Das spaetere Korpuslimit bleibt **7680 insgesamt**, unveraendert.

Die konkrete kanonische synthetische Gesamtausgabe betrug **1112286 Byte**,
einschliesslich beider Termbelege, Projektionen, Verifikation, Auswertung,
131072 Byte Materialisatreserve und 65536 Byte Metadatenreserve. Grenze:
2097152 Byte. Keine allgemeine Worst-case- oder Prozesspeakbehauptung;
der spaetere konkrete Gesamtbeleg bleibt vor Veroeffentlichung zu pruefen.

Technische Verifikation akzeptierte neutrale gueltige Leer-/Mehrdeutigkeits-
befunde unabhaengig von Sollrelationen. Sie wiederholt keine Banddifferenzen,
sondern prueft Bindungen, Termstruktur, Aggregate, Bedingungen und
kanonische Gleichheit gegen die unabhaengige Direktnachrechnung.

## Beleg- und Quellbindungen

- Vorregistrierungsdatei SHA-256:
  `517d139e93ca777369d22346b4463e16ea1d20e97d8a0a571bbfee6014ef5767`.
- Ergebnisdatei SHA-256:
  `166af4647b6e7e224da2a8c642379cba59cd18a734960f62651a8d1afb0e1f80`.
- Kanonischer Ergebnisdigest:
  `2a183e67f21782fec7bdc63e58a6080a49a6d86d90a10fee3681578a55bf2b29`.
- Vergleichsmodul SHA-256:
  `3b8824de8d0ca391a8312d803896544029b2dcbfdfa39e21f7190f81d719ecd8`.
- Direktbaseline SHA-256:
  `2bb83762ff674a26e9df4f36bd5154fff0a15e1dfa20c13f15fc33867d91c495`.
- Auswerter SHA-256:
  `50e4766c2b6f6bec4ba926767a82a18039ffd73046a0a9626c813f75f462b2a9`.
- Testdatei SHA-256:
  `09d49e11bcf8dbbbdc7e71a9f69c6764f1710e373cb4e766c4e326694833fa86`.

Vollstaendige Hashlisten vor/nach dem Aufruf, Testinventar, Interpreterbindung
und Budgets stehen in `preregistration.json` und `result.json`. Null geaenderte
Bindungen. Historische NP-Artefakte wurden ausschliesslich fuer Dateihashes
gelesen, nicht als Werte geladen oder verglichen. Die 576 realen NP-Werte
wurden in dieser Qualifikation nicht verwendet.

Payloadgenerationen, Rezeptor-, NJ-, Memory-, Feld-, Kontext- und Runtime-
aufrufe: jeweils **0**. Gates bleiben `False`. Historische Belege, fremde
Aenderungen und Bootstrap unberuehrt. Kein realer Vergleich freigegeben.

## Rueckmeldung an den Analysten

**STOPP fuer die Qualifikation. RUECKMELDUNG ERFORDERLICH:** Engster naechster
Schritt waere eine ausdruecklich freigegebene Korrektur allein der neutralen
Inf-Eingabekonstruktion, sodass unveraenderliche gueltige Herkunftsmetadaten
den ungueltigen numerischen Testwert bis zur Produktpruefung gelangen lassen.
Keine allgemeine Exception-Erweiterung. Erst nach Freigabe ein neuer neutraler
Einmalaufruf; dieser Fehlbeleg bleibt unveraendert.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses lokalisierten
Testhelperfehlers weiter. Die reale Abdeckungsauswertung bleibt gesperrt.
