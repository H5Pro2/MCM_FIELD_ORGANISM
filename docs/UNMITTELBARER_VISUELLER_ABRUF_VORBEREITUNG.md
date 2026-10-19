# Unmittelbarer visueller Abruf nach einer Formation – Vorbereitung

Stand: 2026-09-12. Nur statische Vorbereitung, keine Ausführung oder neue
Qualifikation. Bezugscommit: `537109994cf777f8d36cda617aafe12226806c25`;
der Arbeitsbaum enthält zusätzliche Änderungen und unversionierte Anschlüsse.
Der Commit allein ist deshalb keine aktuelle Codezulassung.

Der visuelle Konsistenzvergleich ist unverändert geschlossen. Er bestätigte
wiederholbare 288 Werte und die Erhaltung der 32 sichtbaren Werte durch
Okklusion. Er prüfte keinen Memoryabruf. Die vier historischen Enthaltungen
des Videoversuchs werden weder ersetzt noch erneut ausgewertet.

## Kleinster gebundener Eingang

Vorgesehen ist ein Vergleich auf bereits gespeicherten Wahrnehmungswerten,
nicht ein weiterer Decoder- oder Maskierungstest. Ein frischer Memoryzustand
erhält genau eine reguläre AV-Formation. Keine historischen Slots übernehmen.

Quelle der Formation ist ausschließlich `execution.inputs[2]` (e03,
`media-event-03`) aus `media-memory-video-20260912-01/record.json`.
Die Datei besitzt eine äußere Hülle; der Pfad darin lautet
`record.execution.inputs[2]`. Beide Modalitäten dieses einen Eingangs bleiben
zusammen: 48 bereits halbierte Audiowerte und 288 visuelle Werte. Keine
erneute Halbierung, Rohwertrekonstruktion oder künstliche Audiofüllung.

- Historischer Recorddigest:
  `344e8e61004c34e0cb419e04910573a991e32add607043467215a0e9b0669a10`.
- Historischer Verifikationsdigest:
  `8170305ef10b43cd68927264fe9a5e97714bf3f62b944e6c21ef2717e24a41d6`.
- Eingangs-Ereignisdigest:
  `5aad3ee0dc8c4026a729ff71e04a13431843a8ce41bb3703dc2a0c80ab4464ed`.
- PCM-Bindung: `a735fbcf274c7a5d4d8ae1998501f0fd2e0ec74e909374a3d41f87b883b031fd`.
- RGB-Bindung: `040ec13d400f1770e45ce1eb59a09c7d5b19771e7527d5fff96c33d8bfa7e94d`.

Medienherkunft bleibt die bereits untersuchte lokale Datei
`C:/Users/TV/Downloads/17138816-uhd_3840_2160_30fps.mp4`, SHA-256
`df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa`.
Medienfenster 1,0 bis 1,1 s, Auswahlmitte 1,05 s; gebundener Frame-PTS
31031, Zeitbasis 1/30000, native Rate 30000/1001. Kein erneuter Dateizugriff.
Diese Angaben bleiben Herkunft, nicht neue Messwerte.

Der Cue wird einmal mit dem bestehenden MaskedMemoryCue-Builder aus genau
den Positionen 0 bis 31 dieses gespeicherten visuellen Formationseingangs
gebunden. Positionen 32 bis 287 sind `None`, niemals verdeckte Eingaben.
Beide Abrufstellen verwenden dieselben sichtbaren Werte und dieselbe
Quellenherkunft, aber eigene Abrufzeitbindungen. Das ist eine Kontrolle am
gespeicherten Rezeptorausgang, keine erneute RGB-Okklusionsanalyse.

## Folge und Zeiten

| Schritt-ID | Operation | Gebundene gemeinsame Zeit in ns |
| --- | --- | --- |
| immediate-visual-empty | visueller Abruf aus frischem Nullzustand | [300000000,333333333) |
| immediate-visual-form | eine atomare AV-Formation | Audio [400000000,500000000), Visual [466666666,500000000) |
| immediate-visual-after | derselbe sichtbare Cue, ohne Zwischenformation | [500000000,533333333) |

Die historische Herkunfts-ID bleibt separat erhalten. Neue Operations- und
Ownerbindungen dürfen sie nicht als neue Erfahrung umetikettieren. Der
gemeinsame Clock-Bezug bleibt `s2ob-caller-field-clock`; hier wird kein Feld
ausgeführt. Native gespeicherte Audiozeit [19200,24000) auf `audio.sample`
und Visualzeit [14,15) auf `video.frame` bleiben erhalten. Diese Adapterzeiten
sind nicht die originalen Medien-PTS. Paar-Schnittmenge bleibt
[466666666,500000000). Keine Uhr läuft rückwärts, keine Zwischenformation.

## Getrennte Kontrollen und Vorhersagen

1. Verfügbarkeit: Nullzustand ohne Kandidaten; nach Formation tatsächliche
   B4-/Fast-Belegung und Generation aus der Transaktion, nicht aus Sollrollen.
2. Werte: sichtbare Werte des Cues gegen die tatsächlich gespeicherten
   Kandidaten bitgenau prüfen; zusätzlich vollständige B4-/Fast-Gleichheit
   für die bestehende interne A-Auflösung. Keine Toleranz oder Distanzsuche.
3. Entscheidung: vorher `ABSTAIN_NO_CONTEXT`, danach voraussichtlich
   `ADMIT_SINGLE_CONTEXT` in A. Zwei gleichwertige Bankbelege sollen einen
   öffentlichen A-Kontext ergeben; eine einzige Formation begründet keinen
   stabilen B-Abruf. Diese Aussagen sind Auswertungsprognosen, keine Startgates.
4. Unabhängige Direktbaseline bei beiden Abrufen; Zustandsdigest vor/nach
   jedem Cue unverändert. Hypothese getrennt, niemals anwenden.

Eine unerwartete Enthaltung bleibt ein fachlicher Befund. Unmittelbarer
Abruf, späterer Verlust durch Verdrängung und fehlende Slow-Stabilisierung
sind unterschiedliche Fragen. Selbst ein Treffer belegt keine Objektidentität.

## Vorhandene Anschlüsse und noch fehlende Deckung

- `_s2nl_private_half_profile_binding.py:build_config` bindet das bestehende
  Halbprofil; `bind_pair` erhält halbierte Werte ohne Doppelprojektion.
- `_s2ng_private_comparison_verification.py:decode_input` rekonstruiert
  gespeicherte Eingänge und verlangt kanonische Gleichheit. Die konkrete
  Halbprofil-Rekonstruktion des e03-Belegs ist für diese Kontrolle noch nicht
  qualifiziert; kein bloßes Vertrauen auf JSON-Felder.
- `_s2jw_profiled_memory_coordinator.py` bietet Initialzustand, Owner und
  atomare Formation. `_s2oa_private_runtime_binding.py:MemoryBranch`
  (Zeilen 160–175) zeigt den bestehenden regulären Aufrufpfad.
- `_s2kq_private_partial_cue_retrieval_336.py:build_masked_memory_cue_336`,
  `form_partial_cue_retrieval_336`, `_resolve_a` und `_decide` bleiben
  unverändert. `_s2kq_private_direct_slot_scan_baseline.py` bleibt unabhängig.

Der feste 24-Ereignis-Medienrunner wird nicht gelockert. Es fehlt nur die
geschlossene Verbindung des eingefrorenen AV-Eingangs zu einer frischen
Formation mit zwei Cueaufrufen, Herkunfts-/Zeitprüfung und Gesamtbeleg.
Vorhandene 12/12- und 8/8-Diagnosequalifikationen decken Eingangskonsistenz,
nicht diese Kombination. Noch zu prüfen wären Halbprofil-Rekonstruktion,
neue Operationsbindungen, unveränderte Werte, Leer-/Nachabruf, Read-only,
unabhängige Baseline und vollständige Größen-/Fehlerhülle. Kein Test freigegeben.

## Vollständigkeit der Ressourcenbindung

Geplanter Funktionsumfang: eine Formation, zwei Hinweise, vier Scanbelege
einschließlich Direktbaseline, zwei native Zustände. Keine Decoder-, Rezeptor-,
NJ-, Feld- oder Runtimeaufrufe. Keine MP4-Lesemenge und keine Rohdatenablage.
Pro visuellem Scan gelten unverändert höchstens 16 Slotprüfungen (9/3/4),
512 sichtbare und 288 interne Gleichheitsprüfungen: vier Scans höchstens
64 Slotprüfungen und 3.200 Wertevergleiche. Keine auditive Teilscanprüfung.
Unabhängige Verifikation separat: höchstens dieselben vier Scanprüfumfänge
und eine direkte Formationsprüfung innerhalb des bestehenden nativen Ledgers.
Keine erneute Rezeptorprüfung; Auswertung liest nur gespeicherte Befunde.

Vorhandene Referenzdateien, vollständig statt nur per Digest mitgezählt:

| Datei | Istbytes |
| --- | ---: |
| historischer Video-Record | 1.359.778 |
| historische Video-Verifikation | 30.603 |
| Konsistenz-Record | 45.554 |
| Konsistenz-Verifikation | 466 |
| Referenzen zusammen | 1.436.401 |

Konservative Teilbilanz der neuen Hülle: zwei Zustände je 98.304,
drei Eingänge je 16.384, drei Schritte je 16.384, vier Scans je 32.768
(jeweilige echte Scangrenze strikt kleiner), gemeinsame Zusatzhülle maximal
262.144 einschließlich Herkunft, Formation, Generation und vorhandener NJ-
Herkunft; Metadaten einschließlich alternativem Fehlerabschluss maximal
65.536. Mit den vier Referenzen ergibt dies 2.190.065 Byte **vor** aktuellen
Code-/Qualifikationsabhängigkeiten. Gegen 4.194.304 bleiben rechnerisch
2.004.239 Byte; das ist keine Quellenreserve und keine Zulassung.

Offen bleibt die vollständige transitive Referenz-/Code-/Qualifikationsliste
und ihre bestehende Belegklassenzuordnung. Insbesondere darf der große
historische Record nicht ungezählt außerhalb einer Quellen- oder Zusatzgrenze
stehen. Die Tabelle ist daher eine vollständige Kategorien-Vorbilanz mit
benannter offener Abhängigkeit, noch kein Nachweis aller lokalen Grenzen.
Erfolg und Fehler sind alternative Abschlüsse; physisch doppelte Dateien
zählen doppelt. Vor einer späteren Qualifikation sind alle aktiven Dateien,
Reserven und Klassen konkret zu schließen; andernfalls Stopp, keine Erhöhung.

Keine neue Lauf-ID, keine ausführbare Freigabe. Gates bleiben False.

## Vorabstopp nach Anschlussfreigabe

Die nachfolgende Freigabe erlaubt die schmale Implementierung und genau eine
neutrale Qualifikation, verlangt aber zuvor die vollständige transitive
Belegbilanz innerhalb bestehender Grenzen. Die bisher offene Klassifikation
ist kein freier Platz im Gesamtbudget.

Statisch geprüfter Anschluss: `_s2ob_private_caller_binding.py:balance`
(Zeilen 412–426) lässt externe Referenzen ausschließlich in `metadata`,
`sources` oder `verification` zu. `_s2oc_shared_binding.py:ledger` (ab Zeile
241) behält diese Klassifikation bei. Die native OA-Bilanz
`_s2oa_private_administrative_binding.py:LIMITS` und `ledger` bindet
65.536 Byte Metadaten, 174.080 Byte Quellen, 262.144 Byte Verifikation und
262.144 Byte gemeinsame Zusatzhülle. Die früheren privaten OD- und
Videodiagnose-Erweiterungen werden nicht automatisch hierhin übertragen.

Bereits der vollständig benötigte historische Record mit 1.359.778 Byte
überschreitet jede dieser Referenzklassen:

| Mögliche Referenzklasse | Grenze | Überschreitung allein durch den Record |
| --- | ---: | ---: |
| sources | 174.080 | 1.185.698 |
| metadata | 65.536 | 1.294.242 |
| verification | 262.144 | 1.097.634 |

Als Quelle würde er außerdem die gemeinsame Zusatzhülle bereits um
1.097.634 Byte überschreiten, noch ohne Formation oder Generationsbeleg.
Alle vier zuvor genannten Referenzdateien zusammen sind 1.436.401 Byte.
Weitere aktive Code-, Qualifikations- und Abschlussdateien können diese
Untergrenze nur vergrößern. Eine zusätzliche Inventarisierung würde daher
keine tragfähige Vorbilanz ergeben; eine vollständige finale Bilanz wird
hier ausdrücklich nicht behauptet.

Die 2.190.065-Byte-Teilrechnung bleibt als historische Planrechnung stehen,
ist aber kein Beleg lokaler Budgetkonformität. Die dort vorgeschlagene
vollständige historische Recordreferenz ist unter diesem Ledger nicht
ausführungsbereit. Es liegt kein Memory- oder Rekonstruktionsfehler vor.

Kleinste noch zu entscheidende Richtung ist eine eigenständige, vollständig
verfügbare Bindung des eingefrorenen e03-Eingangs einschließlich seiner
Quellen-, Profil- und Zeitbelege. Dafür muss ausdrücklich geklärt werden,
welche historische Integritätsprüfung einmalig beim Binden erfolgt und
welche Belege der spätere Verifikator tatsächlich benötigt. Ein Auszug samt
Elterndigest allein ersetzt keine prüfbare Herkunft. Die große Elternreferenz
darf nicht stillschweigend aus der aktiven Bilanz verschwinden; ein neues
Referenzformat oder eine neue Budgetklasse wird hier nicht eingeführt.

Kein Testaufruf und keine Qualifikations-ID verbraucht. Keine Produktdatei
geändert, kein Projektimport, keine Rezeptor-, Formations- oder Abrufausführung.
Die neutrale Qualifikation und der reale Kontrolllauf bleiben ungestartet.

## Prospektiv freigegebene historische Eingangsbelegklasse

Die nachfolgende Analystenanweisung löst ausschließlich die Klassifikation:
`s2oe.immediate-historical-input.v1` darf den benannten vollständigen Elternrecord
einmal als historische Eingangsdatei bis 2.097.152 Byte führen. Gesamtlimit
4.194.304; Metadaten 65.536, Quellen 174.080, Verifikation 262.144 und gemeinsame
Zusatzhülle 262.144 bleiben bestehen. Keine Übertragung auf andere Dateien.
Der vorstehende Vorabstopp bleibt historische, zutreffende Einordnung der alten
Klassifikation; er ist kein Fehltest.

`_s2oe_immediate_visual_input.py` prüft vollständige Dateibytes und SHA-256 vor
der strukturierten Auswahl von Index 2, Ereignis-ID, Ordinal, Ereignisart,
Ereignisdigest, Profil, Wertedimensionen und Quellenbeleg. Der eigenständige
Auszug muss bytegleich aus demselben geprüften Elterninhalt ableitbar sein.
Ein interner historischer Recorddigest ist nicht mit dem SHA-256 der physischen
Datei gleichgesetzt. Letzterer wird separat in der Vorregistrierung gebunden.
Lesezugriffe werden je Zugriff gezählt, unabhängig von einmaliger Ablage.

Qualifikation: 18 neue Kontrollen, keine Übernahme historischer Passzahlen.
Je Kontrolle frischer synthetischer Elternbeleg; einmal native Folge mit
einer Formation und vier Scans. Null Medien-/Rezeptoranalysen; 18 synthetische
NJ-Fixtureprojektionen, keine Projektion im eingefrorenen Kontrollpfad.
Der Kindprozess sperrt Zugriffe auf den echten Elternrecord und Medienpayloads.
Test, Aufruf und Produktdateien werden vorab im statischen transitiven
Inventar mit Pfad, Größe und Hash gebunden. Nach bestehender OB-Praxis sind
Softwaredateien Voraussetzungen; das vollständige Inventar zählt als aktive
Quellenbelegdatei, nicht eine zweite physische Kopie aller Softwaredateien.

Vorbindung: 65.536 Byte Metadaten einschließlich vollständigem 32.768-Byte-Log,
Präregistrierung 8.192, Ergebnis einschließlich Testresultat/Claim 8.192,
Bilanz 4.096, spätere Laufbindung 8.192 und Bericht 4.096. Kein Kürzen bei Fehler.
Zusätzlich tatsächliches Inventar (maximal 174.080), Verifikation 262.144,
Zusatzbelege 4.096 sowie vollständige neutrale Datenhülle 393.216 Byte.
Historischer Elternrecord 1.359.778 Byte wird trotz Lesesperre im Test in der
gemeinsamen Vorbilanz berücksichtigt. Alle anderen historischen Lauf- und
Diagnosedateien sind Hintergrundbefunde, keine operative Eingangsabhängigkeit:
aktiver Herkunftsnachweis ist hier die ausdrücklich zugelassene vollständige
Elterndatei mit aktueller Inhaltsprüfung und Extraktionsbeziehung. Es wird
keine neue numerische oder historische Verifikation behauptet.

Die tatsächliche Vorbilanz und alle Quellhashes werden vor dem einzigen
Testaufruf gespeichert. Erfolg und Fehler sind alternative Abschlüsse. Ein
überlanges Fehlerlog bleibt erhalten und führt zu NOT_QUALIFIED. Die reale
Kontrolle ist weiterhin gesperrt; keine neue Hauptlauf-ID freigegeben.
