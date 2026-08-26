# W5-B: Erste Primaerquellenkartierung von Substratprinzipien

Stand: 2026-08-09

Entscheidung: `FIRST_SOURCE_MAP_NO_ADMISSIBLE_SUBSTRATE_ROLE`

Auditart: statisch

Runtimeaenderung: nein

Formaler Forschungslauf: nein

## Forschungsfrage

Traegt eine von vier fachlich verschiedenen Primaerarbeiten bereits eine
lokale Naturrolle, die unabhaengig von einem Memoryziel sinnvoll ist und die
sieben Rollen des W5-A-Suchvertrags prinzipiell erfuellen kann, ohne auf eine
geschlossene Projektbaseline zu reduzieren?

## Umfang und Methode

Die Kartierung ist auf vier Mechanismusfamilien und je eine Primaerarbeit
begrenzt. Die Begriffe `memory`, `adaptive` oder `self-organizing` in einer
Quelle gelten nicht als Zulassungsgrund. Entscheidend sind Mechanik,
Kopplungsrichtung, Bilanz, Vorhersage und Abgrenzung gegen die Projektbaselines.

## Quellenledger

### 1. Adaptive Transportnetzwerke

**Quelle:** Atsushi Tero et al., "Rules for Biologically Inspired Adaptive
Network Design", Science 327, 439-442 (2010),
[doi:10.1126/science.1177894](https://doi.org/10.1126/science.1177894).

- **Reale Naturfunktion:** kostenguenstige, effiziente und fehlertolerante
  Transportverbindung zwischen verteilten Nahrungsorten.
- **Lokale Zustaende und Ursachen:** Leitfaehigkeit beziehungsweise
  Rohrstaerke wird durch lokalen Fluss angepasst.
- **Wechselwirkungsrichtung:** Netzleitfaehigkeit bestimmt Fluss; Fluss
  veraendert die Leitfaehigkeit.
- **Bilanz:** Transportkosten und Flussbilanz werden beruecksichtigt; ein
  endlicher, erneut frei nutzbarer lokaler Kapazitaetstraeger ist nicht belegt.
- **Vorhersage:** die adaptive Netzwerkregel erzeugt einen Kompromiss aus
  Effizienz, Kosten und Robustheit.
- **Geometrie:** Wirkung liegt auf expliziten Netzwerkverbindungen zwischen
  vorgegebenen Orten.
- **Pflichtbaseline:** adaptive Mobilitaet/Leitfaehigkeit sowie gespeicherte
  Kanten und Partnerbeziehungen.
- **Projekturteil:** `SOURCE_BASELINE_EQUIVALENT`.

Die relevante Rolle ist eine adaptive Leitfaehigkeit auf Kanten. Damit faellt
sie direkt in zwei W5-A-Ausschlussfamilien.

### 2. Memristive Festkoerperzustaende

**Quelle:** Dmitri B. Strukov et al., "The missing memristor found", Nature
453, 80-83 (2008),
[doi:10.1038/nature06932](https://doi.org/10.1038/nature06932).

- **Reale Naturfunktion:** hysteretische elektrische Leitung durch gekoppelte
  elektronische und ionische Transporte in einem nanoskaligen Bauelement.
- **Lokale Zustaende und Ursachen:** eine durch angelegte Spannung und
  Ladungstransport verschobene Materialgrenze veraendert den Widerstand.
- **Wechselwirkungsrichtung:** Strom veraendert den inneren Widerstandszustand;
  dieser Zustand veraendert spaeter den Strom.
- **Bilanz:** Ladung und ionischer Transport sind physikalisch gebunden, aber
  keine projektgemaesse endliche, lokal umverteilbare und erneut anders
  nutzbare Kapazitaet ist nachgewiesen.
- **Vorhersage:** der innere Zustand erklaert hysteretisches Strom-Spannungs-
  Verhalten nanoskaliger Bauelemente.
- **Geometrie:** der Zustand liegt in einem Zweipol und ist keine verteilte
  MCM-Feldgeometrie.
- **Pflichtbaseline:** unabhaengige Hystereseelemente, adaptive Leitfaehigkeit
  und Standardmaterial.
- **Projekturteil:** `SOURCE_BASELINE_EQUIVALENT`.

Die wechselseitige Zustandskopplung ist real, bleibt fuer die Projektfrage
aber ein explizit ausgeschlossenes memristives Hystereseelement.

### 3. Transiente Mehrfachgedaechtnisse in zyklisch getriebener Materie

**Quelle:** Nathan C. Keim und Sidney R. Nagel, "Generic Transient Memory
Formation in Disordered Systems with Noise", Physical Review Letters 107,
010603 (2011),
[doi:10.1103/PhysRevLett.107.010603](https://doi.org/10.1103/PhysRevLett.107.010603).

- **Reale Naturfunktion:** ein zyklisch getriebenes ungeordnetes System
  entwickelt reversible beziehungsweise irreversible Antworten auf
  Trainingsamplituden.
- **Lokale Zustaende und Ursachen:** Teilchenkonfigurationen veraendern sich
  unter zyklischer Scherung; Wiederholung und Rauschen bestimmen die
  transient erhaltenen Schwellenwirkungen.
- **Wechselwirkungsrichtung:** zyklische Anregung veraendert die Konfiguration;
  ein spaeterer Amplitudensweep liest deren Antwort aus.
- **Bilanz:** die Quelle belegt Lernen und Vergessen als verbundenen
  Nichtgleichgewichtsprozess, aber keine endliche lokal umverteilbare
  Ressource mit nachgewiesener Freigabe und anderer Wiederverwendung.
- **Vorhersage:** mehrere Trainingsamplituden bleiben transient sichtbar;
  langfristig dominiert ohne Rauschen nahezu eine, waehrend Rauschen den
  Verlust verhindern kann.
- **Geometrie:** der Befund beruht auf der Konfiguration eines zyklisch
  gescherten Vielteilchensystems, nicht auf einer konjugierten MCM-Feldrolle.
- **Pflichtbaseline:** Standardmaterial, Hysterese/Schwellenantwort und
  vorgeschriebene Trainings- sowie Auslesephase.
- **Projekturteil:** `SOURCE_BASELINE_EQUIVALENT`.

Der Quelleneffekt ist ein wichtiger Gegenbefund fuer materielles Memory. Seine
relevante Projektrolle bleibt jedoch zyklisches Training plus spaetere
Schwellenablesung und erfuellt den gebundenen Lebenszyklus nicht.

### 4. Nichtreziproke aktive Festkoerper

**Quelle:** Colin Scheibner et al., "Odd elasticity", Nature Physics 16,
475-480 (2020),
[doi:10.1038/s41567-020-0795-y](https://doi.org/10.1038/s41567-020-0795-y).

- **Reale Naturfunktion:** aktive, nichtkonservative mikroskopische
  Wechselwirkungen erzeugen ungerade elastische Moduli und koennen entlang
  quasistatischer Deformationszyklen Arbeit abgeben.
- **Lokale Zustaende und Ursachen:** Dehnung, Spannung, aktive Querkraefte und
  nichtreziproke Scharniere bestimmen die konstitutive Antwort.
- **Wechselwirkungsrichtung:** die aktive nichtreziproke Kopplung durchbricht
  die Symmetrie passiver Elastizitaet; eine geschichtlich veraenderte lokale
  Umformbarkeit ist in der relevanten Rolle nicht ausgewiesen.
- **Bilanz:** das Medium ist aktiv und nichtkonservativ; Arbeit kann in einem
  Zyklus gewonnen werden. Eine endliche wiederverwendbare Substratkapazitaet
  folgt daraus nicht.
- **Vorhersage:** ungerade Moduli erlauben unter anderem Arbeitsextraktion und
  elastische Wellen in ueberdaempften Medien.
- **Geometrie:** Netzwerk- und Kontinuumsgeometrie sind wesentlich fuer die
  nichtreziproke Antwort.
- **Pflichtbaseline:** Standardmaterial beziehungsweise fest vorgegebene
  aktive konstitutive Kopplung, feste Rekurrenz und Attraktordynamik.
- **Projekturteil:** `SOURCE_ROLE_UNDERDETERMINED`.

Diese Arbeit besitzt die staerkste eigenstaendige Feld- und Materialfunktion
der Kartierung. Sie belegt aber weder geschichtsabhaengige Aenderung ihrer
Transformierbarkeit noch Loesung, Ressourcenfreigabe oder andere
Wiederverwendung. Die fehlenden Rollen duerfen nicht positiv ergaenzt werden.

## Vergleichsergebnis

| Familie | Eigenstaendige Naturfunktion | Geschichtlich veraenderte Rueckwirkung | Endliche erneut nutzbare Kapazitaet | Urteil |
|---|---|---|---|---|
| adaptive Transportnetze | ja | als adaptive Kantenleitfaehigkeit | nicht projektgemaess belegt | `SOURCE_BASELINE_EQUIVALENT` |
| Memristor | ja | als hysteretischer Widerstand | nicht projektgemaess belegt | `SOURCE_BASELINE_EQUIVALENT` |
| zyklisch getriebene Materie | ja | als Trainings-/Schwellenantwort | nicht belegt | `SOURCE_BASELINE_EQUIVALENT` |
| ungerade Elastizitaet | ja | nicht belegt | nicht belegt | `SOURCE_ROLE_UNDERDETERMINED` |

Keine Arbeit erhaelt `SOURCE_ROLE_POTENTIALLY_ADMISSIBLE`. Deshalb wird nach
dem W5-A-Vertrag kein W5-C-Kandidatenaudit vorgeschlagen.

## Verwendete Projektquellen

- [W5-A Primaerquellen-Suchvertrag](W5A_PRIMAERQUELLEN_SUCHVERTRAG_UNABHAENGIGES_SUBSTRATPRINZIP.md)
- [S1-AA hartes Wiedereroeffnungstor](S1AA_OPERATIVER_ENTWICKLUNGSANSCHLUSS_NACH_SUBSTRATSTOPP.md)
- [S1-F verteilte kausale Nichtseparierbarkeit](S1F_ZULASSUNGSVERTRAG_VERTEILTE_KAUSALE_NICHTSEPARIERBARKEIT.md)
- [S1-AB Audit des umverteilbaren Kopplungsmediums](S1AB_AUDIT_ENDLICHES_LOKAL_UMVERTEILBARES_KOPPLUNGSMEDIUM.md)

## Aussagegrenze

W5-B zeigt weder, dass ein geeignetes Substrat unmoeglich ist, noch dass eine
der Quellen MCM-Memory, Lernen, Feldzeit, inneren Kontext, Organisation,
Semantik, Selbstregulation oder KI belegt. Es wurde keine Gleichung, Variable,
Runtime, Testmatrix oder Ausfuehrung vorbereitet. Lauf 197 bleibt reserviert
und unberuehrt.

## Bester naechster Schritt

Die Substratimplementierung bleibt pausiert. Vor einer weiteren breiten
Literatursuche wird W5-C als **Suchlueckenentscheid**, nicht als
Kandidatenaudit, statisch formuliert: Er muss aus den vier Negativurteilen
genau die noch unbelegte mechanische Rolle ableiten und entscheiden, ob eine
zweite engere Primaerquellensuche fachlich begruendet ist oder die Linie ohne
neue Naturursache geschlossen bleibt.
