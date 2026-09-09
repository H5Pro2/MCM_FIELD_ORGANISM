# S2-NZ: rezeptorfreie Quellenqualifikation

Vorab gebundener einziger neutraler Testaufruf:
`C:/Python314/python.exe -m reports.s2nz.qualify_once`.
ID `s2nz-source-binding-qualification-20260909-01`, 24 Testgruppen,
`unittest -v -f`, kein Retry. Inventar, Interpreterumgebung und Datei-SHA-256
werden vor dem Unterprozess veroeffentlicht, danach Hashgleichheit geprueft.

01-03: literale Quellen, native Zeiten und getrennte Exaktkopien.
04-07: SHA-256-Stoerindex/-skala, unabhaengige neutrale Byte-Nachrechnung,
Synthese -> Gain -> Noise -> genau ein Float32-Pack; sauber ohne Noise.
08-09: Grenzen, Fail-Closed ohne Clipping, Phasen-/Nullpartialpositionen.
10-13: unabhaengige vollstaendige Metadatenpruefung, Quellen-/Zeit-/Noise-
Manipulationen und feste Reihenfolge ohne Deduplication.
14-18: Praefix-/Zielmetadaten, kein sauberes Rekonstruktionsziel, Fokus N=4
bei separatem D, keine praktische Erfolgsschwelle, Budgets und Rollentrennung.
19-22: Built-in-math, unveraenderte Freeze-Belege, Kollisionen, Profilbindung.
23-24: historische Freeze-Dateien nur lesen, vollstaendige Huelle unter
65.536 Byte, verbotene Modulimporte/Aufrufe und Gates False.

Nur neutrale Gruppen (113/227/349 Hz) und neutrale Stoer-/Phasenseeds,
kleine Sampleindex-Tupel. Keine NZ-Payloads: Generator- und Sealer-Einstiege
werden gesperrt. Hoechstens 16 neutrale Sampleausgaben/64 Byte insgesamt,
24 neutrale PCM-Byte gleichzeitig einschliesslich Bytevergleichsreferenz,
48 Sinus- und 32 Stoeraufrufe; maximal 32.768 Metadaten-Digestpruefungen.
Keine Rezeptor-, NJ-, Prognose-, Empfehlungs-, LOCAL-, Lern-, Memory-, Feld-,
Kontext- oder Runtimeaufrufe. Historische Tests werden nicht erneut gestartet;
nur deren reine synthetische Freeze-Formfixture wird wiederverwendet.

Nach Bestehen ist separat genau ein freigegebener rezeptorfreier Aufruf
`C:/Python314/python.exe -m reports.s2nz.preseal_once` vorgesehen:
`s2nz-source-preseal-20260909-01`, 30 Fenster, 576.000 PCM-Byte erzeugt,
hoechstens ein 19.200-Byte-Payload gleichzeitig, 15 gestoerte Fenster mit
72.000 vorgegebenen Sample-Stoerhashes; keine Rohdatenablage. Anschliessend
eine unabhaengige read-only Bindungspruefung ohne Payloadregeneration.
Bei technischem Fehler Stopp; kein Retry oder Quellenaustausch.

Die Quellenqualifikation prueft die Rezeptrechnung und administrative
Informationsgrenzen, nicht die spaetere funktionale Zukunftssperre. Formel-
metadaten werden hier nicht ausgewertet. Hauptlauf und funktionale Anbindung
bleiben gesperrt. Die fehlende praktische Nutzungsanforderung bleibt offen.
