# S1-JL: STOPP gegen wertidentische vollstaendige Modellsichten

## Ergebnis

S1-JL stoppt den Materialisierungsschemavertrag wegen eines Widerspruchs in
S1-JG. Dort werden einerseits wertidentische vollstaendige Modellsichten,
andererseits das Tragen modelleigener Zustaende und fuer P_IE sogar das
Tragen des vollstaendigen S/H-Ausgangs verlangt. Beides kann nach einer
Modelldivergenz nicht gleichzeitig gelten.

## Modellinterne Vorzustaende

Die sieben Rollen besitzen absichtlich getrennte Zustaende:

- DTS-1: private Ressourcenanatomie und eigener gekoppelter Feldausgang,
- B1: fester Vorfreigabeadapter und eigener Feldausgang,
- B2: privater L-Zustand und eigener Feldausgang,
- B3 bis B5: jeweils privater M-Zustand und eigener Feldausgang,
- B6: privater M-Zustand, eingefrorene Spezifikation und eigener Feldausgang.

Bei P_IE muss Intervall 2 den jeweils eigenen vollstaendigen S/H-Ausgang von
Intervall 1 tragen. Bei P_IH, P_IK und P_IN setzen die gemeinsamen Grenzen
nur S/H; der jeweilige private Zustand bleibt erhalten. Diese Zustaende
duerfen weder gleichgesetzt noch zwischen Modellen kopiert werden.

## Gueltige Fairnessgrenze

Modelluebergreifend wertgleich bleiben muss die aeussere Kausalexposition:

- Geometrie und kanonische Knotenordnung,
- registrierte S/H-Quelle bei einer Anfangs- oder Grenzdirektive,
- Rezeptordistribution, Kontaktwerte und gemeinsames Zeitfenster,
- Ereignisreihenfolge, Checkpointlage und physischer Refinementhorizont,
- Ausschluss von Profil-, Arm-, Fall-, Ziel-, Ergebnis- und Sidecarhinweisen
  fuer B1 bis B6.

Der vollstaendige interne Vorzustand wird dagegen pro Modell validiert und
getragen. Faire Exposition bedeutet gleiche Ursache, nicht erzwungenes
Gleichsetzen der unterschiedlichen Modellreaktionen.

## Erforderliche Digesttrennung

Der korrigierte Vertrag benoetigt zwei unabhaengige Rollen:

1. **Common Exposure Digest:** modelluebergreifend identischer, wertbasierter
   Digest aus Geometrie, registrierter Vorzustandsdirektive, Kontakt, Zeit und
   Checkpoint ohne Versuchslabels oder privaten Modellzustand.
2. **Private Prestate Digest:** nur fuer den Orchestrator bestimmter
   modelleigener Provenienzdigest des vollstaendigen getragenen Feld- und
   Modellzustands. Er ist keine Gleichheitsbedingung zwischen Modellen und darf
   weder Fit noch Verzweigung oder gemeinsame Exposition steuern.

Ein einzelner `input_digest` darf diese Rollen nicht zu einer falschen
modelluebergreifenden Identitaetsaussage zusammenziehen.

## Erhaltener Stand

Alle S1-JK-Zeiten, Sequenz-, Intervall- und Carry-Digests bleiben gueltig.
Ebenso erhalten bleiben die nicht zeitbezogenen S1-JH-Fixtures und alle in
S1-JI festgestellten Anforderungen an Identitaeten, API, Wertpayloads und
Atomaritaet. Alle 24 Baselinefaelle bleiben blockiert.

## Entscheidung

`STOPP_COMPLETE_MODEL_VIEW_VALUE_IDENTITY_CONFLICTS_WITH_REQUIRED_MODEL_STATE_CARRY`

Kanonischer Auditdigest:

`2c0876d32b87fed1d76c3dace55708708ff4426728d7fc2d9d7a7871a228038c`

Es wurde kein Materializer, Adapter oder Modell implementiert oder
ausgefuehrt. Der STOPP ist kein Funktionsbefund. Baselinepassung,
Kandidatenueberlegenheit sowie Speicher-, Lern- und KI-Claims bleiben
gesperrt.

## Naechster zulaessiger Schritt

S1-JM darf ausschliesslich den korrigierten statischen Expositions- und
Vorzustandsvertrag mit getrennten Digestrollen binden. Noch keine
Materialisierung, kein Adapter- oder Modellaufruf, keine Runtime und keine
Forschungsprobe.
