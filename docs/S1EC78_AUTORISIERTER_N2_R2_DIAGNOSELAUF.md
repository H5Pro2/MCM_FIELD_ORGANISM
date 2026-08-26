# S1-EC78: Autorisierter n2/r2-Diagnoselauf

## Freigabe und Vorpruefung

Der Projekteigentuemer gab genau einen nicht persistenten diagnostischen
n2/r2-Lauf unter EC77 mit maximal 3.208 Feldschritten frei. Retry und
Nachparametrierung waren ausgeschlossen.

Unmittelbar vor dem Start wurden im selben Prozess die technische Kette und
die Besitzerfreigabe frisch gebunden:

- freier Arbeitsspeicher: `7.261.044.736` Byte
- freier Datentraeger: `235.033.444.352` Byte
- EC72-Preflight-Digest:
  `da647ddef694a369b848dc81a2b5c2a379d16e76f69131384719de53c66a90d8`
- EC73-Vertragsdigest:
  `b5c77b9ac5dc764060adaa47d7ac642630ba725bae2a018c366cbb5fc7f0bb55`
- EC76-Routendigest:
  `135ffafdc816a38b7064eaf5dcc74c8ce1b262eca22a253010a373139c769514`
- EC77-Gate-Digest:
  `0dc2ef9fb05428221afdf37370392c3facc12bdab994cc3589deb6b1d8972b9a`
- EC78-Autorisierungsdigest:
  `b9e13906e774d10f31b2bb9020e47f1cab8f5a93677d0e7bcdd3faae96fa5431`

EC78 erlaubte exakt einen Start. Persistenz, automatischer Retry,
Nachparametrierung, Forschungsentscheidung und Claims blieben gesperrt.

## Messung

Der EC67-Realmodus-Koordinator wurde genau einmal aufgerufen und gab ein
vollstaendig validiertes Ergebnisobjekt zurueck.

- Ergebnis-Digest:
  `94d7b93af4a73110526de3f3a9c2481162dacccfceef2dcfc4f703f7012197c5`
- vier abgeschlossene Formationen;
- acht getrennte frische Felder;
- acht abgeschlossene Proben;
- 1.608 abgerechnete Bildungsschritte;
- 1.600 abgerechnete Probeschritte;
- insgesamt exakt 3.208 ausgefuehrte Feldschritte;
- alle Zustands- und Rueckwirkungsrouten exakt;
- frische Felder inhaltlich identisch initialisiert und objektseitig getrennt;
- vier gebildete Zustaende objektseitig getrennt;
- keine Persistenz.

Diese Werte sind Invarianten des erfolgreich konstruierten Ergebnisobjekts.
Nach dessen Rueckgabe scheiterte ausschliesslich eine zusaetzliche
Konsolenausgabe an dem nicht vorhandenen Anzeigenamen
`formation_field_steps`; der korrekte Feldname lautet
`accounted_formation_steps`. Der Lauf selbst war zu diesem Zeitpunkt bereits
vollstaendig beendet. Es erfolgte kein Retry.

## Technische Interpretation

Die in EC75 korrigierten typisierten Handoff-Digest-Schemata funktionieren
im realen Wrapperpfad. Die zuvor in EC74 nach 402 Schritten abgebrochene
Kette durchlief nun alle vier Bildungsarme, erzeugte alle acht frischen
Felder und schloss alle acht Proben innerhalb des vorab gebundenen Budgets
ab. Damit ist die technische n2/r2-Gesamtroute erstmals vollstaendig
ausgefuehrt.

## Nichtnachweis

- keine wissenschaftliche Auswertung der AB-/BA- oder Ablationswerte;
- kein Nachweis einer von Baselines unterscheidbaren Pruefwirkung;
- kein Memory-, Feldzeit-, Organisations-, Topologie-, Semantik-,
  Selbstregulations- oder KI-Nachweis;
- keine Aussage, dass E1 ein MCM-Memory ist.

## Offene Annahmen

Der Ergebnis-Digest und die strukturellen Invarianten belegen die technische
Ausfuehrbarkeit, nicht die wissenschaftliche Aussagekraft der Messwerte. Vor
jeder Interpretation muss statisch festgelegt werden, welche bereits im
Ergebnis enthaltenen Messgroessen gegen welche Gegenbaselines verglichen
werden und welche Entscheidungskriterien ohne Nachparametrierung gelten.

Alle fuenf geschuetzten Artefakte sind nach dem Lauf unveraendert. Die
einmalige EC78-Freigabe ist verbraucht.

Am besten geht es mit S1-EC79 weiter: das nicht persistierte EC78-Ergebnis
ausschliesslich anhand seines validierten Ergebnisvertrags und der bekannten
Messdefinitionen statisch einordnen und einen getrennten, nicht
ausfuehrenden Auswertungsvertrag fuer AB/BA und Ablationen formulieren.
