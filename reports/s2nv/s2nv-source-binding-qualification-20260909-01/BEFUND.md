# S2-NV: neutrale Quellenbindung qualifiziert

Einmaliger Aufruf `s2nv-source-binding-qualification-20260909-01`:
**16/16**, Exit-Code `0`, `S2NV_SOURCE_BINDING_QUALIFIED`. Kein Retry.

```text
C:/Python314/python.exe -m reports.s2nv.qualify_once
```

Der vorab gespeicherte [Aufrufbeleg](preregistration.json) bindet alle
16 Testnamen, Budgets, Quellhashes und die Umgebung. Das
[Testprotokoll](stderr.txt) bestaetigt alle 16 erreichten Koerper.
[Ergebnis](result.json), Ergebnisdigest:
`f1509c52733dbe9a7bee69f423fdfcb051bf9cca1dbd90121c9aef48e450ce6d`.

Geprueft sind die 20 literalen Quellenbindungen und nativen Zeiten,
getrennte Identitaeten gleicher Praefixe, neutrale Phasen-/Partialfolge,
Gruppensumme vor Gain und einmaliger Float32-Rundung, Quellenmanipulation,
geschlossene Eingabefelder, zwoelf Prognosestellen und sechs getrennte
Bewertungsbedingungen. Vollstaendige synthetische Planwurzeln und
Metadatengrenzen wurden ohne NV-Payloads geprueft. Built-in-math wurde mit
beiden Herkunftsnachweisen neutral kontrolliert; Profil- und Digestfehler
werden abgewiesen. Alle gebundenen Quellhashes blieben unveraendert.

Nur sechs Samples kleiner neutraler Gruppen wurden synthetisiert. Jeder
Testkoerper sperrte die NV-/NU-Korpus-Fensterfunktionen. Keine NV-Payloads,
Rezeptor-, NJ-, Prognose-, Fehler- oder Systemberechnung; Gate `False`.
Historische Helfer wurden nicht veraendert oder als Haupteinstieg aufgerufen.

Die Zukunftsgrenze ist hier als Metadatenvertrag geprueft, nicht als bereits
funktionsfaehiger Prognosepfad. Dessen geschlossene Eingaben, Bindung vor
Zielanalyse und Nichtwiederverwendung bereits bekannter Zukunftswerte bleiben
spaeter gesondert technisch abzusichern. Keine separate Rezeptormaterialisierung.

Umgebung: CPython 3.14.4, MSC v.1944, AMD64,
`C:/Python314/python.exe`; `math` hat `spec_origin=built-in` und bestaetigte
Built-in-Mitgliedschaft. Interpreter-, Python-DLL-, NumPy-Datei- und
Generatorbindungen stehen im Aufrufbeleg; NumPy wurde nicht importiert.
