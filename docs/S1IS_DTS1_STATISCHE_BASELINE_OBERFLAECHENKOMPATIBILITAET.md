# S1-IS: Statische DTS-1-Baseline-Oberflaechenkompatibilitaet

## Status

S1-IS nimmt die in S1-IQ gestoppte Kompatibilitaetspruefung gegen den
korrigierten S1-IR-Vertrag wieder auf. Geprueft wurden nur Signaturen,
Zustandsrollen, Geometrieannahmen und vorhandene Feldintegrationspfade. Es
wurde kein Adapter implementiert und keine Modellfunktion ausgefuehrt.

Entscheidung:

```text
ALL_SIX_BASELINE_KERNEL_SURFACES_STATICALLY_COMPATIBLE_PRIVATE_ADAPTERS_REQUIRED
```

Auditdigest:

```text
abbced8b76c1fd03259ef01f671db94d03e12896efcfa4c531c7135b8bedf2d7
```

## Kompatibilitaetsmatrix

| Rolle | Zwei Knoten | Drei Knoten | notwendige private Uebergabe |
| --- | --- | --- | --- |
| B1 Fixed Adapter | Kern kompatibel | Kern kompatibel | Informationsbarriere, einmalige Vor-Divergenz-Ableitung, Zeitplan |
| B2 S2-Integrator | Kern kompatibel | Kern kompatibel | S/H/L-Zustand, Generator, Randvektor, Zeitplan |
| B3 F3 Local Leaky | Kern kompatibel | Kern kompatibel | einheitlicher M-Start, F3-Runtime, Zeitplan |
| B4 F3 Linear Coupled | Kern kompatibel | Kern kompatibel | einheitlicher M-Start, F3-Runtime, Zeitplan |
| B5 F3 Full | Kern kompatibel | Kern kompatibel | einheitlicher M-Start, F3-Runtime, Zeitplan |
| B6 CONST-V | Kern kompatibel | Kern kompatibel | eingefrorene Spezifikation, Zwei-Knoten-Handoff, M-Start, F3-Runtime, Zeitplan |

B1 darf das originale DTS-1-Anatomieobjekt nicht erhalten. Ein privater
Adapter muss ausschliesslich den gemeinsamen leitenden Zustand vor der
Armdivergenz in einen einmal fixierten Kantenratenbestand ueberfuehren.
Freie, refraktaere oder transferierte Ressource bleibt unsichtbar.

B2 akzeptiert beliebig lange, gleich geformte S/H/L-Vektoren sowie einen
passenden symmetrischen Generator und Randvektor. L bleibt eine eigene
Baseline-Zustandsrolle und muss ohne DTS-1-Zustandsinformation initialisiert
werden.

B3 bis B6 koennen ihre unveraenderten Kopplungsrechner ueber die vorhandene
generische F3-Runtime zu vollstaendigen S/H-Feldzustaenden integrieren. Die
vorhandene CONST-V-Kernspezifikation ist geometrieunabhaengig; nur der
bisherige E1-E4-Handoff ist auf drei Knoten begrenzt und benoetigt fuer S1-IS
eine private Zwei-Knoten-Form.

## Aussagegrenze

Oberflaechenkompatibilitaet ist keine ausfuehrbare Komposition. Noch offen
sind Adaptervalidierung, ein Konfigurationsdigest je Baseline, numerische
Zulaessigkeit aller Intervalle, Profilrekonstruktion und Kontrollen. Der
Befund schliesst oder verwirft keine Baseline und stuetzt keine
Kandidatenueberlegenheit.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1is_baseline_surface_compatibility.py
tests/test_dynamic_substrate_s1is_baseline_surface_compatibility.py
```

Neun Tests pruefen Quellenbindung, beide Geometrien, alle sechs Rollen, die
B1-Informationsbarriere, B2-L-Rolle, den vorhandenen F3-Integrationspfad,
die CONST-V-Handoff-Grenze, Ausfuehrungsfreiheit und Manipulationsschutz.

## Bester naechster Schritt

S1-IT darf ausschliesslich einen statischen privaten Adaptervertrag binden.
Er muss fuer B1 bis B6 Eingaben, Ausgaben, Zustandsinitialisierung,
Geometrieabbildung, Zeitplanabbildung, Konfigurationsidentitaet und
Fail-Closed-Regeln vor jeder Implementierung festlegen. Noch keine
Parameterwahl, Adapterimplementierung, Modellausfuehrung, Runtime oder
Forschungsprobe.
