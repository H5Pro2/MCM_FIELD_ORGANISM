# S1-JR: Korrigierter rollenspezifischer Refinementvertrag

## Ergebnis

S1-JR loest den S1-JQ-STOPP ohne neue Uhr, neue Gleichung oder neuen
Integrator. Die Labels r2, r4 und r8 bleiben fuer alle sechs Baselines
erhalten, ihre technische Bedeutung wird jedoch an die vorhandene
Kernoberflaeche gebunden.

## B1 und B2: exakte Vollintervallkontrollen

B1 verwendet eine geschlossene spektrale S/H-Auswertung. B2 `model-b2`
verwendet eine deterministische Matrixexponentialauswertung. Beide Kerne
werten das vollstaendige S1-JO-Intervall direkt aus und besitzen keinen
Refinementparameter.

Fuer diese Rollen sind r2, r4 und r8 daher unabhaengige
Bitgleichheitskontrollen:

- Jede Kontrolle beginnt mit demselben unveraenderlichen Feld und privaten
  Kontext.
- Der gebundene Kern wird genau einmal ueber das vollstaendige Intervall
  aufgerufen.
- Kein Ausgang und kein privater Zustand wird zwischen den Labels getragen.
- Das Label gelangt nicht in Kerninput, Outputdigest oder modelleigene
  Diagnostik.
- Vollstaendiges Feld, naechster privater Zustand, Diagnostik und Outputdigest
  muessen fuer r2, r4 und r8 bitgleich sein.

Jede Abweichung ist ein Determinismus- oder Adapterfehler. Toleranzanpassung,
Retry oder Auswahl eines guenstigen Labels sind verboten.

## B3 bis B6: natives Refinement

B3 bis B6 reichen den jeweiligen Wert 2, 4 oder 8 direkt an den bestehenden
Refinementparameter der F3-Runtime weiter. Alle drei Auswertungen beginnen
unabhaengig mit demselben Vorzustand. Die internen Numerikstufen erzeugen
keine sichtbaren Zwischenzeiten im `SharedMCMField`.

Die bereits materialisierte S/H-Grenze und die Rezeptordistribution wirken
genau einmal ueber das vollstaendige physische Fenster. Jeder Level liefert
einen Feldabschluss am urspruenglichen S1-JO-Endtick. Vollstaendige
vorzeichenbehaftete r2-r4- und r4-r8-Residuals bleiben verpflichtend.

## Erhaltene Bindungen

Die Korrektur ersetzt nur die universelle Unterfensterforderung aus S1-JP
fuer B1 und B2 und spezialisiert die entsprechende S1-JK-Formulierung auf
Kerne mit nativem Refinement. Erhalten bleiben:

- die Labels 2, 4, 8 und der Primaerlevel 4 aus S1-JA,
- identische Eingaben, Dauern, Kontakte und Grenzen aller Kontrollen,
- alle S1-JK-Zeiten, Envelope-, Sequenz-, Intervall- und Carry-Digests,
- alle Informations-, Privatstatus-, Ausgabe-, Neutral- und Fail-Closed-
  Regeln aus S1-JP,
- alle bestehenden Kerne und Gleichungen unveraendert.

## Entscheidung

`ROLE_SPECIFIC_EXACT_AND_NATIVE_REFINEMENT_CONTRACT_BOUND_NO_IMPLEMENTATION_OR_EXECUTION`

Kanonischer Vertragsdigest:

`1314e59ef30722c04cf992a88a25c94dd8aedb930dba6c94c20c1fca71f6c2b8`

Es wurde kein Adapter implementiert, kein Modellkern aufgerufen und kein
technischer oder forschungsbezogener Feldschritt ausgefuehrt. Numerische
Zulaessigkeit, Baselinepassung und Kandidatenueberlegenheit sind nicht
gezeigt. Speicher-, Lern- und KI-Claims bleiben gesperrt.

## Naechster zulaessiger Schritt

S1-JS darf ausschliesslich die privaten Adapterkontexte, atomaren
Ausgaberecords und sechs Baselinebruecken gemaess S1-JP und S1-JR
implementieren. Tests duerfen synthetische technische Einzelintervalle und
unabhaengige Kontrollreplikate verwenden. Noch kein Profilfall der
24-Fall-Matrix, kein gemeinsamer Vergleich, keine Runtime oder
Forschungsprobe.
