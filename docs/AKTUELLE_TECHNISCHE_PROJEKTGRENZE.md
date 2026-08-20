# Aktuelle technische Projektgrenze

## Verbindlicher Projektgegenstand

Das Projekt entwickelt und prueft ein technikbasiertes MCM-Wahrnehmungsfeld.
Sein primaerer Kern ist:

```text
kontrollierte Audio-/Video-Testwelt
-> zeitlich geordnete Rezeptorfolgen
-> gemeinsames lokales MCM-Feld
-> schneller technischer S/H-Zustand
-> passive Messung, Baselines und Reproduzierbarkeitspruefung
```

Das Feld verarbeitet kontrollierte Eingangsfolgen in einer gemeinsamen lokalen
Feldgeometrie. Snapshot und Restore sind Runtime-Serialisierung. Nachhall H ist
eine schnelle passive Zustandsrolle. Diese technischen Funktionen begruenden
keine weitergehende Faehigkeit.

Der Repository- und Paketname `MCM_FIELD_ORGANISM` bleibt aus Gruenden der
Kompatibilitaet und Nachvollziehbarkeit bestehen. Er ist keine fachliche
Behauptung ueber die Eigenschaften des Systems.

## Aktueller Evidenzstand

- Lauf 198 ist ausschliesslich eine reale Fixed-Adapter-Gegenbaseline. Seine
  kleine, nichtnullige und ueber r2/r4/r8 konvergierende AB/BA-Wirkung ist kein
  Nachweis einer Speicher- oder Lernfunktion.
- S1-LM ist die statische C10-Fallauswahl abgeschlossen. S1-LN bindet aktuell
  die lokale C10-Anatomie fuer `B3/P_IH_ATTENUATION` inkl. Rollenledger,
  Konservationsidentitaet und expliziten Baseline-/Struktursperren ohne
  Equation, Parameter, Dynamik oder Ausfuehrung.
- S1-LO implementiert diese Auswahl als technisch vollständige dreifach
  ausgefuehrte `r2/r4/r8`-Sequenz mit exakt neun Intervallaufrufen und
  bestätigter Fail-Closed-Rahmung. Auch hier keine Feldkopplung oder
  dynamische Aussage.
- S1-LP bildet den vollständigen Case-Output fuer diese drei Refinements
  (Replica/Komponenten/Digests), inklusive Vergleichsmessung und Primärbezug,
  und bleibt rein statisch. Kein Feldlauf, keine Baselineentscheidung und kein
  Kandidatenvergleich.
- S1-LQ bindet C01 bis C10 als abgeschlossen, mit den zugehoerigen
  Vertrags- und Falloutput-Digests, und nennt als naechsten Fall ausschliesslich
  `C11 / B3 / B3_F3_LOCAL_LEAKY / P_IK_INTERFERENCE`.
- S1-LR bindet C11 statisch als B3/P_IK-Auswahl. S1-LS fuehrt exakt diese
  drei Refinements isoliert aus: `r2/r4/r8`, zwei P_IK-Sequenzen pro
  Replikat, 24 Intervallaufrufe und sechs technische signed Komponenten pro
  Refinement. Der C11-Falloutput, Matrixpublikation, Baseline- oder
  Kandidatenurteil und Runtime-Integration bleiben gesperrt.
- S1-LT bindet den vollstaendigen technischen C11-Falloutput aus den bereits
  vorhandenen S1-LS-Ausgaben. Enthalten sind Provenienz-, Vergleichs- und
  Checkpoint-Digests, `r4` als Primaerrefinement und zwei gerichtete
  Residualbloecke. Matrixpublikation, Baseline- oder Kandidatenurteil und
  Runtime-Integration bleiben weiterhin gesperrt.
- S1-LU bindet C01 bis C11 als abgeschlossen. Damit liegen elf von 24
  Profilfaellen beziehungsweise 33 von 72 Refinement-Ausgaben vor. C12 bis
  C24 fehlen weiterhin; als naechster einzelner Fall ist nur
  `C12 / B3 / B3_F3_LOCAL_LEAKY / P_IN_RELEASE_REUSE` freigegeben. Keine
  Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-LV bindet C12 statisch als B3/P_IN-Auswahl mit zwei getrennten
  Recovery-Sequenzen, drei Refinements und vollstaendigem B3-Frischzustand.
  Es gibt keine Implementierung, keine Ausfuehrung, keinen C12-Falloutput,
  keine Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-LW implementiert und fuehrt genau diese C12-Auswahl isoliert aus. Die
  Recovery-on/off-Terminals sind innerhalb jedes Refinements bitidentisch und
  alle sechs signed Komponenten sind null. Das ist kein Release-/Reuse-,
  Baseline- oder Kandidatenurteil; C12-Falloutput, Matrixkomposition und
  Matrixpublikation bleiben gesperrt.
- S1-LX bindet den vollstaendigen technischen C12-Falloutput aus den bereits
  vorhandenen S1-LW-Ausgaben. Enthalten sind Provenienz-, Vergleichs- und
  Checkpoint-Digests, `r4` als Primaerrefinement, sechs Nullkomponenten und
  zwei gerichtete Null-Residualbloecke. Matrixpublikation, Baseline- oder
  Kandidatenurteil und Runtime-Integration bleiben weiterhin gesperrt.
- S1-LY bindet C01 bis C12 als abgeschlossen. Damit liegen zwoelf von 24
  Profilfaellen beziehungsweise 36 von 72 Refinement-Ausgaben vor. C13 bis
  C24 fehlen weiterhin; als naechster einzelner Fall ist nur
  `C13 / B4 / B4_F3_LINEAR_COUPLED / P_IE_CAUSAL_TWO_SUBSTEP` freigegeben.
  Keine Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-LZ bindet C13 statisch als B4/P_IE-Auswahl mit zwei getrennten
  P_IE-Sequenzen, drei Refinements und vollstaendigem B4-Frischzustand samt
  linear gekoppeltem M-Arm. Es gibt keine Implementierung, keine Ausfuehrung,
  keinen C13-Falloutput, keine Matrixkomposition, keine Matrixpublikation und
  kein Urteil.
- S1-MA implementiert und fuehrt genau diese C13-Auswahl isoliert aus. Alle
  acht signed Komponenten sind null; Provenienz-, Vergleichs- und
  Checkpointdigests bleiben refinementabhaengig. Das ist kein Baseline- oder
  Kandidatenurteil; C13-Falloutput, Matrixkomposition und Matrixpublikation
  bleiben gesperrt.
- S1-MB bindet den vollstaendigen technischen C13-Falloutput aus den bereits
  vorhandenen S1-MA-Ausgaben. Enthalten sind Provenienz-, Vergleichs- und
  Checkpoint-Digests, `r4` als Primaerrefinement, acht Nullkomponenten und
  zwei gerichtete Null-Residualbloecke. Matrixpublikation, Baseline- oder
  Kandidatenurteil und Runtime-Integration bleiben weiterhin gesperrt.
- S1-MC bindet C01 bis C13 als abgeschlossen. Damit liegen dreizehn von 24
  Profilfaellen beziehungsweise 39 von 72 Refinement-Ausgaben vor. C14 bis
  C24 fehlen weiterhin; als naechster einzelner Fall ist nur
  `C14 / B4 / B4_F3_LINEAR_COUPLED / P_IH_ATTENUATION` freigegeben. Keine
  Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-MD bindet C14 statisch als B4/P_IH-Auswahl mit einer P_IH-Sequenz, drei
  Refinements und vollstaendigem B4-Frischzustand samt linear gekoppeltem
  M-Arm. Es gibt keine Implementierung, keine Ausfuehrung, keinen
  C14-Falloutput, keine Matrixkomposition, keine Matrixpublikation und kein
  Urteil.
- S1-ME implementiert und fuehrt genau diese C14-Auswahl isoliert aus:
  `r2/r4/r8`, eine P_IH-Sequenz pro Replikat, neun Intervallaufrufe und acht
  technische signed Komponenten pro Refinement. Das ist kein Memory-Nachweis,
  keine vorhandene Memory-Faehigkeit, kein Baseline- oder Kandidatenurteil und
  kein Systemfaehigkeits-Claim; C14-Falloutput, Matrixkomposition und
  Matrixpublikation bleiben gesperrt.
- S1-MF bindet den vollstaendigen technischen C14-Falloutput aus den bereits
  vorhandenen S1-ME-Ausgaben. Enthalten sind Provenienz-, Vergleichs- und
  Checkpoint-Digests, `r4` als Primaerrefinement, acht nichtnullige
  Komponenten und zwei gerichtete nichtnullige Residualbloecke.
  Matrixpublikation, Baseline- oder Kandidatenurteil, Memory-Faehigkeit und
  Runtime-Integration bleiben weiterhin gesperrt.
- S1-MG bindet C01 bis C14 als abgeschlossen. Damit liegen vierzehn von 24
  Profilfaellen beziehungsweise 42 von 72 Refinement-Ausgaben vor. C15 bis
  C24 fehlen weiterhin; als naechster einzelner Fall ist nur
  `C15 / B4 / B4_F3_LINEAR_COUPLED / P_IK_INTERFERENCE` freigegeben. Keine
  Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-MH bindet C15 statisch als B4/P_IK-Auswahl mit zwei getrennten
  P_IK-Sequenzen, drei Refinements und vollstaendigem B4-Dreiknoten-
  Frischzustand samt linear gekoppeltem M-Arm. Es gibt keine Implementierung,
  keine Ausfuehrung, keinen C15-Falloutput, keine Matrixkomposition, keine
  Matrixpublikation und kein Urteil.
- S1-MI implementiert und fuehrt genau diese C15-Auswahl isoliert aus:
  `r2/r4/r8`, zwei P_IK-Sequenzen pro Replikat, 24 Intervallaufrufe und sechs
  technische signed Komponenten pro Refinement. Das ist kein Interferenz-,
  Baseline- oder Kandidatenurteil, keine Memory-Faehigkeit und kein
  Systemfaehigkeits-Claim; C15-Falloutput, Matrixkomposition und Matrixpublikation
  bleiben gesperrt.
- S1-MJ bindet den vollstaendigen technischen C15-Falloutput aus den bereits
  vorhandenen S1-MI-Ausgaben. Enthalten sind Provenienz-, Vergleichs- und
  Checkpoint-Digests, `r4` als Primaerrefinement, sechs nichtnullige
  Komponenten und zwei gerichtete nichtnullige Residualbloecke.
  Matrixpublikation, Baseline- oder Kandidatenurteil, Memory-Faehigkeit und
  Runtime-Integration bleiben weiterhin gesperrt.
- S1-MK bindet C01 bis C15 als abgeschlossen. Damit liegen fuenfzehn von 24
  Profilfaellen beziehungsweise 45 von 72 Refinement-Ausgaben vor. C16 bis
  C24 fehlen weiterhin; als naechster einzelner Fall ist nur
  `C16 / B4 / B4_F3_LINEAR_COUPLED / P_IN_RELEASE_REUSE` freigegeben. Keine
  Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-ML bindet C16 statisch als B4/P_IN-Auswahl mit zwei getrennten
  P_IN-Sequenzen, drei Refinements und vollstaendigem B4-Dreiknoten-
  Frischzustand samt linear gekoppeltem M-Arm. Es gibt keine Implementierung,
  keine Ausfuehrung, keinen C16-Falloutput, keine Matrixkomposition, keine
  Matrixpublikation und kein Urteil.
- S1-MM implementiert und fuehrt ausschliesslich die drei C16-Replikate
  `B4:P_IN_RELEASE_REUSE:r2/r4/r8` isoliert aus. Es gibt gebundene Output-,
  Vergleichs- und Checkpoint-Digests aus 24 Intervallaufrufen, aber keinen
  C16-Falloutput, keine Matrixkomposition, keine Matrixpublikation und kein
  Urteil.
- S1-MN setzt den technischen C16-Falloutput ausschliesslich aus den S1-MM-
  Ausgaben zusammen. Primaerkomponenten und Residuen sind exakt null; daraus
  folgt kein Release-/Reuse-Urteil, kein Baselineabschluss und kein
  Kandidatenvergleich.
- S1-MO bindet C01 bis C16 als vollstaendige technische Falloutputs mit 48 von
  72 Refinement-Ausgaben. C17 bis C24 fehlen weiterhin; als naechster einzelner
  Fall ist nur `C17 / B5 / B5_F3_FULL / P_IE_CAUSAL_TWO_SUBSTEP` freigegeben.
  Keine Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-MP bindet C17 statisch als B5/P_IE-Auswahl mit zwei P_IE-Sequenzen, drei
  Refinements und vollstaendigem B5-Zweiknoten-Frischzustand samt vollem B5-
  Arm. Es gibt keine Implementierung, keine Ausfuehrung, keinen C17-Falloutput,
  keine Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-MQ implementiert und fuehrt ausschliesslich die drei C17-Replikate
  `B5:P_IE_CAUSAL_TWO_SUBSTEP:r2/r4/r8` isoliert aus. Es gibt gebundene
  Output-, Vergleichs- und Checkpoint-Digests aus 12 Intervallaufrufen, aber
  keinen C17-Falloutput, keine Matrixkomposition, keine Matrixpublikation und
  kein Urteil.
- S1-MR setzt den technischen C17-Falloutput ausschliesslich aus den S1-MQ-
  Ausgaben zusammen. Primaerkomponenten und Residuen sind exakt null; daraus
  folgt kein Baselineabschluss und kein Kandidatenvergleich.
- S1-MS bindet C01 bis C17 als vollstaendige technische Falloutputs mit 51 von
  72 Refinement-Ausgaben. C18 bis C24 fehlen weiterhin; als naechster einzelner
  Fall ist nur `C18 / B5 / B5_F3_FULL / P_IH_ATTENUATION` freigegeben. Keine
  Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-MT bindet C18 statisch als B5/P_IH-Auswahl mit einer P_IH-Sequenz, drei
  Refinements und vollstaendigem B5-Zweiknoten-Frischzustand samt vollem B5-
  Arm. Es gibt keine Implementierung, keine Ausfuehrung, keinen C18-Falloutput,
  keine Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-MU bindet ausschliesslich den Kohaerenzvertrag fuer geschlossene
  Feldkopplung. Kohaerenz ist ein technischer Messrahmen, keine
  Projektfaehigkeit. Stoerung, lokale Ressource, Spaetaufnahme,
  Abschwaechung, Interferenz, Freigabe, Gegenbaselines und
  Verwerfungsbedingungen muessen vor jeder Kandidatengleichung feststehen.
  Es gibt keine Gleichung, keine Parameter, keine Runtime, keinen Feldlauf und
  keinen Memory- oder Systemfaehigkeitsclaim.
- S1-MV waehlt statisch `KFS-1` als einzigen weiterverfolgbaren
  Kandidatenraum fuer diese Kohaerenzrolle. KFS-1 ist ein lokales
  ressourcenbegrenztes Feld-Substrat mit Kohaerenzbelastung und spaeterer
  Aufnahmeaenderung. Reward, Replay, feste Kanten, globale Normalisierung,
  reiner Leaky-Nachhall, reiner Integrator, Fixed Adapter und
  Readout-Klassifikatoren sind als primaere Kandidaten gesperrt. Es gibt keine
  Gleichung, keine Parameter, keine Runtime, keinen Feldlauf und keinen
  Memory- oder Systemfaehigkeitsclaim.
- S1-MW bindet fuer KFS-1 ausschliesslich Funktionsprognose,
  Falsifikationskriterien und Claim-Sperren. Lokale Stoerungsaufnahme,
  Ressourcenbelastung, Spaetaufnahme, Abschwaechung, Interferenz, Freigabe und
  Wiederbindung muessen getrennt messbar sein. Gegenbaselines bleiben Fixed
  Adapter, Leaky-Nachhall, Integrator, Replay, globale Normalisierung, feste
  Kanten, Readout-Klassifikator und F3/CONST-V. Es gibt keine Gleichung, keine
  Parameter, keine Runtime, keinen Feldlauf und keinen Memory- oder
  Systemfaehigkeitsclaim.
- S1-MX bindet fuer KFS-1 ausschliesslich statische Anatomie und Messrollen:
  lokale Traeger- und Kantenidentitaet, read-only S/H-Feldbezug, ein
  endliches `free/bound/blocked`-Ressourcenledger pro Kante, lokale
  Erhaltungsidentitaet, passive Messrollen, verbotene Zustaende,
  Baselineabgrenzung und Fail-Closed-Anatomietests. Es gibt keine Gleichung,
  keine Parameter, keine Runtime, keinen Feldlauf, keinen Funktionsnachweis
  und keinen Memory- oder Systemfaehigkeitsclaim.
- S1-MY bindet fuer KFS-1 ausschliesslich das statische Schema- und
  Digestmodell. Kanonische IDs und getrennte Digests halten Geometrie,
  Feldreferenz, Ressourcenledger, Expositionshistorie und Messrollen
  reproduzierbar auseinander. Ungueltige oder kausal nicht vergleichbare
  Records scheitern fail-closed. Digests sind Identitaetsnachweise und keine
  Funktionsbefunde; Gleichung, Parameter, Runtime, Feldlauf und
  Funktionsentscheidung bleiben gesperrt.
- S1-MZ bindet ausschliesslich den zugehoerigen statischen Validator- und
  Fixturevertrag. Unveraenderte Eingabebytes, Validierungsbeleg und
  Record-Digests bleiben getrennt. Gueltige Minimalfixtures und eindeutig
  mutierte Fehlerfixtures pruefen Schema, Anatomie, lokale Bilanz, faire
  Vorgeschichte, passive Messrollen und deterministische Ablehnung. Es gibt
  keine Kandidatengleichung, keine Dynamikparameter, keine Runtimeintegration,
  keinen Feldlauf und keine Funktionsentscheidung.
- S1-NA bindet ausschliesslich die isolierte Implementierungsgrenze dieses
  Validators. Ein Produktionsmodul, ein testseitiger Fixturekatalog und eine
  fokussierte Testdatei duerfen spaeter Schema, Digests, Anatomie, Bilanz und
  kausale Vergleichbarkeit pruefen. Das endliche Budget erlaubt hoechstens 64
  Validatoraufrufe und genau null MCM-Feldschritte, Runner-, Medien-, Browser-,
  Netzwerk- oder Reportaufrufe. Kandidatendynamik und Funktionsentscheidung
  bleiben gesperrt.
- S1-NB implementiert ausschliesslich diesen statischen Validator und nimmt
  ihn einmal fokussiert ab. Alle 12 Testgruppen mit insgesamt 23 Fixtures
  bestehen bei 27 Validatoraufrufen und genau null MCM-Feldschritten.
  Ungueltige Records werden nicht repariert; ihre Eingabebytes bleiben
  digestgebunden. Das ist ein Validatorbefund und keine KFS-1-Wirkung,
  Runtimeintegration oder Funktionsentscheidung.
- S1-NC bindet ausschliesslich das lokale KFS-1-Uebergangsalphabet. Vier
  ressourcenerhaltende Wechsel und drei Stillstandsrollen sind strukturell
  zugelassen; uebersprungene Rollen, Wechsel zwischen Kanten, globale
  Bilanzkorrektur und Readout-gesteuerte Ereignisse sind fail-closed
  gesperrt. Jeder spaetere Wechsel benoetigt dieselbe lokale Kantenidentitaet,
  geordnete Feldfolge und eine vorangehende Ausloeserbeobachtung. Gleichung,
  Rate, Parameter, Runtime und Funktionsentscheidung bleiben gesperrt.
- S1-ND bindet ausschliesslich Schema, Digests und Fehlergrenze lokaler
  Uebergangsrecords. Vollstaendige Vor-/Nachledger, Bilanzwert, Rollenpaar,
  Ausloeserreferenz, Feldordnung und Vorgaengerverkettung muessen gemeinsam
  gueltig sein. Sieben Alphabetfaelle und achtzehn Fail-Closed-Codes sind
  festgelegt. Die isolierte Validatorerweiterung ist freigegeben; Gleichung,
  Rate, Dynamikparameter, Runtime, Feldlauf und Funktionsentscheidung bleiben
  gesperrt.
- S1-NE implementiert ausschliesslich die isolierte Einzelrecord- und
  Vorgaengerpruefung. Alle sieben Alphabetrecords, achtzehn isolierten
  Fehlerfaelle sowie gueltige und gebrochene Zweierkette werden in 12
  Testgruppen korrekt behandelt. Es gab 29 Uebergangsvalidatoraufrufe und
  genau null MCM-Feldschritte. Der Befund betrifft nur Schema, Bilanz und
  Kettenintegritaet; er ist keine KFS-1-Wirkung oder Funktionsentscheidung.
- S1-NF waehlt ausschliesslich `KFS1-T1_LOCAL_TARGET_REFRACTORY` als erste
  konkrete lokale Regel. Zielbelegung ist `C*p` mit der bestehenden
  symmetrischen Kantenbeteiligung. Positiver Kontakt bindet oder blockiert;
  nur exakter Nullkontakt gibt vorbestehende blockierte Ressource frei. Die
  Regel besitzt keine freie Rate, Schwelle oder Parametersuche und noch keine
  Runtime- oder Feldrueckwirkung. DTS-1 bleibt verpflichtende strukturelle
  Gegenbaseline; ein Funktionsbefund liegt nicht vor.
- S1-NG implementiert und prueft ausschliesslich diese lokale T1-Regel fuer
  eine Kante. Die einmalige fokussierte Abnahme besteht mit 12 Tests, elf
  Uebergaengen und null Feldschritten. Die acht Ledgerprognosen, lokale
  Erhaltung und technische Isolation sind erfuellt. Das ist keine
  Feldwirkung, keine Baselineentscheidung und kein Befund zur hypothetischen
  MCM-Memory. Vor weiterer Ausfuehrung muss S1-NH die endliche Sequenz und
  die faire DTS-1-Gegenbaseline statisch binden.
- S1-NH bindet die endliche lokale Vergleichsfolge und schliesst die
  Profilmenge vor jeder Ausfuehrung. T1 und DTS-1 sehen dieselben sieben
  Beteiligungsereignisse und dieselbe Gesamtressource. DTS-1 darf nur das
  registrierte Profil `0.4/0.3/0.2` in `r1/r2/r4/r8` sowie die statische
  Nullratenkontrolle verwenden. Es gibt noch keine Ausfuehrung,
  Redundanzentscheidung oder Feldwirkung.
- S1-NI fuehrt den gebundenen lokalen Vergleich genau einmal aus. Acht Tests
  bestehen bei sieben T1-Uebergaengen, 112 DTS-1-Subschritten und null
  Feldschritten. Die festen DTS-1-Arme reproduzieren T1 nicht vollstaendig;
  T1 ist jedoch exakt als ereignisgeschaltete DTS-1-Dreirollenabbildung
  darstellbar. T1 bleibt deshalb nur als diskrete DTS-1-Gegenbaseline und
  wird nicht als unabhaengiger Substratkandidat an das Feld gekoppelt.
- S1-NJ schliesst T1 formal als unabhaengigen Kandidaten. Eine spaetere
  KFS-1-Regel muss zusaetzlich zum bestehenden Funktionsvertrag ein
  Nicht-DTS-Gate erfuellen: anderes atomares Transfernetz, zusaetzliche
  endliche nicht rekonstruierbare lokale Zustandskoordinate oder nicht auf
  DTS-1 faktorisierbare lokale Ressourcenverteilung. Eine kontrollierte
  Zustandsinterventionsprognose ist vor jeder Gleichung verpflichtend.
- S1-NK auditiert G1 bis G3 und fuehrt nur G2 als darstellungsoffene Klasse
  eines endlichen lokalen Konfigurationszustands weiter. G1 traegt allein
  keine eigene Zustandsintervention; G3 ist entweder im DTS-1-Kantenledger
  enthalten oder benoetigt selbst eine zusaetzliche G2-Rolle. Es sind noch
  keine Variable, Anatomie, Gleichung, Runtime oder Feldwirkung gewaehlt.
- S1-NL bindet fuer G2 direkte Zustandsintervention und spaetere endogene
  Bildung als getrennte Falsifikationsstufen. Bei bitgleichem Feld-,
  Ressourcen- und Baselinevorzustand darf nur G2 C0/C1 unterscheiden.
  Leaky-/Integratorgegenprognosen, reine G2-Ablation, Abschwaechung,
  Interferenz, Loesung und erneute Bildung bleiben verpflichtend. Eine
  Darstellung, Gleichung oder Feldwirkung ist weiterhin nicht gewaehlt.
- S1-NM bindet zwei direkte F1-Arme mit bitgleichem Feld-, Ressourcen- und
  Baselinevorzustand. Nur C0/C1 unterscheidet sich. Primaer gemessen wird die
  obere lokale Zulassungsgrenze fuer `free -> bound`; fuer C1 ist eine
  geringere Zulassung vorregistriert, waehrend alle Baselines und die
  G2-Ablation exakt null zwischen den Armen vorhersagen. Noch keine
  Zustandsdarstellung, Ausfuehrung oder Feldwirkung.
- S1-NN waehlt nach einem Vierklassen-Audit ausschliesslich die konservative
  Unterteilung `bound_unconfigured + bound_configured = bound`. Sie fuegt
  keine Gesamtressource hinzu und bleibt fuer DTS-1/T1 bei Aggregation
  unsichtbar. Binaerflag, unabhaengiger Skalar und Mehrkantenrelation sind
  fuer F1 gestoppt. Eine Dynamik, Funktion oder Feldwirkung ist nicht
  gebunden.
- S1-NO bindet die D3-Unterteilung als statische Einkantenanatomie mit vier
  disjunkten Rollen und exakter Erhaltung. C0 und C1 projizieren bitgleich
  auf `(free,bound,blocked)=(0.5,0.5,0.0)`. Die reine Ablation bildet C1 auf
  C0 ab, ohne Kapazitaet oder Aggregat zu veraendern. Keine Dynamik,
  Admissibilitaetsfunktion, Ausfuehrung oder Feldwirkung ist gebunden.
- S1-NP bindet additiv ein eigenes D3-Anatomieschema mit getrennten Digests
  fuer Vierrollenressource, Dreirollenprojektion und Gesamtrecord. Spaetere
  reine Einzel- und Paarvalidatoren duerfen nur Anatomie, Erhaltung,
  C0/C1-Aggregation und Ablation pruefen. Das bestehende KFS-1-Schema bleibt
  unveraendert; Implementierung, Dynamik und Feldwirkung sind gesperrt.
- S1-NQ bindet die isolierte Implementierung mit drei neuen Dateien,
  bytefesten C0/C1/MIXED-Fixtures, 18 Einzel- und sechs Paarmutationen,
  zwoelf Testgruppen und einem endlichen Einmalausfuehrungsbudget. C0 und C1
  besitzen bitgleich denselben Dreirollen-Projektionsdigest. Noch gibt es
  keine Validatorausfuehrung, Admissibilitaetsfunktion oder Feldwirkung.
- S1-NR implementiert die drei Dateien. Die einmalige fokussierte Abnahme
  scheiterte an genau einem abgeleiteten Folgefehler fuer ein fehlendes
  Klassenfeld. Die korrigierte Implementierung ist noch nicht erneut
  ausgefuehrt und deshalb nicht abgenommen. Bis zu einem separat gebundenen
  Wiederabnahmeschritt bleiben alle G2-Funktions- und Feldpfade gesperrt.
- S1-NS bindet fuer die bitgleich festgelegte korrigierte Fassung genau eine
  Wiederabnahme nach read-only Digestpreflight. Der Schritt selbst fuehrt
  nichts aus. Nur `10 tests, OK` darf den statischen Validator akzeptieren;
  jede Abweichung haelt alle G2-Funktions- und Feldpfade geschlossen.
- S1-HG beendet den Frozen-E1-Probezweig. Frozen-E1 berechnet aus demselben
  unveraenderten Zustand denselben Adapter und verwendet denselben Integrator
  wie die Fixed-Adapter-Baseline. Der geplante 45-Arm-Lauf wird nicht
  ausgefuehrt.
- Das MCM-Wahrnehmungsfeld und seine kontrollierte Testinfrastruktur bleiben
  der belastbare technische Kern.

## Offene Substrathypothese

S1-HH bindet genau einen moeglichen lokalen, ressourcenbegrenzten und nicht auf
einen vor der Probe fixierten Adapter reduzierbaren Kandidaten. DTS-1 besitzt die
drei Ressourcenrollen frei, leitend gebunden und voruebergehend refraktaer.

S1-LN uebernimmt diese Strukturbindung fuer `B3/P_IH_ATTENUATION` als
statische C10-Konzervierung von Rollenledger, lokaler und globaler Identitaet,
bevor eine dynamische Ausfuehrungsrunde freigegeben wird.

DTS-1 ist bisher nur ein Funktions- und Falsifikationsvertrag. Es gibt keine
ausgewaehlte Gleichung, keine Parameter, keine Runtime und keinen Lauf. Vor
jeder mathematischen Festlegung muessen gebunden bleiben:

- eine eigene technische Funktionsprognose;
- Verwerfungsbedingungen;
- Fixed Adapter, Leaky/Integrator, zweistufiges E1, F3/CONST-V und schneller
  Nachhall als Gegenbaselines;
- direkte Messungen von Abschwaechung und Interferenz;
- ein exaktes endliches Ressourcenledger;
- Freigabe und erneute Beanspruchung lokaler Kapazitaet.

Kann der Kandidat keine eigene Gegenprognose tragen oder wird sein Verlauf von
einer registrierten Baseline vollstaendig erklaert, wird der Kandidat gestoppt.

## Begriffs- und Aussagegrenze

Begriffe wie Gefuehl, Bewusstsein, Erleben, Verstehen, Feldintelligenz, KI und
organische Entwicklung sind keine aktuellen Projektmerkmale und keine
Bezeichnungen fuer technische Messergebnisse. Hypothetische MCM-Memory
bezeichnet ausschliesslich eine offene Entwicklungsrichtung fuer spaetere
MCM-faehige Memory. Eine vorhandene Memory-Faehigkeit oder ein Memory-Nachweis
wird nicht behauptet.

Messbare Zustandsdifferenz, Nachhall, Persistenz, Snapshot, Wiederholbarkeit,
Adapterwirkung oder Substratbilanz duerfen nicht sprachlich zu einer groesseren
Faehigkeit aufgewertet werden. Jede Ergebnisdarstellung trennt:

1. direkte Messung;
2. begrenzte technische Interpretation;
3. offene Hypothese;
4. Nichtnachweis und gesperrte Aussage.

## Forschungsregel

Vor jeder neuen Gleichung stehen Funktionsprognose, Falsifikation,
Gegenbaselines und direkte Ressourcenmessung. Eine neue Richtung benoetigt eine
eigene technische Gegenprognose. Fehlt sie, endet der Zweig mit `STOPP`.

Historische Plaene und Forschungsprotokolle bleiben fuer Reproduzierbarkeit
erhalten. Sie beschreiben fruehere Fragestellungen und sind keine aktuellen
Projektclaims. Fuer neue Arbeit haben diese Dokumente Vorrang:

1. `docs/AKTUELLE_TECHNISCHE_PROJEKTGRENZE.md`;
2. `AKTUELLER_FORSCHUNGSWEG.md`;
3. `docs/S1HH_DYNAMISCHER_SUBSTRAT_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG.md`;
4. `docs/S1LN_B3_PIH_C10_ANATOMY_UND_KONSERVATION_VERTRAG.md`.
