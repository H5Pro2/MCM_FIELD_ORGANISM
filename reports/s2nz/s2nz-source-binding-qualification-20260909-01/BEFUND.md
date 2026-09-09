# S2-NZ: neutrale Quellen-/Stoerbindung qualifiziert

ID: `s2nz-source-binding-qualification-20260909-01`.
Genau ein vorgebundener `unittest -v -f`-Aufruf, Exit-Code 0,
**24/24 bestanden**, Status `S2NZ_SOURCE_BINDING_QUALIFIED`. Kein Retry.
Inventar, Budgets und Hashes wurden vor dem Testprozess in
[preregistration.json](preregistration.json) gespeichert. Der vollstaendige
[Testoutput](stderr.txt) erreicht alle 24 Gruppen.

## Gepruefte Grenzen

- Synthese in fester Partialfolge, Pegelmultiplikation, danach Stoeraddition
  und genau ein Float32-Pack je Sample. Kleine neutrale Samples wurden
  unabhaengig byteweise nachgerechnet; der saubere Pfad bleibt ohne Noise.
- Fester SHA-256-Stoerindex aus Seed, Fenster und lokalem Sample;
  Nenner 1024, keine Zwischenrundung, Normalisierung oder Clipping.
- 30 literale Quellen-/Zeitformen, getrennte Exaktkopien, native Indizes,
  Phasenpositionen einschliesslich Nullpartial und eindeutige Manipulationsfehler.
- Unabhaengige literale Metadatenrekonstruktion, getrennte Planwurzeln,
  18 Prognose- und zwoelf LOCAL-Stellen als noch unausgefuehrte Metadaten.
- Alle vier diagnostischen Schwerpunktstellen fest mit N=4; ausgegebene
  Empfehlungen erhalten spaeter einen separaten D-Nenner. Keine praktische
  Schwelle und kein praktischer Erfolgs- oder Robustheitsstatus.
- Ziel bleibt der naechste tatsaechlich beobachtete Halbvektor derselben
  Folge. Saubere Gegenfolgen sind weder operative Eingabe noch Rekonstruktionsziel.
- Historische NX-Freeze-Dateien nur lesend gebunden, ohne Lernrechnung oder
  Owneroeffnung. Built-in-math durch Herkunft und Modulmitgliedschaft gebunden.
- Vollstaendige synthetische Plan-/Vorregistrierungshuellen innerhalb
  65.536 Byte; falsche Budgets und Uebergroesse werden abgewiesen.

NZ-Payloads und historische Sealer waren im Test durch Aufrufsperren
ausgeschlossen. Verwendet wurden nur kleine neutrale Gruppen/Seeds sowie
synthetische Quellenhashes fuer die Metadatenhuellen. Keine Rezeptor-, NJ-,
Prognose-, Empfehlungs-, LOCAL-, Lern-, Memory-, Feld- oder Runtimeaufrufe.
Historische Tests wurden nicht wiederholt.

## Bindungen und Aussagegrenze

[result.json](result.json) bindet alle Quellhashes vor/nach dem Aufruf identisch.
Ergebnisdigest:
`73c6d30049e7aa40437a96ed768727ddf70b22ac7225b7df3e84179bcb5cbfcb`.
Datei-SHA-256 dieses Ergebnisses, anschliessend im Siegel gebunden:
`fc2dbdb0f3c104de882f145cd38dd805e8653a850f0227d6d52840376fd1e54c`.
Die qualifizierten sechs neuen Dateien und der historische NZ-Plan wurden
nach dem Test nicht geaendert. CPython 3.14.4/64 Bit; NumPy 2.4.4 nur als
Datei-/Profilidentitaet gebunden, nicht importiert.

Qualifiziert ist die rezeptorfreie Quellen- und Metadatenanbindung, nicht
die spaetere funktionale Zukunftssperre oder Empfehlungs-/LOCAL-Rechnung.
Der genehmigte einmalige Vorversiegelungsschritt folgte separat; sein
[Befund](../s2nz-source-preseal-20260909-01/BEFUND.md) ist kein Funktionslauf.
Hauptgate False, ME/MI und Systemintegration unveraendert gesperrt.
