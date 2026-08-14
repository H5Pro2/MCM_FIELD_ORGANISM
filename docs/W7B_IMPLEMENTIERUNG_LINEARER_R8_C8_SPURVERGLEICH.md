# W7-B: Implementierung des linearen R8/C8-Spurvergleichs

Stand: 2026-08-09

Entscheidung: `LINEAR_RECIPROCAL_TRACE_SUFFICIENT`

Arbeitsart: additive technische In-Memory-Implementierung

Browser gestartet: nein

Report geschrieben: nein

Formaler Memory-Forschungslauf: nein

## Implementierungsfrage

Kann der in W7-A gebundene R8/C8-Vergleich B0, eine echte einseitige B1-Spur,
den Produktions-S1-B-Pfad und eine unabhaengige B2-Rechnung auf denselben
reduzierten Rezeptorkontakten vergleichen, ohne den neutralen Pfad zu aendern
oder Trajektorien zu persistieren?

## Implementierung

`mcm_field_organism/w7b_linear_history_discrimination.py` stellt bereit:

- `W7BLinearHistoryDiscriminationResult`;
- `run_w7b_linear_history_discrimination()`;
- einen temporaeren B1/B2-Referenzzustand auf den vorhandenen
  S2-C11-R8/C8-Kontakten;
- einen unabhaengigen allgemeinen Matrixexponentialpfad fuer B2;
- ein rein skalares unveraenderliches Rueckgabeobjekt.

B1 und die unabhaengige B2-Rechnung werden nicht als
`SharedMCMField.development` serialisiert. Dadurch wird die einseitige
Kontrollspur nicht faelschlich als S1-B-Naturvertrag ausgegeben.

Der Produktions-B2-Arm verwendet weiterhin die bestehende transiente
S1-B-Runtime. Die Referenzarme erhalten dieselben lokalen Kontakte,
Zeitpunkte, Diffusionsgeometrie, Feldparameter und dieselbe externe
S/H-Angleichung. Referenztrajektorien existieren nur waehrend des Aufrufs und
werden weder zurueckgegeben noch geschrieben.

## Technische Kontrollen

```text
R8-Formationssupport:       871
C8-Formationssupport:       871
Probe-Observerzeitpunkte:   31
B0 exakt:                   true
B1 ohne spaetere S/H-Wirkung: true
B2-Produktion reproduziert: true
endliche Skalare:           true
Browser gestartet:          false
Report geschrieben:         false
Rohtrajektorien behalten:   false
```

30 fokussierte W7-/S2-/S1-B-/API-Tests bestehen.

## Skalare technische Auswertung

```text
l_pair_b1:          0.0003494374659592271
l_pair_b2:          0.000217462367578386
d_pair_b0:          0.0
d_pair_b1:          0.0
d_pair_b2:          0.00001649978068007929
b2_reference_error: 0.00000000000004570128997460898
Toleranz:            0.000000000002
Resultatdigest:      35b25585bb5ad4d11632a7eb1cc1fa2ecd464565533ef3061859beb3419df040
```

B1 bildet unterschiedliche R8/C8-L-Lagen, kann diese nach der externen
S/H-Angleichung aber nicht auf die spaetere Probe zurueckwirken lassen. B2
erzeugt einen aufgeloesten Probeunterschied. Der Produktions-S1-B-Pfad und
die unabhaengige B2-Rechnung stimmen weit innerhalb der vorregistrierten
Toleranz ueberein.

## Entscheidung

`LINEAR_RECIPROCAL_TRACE_SUFFICIENT` bedeutet hier:

```text
zeitlich unterschiedlich gegliederter Weltkontakt
-> unterschiedliche lineare L-Spur
-> durch feste reziproke L-nach-S-Kopplung unterschiedliche spaetere S/H-Lage
```

Der beobachtete R8/C8-Unterschied benoetigt die Rueckwirkung, aber keine
zusaetzliche Substratfunktion jenseits des festen linearen Zweizeitensystems.
S1-B ist damit eine technisch funktionierende und unabhaengig bestaetigte
Referenzspur. Es ist kein eigenstaendiger MCM-Memorykandidat.

## Aussagegrenze

W7-B belegt keine Praegung im engeren Sinn, keine Verdichtung, keine
zustandsabhaengige Feldzeit, keine Rekonstruktion, kein funktionales
Vergessen, keine Kapazitaetswiederverwendung, keine Organisation, Semantik,
Selbstregulation oder KI.

Der Befund beendet nicht das Projektziel. Er zeigt konkret, dass der fuer
Memory benoetigte naechste Freiheitsgrad nicht durch weitere Auswertung der
unveraenderten linearen S1-B-Spur entstehen kann.

## Bester naechster Schritt

W7-C bindet vor jeder neuen Gleichung den minimalen Funktions- und
Ressourcenunterschied gegen S1-B/B2. Ein neuer Kandidat muss mindestens
lineare Superposition brechen, lokale Verdichtung und spaetere Loesung aus
derselben homogenen Mechanik tragen sowie freigewordene begrenzte Kapazitaet
anderswo wieder nutzbar machen. W7-C implementiert noch keinen Kandidaten.
