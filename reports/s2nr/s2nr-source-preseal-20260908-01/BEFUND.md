# S2-NR: rezeptorfreie Vorversiegelung

2026-09-08. Lauf-ID: s2nr-source-preseal-20260908-01.
Ausgangscommit c4c848b. Genau ein Aufruf nach bestandener neutraler 12/12-
Qualifikation, neues Verzeichnis, kein Retry:

```text
C:/Python314/python.exe -m reports.s2nr.preseal_once
```

Exit-Code 0. S2NR_SOURCES_PRESEALED, anschliessend genau eine unabhaengige
read-only Pruefung: S2NR_PRESEAL_BINDINGS_VALID. Keine Wiederholung von
Quellengenerierung oder historischen Haupteinstiegen.

## Beobachtete Quellen- und Ereignisbindung

- 17/17 Quellen einmal erzeugt: sechs PCM-Fenster, elf volle RGB8-Frames.
- PCM: je 4.800 Samples, 48.000 Hz, Mono PCM_F32LE, 19.200 Byte;
  insgesamt 115.200 Byte. RGB: je 1920x1080x3, 6.220.800 Byte;
  insgesamt 68.428.800 Byte durch den Generator, keine Rohablage.
- Jeweils hoechstens ein vollstaendiger Payload je Modalitaet; Hashbildung
  per memoryview ohne Vollpayloadkopie und Freigabe vor der naechsten Quelle.
  Kein neuer Prozesspeaknachweis; Budget bezieht sich auf lebende Payloads.
- Die literale 18-Ereignis-Folge ist versiegelt, nicht ausgefuehrt:
  14 AV-Formationen und vier auditive Hinweise e02/e04/e17/e18.
- Beide festen Masken mit Originalindizes und Komplementen sowie getrennte
  native Audio-/Videozeit und gemeinsame Felduhr s2nr-transfer-field-clock
  sind gebunden. Keine Umordnung oder Verschiebung von Fenstern.
- Rollen, Zielzuordnung, Vorhersagen und Erhaltungsbewertung liegen nur in
  evaluation-plan.json. Formation, Support oder Abruf werden nicht als
  erfolgreiche Startbedingung vorausgesetzt.

Die einzige Payloadkollision ist die beabsichtigte Exaktkopie nr-a01/nr-a03:
`f9246b632585f6c0275bfd285796d52d01953b035002cbfe6ef7da643207eac0`.
Keine weiteren Kollisionen; keine Quelle ersetzt oder dedupliziert.
Getrennte Quelldigests einschliesslich eigener Ereignis-/Zeitbindungen:

- nr-a01: `74b3fca052577c3f86965380eb272b183f106fb7b88a5a649b797d4ed13c09b4`
- nr-a03: `e077c7fe1f80f484ac9141b6b5755f0dfb98bb85cd3b8214dbd72db1994e0015`

Alle 17 Rezept-, Payload- und Quelldigests stehen unverkuerzt in
[execution-plan.json](execution-plan.json), zusammen mit den 18 Ereignissen.

## Bindungsbelege

| Beleg | Inhalt-/Wurzeldigest | Datei-SHA-256 |
| --- | --- | --- |
| execution-plan.json | 3471deefa0e1eda1f1b2b4b28a6100494bdc5bece758ab0a4a466d175704295a | 097fbae1667ee47288aad0a27634e94da93f6caf0863a2b9bdf2bd4f9c19437a |
| evaluation-plan.json | eed797d737589a235700fe174d563ef428a1d938edf696511e87a3140dcd74fb | 819e6292d5d77f90de2572457e258d0ffd06ed0d49667c2f7ba5247768b7de87 |
| seal.json | 147897b2fa4f8f91c37b65cd8de2215e2d67c9270fe9fc805163f2e5e5599a31 | 33087a1b0714a8c6dff847471f8d15cfc6935d590f87f13a4f511f663ea672c3 |
| verification.json | fa0b98a23a4ae7d6fbd04f7bff223b41ef57a462ed5e0303b30e277b82a1ae14 | e24233a82140eba02d2ab97bc87c1c4c740abb34d7462e40d54f2f7a5b6c495e |

Vertrag unveraendert, SHA-256:
`c8fde31c841fab4a61cf1166a35084d39dda53738ec8d36e7364807bb3ec7791`.
Alle Generator-/Komponentenhashes vor/nach identisch und an die neutrale
Qualifikation gebunden. Ausfuehrungswurzel 35.731 Byte, Evaluationswurzel
1.244 Byte, Vorregistrierung 25.870 Byte, Siegel 6.868 Byte,
Pruefbeleg 1.437 Byte: zusammen 71.150 Byte, deutlich unter 4.194.304 Byte;
jeder Metadatenbeleg unter 65.536 Byte.

CPython 3.14.4, MSC v.1944 64 bit AMD64, C:/Python314/python.exe;
Interpreterhash 7ca24f26d6e3f463419ee4f537ddd3acd312c38fe45e678cce08572f26a8bd1a.
math: spec.origin=built-in UND builtin_membership=true, keine erfundene
Moduldatei. Python-DLLs und NumPy 2.4.4 samt geladenem Paketpfad,
Initialisierungsdatei und Binaerdateien sind gehasht gebunden.
NumPy wurde ausschliesslich fuer die reine RGB-Erzeugung verwendet.

Rezeptor-/NJ-Metadaten nur gelesen, nicht ausgefuehrt:
Rohprofildigest 5c6b2b19281a44023497b435a96b1051905af4bbac493cae7e699ea1320392c7;
Halbprofildigest 4a56de2f630055816533ecb45cdef5662157993bc1192023d01cf29e92247c9f.
Neue Skala, halbierte Audiogrenzen und feste Fast-Rangumrechnung sind
explizit getrennt gebunden; historische Profile/Defaults unveraendert.

## Pruefgrenze und Nichtnachweis

[verification.json](verification.json) prueft Wurzeln, gespeicherte Hashes,
Code-/Umgebungsidentitaeten, Quellen-/Ereignisformen, Zeitfenster, Masken,
Profilmetadaten, Exaktkopien, Kollisionstabellen und Zaehler. Alle vier
geprueften Eingabedateien blieben bytegleich. Keine Payloadregeneration;
die Pruefung bestaetigt die Bindung der gespeicherten Payloadhashes, nicht
eine zweite unabhaengige Erzeugung der zugrunde liegenden Bytes.

Rezeptor-, NJ-, Distanz-, Scan-, Memory-, Kontext-, Feld- und Runtimeaufrufe:
jeweils null. Keine Rezeptorwerte, Treffer oder Funktionsauswertung.
Die 18 Ereignisse sind nur spezifiziert. Vorversiegelung ist weder ein
Normalformnachweis der Rezeptorausgabe noch ein Selektivitaetsgewinn.
Historische Befunde einschliesslich S2-NQ bleiben unveraendert.

Alle Hauptgates blieben False. Runtime-/Hypothesenanbindung,
Rezeptormaterialisierung und Hauptlauf bleiben separat gesperrt.
Fremde Aenderungen und Bootstrap sind nicht Bestandteil dieser Arbeit.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser
Vorversiegelung und der getrennten Freigabe des minimalen
Runtime-/Hypothesenanschlusses weiter.
