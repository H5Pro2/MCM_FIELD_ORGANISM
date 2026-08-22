# S1-VA: Statischer Kandidatenraumaudit lokaler technischer Ursachen

## Freigabe und Grenze

S1-VA setzt die ausdrueckliche Freigabe fuer einen statischen
Kandidatenraumaudit um. Verglichen werden mehrere moegliche lokale Ursachen.
Der Audit legt keine Mechanik, Gleichung, Parameter, Zustandsdarstellung,
Runtime, Feldintegration oder Ausfuehrungsmatrix fest.

Fuer jeden Vorschlag werden ausschliesslich folgende Rollen geprueft:

1. lokale technische Ursache;
2. begrenzter Zustand oder Bilanz;
3. Erreichbarkeit durch normale Feldgeschichte;
4. spaetere eigene Feldwirkung;
5. staerkste Gegenbaseline;
6. eindeutige Stoppbedingung.

Die Begriffe bezeichnen technische Pruefrollen. S1-VA liefert keinen Befund
fuer eine hypothetische MCM-Memory und keine Freigabe zur Implementierung.

## Ausgangsgrenze des Projektbestands

Bereits geschlossen oder als Baseline gebunden sind:

- einzelne lokale Leaky-Spuren, Integratoren und Retentionszustaende;
- feste oder adaptive Gains und Mobilitaeten;
- F3 sowie konservierte skalare Traeger;
- DTS-1/T1, G2/D3 und Capacity-Clamp;
- relationale Kanten- und Kantenmotivzustaende aus RFM-1 und ACM-1H sowie
  ihre CGR-1-Reduktion;
- passive Viskoelastik, Hysterese, Phasenfeld, Reaktions-Diffusion,
  Standardmaterial und adaptive Topologie;
- LRD-E1 und weitere geschichtsabhaengige lokale Dispositionswerte mit
  festem Leser.

Ein neuer Name fuer eine dieser Rollen ist kein neuer Kandidat.

## Anatomischer Ausgangspunkt

Der aktive Feldkern besitzt eine feste explizite zweidimensionale Geometrie.
Die kontrollierte Audio-Video-Feldstrecke verwendet symmetrische orthogonale
Nachbarschaftsoffsets. Die visuelle Dockanatomie umfasst ein rechteckiges
lokales Raster. Damit existieren in hinreichend grossen Ausschnitten
elementare geschlossene Nachbarschaftsschleifen.

Diese Schleifen werden nicht durch Wahrnehmung erzeugt und duerfen nicht
veraendert werden. Sie sind lediglich aus der vorgegebenen Anatomie
ableitbare lokale Pruefmotive.

## Kandidat K1: Lokal umverteilbarer skalarer Kopplungstraeger

| Pruefrolle | Audit |
|---|---|
| lokale Ursache | lokaler Feldfluss verschiebt einen endlichen skalaren Traeger zwischen benachbarten Orten |
| Bilanz | feste nichtnegative Gesamtmenge, lokaler Gewinn nur gegen lokale Abgabe |
| Feldgeschichte | normale lokale Flussgeschichte kann die Verteilung erreichen |
| spaetere Feldwirkung | veraenderte Verteilung beeinflusst spaetere lokale Kopplung |
| staerkste Gegenbaseline | F3, adaptive Mobilitaet, DTS-1/G2 und umverteilbare Leitfaehigkeit |
| Stoppbedingung | vollstaendige Rekonstruktion durch eine dieser Baselines |

Urteil: `BASELINE_EQUIVALENT`. Diese Rolle wurde in S1-AB bereits statisch
geschlossen. Die Bilanz ist sauber, aber ihre Feldwirkung bleibt skalarer
adaptiver Transport.

## Kandidat K2: Lokale geschichtsabhaengige Umformbarkeit

| Pruefrolle | Audit |
|---|---|
| lokale Ursache | fruehere Feldbeanspruchung veraendert die spaetere Aenderbarkeit eines Ortes |
| Bilanz | eine unabhaengig begruendete begrenzte Rolle fehlt |
| Feldgeschichte | funktional formulierbar, anatomisch ohne neue Ursache unterbestimmt |
| spaetere Feldwirkung | identische Fortsetzung entwickelt sich nach verschiedener Vorgeschichte unterschiedlich |
| staerkste Gegenbaseline | adaptiver Gain, Metadisposition, LRD-E1, Hysterese und zustandsabhaengige Mobilitaet |
| Stoppbedingung | Leser- oder Zustandspaar wird durch eine Pflichtbaseline rekonstruiert |

Urteil: `UNDERDETERMINED_AND_REDUCIBLE`. Der Vorschlag benennt die gesuchte
Funktion, aber noch keine von ihr unabhaengige technische Ursache.

## Kandidat K3: Reversible lokale Kontakt- oder Domaenenumlagerung

| Pruefrolle | Audit |
|---|---|
| lokale Ursache | lokale Feldbeanspruchung ordnet endliche Kontakt- oder Domaenenanteile um |
| Bilanz | Materialanteile oder Bindungsrollen koennen endlich bilanziert werden |
| Feldgeschichte | lokale Beanspruchungs- und Entlastungsgeschichte ist prinzipiell erreichbar |
| spaetere Feldwirkung | veraenderte Kontaktlage beeinflusst spaetere Weiterleitung oder Verformung |
| staerkste Gegenbaseline | Phasenfeld, Viskoelastik, Hysterese, Standardmaterial und adaptive Kante |
| Stoppbedingung | Wirkung folgt vollstaendig aus vorgegebener Materialkennlinie oder unabhaengigen Kantenzustaenden |

Urteil: `BASELINE_EQUIVALENT`. Ohne eine weitere Ursache ist die
Kontaktumlagerung eine bekannte Material- oder Kantenplastizitaet.

## Kandidat K4: LCB-1, lokaler schleifengebundener Zirkulationsbilanztraeger

### Lokale technische Ursache

LCB-1 wird nur fuer eine bereits vorhandene elementare geschlossene
Nachbarschaftsschleife betrachtet. Als moegliche Ursache gilt eine
abgeschlossene orientierte lokale Feldflussgeschichte entlang dieser
Schleife. Eine im Uhrzeigersinn und eine entgegengesetzt orientierte
Geschichte sind technisch unterscheidbar, obwohl ihre Knoten- und
Einzelkantenmarginalen angeglichen werden koennen.

Nicht ausreichend sind aktuelle Aktivierung, reine Reihenfolgezuege ohne
lokalen Feldfluss oder ein Observer, der nachtraeglich eine Orientierung
zuweist.

### Begrenzter Zustand oder Bilanz

Der vorgeschlagene Traeger besitzt ausschliesslich eine endliche lokale
Schleifenbilanz. Gegenlaeufige Anteile beanspruchen dieselbe Kapazitaet.
Unbilanzierte Erzeugung, globale Normierung, unabhaengiges Anwachsen aller
Schleifen und Speicherung einzelner Episoden sind ausgeschlossen.

S1-VA legt nicht fest, ob diese Bilanz spaeter diskret oder kontinuierlich
dargestellt wird. Es wird auch keine Fortschreibungsregel bestimmt.

### Erreichbare Feldgeschichte

Die Bildungsprognose verwendet nur den normalen Rezeptor-, Dock- und
Feldpfad in der festen Geometrie:

```text
orientierte lokale Exposition A_cw oder A_ccw
-> abgeschlossene Feldfluesse auf derselben elementaren Schleife
-> Angleichung von aktuellem Kontakt, S, H sowie Knoten- und Kantenmarginalen
-> identische spaetere Probe B
```

Kann die Bilanz nicht ueber diesen normalen Pfad erreicht werden, wird LCB-1
verworfen.

### Eigene spaetere Feldprognose

Bei identischer Probe B sagt LCB-1 eine entgegengesetzt orientierte lokale
Flussumverteilung fuer A_cw und A_ccw voraus. Die Prognose darf nicht aus
einem verbleibenden Knotenwert, einer einzelnen Kantenspur, einem
Kantenhistogramm oder einem aktuellen S/H-Unterschied berechnet werden.

Die isolierende Zusatzprognose ist eine vorregistrierte
Schleifenunterbrechung: Wird genau eine Kante des Pruefmotivs als externe
Forschungsintervention entfernt, darf eine echt schleifengebundene Wirkung
nicht wie vier unabhaengige gerichtete Kantenspuren fortbestehen. Die
Intervention veraendert keine produktive Topologie; sie gehoert nur zum
spaeteren Falsifikationsaufbau.

### Staerkste Gegenbaseline

Die staerkste Gegenbaseline ist nicht nur Fixed Adapter oder Integrator,
sondern ein gleich budgetierter, zyklusblinder Satz unabhaengiger gerichteter
Kantenspuren beziehungsweise Kantengains. Er erhaelt dieselbe orientierte
Geschichte, dieselben Kantenbudgets und denselben spaeteren Probeverlauf.

Zusaetzlich verpflichtend bleiben:

- ACM-1H und CGR-1 als relationale Motiv- und gekoppelte Gainbaseline;
- Leaky-, Integrator- und Retentionsbaseline;
- F3 beziehungsweise konservierter skalarer Transport;
- DTS-1/T1, G2/D3 und Capacity-Clamp;
- feste nichtreziproke Kopplung und lokaler Oszillator.

### Stoppbedingungen

LCB-1 wird ohne Gleichung oder Implementierung verworfen, wenn mindestens
eine der folgenden Bedingungen eintritt:

1. die gebundene Feldgeometrie besitzt im vorgesehenen Korridor keine
   elementare geschlossene Schleife;
2. die normale Feldgeschichte kann keine orientierte lokale Ursache bilden;
3. der vorgeschlagene Zustand ist aus Knotenwerten, unabhaengigen
   Kantenspuren oder deren Marginalen rekonstruierbar;
4. die zyklusblinde gerichtete Kantenbaseline reproduziert Bildungs-,
   Probe- und Unterbrechungsverlauf vollstaendig;
5. ACM-1H/CGR-1 oder eine andere Pflichtbaseline reproduziert die gesamte
   Gegenprognose mit einem festen Parametersatz;
6. die Bilanz benoetigt einen globalen Observer, eine adaptive Topologie,
   einen Reset oder eine getrennte Schreib-/Leseregel;
7. der Effekt ist nur Amplituden-, Nachhall-, Oszillations- oder
   Instabilitaetsunterschied.

Urteil: `STATICALLY_ADMISSIBLE_FOR_LATER_CONTRACT_ONLY`.

LCB-1 ist nicht als technische Ursache bestaetigt. Im Unterschied zu K1 bis
K3 besitzt der Vorschlag jedoch bereits vor einer Gleichung eine eigene
isolierbare Gegenprognose: Abhaengigkeit von geschlossener Zyklusstruktur bei
angeglichenen lokalen Marginalen und gezielter Schleifenunterbrechung.

## Vergleichsentscheidung

| Vorschlag | Ursache | Bilanz | Feldgeschichte | eigene Feldprognose | Baselineabgrenzung | Entscheidung |
|---|---:|---:|---:|---:|---:|---|
| K1 skalarer Kopplungstraeger | ja | ja | ja | nein | nein | geschlossen |
| K2 Umformbarkeit | nein | nein | offen | funktional ja | nein | geschlossen |
| K3 Kontakt-/Domaenenumlagerung | ja | ja | ja | nein | nein | geschlossen |
| K4 LCB-1 | vorlaeufig ja | ja | anatomisch moeglich, kausal zu pruefen | ja | vorab falsifizierbar | genau ein Vorschlag |

## Verbindlicher Auditausgang

```text
S1_VA_FOUR_LOCAL_CAUSE_CLASSES_COMPARED
S1_VA_K1_K2_K3_REJECTED_AS_BASELINE_EQUIVALENT_OR_UNDERDETERMINED
S1_VA_LCB1_ONLY_STATICALLY_ADMISSIBLE_PROPOSAL
S1_VA_LCB1_NOT_IMPLEMENTED_NOT_CONFIRMED
S1_VA_NO_EQUATION_NO_PARAMETER_NO_RUNTIME_NO_FIELD_INTEGRATION
S1_VA_NO_MEMORY_OR_OTHER_EXTENDED_CLAIM
```

Genau ein Kandidat wird fuer einen moeglichen spaeteren Forschungszweig
vorgeschlagen:

```text
LCB-1 - lokaler schleifengebundener Zirkulationsbilanztraeger
```

Diese Auswahl autorisiert noch keinen Kandidatenvertrag und keine technische
Umsetzung.

## Bester naechster Schritt

S1-VB darf erst nach ausdruecklicher fachlicher Freigabe ausschliesslich einen
statischen Funktions- und Falsifikationsvertrag fuer LCB-1 binden. Vor jeder
Anatomie oder Gleichung muss S1-VB festlegen:

- die minimale elementare Schleifengeometrie;
- die zwei kausal angeglichenen orientierten Geschichten;
- die vollstaendige Marginalenangleichung;
- die Schleifenunterbrechungsintervention;
- die gleich budgetierte gerichtete Kantenbaseline sowie ACM-1H/CGR-1;
- die sofortigen Stopp- und Claimgrenzen.

S1-VB darf noch keine Zustandsdarstellung, Gleichung, Parameter, Runtime,
Snapshotaenderung oder Feld-/Matrixausfuehrung einfuehren.

## Projektgrundlagen

- [S1-PQ Bestands- und Lueckenaudit](S1PQ_STATISCHER_BESTANDS_UND_LUECKENAUDIT_PRIMAERES_MCM_WAHRNEHMUNGSFELD.md)
- [S1-UO repositoryweiter Anhaltspunktaudit](S1UO_REPOSITORYWEITER_MEMORY_ANHALTSPUNKTAUDIT.md)
- [S1-F verteilte kausale Nichtseparierbarkeit](S1F_ZULASSUNGSVERTRAG_VERTEILTE_KAUSALE_NICHTSEPARIERBARKEIT.md)
- [S1-AB umverteilbares Kopplungsmedium](S1AB_AUDIT_ENDLICHES_LOKAL_UMVERTEILBARES_KOPPLUNGSMEDIUM.md)
- [W5-C Suchlueckenentscheid](W5C_SUCHLUECKENENTSCHEID_GESCHICHTSABHAENGIGE_UMFORMBARKEIT.md)
- [S1-UZ Abschluss der Aktivkern-Konsolidierung](S1UZ_STATISCHER_ABSCHLUSSAUDIT_AKTIVKERN_KONSOLIDIERUNG.md)
