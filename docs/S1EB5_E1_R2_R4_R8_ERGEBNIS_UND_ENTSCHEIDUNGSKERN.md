# S1-EB5: E1-r2/r4/r8-Ergebnis- und Entscheidungskern

## Status

Der private Ergebnis- und Entscheidungskern fuer den S1-EB-Korridor ist
implementiert und nur mit synthetisch konstruierten Resultaten abgenommen.
Er ruft keine Runtime auf, schreibt keine Datei und verwendet keinen
kanonischen Feld- oder Probeausgang.

## Implementierung

```text
mcm_field_organism/e1_confirmation_result_core.py
tests/test_e1_confirmation_result_core.py
```

Normalisierter Implementierungsdigest:

```text
614c8ee2e2a6a3e84314b073a0af0ea641e66b1ca6373f7526799fd26a2a08a6
```

## Ergebnisgrenze

Ein gueltiges Resultat muss geordnet `r2`, `r4` und `r8`, je fuenf
Bildungszustandsdigests, sieben Probefelddigests, die vollstaendige
S1-EB4-Metrikoberflaeche und alle elf Pflichtkontrollen enthalten. Die vier
feinen Hauptmetriken muessen exakt mit dem `r8`-Resultat uebereinstimmen.

Exakte Kontrollen und zugehoerige Residuen duerfen sich nicht
widersprechen. Der Ressourcenbilanzfehler darf `1e-12` nicht ueberschreiten.

## Entscheidungsregel

Die Reihenfolge ist unveraendert:

1. Eine falsche Pflichtkontrolle ergibt `TECHNICALLY_INVALID`.
2. Exakt null fuer Zustand und beide Probensignale in allen drei
   Verfeinerungen ergibt `NO_CONFIRMED_REFINED_EFFECT`.
3. Nur konvergierende Reststufen und `r8`-Signale, die strikt groesser als
   das Achtfache ihres passenden `r4/r8`-Rests sind, ergeben
   `CONFIRMED_REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT`.
4. Jeder andere technisch gueltige Ausgang ergibt
   `NUMERICALLY_UNDECIDABLE`.

Die synthetische Gleichheitskontrolle bestaetigt ausdruecklich:

```text
Signal = 8 * Rest  -> NUMERICALLY_UNDECIDABLE
```

## Synthetische Referenzen

```text
CONFIRMED_REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT
b2d9743e205afbdeffca9b54cdf32bd3add1e073ca7719ea36eea78b1785a661

NO_CONFIRMED_REFINED_EFFECT
f7cd9a514b4726ca08eb6daa72bcb834e9b0b6066038f837761582288a575647

NUMERICALLY_UNDECIDABLE
254dfde04de8c14b75513145d73d0d4dac5ca609e41aaf54360805ed518d0ce0
```

Diese Digests stammen aus konstruierten Testwerten und sind keine
Forschungsergebnisse.

## Technische Abnahme

```text
9 fokussierte S1-EB5-Tests
456 Tests im vollstaendigen E1-Verbund
OK
```

Die registrierten S1-EB-Ergebnis-, Attempt- und Lockpfade bleiben frei.

## Aussagegrenze

S1-EB5 beweist nur die korrekte Anwendung der vorregistrierten
Entscheidungsregel auf vollstaendige Ergebnisobjekte. Es liefert keinen
kanonischen Zustands-, Transfer-, Memory-, Semantik-, Organisations-,
Topologie-, Selbstregulations- oder KI-Befund.

## Anschluss

S1-EB6 hat den privaten synthetischen siebenarmigen Probeadapter fuer die
neuen `r2/r4/r8`-Bildungsergebnisse implementiert. Eingefrorene E1-
Zustaende, Ablation und Fixed-Adapter sind exakt kontrolliert; kanonische
Probe und S1-EB-Pfade blieben gesperrt. Siehe
[S1-EB6 synthetischer siebenarmiger Probeadapter](S1EB6_E1_SYNTHETISCHER_SIEBENARMIGER_R2_R4_R8_PROBEADAPTER.md).
