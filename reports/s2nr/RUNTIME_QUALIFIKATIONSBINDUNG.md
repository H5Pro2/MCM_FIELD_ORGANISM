# S2-NR: einmalige neutrale Runtime-/Hypothesenqualifikation

2026-09-08, Ausgangscommit 39fd18d. Keine NR-Payloads und keine Hauptgeschichte.
Die 17 vorversiegelten Quellen, beide Planwurzeln und alle historischen
Belege bleiben bytegleich. Keine neue Quellenversiegelung.

## Anschluss

Einzige historische Codeanschlussaenderung: S2-MR erhaelt eine zweite,
exakte Configform MaskedMCMRuntimeConfig336V2 und den exakten Typ
MaskedAudioHypothesisV2. V1-Configpayload, Digestbildung, Defaults und
historische visuelle/auditive Typakzeptanz bleiben gleich. V2 akzeptiert
keinen umetikettierten KZ-Typ; V1 akzeptiert keinen neuen Maskentyp.
Die Erweiterung aendert den MR-Dateihash. Die vorversiegelte historische
MR-Codeidentitaet wird NICHT ersetzt oder als aktueller Hash ausgegeben.
Quellenplan und historische Codebindung bleiben Herkunftsbeleg; die neue
Anschlussidentitaet wird separat in dieser Qualifikation gebunden.

NN liefert einmal halbierte neutrale Eingaben. NR validiert den gemeinsamen
Elternbeleg und setzt je Arm nur eine neue Cueoperation ein. Feldpayload,
Quellenbeleg und drei LM-Projektionsdigests bleiben gemeinsam. Die eigene
Packpruefung bindet diese an Cue, Originalindizes, PCM-/NJ-Elternidentitaet,
Wertedigest und Zeiten. Ausschliesslich 24 Cuewerte gelangen zu NQ/direct;
die Feldprojektion darf weiterhin die echten 48 Audiowerte besitzen.

NGs Branchbeobachtung, Zustandspool und Instanzpruefung werden wiederverwendet;
LM, LO-Feldadapter, Koordinator, NQ/direct und alle Kerne bleiben unveraendert.
Kein historischer Haupteinstieg, kein Monkeypatching im Produktpfad.
Ein kleiner eigener NR-Kompositionsadapter und Offline-Verifikator sind
notwendig, da historische NG-Eingabe-/Hypothesentypen maskenfest sind.

Der neue Einstieg bleibt vorerst strikt NEUTRAL, maximal sechs Ereignisse
und zwei Formationen pro Arm. MAIN_GATE bleibt False; kein realer NR-Einstieg
und keine Quellenmaterialisierung werden freigegeben oder ausgefuehrt.

## Inventar vor dem einen Aufruf

ID: s2nr-runtime-binding-qualification-20260908-01.
Kommando: C:/Python314/python.exe -m reports.s2nr.qualify_runtime_once.
Genau ein unittest-Unterprozess mit -v -f, 16 Testkoerpern. Kein Retry.
Vor diesem Aufruf werden Testnamen, alle geaenderten und verwendeten
Quellhashes sowie die unberuehrte Vorversiegelung gehasht vorregistriert.

1. Zwei feste Masken, Profil, Regeln, Defaults und geschlossenes Hauptgate.
2. Gemeinsamer Elternbeleg, getrennte Cueformen, nur 24 Originalindexwerte.
3. Getrennte Runtime-/Feld-/Memoryinstanzen, identische korrespondierende Zustaende.
4. Exakte Hypothesenform, 24 Komplementwerte, Herkunft und Bereich.
5. Historische V1-Payload-/Digest- und Typregression; gegenseitige Typablehnung;
   CONTIGUOUS gegen den bestehenden Halbprofil-ALL-BANDS-Abruf.
6. Falsche Maske, Komplement, Profil, Quellen- und Herkunftsform, getrennte Unterfaelle.
7. Verdeckte Cuewerte unzugaenglich; Direktbaseline ohne produktiven Scanner;
   manipulierte Gesamtwertbindung wird am Elternbinder abgewiesen.
8. Read-only-Hinweise und fortgesetzte atomare Bildung.
9. Vollstaendige 9/3/8-Scans und direkte Baseline; unveraenderter Visualpfad.
10. Scanfehler nimmt Feldkontakt nicht zurueck; Fehlerabschluss/close.
11. Feldfehler verhindert Memoryformation nicht; Fehlerabschluss/close.
12. Lifecycle und unveraenderliche Datentypen.
13. Gueltige Enthaltung trotz abweichender fachlicher Erwartung technisch gueltig.
14. Fehlende/vertauschte Belege, Quellen- und Zustandsmanipulation, unabhaengig.
15. Profilmischung, Zeitbindung, Doppelprojektion und dreifacher neutraler NJ-Aufruf.
16. Teilbudgets, volle Artefakthuelle, getrennte Verifikationsarbeit und Uebergroesse.

## Endliche neutrale Ausfuehrung

Eine gemeinsame synthetische Folge AV/AUDIO_CUE/AV/VISUAL_CUE; rohe neutrale
Rezeptorzustandsdatentypen, keine PCM-/RGB-Generatoren oder Rezeptoranalysen.
Drei NJ-Projektionen. Zwei weitere begrenzte Fehlerkonstellationen nutzen
nur dieselben Eingaben: Praefix von zwei bzw. einem Ereignis, kein Neuaufbau
der Wahrnehmungsquellen. Insgesamt maximal 14 Runtimeereignisse,
acht Formationsversuche und 2.784 erfolgreiche Feldkontakte.
Acht gespeicherte Scans; zusaetzlich ein historischer Abruf und zwei
isolierte neutrale Audio-Scans. Keine Hypothesenanwendung.

Genau acht technische Verifikatoreintritte inklusive fuenf Manipulations-
abweisungen; drei gueltige Belege (davon zwei Fehlerabschluesse).
Konservativ inklusive abgewiesener Belege: maximal 64 Offline-Scanpruefungen,
33.792 Audio- bzw. 51.200 Visual-Wertvergleiche als getrennte Obergrenzen,
24 Zustandsdekodierungen, 32 Formationsrelationspruefungen. Keine davon
wird als Abrufarbeit ausgegeben. Keine Formation oder Feldfortschreibung
durch den Verifikator. NQ/direct.verify darf gespeicherte Audioscans mit
separat gezaehlter Direktarithmetik pruefen; keine Rezeptorwiederholung.

Fuer die spaetere 18-Ereignis-Groesse wird nur ein synthetischer
Serialisierungshuellen-Grenztest aufgebaut, keine 18-Ereignis-Ausfuehrung:
15 Zustandspositionen, 18 Eingaben und Paare, 16 Scanpositionen, Metadaten,
Mapschluessel und JSON-Rahmen. Obergrenze 2.665.194 Byte, kleiner als
4.194.304 Byte. Je Zustand 98.304, gepacktem Eingang/Paar 16.384,
Scan 32.768 und Metadaten 65.536 Byte. NJ-/Cue-/Hypothesenanteile sind in
den tatsaechlich serialisierten Eingangs- und Paarobjekten enthalten.

Zusaetzliche Anschlussvalidierung je 18-Ereignis-Beleg separat:
hoechstens 72 Eingabepackungen, 64 Hypothesenvalidierungen, 608 Pruefungen
der endlichen Quelldateiliste; innerhalb eines Listendurchgangs genau ein
Hash pro gelisteter Datei. Offline zusaetzlich 36 Elternvalidierungen,
15 Zustandsdekodierungen, 28 Formationsrelationen, 16 Armpruefungen;
deren obere 320 Slotinspektionen, 7.680 Banddifferenzen und 768
Vollkandidatengleichheitsvergleiche stehen getrennt vom Abrufbudget.
Die bestehenden endlichen rekursiven Typ-/Digestpruefungen der Adapter
bleiben enthalten, nicht als kostenlose Memory-/Scanoperation umgedeutet.

## Aussagegrenze

Technische Verifikation erhaelt keine Solltreffer. Die neutrale fachliche
Gegenpruefung stellt nur fest, dass eine gueltige Enthaltung einer
Hypothesenvorhersage widersprechen kann. Keine NR-Funktionsauswertung.
NQ-Beziehungs-/Erhaltungslogik bleibt unveraendert; eine reale NR-Auswertung
und ein geschlossener Quellenhauptlauf bleiben getrennt zu binden.
Kein Alt-/Neu-Feldvergleich, keine universelle Skalenbedeutungsgleichheit.
Fremde Aenderungen, Bootstrap und historische Versiegelung bleiben erhalten.
