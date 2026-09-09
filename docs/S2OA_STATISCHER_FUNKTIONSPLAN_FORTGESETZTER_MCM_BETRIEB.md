# S2-OA: statischer Funktionsplan fuer fortgesetzten MCM-Betrieb

Stand 2026-09-09. Nur Plan, keine Laufnummer oder Ausfuehrungsfreigabe.
NW bis NZ bleiben geschlossen, der Prognosezweig ruht. ME/MI bleiben gesperrt.

## Aufgabe und feste Konfiguration

Eine private Runtime verarbeitet ohne Abschnittsreset wiederholte reale
AV-Wahrnehmungen und eingeschobene read-only Hinweise. Prueffrage: Bleiben
Aufnahme, begrenzte Speicherung, Stabilisierung, Verdraengung, Ersetzung und
Abruf ueber diese fortgesetzte Geschichte korrekt? Keine Prognosekennzahl,
allgemeine Intelligenz- oder unbegrenzte Dauerbetriebsbehauptung.

Genau eine `MinimalMCMRuntime336`, ein frischer Feldzustand und ein frischer
Memoryzustand; neue einmalige Ereignis-/Formationsowner, aber keine neuen
Runtimeinstanzen zwischen Abschnitten. `max_event_count=28`.

Festes qualifiziertes Halbprofil `s2nj.auditory.hann48.output-half.v1`,
Profilanschluss `s2nl.default-live-half-profile.v2`, Koordinatorkonfiguration
`55f1de8602c945749728ce17c74cdff8320d1b5fc72c800f239bc86737db1a1e`.
Grundlage sind [NN](../reports/s2nn/s2nn-half-profile-runtime-qualification-20260907-02/BEFUND.md)
und der reale [NO-Funktionspfad](../reports/s2no/s2no-half-runtime-20260907-01/BEFUND.md).
Keine verlustfreie Migration des historischen Profils behaupten; NM bleibt Grenze.

- Audio A: `ALL_BANDS_24`, Originalindizes 0..23, Maximum `<=0.1`.
  Audio-Slow: historische `sum(terms)/24 <=0.01`. Keine Maskenwahl.
- Visual: unveraenderter KQ-Exaktvergleich auf Originalpositionen 0..31;
  Ausgabe-Komplement 32..287, niemals angewandt. Keine visuelle L1-Regel
  anstelle dieser Teilhinweisregel einfuehren.
- Formation: native Vollvektor-Mittelwerte, Audio-Fast 0.1, Visual-Fast 0.2;
  Rang `(max(2*d_audio,d_visual),2*d_audio+d_visual,slot_id)` mit bestehenden
  Tie-Breaks. Fast-Update 0.5, Supportgrenze 2, Ablauf nach 8 Expositionen.
- B4/Fast/Audio-Slow/Visual-Slow: 9/3/8/4 Slots. PPB-Grenzen 0.01/0.01,
  Update 0.05, Supportgrenze 3, Ablauf 256/64 PPB-Schritte. Keine Aenderung.
- A/B-Aufloesung, Bankmehrdeutigkeit und Kandidatengleichheit unveraendert.
  Kein B-Vorrang, keine Vorhersage, keine neue Memoryebene oder Feldverstaerkung.

## Quellen und eine literale Geschichte

Gezielter Betriebsnachweis mit bereits untersuchten reinen Quellenbausteinen,
kein neuer Generalisierungskorpus. Ein unveraendertes PCM-Rezept: `np-a02`
aus der [NP-Vorversiegelung](../reports/s2np/s2np-source-preseal-20260907-01/BEFUND.md).
Fuenf volle RGB-Rezepte aus dem vorhandenen JX-/NE-Generator:
1920x1080 RGB8, 12x8 Zellen; Kanal i ist 255 genau dann, wenn
`(i+o)%11 in {1,3,4,5,9}`, sonst 0. Ordinale fest `o=0,2,3,4,5`.
Diese Auswahl begrenzt die Geschichte auf die vier vorhandenen visuellen
Slow-Slots plus genau einen verdraengenden Inhalt; keine Distanzsuche.
Vier Expositionen je Inhalt pruefen jeweils die vollstaendige Stabilisierung:
vier stabile Generationen fuellen die Bank, die fuenfte ersetzt und stabilisiert
sich erneut. Zusaetzliche einmalige Druckquellen sind dadurch unnoetig.

Nur zur Darstellung/Evaluation: A,B,C,D,E bezeichnen dieselbe Audioquelle P
mit den fuenf Bildern in obiger Reihenfolge. `a(P)` ist ein auditiver Hinweis;
`v(A)`/`v(E)` ein visuell okkludierter Hinweis. Technische Eingaben erhalten
neutrale Quellen-/Ereignis-IDs, keine Abschnittsaufgabe oder Sollzuordnung.
Die beiden Cue-RGB-Rezepte erhalten nur Kanaele 0..31 ihres Grundbildes;
alle anderen Kanaele werden bereits im RGB-Frame genullt, vor Rezeptoranalyse.

| Ereignisse | Formation f / Inhalt | Hinweis und fachliche Vorhersage |
| --- | --- | --- |
| e01 | noch keine | q01 v(A): keine Anwendbarkeit im Nullzustand |
| e02 | f01 A | |
| e03, e04 | keine | q02 a(P): eindeutig A_RECENT; q03 v(A): eindeutig A_RECENT |
| e05..e07 | f02..f04 A,A,A | |
| e08 | keine | q04 a(P): A-interne Mehrdeutigkeit, trotz stabilem Audio-B |
| e09..e12 | f05..f08 B,B,B,B | |
| e13..e16 | f09..f12 C,C,C,C | |
| e17 | f13 D | |
| e18 | keine | q05 v(A): eindeutig B_STABLE nach Verlust aus A_RECENT |
| e19..e21 | f14..f16 D,D,D | |
| e22 | f17 E | |
| e23 | keine | q06 v(E): eindeutig A_RECENT, noch kein E-Slow-Eintrag |
| e24 | f18 E | |
| e25 | keine | q07 v(A): nach Ersetzung nicht verfuegbar, Enthaltung |
| e26,e27 | f19,f20 E,E | |
| e28 | keine | q08 v(E): A-interne Mehrdeutigkeit, E zugleich stabil in B |

**28 Ereignisse, 20 Formationen, zwei auditive und sechs visuelle Hinweise.**
Keine Ruecksetzung, kein direktes Slotloeschen und keine manuelle Slotbelegung.
Der bereits bei q05 ausgegebene historische Beleg bleibt historisch gueltig,
darf bei q07 aber nicht als aktuelle Verfuegbarkeit behandelt werden.

Pro globalem Ereignis g=0..27: Audio, falls vorhanden, Uhr `audio.sample`,
Fenster `[9600*g,9600*g+4800)`, nativer Snapshotindex `20*g` nach exakter
Teilbarkeitspruefung durch 480. Direkte Analyse, keine rollende Pipeline.
Video, falls vorhanden: Uhr `video.frame`, Fenster `[6*g+2,6*g+3)`.
Gemeinsame Felduhr `s2oa-continuous-field-clock` in ns:
Audio `[200000000*g,200000000*g+100000000)`, Video
`[floor((6*g+2)*1000000000/30),200000000*g+100000000)`.
Modalitaetsfenster nicht angleichen; AV-Schnittmenge ist das Videozeitfenster.
Feldfortschreibung vom vorigen Feldende, initial 0, bis zum aktuellen Ende.
Hinweise zaehlen fuer Ereignis-/Feldzeit, nicht als Formation oder PPB-Update.

Vor spaeterer Verarbeitung neue Ereignis-/Zeit- und Cue-Payloadbindungen
rezeptorfrei versiegeln; alte Rezept-/Payloadidentitaeten separat erhalten.
Jeder Payloadhash vor Analyse pruefen. Je Audioereignis genau eine direkte
Analyse und NJ genau einmal vor jeder Audiokontaktbildung. Keine Wiederverwendung
berechneter Zustandswerte als neue Erfahrung. Rohpayloads danach verwerfen.

## Statische Zustandsprognose aus den bestehenden Regeln

Die JX-Ordinalbilder sind vollvektoriell bereits statisch getrennt
(siehe [NE](S2NE_PRIVATER_AUDITIVER_MEMORY_TRANSFER_VERTRAG.md)); ihre ersten
32 Kanaele enthalten unterschiedliche vollstaendige Perioden. Verschiedene
Bilder treffen deshalb weder gemeinsam in Fast noch exakt im visuellen Cue.
Wiederholungen liefern denselben binaeren Bildvektor. PPB-Updates und ihre
Binary64-Werte bleiben trotzdem aus der wirklichen Transaktion nachzuweisen.

| Formation | Erwartete konkrete Aenderung |
| --- | --- |
| f01..f04 | Fast F0=A; ab f02 je Modalitaet PPB S0 CREATED, MATCHED, MATCHED; Support 1,2,3. |
| f05..f08 | Fast F1=B; Visual S1 mit Support 1,2,3 ab f06. Audio S0 bleibt dieselbe Generation, weitere MATCHED-Updates. |
| f09..f12 | Fast F2=C; Visual S2 ab f10. Bei f12 laeuft Fast F0 aus: 12-4=8. |
| f13..f16 | Freier Fast F0=D; Visual S3 ab f14. Bei f16 laeuft F1 aus: 16-8=8. |
| f17..f20 | Freier Fast F1=E; bei f18 Visual S0 REPLACED/Support1, f19 MATCHED/2, f20 MATCHED/3. Bei f20 laeuft F2 aus: 20-12=8. |

Slotnummern F0/S0 meinen die jeweils kleinste native Slot-ID, keine neue ID-Form.
B4 ist immer der Ring der letzten neun Formationen. Bei f13 ist der letzte
A-Eintrag f04 verdraengt; q05 hat keinen A-Rest. Visual-Slow ist bei f16 voll;
die letzten PPB-Auswahlschritte fuer S0..S3 sind 3,6,9,12. Bei PPB-Schritt13
(f18) ersetzt LRU somit S0, keine Ablaufloeschung: Alter 10 liegt unter 64.
Am Ende B4 chronologisch C,D,D,D,D,E,E,E,E; Fast F0=D/F1=E/F2=frei;
Visual-Slow S0=E,S1=B,S2=C,S3=D, jeweils Support3.

Je Modalitaet 15 PPB-Aufrufe, zusammen 30: Audio 1 CREATED/14 MATCHED;
Visual 4 CREATED/10 MATCHED/1 REPLACED. Auditive Herkunft bleibt die reale
gemeinsame Audioquelle P, nicht eine behauptete Identitaet der fuenf AV-Inhalte.
Audio-Slow-Kapazitaetsersetzung und zeitlicher Slow-Ablauf sind **nicht**
abgedeckt. Geprueft werden B4-Verdraengung, Fast-Ablauf und visuelle Slow-Ersetzung;
kein kuenstliches Verlaengern bis zu allen Ablaufgrenzen.

Generationsbelege werden aus den tatsaechlichen Pre-/Postzustaenden und
Transaktionen abgeleitet: neue Belegung/Ersetzung erzeugt neue Bindung,
MATCHED behaelt sie, Ablauf/freier Slot hat keine aktuelle Bindung.
Bei f18 darf dieselbe Visual-Slot-ID keinesfalls die A-Generation weitertragen.
Alte Belege bleiben nur im endlichen Auswertungsartefakt, nicht als abrufbarer
Zusatzspeicher. Reine Wertegleichheit ersetzt keinen Herkunftsnachweis.

## Vorhandene Anschluesse und eng fehlende Anbindung

- [MR](../tools/_s2mr_private_minimal_mcm_runtime.py): `process_once`, Snapshot,
  `close`; LM-Geschwisterrouting und JW-Formation unveraendert verwenden.
- [NN](../tools/_s2nn_private_half_runtime_binding.py): Halbprofil-Ereignisbindung;
  NO-Prinzip fuer getrennte Quellen-/Profilbindung, Modalitaetsfenster und
  kompakte NJ-Belege. Kein historischer NH/NO-Materialisierungs-Haupteinstieg.
- [NG-Adapter](../tools/_s2ng_private_runtime_comparison.py): `ObservedBranch`,
  `AudioAdapter` fest ALL_BANDS_24 sowie `VisualAdapter`, je mit Direktbaseline.
  Die vorhandene Vergleichshuelle erzeugt zwei Runtimes und begrenzt visuelle
  Hinweise auf vier: **nicht unveraendert aufrufen oder global lockern**.
  Notwendig ist nur eine eigene private Eininstanzbindung fuer diese feste
  20/2/6-Folge. Gesamtzahl bleibt innerhalb 28/20, Scanarbeit sinkt gegen NO.
- [NQ-Zustandspruefung](../tools/_s2nq_private_verification.py) und
  [NL-Rangdirektrechnung](../tools/_s2nl_private_rank_verification.py): B4-Ring,
  Fast-Auswahl/Ablauf/Updates und PPB-Auswahl/Updates read-only nachrechnen.
  Native JW-Owner-/Receiptdaten beim vorhandenen Adapterabschluss mitnehmen;
  lediglich deren ereignisspezifische Namensbindung anschliessen, nicht erfinden.
- [NS-Generationsableitung](../tools/_s2ns_private_run_verification.py) ist
  bisher auditiv (B4/Fast/Audio-Slow). Kleinster zusaetzlicher Anschluss:
  dieselbe transaktionsgebundene Ableitung fuer Visual-Slow ausweisen,
  ohne NS-Zwei-Sichten-Regel oder deren freien Inventartyp als Memory zu nutzen.
- Die NG-Gesamtpruefung erwartet zwei Arme. Eine feste Eininstanz-Gesamthuelle
  mit einmaliger read-only Pruefung und getrenntem Auswerter ist noch
  anzubinden. Atomare Dateipublikation wiederverwenden; keine Recorderplattform.

## Feste Grenzen und Abschlusskriterien

Spaeter maximal 22 Audioanalysen/NJ-Projektionen und 26 visuelle Analysen;
keine separaten Vorlaeufe. **8.544 Feldkontakte**, 28 Feldschritte,
20 atomare Formationen, acht read-only Hinweisereignisse, 16 Scanbelege
einschliesslich Direktbaselines. Vollstaendige Audio-9/3/8- und Visual-9/3/4-Scans.

| Arbeit / Ausgabe | Fester Deckel |
| --- | --- |
| Scan einschliesslich Direktbaseline | 272 Slotinspektionen; 1.920 auditive Differenzen, 6.144 visuelle Gleichheitspruefungen, 3.648 interne Vollvektorvergleiche; zusammen 11.712; 200 logische Operationen |
| Formation | 20 JW-Transaktionen; funktionaler L1-Deckel 71.040 nach bestehendem Ledger |
| Read-only Verifikation separat | 16 Scanpruefungen mit nochmals maximal 11.712 Wertvergleichen; 20 Formationspruefungen, 20.160 Fast-Rangterme, 30.720 PPB-Auswahlterme, 13.440 Updatekomponenten |
| Bindungspruefung separat | 21 Zustandsdekodierungen; bis 116 Zustandsvalidierungen/645.888 Zustandswerte; 28 Quellenbindungen/84 Projektionsvalidierungen; 8.544 Eingangswerte; 480 Slot-Generationsuebergaenge |
| Laufender Zustand | maximal 9/3/8/4 Slots mit insgesamt 5.568 gespeicherten Wahrnehmungskomponenten, zusaetzlich bestehende Support-/Zeit-/Digestfelder innerhalb des Zustandsbytelimits; unveraenderter endlicher Feldkern; keine Hypothesenablage im Runtimezustand |
| Artefakt | 21 Memoryzustandsbelege zu maximal 98.304 Byte; 28 Eingaben und 28 Schrittbelege je maximal 16.384 Byte; 16 Scans je strikt unter 32.768 Byte; Metadaten 65.536 Byte |
| Quellen-/NJ-/Formations-/Generationszusatzhulle | insgesamt maximal 262.144 Byte; keine nochmalige Vollkopie der Eingangsmaterialisate |
| Vollstaendiger Gesamtbeleg | unveraendert maximal 4.194.304 Byte, einschliesslich aller Huellen; spaeter neutral vollstaendig absichern, keine Grenzerhoehung bei Ueberschreitung |
| Getrennte Verifikation / Auswertung | je maximal 262.144 Byte; referenzieren den Gesamtbeleg, keine zweite Vollkopie |

Hoechstens ein PCM-Fenster (19.200 Byte) und ein RGB-Frame (6.220.800 Byte)
gleichzeitig als Rohpayload. Die Artefakthistorie ist kein laufender Memorybereich.
Die endliche 28-Ereignisbindung ist kein universeller Langzeit-Speicherpeaknachweis.
Offline werden Quellen-/NJ-Herkunftsbindungen und gerundete Werte geprueft;
keine Rohspektren aus Halbwerten rekonstruieren. Feldreceipts belegen Kontakt-
und Zeitbindung, keine unabhaengige numerische Wiederholung der Feldtrajektorie.

Technische Pruefung: vollstaendige Ereignis-/Transaktionskette, gleiche
Wahrnehmungsprojektion fuer unabhaengige Feld-/Memoryzweige, kein Teilcommit,
Read-only-Digests aller Hinweise, aktuelle Generationsbindungen und exakte
Baselinegleichheit. Fehlerisolation stammt zusaetzlich aus NN-Qualifikation;
in diesen realen Strom werden keine kuenstlichen Fehlerereignisse eingeschoben.
Ein fehlerfreier Lauf allein waere kein neuer Nachweis aller Fehlerpfade.

Funktionsauswertung erst danach: jede tabellierte Zustands-/Abrufvorhersage
einzeln CONFIRMED/FALSIFIED, keine Kompensation von Fehlzulassungen durch
richtige Abrufe. Nullzustand, Verlust nach Ersetzung und Mehrdeutigkeit
separat; Enthaltung ist keine Unbekanntheitserkennung. Vollstaendiger Erfolg
verlangt alle bestehenden Aufgaben in dieser Folge, nicht nur technische
Verifizierbarkeit. Unerwartete stabile/instabile Inventare oder gueltige
Enthaltung bleiben auswertbare Gegenbefunde, keine Erfolgsgates.

Regulaer einmal `close()`: CLOSED, 28 verarbeitete Ereignisse, Memorygeneration 20,
unveraenderte Memory-/Felddigests gegen den letzten offenen Snapshot; nur
Lifecycle-/Gesamtdigest darf sich beim Schliessen aendern. Bei technischem
Fehler phasengenau NOT_EVALUABLE, erreichte Zaehler und letzter gueltiger
Snapshot; schliessen und Gates False, kein Retry oder Quellenersatz.

Jetzt keine Implementierung, Vorversiegelung, Berechnung oder Tests.
Quellenbindung, kleine Anschlussqualifikation und realer Einmallauf benoetigen
jeweils Freigabe. Historische Belege, Defaults, fremde Aenderungen und
Bootstrap unveraendert. Keine Prognose-, ME/MI- oder Kontextanwendung.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser einen
fortgesetzten Geschichte und ihrer eng benannten Anschlussgrenzen weiter.
