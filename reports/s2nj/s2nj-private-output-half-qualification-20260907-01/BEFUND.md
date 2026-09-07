# S2-NJ: private Ausgangsprojektion neutral qualifiziert

Qualifikations-ID: `s2nj-private-output-half-qualification-20260907-01`.
Status: `S2NJ_PRIVATE_OUTPUT_PROJECTION_QUALIFIED`.
Ausgangsstand: `7fe79c2`. Keine Produktionsumstellung und keine NH-Wiederholung.

## Umsetzung und Aufruf

Ein privates Modul und eine fokussierte Testdatei; bestehende Rezeptoren,
Defaultadapter, Memory-, Feld- und Runtimekomponenten bleiben unveraendert.
Vorabbindung: [QUALIFIKATIONSBINDUNG.md](../QUALIFIKATIONSBINDUNG.md).

`project_auditory_half_v1` prueft das gebundene alte Hann-/FFT-/48-Band-Profil
und multipliziert die unveraenderte Spektralausgabe komponentenweise genau
einmal mit `0.5`. Erst nach vollstaendiger Validierung aller Werte als endlich
und `0<=z<=1` entsteht `HalfScaleAuditory48V1`. Fehler sind typisiert; keine
Teilprojektion. Eigener unveraenderlicher Typ, eigene Geometrie und explizite
Profil-/Quellzustands-/Quellwert-/Projektionsdigests. Der neue Typ wird als
Eingang einer weiteren Halbierung abgewiesen. Kein Clipping oder Fallback.

Genau einmal aus dem Workspace-Root:

```powershell
& C:/Python314/python.exe -B -m reports.s2nj.qualify_once
```

Der Aufrufer band vorab Testinventar, acht literale Quellenrezepte, Rechenfolge,
Kommando, Umgebungsidentitaet und Dateihashes. Anschliessend genau ein
`unittest`-Subprozess mit 16 Testkoerpern und Fail-fast, keine Wiederholung.
Ergebnis: **16/16**, Exit-Code **0**, **OK**. CPython 3.14.4, NumPy 2.4.4;
vollstaendige Interpreter-/Binarmodulidentitaeten in `preregistration.json`.

## 1. Analytische Aussage

Der [S2-NI-Vertrag](../../../docs/S2NI_STATISCHER_AUDITIVER_REZEPTOR_KONTAKT_SKALIERUNGSVERTRAG.md)
leitet fuer das ideale reelle Hann-/FFT-Profil quellenunabhaengig
`E_b <= sqrt(14400/4799) < 2` ab. Daraus folgt dort `0.5*E_b < 1`.
Diese Herleitung wurde nicht aus einem Korpusmaximum gewonnen und durch
die heutige Qualifikation weder ersetzt noch zu einer Maschinengarantie erweitert.

## 2. Beobachtete lokale Implementierung

Acht neue neutrale PCM-Fenster, acht direkte Aufrufe des unveraenderten
`LogSpectralReceptor.analyze`, **384 reale Rezeptorwerte** und 384 zugehoerige
skalierte Werte. Alle acht Projektionen sind normalformgueltig und stimmen
komponentenweise bitgenau mit `float(Fraction.from_float(E)/2)` ueberein.

| Fester neutraler Fall | Rohmaximum | Ausgangsmaximum |
| --- | ---: | ---: |
| Null | 0.0 | 0.0 |
| konstant +1 | 1.7372237017082406e-05 | 8.686118508541203e-06 |
| konstant -1 | 1.7372237017082406e-05 | 8.686118508541203e-06 |
| alternierend +1/-1 | 8.141646101989034e-09 | 4.070823050994517e-09 |
| Impuls am Fensterrand | 0.0 | 0.0 |
| Impuls in Fenstermitte | 0.009610334282056713 | 0.0048051671410283565 |
| feste Mischung eins | 0.23984126036947234 | 0.11992063018473617 |
| feste Mischung zwei | 0.322069648501795 | 0.1610348242508975 |

Die Tabelle ist aus den gespeicherten Beobachtungen uebernommen; keine
Nachmessung. Alle Roh-/Ausgangswerte, Binary64-Hexdarstellungen, PCM-Digests,
Quellzustandsdigests und Projektionen stehen in `observations.json`.
Keine PCM-Rohdaten gespeichert. Keine NH-Quelle erzeugt oder analysiert.

Weitere neutrale Kontrollen bestaetigten Profil-, Typ-, Carrier-, Zeit- und
Digestabweisung, unveraenderte Quellen, unveraenderliche Ausgaben und
fehlende Integrationsimporte. NaN/Inf, negative Rohwerte und Ausgangswerte
ueber Eins werden abgewiesen. Synthetisch gilt inklusive: Rohwert `2.0`
ergibt `1.0`; der naechstgroessere Binary64-Rohwert wird abgewiesen, nicht
gesaettigt. Diese synthetischen Rohwerte sind **keine** durch PCM erzeugten
Schrankenfaelle und kein Nachweis erreichbarer Rezeptormaxima.

Unterlauf/Subnormale, lokal beobachtet:

- kleinster positiver Binary64-Subnormalwert mal 0.5 rundet zu Null;
  der betroffene Index wird als Unterlauf gebunden;
- dessen doppelter Wert halbiert sich zum kleinsten Subnormalwert;
- dessen dreifacher Wert rundet nach Halbierung zum doppelten Subnormalwert;
- der kleinste normale Wert halbiert sich zu einem Subnormalwert;
- negative Null bleibt negative Null; kein Flush-to-zero oder zusaetzliches
  dezimales Runden im Adapter.

Der Erhalt aller positiven Eingangsenergien oder allgemeine Invertierbarkeit
wird deshalb nicht behauptet. Die Ausgabe haelt das tatsaechlich gerundete
Ergebnis sowie Subnormal-/Unterlaufindizes getrennt fest.

## 3. Nicht nachgewiesen

**Keine universelle Gleitkommagarantie** fuer alle gueltigen PCM-Eingaenge und
die gesamte Hann-/FFT-/Filterbankrechnung. Die endliche Qualifikation ist kein
Ersatz fuer einen solchen Fehlernachweis. Die realen neutralen Maxima liegen
hier deutlich unter der analytischen Schranke; insbesondere wurde kein
rezeptorseitig erzeugter Extremwert nahe dieser Schranke nachgewiesen.
Die Ausgabepruefung bleibt bei jeder Projektion zwingend fail-closed.

Auch die Profildeklaration beweist nicht die Herkunft absichtlich falsch
umetikettierter Rohobjekte. Qualifiziert ist die vorgesehene explizite,
typisierte Bindung, keine neue allgemeine Authentizitaetsinfrastruktur.

## Ressourcen und Integritaet

- Groesste gespeicherte reale Einzelprojektion: **3.217 Byte**, Grenze 16.384.
- Beobachtungsdatei: **50.197 Byte**, Grenze 131.072 je JSON-Artefakt.
- **17/17** gebundene Dateihashes vor/nach unveraendert.
- Produkt-SHA-256: `e052cc76cf4c9678e11673d95390dea21634bba8082187567a760faaaf4904e5`.
- Test-SHA-256: `f7039dc62e958b165c3bbb7daa32381993f3e84045a1e1073dc7b118398311e5`.
- Aufrufer-SHA-256: `fc34e94c7e217a3263ccc4a3ded691f6ecaba2e4e18f25fcc68a015c426be3ac`.
- Neue Profilbindung: `4a56de2f630055816533ecb45cdef5662157993bc1192023d01cf29e92247c9f`.
- Bindung der unskalierten Eingangssemantik: `5c6b2b19281a44023497b435a96b1051905af4bbac493cae7e699ea1320392c7`.
- Ergebnisdigest: `eb6aeb8672c653f8438ff6f8e60c52dc33c580ac667d7e2ab313eaa50a35236d`.

## Abschlussgrenze

Private Ausgangsprojektion neutral qualifiziert; noch keine Feld-, Memory-
oder Runtimeintegration. Kein Feld-/Memory-/Kontext-/Runtimeaufruf, keine
Schwellenaenderung und keine Hypothesenanwendung. Beide Hauptgates bleiben
`False`. S2-NH bleibt `NOT_EVALUABLE`; S2-NG und historische Belege bleiben
unveraendert gueltig. Fremde Aenderungen und Bootstrap bleiben ausgeschlossen.

WEITER: Am besten geht es jetzt mit der Analystenentscheidung zur Bedeutung
der Matchinggrenzen in der neuen Ausgangsskala weiter, bevor irgendeine
Integration oder Uebernahme von `0.2` und `0.02` freigegeben wird.
