# S2-NR: neutrale Runtime-/Hypothesenanbindung

2026-09-08, Ausgangscommit 39fd18d.
Lauf-ID s2nr-runtime-binding-qualification-20260908-01.
Genau ein Qualifikationsaufruf, kein Retry:

```text
C:/Python314/python.exe -m reports.s2nr.qualify_runtime_once
```

Einziger Testunterprozess:

```text
C:/Python314/python.exe -m unittest tests.test_s2nr_private_runtime_binding -v -f
```

**S2NR_RUNTIME_BINDING_QUALIFIED, 16/16, Exit-Code 0.**
Originalprotokoll: Ran 16 tests in 9.821s, OK.
Vorher gebundene Namen, Grenzen und Quellhashes in
[preregistration.json](preregistration.json); alle Hashes vor/nach identisch.
Keine Nachkorrektur oder weitere Testausfuehrung.

## Qualifizierter Anschluss

- Zwei feste Sichten CONTIGUOUS_24 und DISTRIBUTED_24. A weiterhin
  Maximum <= 0.1, Slow historisches sum/24 <= 0.01. Keine neue Auswahlregel.
- Gemeinsamer unveraenderlicher NN-Halbprofil-Eingang, je Sicht eigene
  MaskedAudioOperationV2. Der Scanner erhaelt nur 24 Werte und deren
  Originalindizes. Kein Umordnen der gespeicherten 48 Werte.
- Exakte MaskedAudioHypothesisV2 mit Masken-/Komplement-, Profil-, Quellen-,
  Cue- und Zustandsbindung. 24 Kandidatenwerte als getrennte Hypothese.
- Exakte MaskedMCMRuntimeConfig336V2 in MR. Die historische V1-Configform,
  kanonische Payload-/Digestbildung und Typakzeptanz bestehen die gezielte
  Regression. Neue und alte Audiohypothesentypen werden gegenseitig
  abgewiesen. Keine Erweiterung auf beliebige Objekte oder Duck-Typing.
- Getrennte Runtime-, Prozessor-, Feld- und Memoryinstanzen, identische
  korrespondierende Feld-/Memoryzustaende innerhalb des Halbprofils.
- Fieldadapter, LM, Memorykerne, NQ-Scanner und unabhaengige Direktbaseline
  unveraendert wiederverwendet. CONTIGUOUS gegen bestehenden Halbprofil-
  ALL-BANDS-Abruf neutral verglichen; Visualbefunde zwischen Armen identisch.

Private Oberflaeche: tools/_s2nr_private_runtime_binding.py,
MaskRuntimeComparison mit process_next/finish. Sie nimmt bereits gebundene
NN-Eingaben an; aktuell nur NEUTRAL, maximal sechs Ereignisse und zwei
Formationen je Arm. Keine NR-Quellenerzeugung oder reale Laufanbindung.

## Beobachtete neutrale Ergebnisse

Gemeinsame vierteilige Folge AV -> AUDIO_CUE -> AV -> VISUAL_CUE:
je Arm vier Ereignisse, zwei Formationen, ein auditiver und ein visueller
read-only Hinweis; acht Scanbelege einschliesslich Direktbaselines.
2.016 Feldkontakte, beide Runtimes abschliessend CLOSED.
Der auditive Hinweis liefert je Sicht eine A_RECENT-Hypothese mit passendem
Komplement. Nach zweiter Formation ist die visuelle Enthaltung wegen
interner Mehrdeutigkeit technisch gueltig, auch bei gegenteiliger
synthetischer Hypothesenvorhersage. Keine funktionale Erwartung im Verifikator.

Zwei kurze Fehlerpraefixe verwenden dieselben neutralen Eingaben:
Scanfehler behaelt Feldkontakt und Memoryzustand; Feldfehler verhindert die
Memoryformation nicht. Beide Fehlerbelege sind technisch nachvollziehbar
NOT_EVALUABLE und beide Runtimepaare CLOSED.

Insgesamt einschliesslich Fehlerpraefixen: 14 Runtimeereignisse,
acht Formationsversuche, 2.784 erfolgreiche Feldkontakte, acht gespeicherte
Scans. Drei NJ-Projektionen auf synthetischen neutralen Rezeptorzustaenden,
null Rezeptoranalysen und null NR-Payloads. Keine Hypothesenanwendung.
Die beiden isolierten Audio-Kontrollen und der historische Referenzabruf
sind zusaetzlich im vorab gebundenen neutralen Inventar enthalten.

Acht Verifikatoreintritte: drei gueltige Gesamtbelege, vier unabhaengige
Manipulationsabweisungen und eine Uebergroessen-/Integritaetsabweisung.
Die erfolgreiche Hauptpruefung decodiert drei Memoryzustaende, prueft vier
Formationsrelationen, acht Elternbindungen und acht Scanbelege. Ihre
zusaetzlichen 768 Wertvergleiche sind kein Teil des Ausfuehrungsscans.
Keine Feld-, Memoryfortschreibungs- oder Rezeptorwiederholung durch Verifikation.

Die Bit-/Zeit-/Profil-/Masken-/Herkunftsformmanipulationen und die
Doppelprojektionsabwehr wurden separat neutral geprueft. Die volle
numerische Slot-/Hypothesenherkunft wird durch die Offline-Scanpruefung
gegen gespeicherte Zustaende geprueft; die MR-Typgrenze ersetzt diese nicht.

## Ressourcen und Bindungen

Tatsaechlicher kompletter neutraler Beleg: 168.512 Byte. Fehlerbelege:
57.206 und 45.573 Byte. Synthetische maximale 18-Ereignis-Serialisierungshuelle:
2.655.427 Byte bei statischer Grenze 2.665.194 Byte, unter 4.194.304 Byte.
Dies ist ein Huellentest mit Platzhaltern, keine 18-Ereignis-Ausfuehrung.
NR-Quellen-/Cue-/NJ-Anteile sind in gepackten Eingaben und Hypothesenpaaren
enthalten. Ein realer Beleg muss die Einzel- und Gesamtgrenzen erneut einhalten.

Separat gebundene obere Offlinearbeit fuer einen spaeteren NR-Beleg:
16 Armpruefungen, 320 Slotinspektionen, 7.680 Banddifferenzen und
768 Kandidatengleichheitsvergleiche; zusaetzlich Eltern-, Zustands- und
Formationspruefungen gemaess RUNTIME_QUALIFIKATIONSBINDUNG.md/size-metrics.json.
Statische Obergrenzen fuer interne Validierungs-/Hashaufrufe sind keine
gemessenen Prozesspeak- oder allgemeinen Laufzeitgarantien.

Resultdigest:
`2fbac9ca4c4a1a794bcc774ef47a2924163f8311e18f01a4d8bae615a9a2513b`.
result.json-Dateihash:
`f053795a4b4b98d8bd6e258338f97448462336deb9ff50e2704fdc8af757fe6f`.
preregistration.json-Dateihash:
`b845010b64a6d87cc8e1fb2766dd8f792d08b6415c2831f6c43dd1b3d850fe1b`.
stderr.txt-Dateihash:
`00f8d23de723fe19289703334aa90df8143bea52759c5274e6e57c80dfd8bce8`.

| Qualifizierte Datei | SHA-256 |
| --- | --- |
| tools/_s2nr_private_runtime_types.py | 0e7e3dc849581c7c36128c681833ccd5e9b38aaae7a61bc2f2f1e9f1f791e90d |
| tools/_s2nr_private_runtime_binding.py | 2dbf506ae23debeefd0437d50c9240eaed97ee2c6fc3b0b4c818e9b243505733 |
| tools/_s2nr_private_runtime_verification.py | 54014cbb5962eb35d12fb44518a953940214f7da380b7362036f45de424a1eca |
| tools/_s2mr_private_minimal_mcm_runtime.py | e419d72ad5b5dd668eb36a90081f21a2902ad900c166289a2e9de79db56e618d |
| tests/test_s2nr_private_runtime_binding.py | 9c0eddf8be521ec99e29b7f28bba5cc73335cc3fc3a351a7373efb8eb7234e98 |

## Verbleibende Grenze

Qualifiziert ist diese neutrale Typ-/Adapterkomposition, kein NR-Funktions-
oder Erhaltungsnachweis. Keine versiegelten NR-Payloads oder reale
18-Ereignis-Folge ausgefuehrt; keine Rezeptormaterialisierung, keine
Hypothesenanwendung. Alle Hauptgates False. Die reale Quellenmaterialisierung,
deren geschlossener Einmaleinstieg und die NR-spezifische nachgelagerte
Herkunfts-/Erhaltungsauswertung bleiben vor einem Hauptlauf separat anzubinden
und freizugeben. Keine technische Treffergarantie oder Erfolgsgates daraus ableiten.

Die NR-Vorversiegelung samt Dokument und allen Wurzeln ist bytegleich.
Ihr historischer MR-Dateihash bleibt Herkunftsbeleg; der neue MR-Dateihash
ist eine separate, explizit qualifizierte Anschlussversion, keine neue
Quellenversiegelung. Historische Payloads/Defaults, fremde Aenderungen und
Bootstrap bleiben unveraendert.

WEITER: Am besten geht es jetzt mit der Analystenpruefung der qualifizierten
Typ-/Maskenanbindung und der eng begrenzten realen NR-Laufanbindung weiter.
