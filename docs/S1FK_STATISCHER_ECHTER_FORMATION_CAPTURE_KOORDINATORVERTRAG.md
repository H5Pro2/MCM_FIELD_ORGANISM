# S1-FK: Statischer echter Formation-Capture-Koordinatorvertrag

## Gebundene echte Kette

S1-FK bindet die Schnittstellen fuer den spaeteren nicht persistenten Lauf:

1. S1-FI unmittelbar mit aktuellem RAM erneut pruefen;
2. exakt gebundenen Besitzer-Token einmal verbrauchen;
3. vorhandene Fuenf-Arm-Formation fuer r2, r4 und r8 ausfuehren;
4. alle 15 Ergebnisse atomar an S1-FF uebergeben;
5. die 15 Vektoren einmal mit S1-FD auswerten;
6. nur einen vollstaendigen In-Memory-Befund zurueckgeben.

Der vorhandene Fuenf-Arm-Runner prueft pro Verfeinerung Identitaetswiederholung,
beide Bildungsablationen, Objekttrennung, Feldkontrollen und Ressourcenbilanz.
S1-FK fuehrt ihn noch nicht aus.

## Autorisierungsgrenze

Der spaetere Token akzeptiert nur folgenden exakten Besitzertext:

```text
Ich gebe genau einen nicht persistenten S1-FK Formation-Capture-Lauf mit maximal 14.000 Feldschritten frei. Kein Retry, keine Nachparametrierung und keine Probe. Die Ausfuehrung darf nur starten, wenn der S1-FI-Preflight unmittelbar vor dem ersten Formation-Arm erneut vollstaendig besteht.
```

Der Token wird an S1-FK-Vertragsdigest und aktuellen S1-FI-Preflightdigest
gebunden. Er darf genau einmal und erst nach bestandener unmittelbarer
RAM-Pruefung verbraucht werden. `ok weiter` wird abgelehnt.

## Grenzen

Der Vertrag autorisiert keine Ausfuehrung. Probe, Persistenz, Retry,
Nachparametrierung und Teilrueckgabe bleiben geschlossen. Bei jedem Fehler
gibt es keinen Forschungsbefund. Memory, Feldzeit, Organisation, Semantik,
Selbstregulation und KI bleiben unbelegt.

Entscheidung:
`REAL_COORDINATOR_CONTRACT_BOUND_AWAITING_IMPLEMENTATION_AND_OWNER_AUTHORIZATION`.

## Bester naechster Schritt

Am besten geht es mit S1-FL weiter: den echten Koordinator entsprechend diesem
Vertrag implementieren und mit injizierten, zaehlenden Testadaptern abnehmen.
Die echte Formation bleibt bis zur separaten exakten Besitzerautorisierung
unausgefuehrt.
