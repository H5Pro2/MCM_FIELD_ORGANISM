# S1-VY: Statischer PPB-1-Produktions-Ressourcenmess- und Gatevertrag

## Auftrag und Grenze

S1-VY bindet vor jeder Messimplementierung, wie der Ressourcenbedarf der
privaten PPB-1-Einmallaufhuelle kalibriert und spaeter in H0 geprueft werden
muss. Der Vertrag ist als kanonisches JSON festgehalten:

[S1-VY Ressourcenvertrag v1](S1VY_PPB1_PRODUKTIONS_RESSOURCENMESS_UND_GATEVERTRAG_V1.json)

S1-VY fuehrt keine Ressourcenabfrage, Fixturekonstruktion, Pipelinefunktion,
Matrix, Produktionsverdrahtung oder Autorisierung aus.

## Kalibriergrundlage

Eine spaetere Kalibrierung muss genau drei getrennte frische Prozesse
verwenden. Jeder Prozess darf nur die vorhandene konstruierte
528-Receipt-/75.808-Beobachtungs-Fixture durch die synthetische Handoff- und
S1-VT-Pipeline fuehren. Der reale S1-VQ-Producer und alle registrierten
Matrixpfade bleiben gesperrt.

Jede Replik bindet:

- Python-Implementierung und -Version;
- Betriebssystem, Maschinenarchitektur und Pointerbreite;
- Quellcodedigests von S1-VQ, S1-VT, S1-VW und dem spaeteren
  Kalibrierungsmodul;
- Prozess-RSS vor der Fixture sowie Peak-RSS nach Fixture, Versiegelung,
  Komposition, Auswertung und Serialisierung;
- groessten RSS-Zuwachs gegenueber dem Startwert;
- Bytegroessen von Lock-, Erfolgs- und temporaerem Artefakt;
- freien Speicherplatz auf dem Artefaktvolume vor und nach der Replik;
- erfolgreichen atomaren Replace-Test auf demselben Volume.

Eine fehlende Stufe, ein negativer oder inkonsistenter Zaehler oder eine
fehlgeschlagene Replik macht die gesamte Kalibrierung ungueltig. Mittelwerte
werden nicht verwendet; fuer Speicher und Artefakte gilt jeweils das Maximum
aller drei Repliken.

## Gebundene Sicherheitsreserven

Alle Werte werden auf volle MiB aufgerundet.

Fuer unmittelbar frei verfuegbaren physischen Speicher gilt:

```text
M_peak = groesster gemessener RSS-Zuwachs

M_min = max(
    2 * M_peak,
    M_peak + 512 MiB,
    2 GiB
)
```

Fuer freien Speicherplatz auf dem spaeteren Artefaktvolume gilt:

```text
A_peak = max(groesstes Erfolgsartefakt, groesster Temporaerstand)

D_min = max(
    3 * A_peak,
    A_peak + 512 MiB,
    1 GiB
)
```

Die Faktoren decken Prozessschwankung, gleichzeitige In-Memory- und
Serialisierungsrollen sowie temporaere und terminale Dateistaende ab. Die
absoluten Untergrenzen verhindern, dass ein zufaellig kleiner Messwert zu
einem zu schwachen Gate fuehrt. Historische Ressourcenwerte abgeschlossener
Zweige werden nicht uebernommen.

## Spaeteres H0-Ressourcengate

Ein spaeteres Produktions-H0 darf nur bestehen, wenn unmittelbar gemeinsam
gilt:

- Quellcodedigests und Plattformbindung stimmen bitgleich mit der
  Kalibrierung ueberein;
- frei verfuegbarer physischer Speicher ist mindestens `M_min`;
- freier Speicherplatz auf dem Artefaktvolume ist mindestens `D_min`;
- Lock-, Success-, Error- und Temporaerpfade sind frei;
- Temporaer- und Terminalpfad liegen auf demselben Volume;
- atomarer Replace ist dort nachgewiesen;
- Mess-, Kalibrierungs- und Ressourcengatedigests sind gueltig.

Jede Abweichung stoppt vor H1. Dabei wird keine Autorisierung verbraucht und
kein Producer gestartet. Nach einem spaeter erfolgreich angelegten H1-Lock
bleibt ein Retry dagegen auch bei Ressourcen- oder Publikationsfehler
verboten.

## Kanonische Bindung

```text
Schema:
ppb1.s1vy.production-resource-contract.v1

S1-VX-Elterndigest:
a52bb0c852769591aee47dcfce399d6f99a82632e53cd9beb51842f1385e27e5

S1-VY-Vertragsdigest:
ed2872f48ef83b26121bc68ce99ff75462cef9fc60915a7b5b073c45744992cd
```

Der Digest wird aus dem JSON-Inhalt mit sortierten Schluesseln und kompakten
UTF-8-JSON-Trennzeichen gebildet. Dateieinrueckung und Zeilenenden besitzen
keine Digestrolle.

## Entscheidung

```text
S1_VY_EXACT_THREE_CLEAN_SYNTHETIC_CALIBRATION_REPLICATES_BOUND
S1_VY_PLATFORM_AND_SOURCE_BINDING_BOUND
S1_VY_STAGEWISE_RSS_AND_ARTIFACT_MEASUREMENTS_BOUND
S1_VY_MAXIMUM_ONLY_AGGREGATION_BOUND
S1_VY_MEMORY_AND_DISK_SAFETY_FORMULAS_BOUND
S1_VY_SAME_VOLUME_ATOMIC_REPLACE_GATE_BOUND
S1_VY_H0_FAIL_CLOSED_BEFORE_AUTHORIZATION_CONSUMPTION_BOUND
S1_VY_NO_HISTORICAL_RESOURCE_FLOOR_REUSE_BOUND
S1_VY_NO_RESOURCE_MEASUREMENT
S1_VY_NO_MATRIX_OR_PIPELINE_EXECUTION
S1_VY_NO_PRODUCTION_BINDING_OR_AUTHORIZATION
```

S1-VY schliesst den Ressourcenvertrag, aber noch nicht den S1-VX-Blocker
`PRODUCTION_RESOURCE_GATE_AND_MINIMA_MISSING`: Reale Minima und ein
Kalibrierungsdigest entstehen erst durch die spaetere synthetische Abnahme.

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-VZ - private synthetische Ressourcen-Kalibrierung und Gatevertragsabnahme
```

S1-VZ darf den privaten Kalibrierer implementieren und exakt drei frische
synthetische Prozesse ausfuehren. Zulaessig sind nur konstruierte Receipts,
temporaere Testartefakte und Ressourcenmessungen nach diesem Vertrag. Reale
S1-VQ-Pfade, Produktionsartefakte, Produktionsentry, Autorisierung sowie
Feld- und Medienruntime bleiben gesperrt.

## Grundlagen

- [S1-VX Post-Integrations- und Ressourcen-Preflight](S1VX_PPB1_STATISCHER_POST_INTEGRATIONS_UND_RESSOURCEN_PREFLIGHT.md)
- [S1-VW synthetische Einmallaufhuelle](S1VW_PPB1_PRIVATE_SYNTHETISCHE_EINMALLAUF_HANDOFF_UND_TERMINALHUELLEN_ABNAHME.md)
- [S1-VV Einmallauf- und Handoffvertrag](S1VV_PPB1_STATISCHER_EINMALLAUF_HANDOFF_ERGEBNIS_UND_FEHLERVERTRAG.md)
