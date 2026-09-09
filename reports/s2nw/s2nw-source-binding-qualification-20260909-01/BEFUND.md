# S2-NW: neutrale rezeptorfreie Quellenqualifikation

Lauf-ID `s2nw-source-binding-qualification-20260909-01`.
Genau ein Aufruf `C:/Python314/python.exe -m reports.s2nw.qualify_once`
aus workspace; genau ein unittest-Prozess, kein Retry.
Ergebnis: **20/20**, Exit-Code `0`, `S2NW_SOURCE_BINDING_QUALIFIED`.
Alle 20 Testkoerper sind im gespeicherten stderr-Protokoll als `ok` erreicht.

Testinventar, Grenzen, Interpreter und Quellhashes wurden vor dem Test in
`preregistration.json` gebunden. `result.json` bestaetigt unveraenderte
Vorher-/Nachherhashes. Der NW-Plan wurde nicht geaendert.

Abgedeckt sind Quellen-/Rezeptidentitaet, native Fensterindizes, getrennte
Exaktkopien, Phasen- und Partialfolge einschliesslich Nullpartialposition,
lokale Synthesezeit, Gain vor genau einer Float32-Rundung, unveraenderliche
Spezifikationen, Profile, Digests, geschlossene Metadatenformen und Budgets.
Vier Updatepositionen, Freeze vor dem ersten Prueffenster, zwoelf getrennte
Pruefstellen und neun nachgelagerte Bedingungen sind als Metadaten geprueft.
Manipulierte Zeit-, Quellen-, Freeze- und Eingabebindungen, Testupdates und
ein vorgegebener Koeffizient werden typisiert abgewiesen.

Nur sechs neutrale Samples, keine NW-Fenster, wurden durch den Renderhelfer
erzeugt. Alle Testkoerper sperren die NW-/NU-Fenstergeneratoren. Synthetische
Payloadhash-Tokens stammen aus Metadaten, nicht aus NW-PCM. Die unabhaengige
Bundlepruefung wurde mit gesperrten Render-/Phasenhelfern erreicht.
Keine Rezeptor-, NJ-, Koeffizienten-, Prognose-, Fehler- oder Systemberechnung.

Ergebnisdigest: `f869d6f437acc9395b873fe1bf07d0fa39ae3828fdabfdff7640c3ba52d17f27`.
Quellenmodul: `84687bf236bf383772ceca6791019d8de64e3fd6598e2557b27ff59ae36fe9e1`.
Verifikator: `255d80026177b18f25195bfdac650d6e0ebd689668f1a772a12b9c15088c793d`.
Testdatei: `7159887e47de76fbbf26e02f6c895499af7fe388890003d24f77d7b81f6407b0`.
Vollstaendige weitere Hashes stehen in Vorbindung und Ergebnis.

Dies qualifiziert nur die rezeptorfreie Anbindung. Kein funktionaler Lerner,
kein Prognosecontroller und keine tatsaechliche Update-/Freeze-Ausfuehrung
sind implementiert oder qualifiziert. Hauptgate `False`; ME/MI gesperrt.
Die anschliessend autorisierte einmalige Quellenversiegelung ist separat
unter ihrer eigenen Lauf-ID dokumentiert.
