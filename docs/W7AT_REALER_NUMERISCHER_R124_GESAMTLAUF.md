# W7-AT: Realer numerischer R1/R2/R4-Gesamtlauf

## Status

W7-AT ist real abgeschlossen.

Der bestehende 36-Phasen-Koordinator wurde in der Primaerfolge R1/R2/R4 und
im Gegenlauf R4/R2/R1 vollstaendig ausgefuehrt. Der Abschluss wurde im selben
Prozess ueber W7-AS an W7-AP und W7-AR uebergeben. Es wurde kein W7-Report
geschrieben.

## Laufzeit

```text
Gesamte Shell-Laufzeit: 5576,3 Sekunden
                       92 Minuten 56,3 Sekunden
Kanonischer Vorlauf:   445,3013531 Sekunden
```

Die tatsaechliche Laufzeit lag damit ueber dem historischen Richtwert von
rund 76 Minuten.

## Kanonische Eingangs- und Containerdigests

```text
CAP:
b70a4b4563bb73d50685d1a8475376f0b00377d72369c030027f44f2725af013

Mess-Handoff:
898e94bdbc2b5b0f893c5c512a684fd15544845d25de1a97febc83ffc8bcccd8

CAP/P0-Rohkontrast:
ca047546d37a0ebd5728ee6adcf27d083c2a7fce3aad82f882284f08629f1fc3

W7-AN-R1/R2/R4-Container:
4f150aad9f5c3803f1432550aa4db79b40aea3f7a4975b49802694fad2fff3e5
```

Alle sechs Primaer-/Gegenlauf-Aufloesungsabschluesse wurden erreicht. Der
Container reproduziert den bereits nachgewiesenen kanonischen Digest.

## W7-AP- und W7-AR-Ergebnis

Die kompakte reine Wiedergewinnung der bereits bestaetigten drei
Primaeraufloesungen reproduzierte den kanonischen Container und lieferte die
exakten Abschlusswerte:

```text
W7-AP-Kompositionsdigest:
901b86f140c515787f35cbabcaf00f5c4983acbe18fbe83b3dc5520c7ebb2b3d

W7-AR-Auswertungsdigest:
b6ff73ac1b85344a5aa925506dba599bb9b3956abeb4eca0e6b0f9e63087b99c

W7-AS-Terminaldigest:
7a65a8926b328a27743c535f35d53552440ee584cb9600c10078b08743e25a20
```

Die Wiedergewinnung dauerte 2.544,626 Sekunden. Sie wiederholte nicht den
Gegenlauf und ist kein zweiter Forschungslauf; sie diente nur dazu, die in
der langen Terminalausgabe abgeschnittenen Abschlusskennwerte exakt sichtbar
zu machen.

## Numerisches Ergebnis

```text
outcome = RESOLUTION_COMPARISON_CONVERGED
all_components_converged = true
component_count = 70
failed_component_count = 0
exact_zero_exception_count = 0
epsilon_num = 1.891576895118874e-08
effect_floor = 1.8915768951188738e-07
```

Alle 35 Rollen bestehen fuer S-Linf und H-Linf die vorregistrierte strikte
Regel `D24 < D12`. Keine Komponente benoetigt die exakte Doppelnullausnahme.
Der numerische Boden ist das Maximum aller 70 R2/R4-S/H-Linf-Distanzen; der
Effektboden ist vorregistriert dessen Zehnfaches.

## Zulassige Aussage

W7-AT weist ausschliesslich nach:

- der kanonische CAP/P0-Rohkontrast ist ueber R1/R2/R4 nach der gebundenen
  rollenweisen Regel numerisch aufgeloest;
- die Verfeinerungsdifferenzen schrumpfen in allen 70 Primaerkomponenten;
- Numerik- und Effektboden koennen fuer spaetere gebundene Vergleiche
  verwendet werden.

## Nicht zulassige Aussage

```text
field_function_decision_allowed = false
memory_claim_allowed = false
```

LEAK, LIN, F3, CONST-V, SAT, MOB, NORM, ETA0, KAPPA0 und SIGN wurden in
diesem Container nicht verglichen. Daher folgt aus W7-AT kein Nachweis einer
kapazitaetsspezifischen Feldfunktion, Freisetzung, Wiederverwendung,
Praegung, Memory, Feldzeit, Organisation, Semantik, Selbstregulation oder
KI.

## Naechster Schritt

W7-AU muss vor jeder weiteren teuren Ausfuehrung statisch klaeren, welche
der zehn fehlenden W7-L-Gegenbaselines im bestehenden Projekt bereits
implementiert und kanonisch anschlussfaehig sind und welche technische
Materialisierung noch fehlt. Erst daraus darf ein minimaler, nicht
redundanter Funktionsvergleich abgeleitet werden.
