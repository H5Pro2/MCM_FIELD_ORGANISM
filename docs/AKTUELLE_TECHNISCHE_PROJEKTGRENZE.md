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
