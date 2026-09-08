# S2-NR: Laufanbindung V3, Qualifikation nicht bestanden

## Entscheidung

`NOT_QUALIFIED`: genau ein neutraler Qualifikationsaufruf, **11/12 bestanden**,
Exit-Code `1`. Kein Retry und keine nachtraegliche Code-/Testkorrektur.
Der reale NR-Hauptlauf bleibt gesperrt. Keine versiegelten NR-Payloads erzeugt,
keine NR-Rezeptormaterialisierung und keine reale 18-Ereignis-Geschichte.
Die fruehere 16/16-Typ-/Maskenqualifikation bleibt unveraendert erhalten.

## Vorab gebundener Umfang

ID: `s2nr-main-binding-qualification-20260908-01`.
Aufruf aus dem workspace:

```powershell
& C:/Python314/python.exe -m reports.s2nr.qualify_main_once
```

Der Aufruf erzeugte vor dem einzigen unittest-Unteraufruf
`preregistration.json` mit zwoelf Testnamen, Kommando, Interpreteridentitaet,
Quellhashes und Ressourcenbudgets. Die vorhandenen 16 Tests wurden nicht
wiederholt. `stderr.txt` enthaelt `Ran 12 tests` und `FAILED (failures=1)`.

Ergebnisdigest:
`5497d82ced7440682801fa2d41474ef083ea76f2b6342fa2f725d44b9614a852`.
Testprotokoll-SHA-256:
`0f87f314e46f107afa3449fb98a8efae1c89fc29f5164c470d67cfef5f491f2f`.
Alle vorab gebundenen Quellhashes sind nach dem Aufruf identisch; vollstaendige
Tabellen in `result.json`. Historische Versiegelung und Komponenten unveraendert.

## Implementierter Anschluss

- Eigene, versionierte NR-Materialisierung ueber bestehende reine Generatoren,
  einen fortgefuehrten HearingPath und NJ vor jeder Audiokontaktbildung.
- Geschlossener Einmaleinstieg, exklusive Zielverzeichnisbindung, getrennte
  Runtimearme, atomarer Gesamtbeleg, phasengenauer Fehlerabschluss und Lifecycle.
- Offline-Decodierung gespeicherter gerundeter Elternprojektionen, Quellen- und
  Zeitbezug, komplette Scanbelege, Fast-Auswahl/Updates und PPB-Relationspruefung.
- Getrennter Auswerter fuer Slotgenerationen, Herkunft, A-/B-Erhaltung,
  Verluste/Gewinne, Fehlzulassungen und verworfene Zielanwendbarkeit.
  Rezeptorvariation bezieht sich auf Formationseingaenge; Kandidatendrift bleibt
  ein anderes Merkmal. Fehlende/mehrdeutige Referenzen bleiben null.

Hauptumfang ist unveraendert 18 Ereignisse / 14 Formationen je Arm,
9792 Feldkontakte und 16 Scanbelege insgesamt. Er wurde nicht ausgefuehrt.
`run_main_once` verlangt zusaetzlich einen bestandenen neuen Qualifikationsbeleg.
Der hier gespeicherte Fehlbefund erfuellt diese Voraussetzung nicht.

## Beobachtete neutrale Ausfuehrung

Vier neutrale Ereignisse AV / Audiohinweis / AV / Audiohinweis:
vier Audiofenster, 40 Hops, 31 rollende Abschluesse, vier NJ-Projektionen,
zwei visuelle Analysen. Zwei getrennte Arme: acht Runtimeereignisse,
vier Formationen, 1536 Feldkontakte und acht Scanbelege.

Der neutrale Gesamtbeleg erreichte `RECORDING_COMPLETE` und bestand die
unabhaengige Offline-Pruefung: gleiche Feld-/Memorygeschwisterzustaende,
Baselinegleichheit, read-only Hinweise und beide Endsnapshots `CLOSED`.
Ein als Hypothese vorhergesagter spaeter Hinweis enthielt sich gueltig;
die technische Pruefung akzeptierte dies, der getrennte Auswerter nicht als
erfuellte Funktionsvorhersage. Das ist nur eine neutrale Vertragskontrolle.

Zusaetzliche absichtlich falsche Payloadbindung: `PAYLOAD_HASH_INVALID`,
Phase `PAYLOAD_HASH`, Ordinal 1, Quelle `neutral-audio`. Null Rezeptor-, NJ-
oder Runtimearbeit in diesem Fehlerfall; kompakter Fehlerbeleg akzeptiert.
Insgesamt neun Gesamtverifikator-Eintritte einschliesslich Manipulationsabwehr.

Gemessene kanonische Beleggroesse: 155507 Byte. Die synthetische vollstaendige
Maximalhuelle umfasst 2720999 Byte, unter dem vorgebundenen Nachweiswert
2730730 Byte und der unveraenderten Grenze 4194304 Byte. Kein NR-Rohpayload
gespeichert. Alle gemeldeten neutralen Zaehler liegen innerhalb der Vorbindung.

## Exakte Abbruchstelle

Test 12 veraendert die Ordinalzahl im bereits gespeicherten neutralen
Payloadfehlerbeleg. Dieser Fehlerbeleg gehoert zum in Test 05 absichtlich
geaenderten neutralen Plan:
`f89d09e54af774bd4e3bba82c88614b38eb6ca41abc0dda6f9b46d1c4a33ba00`.

Test 12 uebergibt jedoch `self.bound`, also den urspruenglichen neutralen Plan:
`fb4a93ad0e9dc1c458316ae9a9175b25903ff76d6235a19c58445837c9796bb8`.

Damit verletzt der Test bereits die vorgelagerte Ausfuehrungswurzelbindung.
Beobachtet wurde der typisierte Fehler `TOTAL_BINDING_INVALID`, erwartet war
`FAILURE_PHASE_PROGRESS_INVALID`. Die beschaedigte Evidenz wurde nicht akzeptiert.
Die vorgesehene Fortschrittskontrolle und die anschliessende zweite Assertion
in Test 12 wurden nicht erreicht. Der technische Gesamtumfang ist deshalb
trotz elf bestandener Testkoerper nicht qualifiziert.

Dieser Befund ergibt sich aus dem gespeicherten Testprotokoll, den zwei
Planbindungen und dem gelesenen Aufrufpfad. Keine erneute Verifikation,
Rezeptorausfuehrung oder Testwiederholung zur Ursachenbeschreibung.

## Grenze und naechster Vorschlag

Alle Hauptgates bleiben False. Bootstrap, fremde Aenderungen und historische
Belege bleiben ausgeschlossen. Kein NR-Funktions- oder Selektivitaetsbefund.
Die Offline-Pruefung kann aus den gespeicherten Rohwertdigests keine numerische
Halbierung rekonstruieren; sie prueft Herkunftsbindungen und die tatsaechlich
gespeicherten gerundeten Projektionen. Diese Grenze bleibt bestehen.

RUECKMELDUNG ERFORDERLICH: Engste naechste Korrektur waere, Test 12 den
tatsaechlich zu seinem Fehlerbeleg gehoerenden neutralen Plan zu uebergeben und
beide Unterkontrollen unabhaengig zu halten. Keine Produktkorrektur aus diesem
Fehler ableiten; jede neue Qualifikation benoetigt eine gesonderte Freigabe.
