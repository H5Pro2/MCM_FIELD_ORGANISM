# S1-NG KFS-1/T1 Einkantenimplementierung und Abnahme

## Status

S1-NG implementiert ausschliesslich die in S1-NF gebundene Regel
`KFS1-T1_LOCAL_TARGET_REFRACTORY` fuer genau eine lokale Kante. Das Modul
`mcm_field_organism/kfs1_t1_transition.py` ist rein funktional, parameterfrei
und von Feldklasse, Runner, Audio-/Video-Pfad und DTS-1-Implementierung
getrennt.

S1-NG ist kein Feldlauf und kein Funktionsnachweis. Der Schritt prueft nur,
ob die vorab gebundene lokale Ressourcenbuchung deterministisch,
ressourcenerhaltend und ohne ungebundene Seiteneingaenge ausfuehrbar ist.

## Implementierte Grenze

Die Implementierung akzeptiert:

- genau ein geschlossenes Kantenledger mit `capacity`, `free`, `bound` und
  `blocked`;
- genau zwei aktuelle schnelle Feldwerte im gebundenen Bereich `[-1, 1]`;
- die parameterfreie lokale Beteiligung `p=((S_i-S_j)/2)^2`;
- genau einen atomaren T1-Uebergang mit einzeln sichtbaren Bruttotransfers.

Sie verwirft nicht endliche, negative oder nicht exakt erhaltene Ledger,
ungueltige Feldwerte und unvollstaendige Eingaben vor der Ausgabe. Eingabe,
Nachzustand, Transfers und Ergebnisrecord sind unveraenderlich.

Nicht enthalten sind:

- Feldrueckwirkung oder Mehrkantenkopplung;
- Runner-, Zeit- oder Dateisystemzugriff;
- Parameter, Raten, Schwellen, Optimierung oder Fit;
- H, Labels, Reward, Zielwerte, Rohdaten oder Readout;
- DTS-1-Code oder eine Baselineentscheidung.

## Einmalige fokussierte Abnahme

Die Abnahme wurde genau einmal ausgefuehrt:

```text
python -m unittest tests.test_kfs1_s1ng_t1_transition
............
----------------------------------------------------------------------
Ran 12 tests in 0.008s

OK
```

Die zwoelf Tests decken die acht vorregistrierten Ledgerprognosen sowie
Symmetrie und Wertebereich der lokalen Beobachtung, Unveraenderlichkeit und
Erhaltung, Importisolation und Abwesenheit einer Laufzeit- oder
Feldschritt-API ab. Dabei wurden elf T1-Uebergaenge und null MCM-Feldschritte
ausgefuehrt.

## Gebundene Dateidigests

```text
mcm_field_organism/kfs1_t1_transition.py
SHA256 2A5C04819B14AEC5B574591DEF8D6191DD3D67DE7E6F19BEB15D8F3E52693AD4

tests/test_kfs1_s1ng_t1_transition.py
SHA256 B6B895F69F9E9B16CF4A18DA8A2CFE2F15F3B36F3AF2EB63ABB8AC5A9CB1BE18
```

## Technischer Befund

Die Regel erfuellt innerhalb der isolierten Abnahme ihre acht lokalen
Ledgerprognosen. Insbesondere wird neu blockierte Ressource nicht im selben
Nullkontakt freigegeben, positiver Kontakt gibt blockierte Ressource nicht
frei, und ein fremdes Kantenledger beeinflusst das gepruefte Ergebnis nicht.

Damit ist nur gezeigt, dass T1 als wohldefinierte lokale Buchungsregel
implementierbar ist. Noch offen ist, ob ihre endliche Folgegeschichte eine
eigene technische Gegenprognose gegen DTS-1 traegt und ob spaeter eine
begruendete Feldrueckwirkung formulierbar ist.

## Aussagegrenze

S1-NG begruendet keine Feldwirkung, keine Lernfunktion, keine vorhandene
Memory-Faehigkeit und keinen Systemfaehigkeitsclaim. Hypothetische MCM-Memory
bleibt eine offene Entwicklungsrichtung, deren notwendige funktionale
Evidenz hier nicht erhoben wurde.

## Naechster erlaubter Schritt

S1-NH darf ausschliesslich einen endlichen, feldfreien Sequenz- und
DTS-1-Gegenbaselinevertrag binden. Vor jeder Ausfuehrung muessen fuer dieselbe
lokale Beteiligungsfolge, denselben gueltigen Anfangszustand und dieselben
Ledger-Readouts feststehen:

- die konkrete T1-Folgeprognose;
- eine endliche, vorab registrierte DTS-1-Profilmenge ohne Fit;
- das Aequivalenz- und Redundanzkriterium;
- die Verwerfungsbedingung fuer T1;
- die weiterhin gesperrte Feldrueckwirkung.

S1-NH fuehrt noch keine Sequenz, Baseline oder Feldmechanik aus.
