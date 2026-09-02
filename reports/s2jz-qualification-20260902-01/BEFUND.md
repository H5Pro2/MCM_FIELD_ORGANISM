# S2-JZ Implementierungs- und Qualifikationsbefund

Status:

`S2JZ_PRIVATE_VARIATION_RUN_BOUNDARY_QUALIFIED`

Die private S2-JZ-Grenze wurde mit vier neuen Modulen umgesetzt:

- reale kanonische RGB8-/PCM-Fixtures fuer `R0`, `E0`, `V1`, `A1`, `C1`
  und `Z1`;
- Messung der tatsaechlich erzeugten Rezeptorabstaende und eine direkte
  L1-/Prototypbaseline;
- geschlossener Einmallauf-Runner fuer die gebundenen `20/9/116`;
- unabhaengiger read-only Ergebnisverifikator.

Rohpixel und PCM-Samples werden nur waehrend der Rezeptorreduktion gehalten.
Sie erscheinen weder in Memoryzustaenden noch in Ergebnisbelegen. Die fuenf
Hauptgeschichten verwenden jeweils einen frischen Composite-Zustand und einen
eigenen Story-Owner. Identische leere Anfangszustaende duerfen dabei denselben
Digest besitzen; die Isolation wird nicht durch erfundene unterschiedliche
Zustandsdigests behauptet.

## Einmalige Qualifikation

Qualifikations-ID: `s2jz-qualification-20260902-01`

Genau ein Testaufruf wurde ausgefuehrt:

```text
python -m unittest -v tests.test_s2jz_perceptual_variation_qualification
Ran 12 tests in 0.686s
OK
Exit-Code 0
```

Der aus den materialisierten Rezeptorwerten gemessene auditive A1-Abstand
betrug:

```text
0.00047956059581593546
```

Damit ist A1 nachweislich nicht bitidentisch zu R0, liegt aber innerhalb des
vorab gebundenen Variationsintervalls. Der Wert wurde nicht allein aus der
theoretischen Amplitudenaenderung abgeleitet.

Die Qualifikation bestaetigt ausserdem:

- sechs reale Fixture-Reduktionen mit exakt `48 + 288` Werten;
- unveraenderte Bereiche `20` Formationen, `9` Proben, `116`
  Memory-Operationen und `153120` begrenzte L1-Terme;
- einen kleinen echten atomaren Formation-/Probeweg;
- read-only Zustandsidentitaet bei Probe und direkter Baseline;
- unabhaengige Annahme einer vollstaendigen synthetischen Aufzeichnung;
- Trennung einer auswertbaren funktionalen Falsifikation von
  `NOT_EVALUABLE`;
- fail-closed bei manipuliertem Messungsdigest, Rohpayload und Ueberschreiben.

Alle fuenf Produkt- und Testquellhashes waren vor und nach dem einzigen Lauf
identisch. Es gab keinen Retry und keine Nachkorrektur.

## Aussagegrenze

Der Hauptschalter blieb durchgehend `False`; `AUTHORIZED_RUN_ID` blieb `None`.
Die fuenf vollstaendigen Geschichten und der gebundene `20/9`-Funktionslauf
wurden nicht ausgefuehrt.

Dieser Befund qualifiziert ausschliesslich Fixtures, Messung, Runner und
Verifikator. Er bestaetigt weder perzeptive Identitaet noch Lernen. Ein spaeter
positiver Funktionslauf wuerde zunaechst nur Toleranz gegenueber gezielt
innerhalb vorhandener Schwellen konstruierten, nicht bitidentischen
Wahrnehmungen und gemeinsame Verdichtung zeigen. Die direkte L1-Baseline
bleibt die erwartete vollstaendige Engineeringerklaerung.

