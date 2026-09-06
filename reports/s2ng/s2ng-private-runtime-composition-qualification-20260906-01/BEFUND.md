# S2-NG: neutrale Kompositionsqualifikation nicht bestanden

- Qualifikations-ID: `s2ng-private-runtime-composition-qualification-20260906-01`
- Status: `NOT_QUALIFIED`
- Genau ein Testaufruf: 22 Testkoerper, 21 bestanden, ein Fehler; Exit-Code `1`.
- Terminal: `FAILED (errors=1)`. Kein Retry und keine Korrektur nach dem Aufruf.
- `MAIN_GATE = False`; keine S2-MT-Quelle, Rezeptoranalyse oder Hauptgeschichte.

## Implementierter Umfang

Drei kleine private Module binden zwei unveraenderliche Audio-Regelarme an
getrennte bestehende S2-MR-/S2-LM-Instanzen, den vorhandenen Feldadapter,
atomare Memorybildung, S2-NE-Audioarme und den unveraenderten visuellen
S2-KQ-/Direktpfad. Hinzu kommen eine neue fokussierte Testdatei und ein
einmaliger Qualifikationscaller. Keine historische Produktdatei wurde geaendert.

Feld-, Memory-, Prozessor- und Runtimeobjekte sind getrennt; Ereignisse werden
als identisches unveraenderliches Tupel uebergeben. Alle Scanbelege bleiben
erhalten. Die technische Gesamtpruefung und die nachgelagerte Auswertung sind
getrennt. Teilbudgets und maximale Gesamtserialisierung wurden vor dem Test
in [KOMPOSITIONSBINDUNG.md](../KOMPOSITIONSBINDUNG.md) und der Vorregistrierung
gebunden, nicht nach dem Ergebnis angepasst.

## Beobachteter Fehler

`test_11_source_and_state_tampering` manipuliert unter anderem die Generation
eines gespeicherten Composite-Zustands. Der NG-Verifikator delegiert die
Rekonstruktion an den historischen `old.decode_state(...)`. Dessen bestehende
Memoryvalidierung weist den beschaedigten Zustand korrekt ab mit:

`S2JWCoordinatorError: S2JW_PRESTATE_INVALID: composite state relation differs`

Die Exception erreicht den Test unveraendert. Die NG-Grenze erwartet einen
`S2NGError`; ihre aktuelle Ausnahmebehandlung erfasst den von `RuntimeError`
abgeleiteten Koordinatorfehler nicht. Das ist eine Fehlerabbildungsluecke im
privaten Verifikator, kein akzeptierter manipulierter Zustand und kein
Memory-, Feld- oder Regelbefund. Die drei Manipulationen dieses Testkoerpers
wurden durch getrennte `subTest`-Bloecke ausgefuehrt.

## Begrenzte beobachtete Teilbefunde

- Die normale neutrale Vier-Ereignis-Komposition pro Arm endete
  `RECORDING_COMPLETE`: zwei neutrale Formationen insgesamt, 1.440
  Feldkontakte, zwoelf vollstaendige Scanbelege, gleiche Geschwisterzustaende
  und uebereinstimmende Direktbaselines. Der Beleg wurde read-only verifiziert.
- Die separate Zwei-Ereignis-Fehlerfixture pro Arm bildete zwei weitere
  neutrale Formationen. Eine fremde native Audiouhr fuehrte zu Scanfehlern
  und regulaer `NOT_EVALUABLE`; alle 768 Feldkontakte blieben erhalten.
  Die lesende Pruefung bestaetigte diesen technischen Fehlerabschluss.
- Insgesamt vier neutrale Formationen und 2.208 Feldkontakte. Das Metrikfeld
  `runtime_events = 8` betrifft die normale Fixture; der getrennte Fehlerbeleg
  enthaelt vier weitere verarbeitete Runtimeereignisse.
- Historische Mittelwertreihenfolge, unveraenderte Slow-Arithmetik,
  visuelle Gleichheit, Lifecycle, Read-only-Hinweise, volle Scans, gueltige
  Enthaltung, fehlende/vertauschte Belege und Ressourcenchecks bestanden.
- Synthetische Auswerterkontrollen trennten Gewinne und Verluste, erhielten
  verworfene Zielkandidaten im Bericht und fuellten auditives `D=0` nicht mit
  visuellen Treffern auf. Das ist keine reale Erhaltungsauswertung.

Gemessene kanonische Groessen der normalen neutralen Komposition:
Gesamtbeleg 242.452 Byte; maximaler Eingabebeleg 5.377 Byte; Schrittpaar
11.215 Byte; Scanbeleg 14.643 Byte; Memoryzustand 8.118 Byte. Die vorab
gebundene Gesamtobergrenze bleibt 4.194.304 Byte. Kein Ressourcenlimit
wurde erhoeht. Die kleinen Fixturegroessen behaupten keinen ausgefuehrten
28-Ereignis-Transfer.

## Bindungsbelege

Caller: `C:/Python314/python.exe -B -m reports.s2ng.qualify_once`.
Genau ein daraus gestartetes Kommando:

```text
C:\Python314\python.exe -m unittest tests.test_s2ng_private_runtime_comparison -v
```

- Vorregistrierung: `preregistration.json`, einschliesslich 22 Test-IDs,
  Interpreter, AST-Codecheck und vorab erhobener Quellhashes.
- Ergebnis: `result.json`; saemtliche Vor-/Nachherhashes identisch,
  einschliesslich gebundener historischer NF-Belege und Produktquellen.
- Ergebnisdigest:
  `d99b36bea52b064f242f439c49dec7d923daee786f802451a973547ee845ef72`.
- Normaler Belegdigest:
  `b9a5d706a7e4d91a2ac7aa2bb93a854d2e782bf83e0d025a250af085e41ed05d`.
- Normale Verifikation:
  `6dd1f5b5049b3f71f923c9fda6696b2f0763e1314cefa57fb27639f679ddfeb4`.
- Fehlerfixture und deren Verifikation liegen getrennt als
  `neutral-scan-failure.json` und `neutral-scan-failure-verification.json` vor.
- `stdout.txt` und `stderr.txt` sind die unveraenderten Prozessausgaben.

S2-NF bleibt abgeschlossen und unveraendert. Bootstrap und fremde Aenderungen
werden nicht aufgenommen. Die drei NG-Module und die Testdatei bleiben exakt
auf dem qualifizierten, insgesamt noch fehlerhaften Quellenstand.

## Grenze und Vorschlag an den Analysten

RUECKMELDUNG ERFORDERLICH: Vor einer Neuqualifikation ausschliesslich die
Abbildung des typisierten `S2JWCoordinatorError` an der NG-Zustandslesegrenze
pruefen. Vorschlag: expliziter NG-Zustandsbindungsfehler unter Erhalt des
urspruenglichen Fehlergrunds, ohne Memoryvalidator oder Testerwartung zu
lockern. Keine pauschale Unterdrueckung beliebiger Exceptions.

Der Hauptvergleich bleibt gesperrt. Aus 21 bestandenen Testkoerpern folgt
weder eine bestandene Kompositionsqualifikation noch ein Runtime-Transfergewinn.
