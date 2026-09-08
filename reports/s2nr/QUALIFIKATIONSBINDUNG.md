# S2-NR: rezeptorfreie Quellenbindung, neutrale Qualifikation

Vor dem einzigen Testaufruf festgelegt, 2026-09-08. Ausgangscommit c4c848b.
Vertrag: docs/S2NR_PRIVATER_RUNTIME_ANBINDUNGSPLAN_VERTEILTE_AUDIOBANDSICHT.md,
SHA-256 c8fde31c841fab4a61cf1166a35084d39dda53738ec8d36e7364807bb3ec7791.
Keine Aenderung des Vertrags oder historischer Komponenten.

## Ein Aufruf und festes Inventar

Qualifikations-ID: s2nr-source-binding-qualification-20260908-01.
Aufruf aus workspace: C:/Python314/python.exe -m reports.s2nr.qualify_once.
Dieser erzeugt vor genau einem unittest-Unterprozess eine Vorregistrierung
mit allen Testnamen, Quellenhashes, Binaer-/Interpreteridentitaeten und Budgets.
Kein Retry. Bei Nichtbestehen bleibt die Quellenproduktion geschlossen.

Zwoelf Testkoerper, Unterfaelle jeweils unabhaengig:

1. Sechs literale Audio- und elf RGB-Rezepte; getrennte Exaktquellen.
2. Unveraenderliche Spezifikation, Quellen-ID und kanonisches Rezept.
3. Neutrale PCM-Partialfolge, Phase und einmalige Float32-Rundung.
4. Neutrales RGB8-Vollformat, Bitfolge, Zellgeometrie und Schreibschutz.
5. 18 literale Ereignisse, Quellenvorkommen und vier Hinweispositionen.
6. Native Audio-/Videozeiten und getrennte gemeinsame Fenster.
7. Zwei feste Masken und ihre Komplemente; Halbprofil nur als Metadaten.
8. Getrennte Planwurzeln, gueltige synthetische Belege, Unveraenderlichkeit.
9. Quellen-ID-, Laengen- und Rezeptdigestmanipulationen.
10. Zeit-, Masken- und Evaluationsmanipulationen.
11. Built-in-math nur mit origin und bestaetigter Built-in-Mitgliedschaft.
12. Metadatengrenze, exklusives Schreiben, Uebergroesse, Importsperre, Gate.

## Neutrales Budget und Grenzen

Keine NR-Payloads. NR-Rezept-/Ereignismetadaten sind erlaubt; Planpruefungen
nutzen synthetische Payloadhashes. Genau ein neutraler PCM-Generatoraufruf
mit 16 Samples (64 Byte) plus unabhaengige skalare Byte-Referenz; genau ein
neutraler RGB-Aufruf mit eigenem Seed und einem Frame von 6.220.800 Byte.
Kein Rezeptor, NJ, Kontakt, Scan, Memory, Feld oder Runtimeimport/-aufruf.
Keine Distanzberechnung, keine fachliche Auswertung. MAIN_GATE bleibt False.
Je Metadatenobjekt hoechstens 65.536 Byte, Vorversiegelungsbelege zusammen
unter 4.194.304 Byte. Kein neuer Prozesspeakanspruch.

Der Sealer nutzt unveraenderte NP/ND-Kanonisierung, Identitaets- und
Publikationshelfer. Nur die reinen, dateigehashten NC-pcm_bytes- und
NH-rgb_recipe/rgb_payload-Definitionen werden per AST uebernommen; kein
historischer Haupteinstieg oder Rezeptormodul wird importiert/ausgefuehrt.

## Erst nach Bestehen

Genau ein Aufruf C:/Python314/python.exe -m reports.s2nr.preseal_once unter
s2nr-source-preseal-20260908-01. Das Verzeichnis muss unbenutzt sein.
Sechs PCM- und elf RGB-Payloads, in Quellenreihenfolge, keine Deduplikation.
Alle Payloads werden nur gehasht und unmittelbar freigegeben; hoechstens
ein PCM-Fenster (19.200 Byte) und ein RGB-Frame (6.220.800 Byte) gleichzeitig.
Keine Rohablage. Exaktkopie a01/a03 mit getrennten Herkunftsbindungen;
andere Hashkollisionen berichten, keine Ersatzquelle.

Danach genau ein unabhaengiger read-only Verifikationsaufruf. Er prueft
gespeicherte Wurzel-/Dateihashes, Zeitformen, Masken, Code, Profile,
Generator-/Interpreterbindung und Zaehler. Er erzeugt keine Payloads und
kann deren Bytes deshalb nicht erneut unabhaengig nachrechnen. Er nutzt
gemeinsame kanonische Spezifikationen, aber eigene Hash-/Zeit-/Wurzelchecks.
Die Pruefung ist keine Rezeptor- oder Funktionsqualifikation.
