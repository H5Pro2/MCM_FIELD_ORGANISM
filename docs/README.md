# Dokumentationsübersicht

## Verbindlicher Einstieg

- [Aktueller verbindlicher Forschungsweg](../AKTUELLER_FORSCHUNGSWEG.md):
  gegenwaertiger Projektstand, Testwelt-Grenze, aktive Forschungsfrage,
  Rollen und naechster entscheidbarer Versuch. Dieses Dokument hat fuer neue
  Arbeiten Vorrang vor historischen Entwicklungsabschnitten.

Aktueller Kurzstand: S1-WP bindet kausale Frische, Einmaligkeit und den
vollstaendigen exklusiven H1-Lock als einzigen Verbrauchs-Commitpunkt.
Wiederverwendung, stale Bindung, Konflikt und Teilverbrauch stoppen ohne
Retry. `10 von 10` neue und `318 von 318` aktuelle fokussierte PPB-1-Tests
bestehen. Siehe
[S1-WP](S1WP_PPB1_STATISCHER_FRISCHE_EINMALIGKEITS_UND_VERBRAUCHSVERTRAG.md).

S1-YC schliesst S1-YB mit `24 von 24` statisch bestandenen Rollen ab. Der
Runner wurde nicht erneut ausgefuehrt; Ergebnis und private Grenzen bleiben
digestgebunden. Siehe
[S1-YC](S1YC_PPB1_STATISCHER_RUNNER_UND_ERGEBNISABSCHLUSSAUDIT.md).

S1-YD waehlt `AOPB-1`, eine kapazitaetsgleiche adaptive
Online-Prototypbank, als genau eine staerkere dynamische Engineeringbaseline.
Es wurden keine Mechanik und kein Lauf hinzugefuegt. Siehe
[S1-YD](S1YD_PPB1_STATISCHE_ENGINEERINGEINORDNUNG_UND_DYNAMISCHE_BASELINEAUSWAHL.md).

S1-YE schliesst AOPB-1 als Duplikat derselben beobachtbaren
Online-Prototypfamilie. PPB-1 bleibt als private Engineeringkomponente
erhalten; es wurde keine zweite Baseline implementiert oder ausgefuehrt.
Siehe
[S1-YE](S1YE_PPB1_STATISCHER_NICHTDUPLIZIERUNGS_INFORMATIONS_UND_AEQUIVALENZAUDIT.md).

S1-YB bestaetigt in zehn synthetischen Plaenen die gebundene zeitliche
Aktualisierungsfunktion gegen die statische Baseline. Alle Pflichtvorteile
und Negativkontrollen bestehen; der Befund bleibt privat und ohne
MCM-spezifischen Memory- oder Feldclaim. Siehe
[S1-YB](S1YB_PPB1_PRIVATER_ZEITLICHER_AKTUALISIERUNGSVERGLEICH.md).

S1-YA implementiert die private eingefrorene Prototypbaseline. `12 von 12`
Tests bestaetigen `36` Bildungsuebergaenge, `28` spaetere Handoffs und einen
bitidentischen Bankzustand nach jedem Handoff. Siehe
[S1-YA](S1YA_PPB1_PRIVATE_STATISCHE_PROTOTYPBASELINE.md).

S1-XZ implementiert das private unveraenderliche Bundle aus zwei
Modalitaeten und zehn Geschichtsplaenen. `12 von 12` synthetische
Vertragstests bestehen; Zustand, Probe, Baseline und Runner bleiben
geschlossen. Siehe
[S1-XZ](S1XZ_PPB1_PRIVATE_ZEITLICHE_AKTUALISIERUNGSFIXTURE_UND_VALIDATOR.md).

S1-XY bindet die spaetere private Fixture-, Baseline-, Receipt- und
Runneranatomie samt exakten Aufrufbudgets. Es wurde nichts implementiert
oder ausgefuehrt. Siehe
[S1-XY](S1XY_PPB1_STATISCHER_PRIVATER_IMPLEMENTIERUNGSPREFLIGHT.md).

S1-XX bestaetigt `30 von 30` statische Zahlen-, Ereignis-, Budget- und
Quellenrollen von S1-XW. Keine Tests oder Projektfunktionen wurden
ausgefuehrt. Siehe
[S1-XX](S1XX_PPB1_STATISCHER_NUMERISCHER_KONSISTENZ_UND_QUELLENKOMPATIBILITAETSAUDIT.md).

S1-XW schliesst die sechs S1-XV-Blocker mit konkreten Modalitaetswerten,
Budgets, Konflikt- und Verdraengungsrollen sowie einem nichtzirkulaeren
Verhaltenskomparator. Keine Tests oder Projektfunktionen wurden ausgefuehrt.
Siehe
[S1-XW](S1XW_PPB1_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG.md).

S1-XV bestaetigt S1-XU fachlich, bindet aber sechs verbleibende
Materialisierungsblocker. Keine Tests oder Projektfunktionen wurden
ausgefuehrt. Siehe
[S1-XV](S1XV_PPB1_STATISCHER_VOLLSTAENDIGKEITS_FAIRNESS_NICHTZIRKULARITAETS_UND_MATERIALISIERBARKEITSAUDIT.md).

S1-XU bindet die zeitliche Aktualisierung unter begrenzter Kapazitaet mit
fuenf fairen Geschichten, getrennten Messrollen und eindeutigen Erfolgs-,
Stopp- und Ungueltigkeitsregeln. Implementierung, Tests und Ausfuehrung sind
nicht freigegeben. Siehe
[S1-XU](S1XU_PPB1_STATISCHER_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG_ZEITLICHE_AKTUALISIERUNG.md).

S1-XT behaelt PPB-1 als private Engineeringkomponente und Vergleichsbasis.
Als einzige naechste Funktionsfrage ist die zeitliche Aktualisierung unter
begrenzter Kapazitaet ausgewaehlt; Implementierung und Ausfuehrung bleiben
geschlossen. Siehe
[S1-XT](S1XT_PPB1_STATISCHE_ENGINEERINGEINORDNUNG_UND_EINZELFUNKTIONSWAHL.md).

S1-XS schliesst S1-XR mit `19 von 19` statisch bestandenen Rollen ab. Das
Audit nutzt nur Digests, Quelltext und AST; alle Ausfuehrungszaehler sind
null. Die technische Gleichheit zur statischen Nullprototypbaseline bleibt
ohne Memory- oder Feldwirkungsclaim. Siehe
[S1-XS](S1XS_PPB1_STATISCHER_ENGINEERINGREGRESSION_ABSCHLUSSAUDIT.md).

S1-XR implementiert die private 20-Zellen-Engineeringregression aus zwei
PPB-1-Bildungen, zehn read-only Proben und zehn statischen
Baselinedistanzen. `12 von 12` Tests bestehen; sie bleibt unexportiert und
matrixfrei. Siehe
[S1-XR](S1XR_PPB1_PRIVATE_ENGINEERING_REGRESSION_IMPLEMENTIERUNG.md).

S1-XQ bindet eine private 20-Zellen-Engineeringregression aus zwei
PPB-1-Bildungen, read-only Margin-Proben und statischer Prototypbaseline.
Erwartete Gleichheit ist technische Referenz, keine Neuheit. Siehe
[S1-XQ](S1XQ_PPB1_STATISCHER_PRIVATER_ENGINEERING_REGRESSIONSVERTRAG.md).

S1-XP bestaetigt `18 von 18` statische S1-XO-Rollen ohne Projektimport oder
Fixtureausfuehrung. Numerik, Digests, Privatheit und historische Trennung
sind geschlossen. Siehe
[S1-XP](S1XP_PPB1_STATISCHER_MARGIN_FIXTURE_IMPLEMENTIERUNGSABSCHLUSSAUDIT.md).

S1-XO implementiert die private auditive und visuelle Margin-Fixture samt
Produktionsmetrikvalidierung, separaten `nextafter`-Operatorfaellen und
Digestbindung. Zustands-, Runner- und Feldpfade bleiben ausgeschlossen.
Siehe [S1-XO](S1XO_PPB1_PRIVATE_NUMERISCHE_MARGIN_FIXTURE_UND_VALIDATOR.md).

S1-XN bindet die erhaltenen PPB-1-Engineeringrollen und eine neue private
Margin-Fixture mit binaer exakten, schwellenfernen Testwerten. Historischer
Vergleich und S1-XL-Receipt bleiben unveraendert. Siehe
[S1-XN](S1XN_PPB1_STATISCHER_ENGINEERING_UND_NUMERISCHER_FIXTURE_KORREKTURVERTRAG.md).

S1-XM ordnet die einzige S1-XL-Abweichung als inkonsistente
Gleitkomma-Grenzwertvorregistrierung ein. Der formale Fail bleibt bestehen;
zugleich ist das beobachtete Verhalten durch vier einfachere Baselines
vollstaendig erklaert. Siehe
[S1-XM](S1XM_PPB1_STATISCHER_ERGEBNIS_RECEIPT_UND_NUMERISCHER_GRENZWERTAUDIT.md).

S1-XL fuehrt die registrierten 60 Zellen genau einmal aus. Das methodisch
gueltige Receipt entscheidet bei `9 von 10` Kandidatenzellen
`TECHNICAL_MEMORY_FUNCTION_FAIL`; eine auditive Grenzwertzelle liegt mit
`0.20000000000000004` knapp ueber der `0.2`-Schwelle. Siehe
[S1-XL](S1XL_PPB1_EINMALIGER_PRIVATER_REGISTRIERTER_60_ZELLEN_LAUF.md).

S1-XK schliesst alle neun technischen Go/No-Go-Gates. Die registrierte
Ausfuehrung bleibt bis zum exakten Eigentuemerauthorisierungstext geschlossen;
alle Zaehler sind null. Siehe
[S1-XK](S1XK_PPB1_STATISCHER_REGISTRIERTER_AUSFUEHRUNGS_GO_NO_GO_UND_AUTORISIERUNGSPREFLIGHT.md).

S1-XJ bestaetigt `20 von 20` Vollrunner-, Sperren-, Receipt-, Aggregator-
und Trennungsrollen rein statisch. Die Implementierungsluecken sind
geschlossen, die registrierte Ausfuehrungsautorisierung fehlt weiterhin und
alle Auditzaehler bleiben null. Siehe
[S1-XJ](S1XJ_PPB1_STATISCHER_VOLLFORM_RUNNER_SPERREN_RECEIPT_UND_AGGREGATOR_ABSCHLUSSAUDIT.md).

S1-XI implementiert privaten Vollform-Runnerkern, 19-Rollen-Zellreceipt,
15-Rollen-Matrixreceipt und Aggregator. `12 von 12` Ersatzplantests bestehen;
der registrierte Entry stoppt vor Materialisierung und bleibt unausgefuehrt.
Siehe
[S1-XI](S1XI_PPB1_PRIVATER_VOLLFORM_RUNNER_RECEIPT_UND_AGGREGATOR_MIT_ERSATZPLAENEN.md).

S1-XH grenzt acht wiederverwendbare Rollen und drei fehlende
Vollmatrixbausteine ab. Ausfuehrungsfreigabe und registrierte Matrix bleiben
geschlossen; alle Zaehler sind null. Siehe
[S1-XH](S1XH_PPB1_STATISCHER_REGISTERED_MATRIX_IMPLEMENTIERUNGSDELTA_UND_AUSFUEHRUNGSPREFLIGHT.md).

S1-XG bestaetigt `18 von 18` statische Miniaturrunner-, Receipt-,
Reihenfolge- und Trennungsrollen. Keine Projektfunktion wurde importiert
oder ausgefuehrt; die registrierte Matrix bleibt geschlossen. Siehe
[S1-XG](S1XG_PPB1_STATISCHER_MINIATURRUNNER_ABSCHLUSSAUDIT.md).

S1-XF fuehrt pro privatem Miniaturlauf sechs PPB-1-Bildungsschritte vor dem
Vorlagenvergleich und danach 24 eigene Ersatzmatrixzellen aus. `12 von 12`
Abnahmetests bestehen; registrierte Matrixzellen und Ergebnisentscheidungen
bleiben null. Siehe
[S1-XF](S1XF_PPB1_PRIVATER_MINIATURRUNNER_UND_RECEIPTABNAHME.md).

S1-XE bindet den privaten 60-Zellen-Runner, atomare Receipts und die
Entscheidungsreihenfolge. Sechs echte Kandidatenbildungsschritte sind vor
jeder Probe Pflicht; die S1-XC-Vorlage darf Bildung nicht ersetzen. `12 von
12` statische Vertragstests bestehen, Ausfuehrungszahl null. Siehe
[S1-XE](S1XE_PPB1_STATISCHER_PRIVATER_MATRIXRUNNER_RECEIPT_UND_ENTSCHEIDUNGSVERTRAG.md).

S1-XD bestaetigt `17 von 17` statische S1-XC-Quell-, Digest-, Export- und
Nichtausfuehrungsrollen. Keine Projektfunktion wurde importiert oder
ausgefuehrt; die Matrix bleibt geschlossen. Siehe
[S1-XD](S1XD_PPB1_STATISCHER_QUELL_DIGEST_EXPORT_UND_NICHTAUSFUEHRUNGSAUDIT.md).

S1-XC implementiert private In-Memory-Fixtures, 60 Zellplaene und fuenf
read-only Baselineadapter ohne Nachzustand. `13 von 13` synthetische
Vertragstests bestehen; Matrix, PPB-1-Probe und Feld bleiben unausgefuehrt.
Siehe [S1-XC](S1XC_PPB1_PRIVATE_FIXTURE_REGISTRY_UND_READ_ONLY_BASELINEADAPTER.md).

S1-XB bestaetigt `18 von 18` statische Materialisierungs-, Registry- und
Nichtausfuehrungsrollen. Es grenzt drei private Implementierungsluecken ab;
alle Ausfuehrungszaehler bleiben null. Siehe
[S1-XB](S1XB_PPB1_STATISCHER_MATERIALISIERUNGS_REGISTRY_UND_NICHTAUSFUEHRUNGSAUDIT.md).

S1-XA bindet das kontrollierte 12/72-Profil, endliche Bildungs- und
Probeframes sowie die 60-Zellen-Registry bei Ausfuehrungszahl null. `11 von
11` statische Vertragstests bestehen. Siehe
[S1-XA](S1XA_PPB1_STATISCHER_FIXTURE_UND_MATRIXMATERIALISIERUNGSVERTRAG.md).

S1-WZ bestaetigt `20 von 20` statische Rollen der korrigierten
S1-WW-/S1-WY-Vertragslage. Alle vier S1-WX-Blocker sind geschlossen; die
Ausfuehrungszaehler bleiben null. `8 von 8` Auditstrukturtests bestehen.
Siehe [S1-WZ](S1WZ_PPB1_STATISCHER_KORRIGIERTER_VERTRAGSABSCHLUSSAUDIT.md).

S1-WY schliesst die vier S1-WX-Blocker durch erreichbare Probeabstaende,
verhaltensbezogene Baselinegleichheit, No-Memory-Nullrollen und
All-of-Aggregation. `10 von 10` statische Vertragstests bestehen. Siehe
[S1-WY](S1WY_PPB1_STATISCHER_VIER_BLOCKER_KORREKTURVERTRAG.md).

S1-WX bestaetigt `12 von 16` S1-WW-Strukturrollen und stoppt vier begrenzte
Vertragsluecken vor jeder Ausfuehrung. `8 von 8` statische Audittests
bestehen. Siehe
[S1-WX](S1WX_PPB1_STATISCHER_VOLLSTAENDIGKEITS_FAIRNESS_UND_NICHTZIRKULARITAETSAUDIT.md).

S1-WW bindet den vollstaendigen privaten Bildungs-/Probeablauf mit drei
Positiv-, zwei Negativproben und fuenf Gegenbaselines als statische
60-Zellen-Matrix. Ausfuehrung bleibt null; `12 von 12` Vertragstests
bestehen. Siehe
[S1-WW](S1WW_PPB1_STATISCHER_BILDUNGS_UND_PROBE_FUNKTIONSVERTRAG.md).

S1-WV bestaetigt `16 von 16` statische Rollen der privaten S1-WU-Probe bei
null Probe-, Zustands- und Advance-Ausfuehrungen. Quellbindung,
Zustandsunveraenderlichkeit sowie API-, Snapshot-, Produktions- und
Feldtrennung bestehen. Siehe
[S1-WV](S1WV_PPB1_STATISCHER_READ_ONLY_PROBE_ABSCHLUSSAUDIT.md).

S1-WU implementiert die private reine read-only Probe gegen stabilisierte
PPB-1-Plaetze. Der Befund enthaelt keinen Nachzustand; Bank- und
Lebenszykluswerte bleiben unveraendert. `12 von 12` synthetische
Vertragstests bestehen. Siehe
[S1-WU](S1WU_PPB1_PRIVATE_READ_ONLY_PERZEPTIVE_PROBE.md).

S1-WT bestaetigt `14 von 14` statische Wiederverwendungsrollen fuer die
spaetere read-only Probe. Vorhandene Validierung, Distanz, Digests und
Identitaet reichen ohne neue Regel oder Parameter aus; alle
Ausfuehrungszaehler bleiben null. `8 von 8` Dokumentstrukturtests bestehen.
Siehe
[S1-WT](S1WT_PPB1_STATISCHER_READ_ONLY_PROBE_IMPLEMENTIERUNGSPREFLIGHT.md).

S1-WS bindet eine private read-only perzeptive Probe gegen stabilisierte
belegte PPB-1-Plaetze. Befund und Vergleich sind digestgebunden; Nachzustand,
Advance-Aufruf, Semantik und Feldwirkung bleiben ausgeschlossen. `10 von 10`
statische Vertragstests bestehen. Siehe
[S1-WS](S1WS_PPB1_STATISCHER_READ_ONLY_PERZEPTIVER_PROBEVERTRAG.md).

S1-WR bestaetigt `14 von 14` statische Strukturrollen des privaten
S1-WQ-Zustandslebenszyklus. Ziel- und Referenzmodul wurden nicht importiert
oder ausgefuehrt; neue Tests, Runtimepfade und Feldwirkungen bleiben null.
Siehe [S1-WR](S1WR_PPB1_STATISCHER_ZUSTANDSLEBENSZYKLUS_AUDIT.md).

S1-WQ bildet den privaten perzeptiven Zustandslebenszyklus als
digestgebundene Sicht auf genau einen Schritt des bestehenden reinen
PPB-1-Referenzkerns ab. Bildung, Fortsetzung, Stabilisierung, begrenzte
Aktualisierung und Verwerfen werden unterschieden; Semantik, Persistenz,
Feldrueckwirkung und Produktion bleiben ausgeschlossen. `14 von 14` neue und
`332 von 332` aktuelle fokussierte PPB-1-Tests bestehen. Siehe
[S1-WQ](S1WQ_PPB1_PRIVATER_PERZEPTIVER_ZUSTANDSLEBENSZYKLUS.md).

S1-WO bestaetigt statisch acht private Strukturrollen
der S1-WN-Komposition. Exakt sechs Produktionsbindungen bleiben offen; keine
Receipt-, Adapter- oder Koordinatorfunktion wurde ausgefuehrt. `10 von 10`
neue und `308 von 308` aktuelle fokussierte PPB-1-Tests bestehen. Siehe
[S1-WO](S1WO_PPB1_STATISCHER_RECEIPT_KOMPOSITIONSPREFLIGHT.md).

S1-WN komponiert drei bereits erzeugte private
Root-/Ressourcen-/Textvalidierungsreceipts digestgebunden in der bestehenden
In-Memory-H0A-bis-H1-Reihenfolge und stoppt vor H2. Neun
Produktionswirkungen bleiben null. `12 von 12` neue und `298 von 298`
aktuelle fokussierte PPB-1-Tests bestehen. Siehe
[S1-WN](S1WN_PPB1_PRIVATE_RECEIPT_KOORDINATORKOMPOSITION.md).

S1-WM bestaetigt statisch acht private Strukturrollen
des S1-WL-Validators. Exakt sechs Produktionsbindungen bleiben offen; keine
Validator- oder H0D-Funktion wurde ausgefuehrt. `10 von 10` neue und `286 von
286` aktuelle fokussierte PPB-1-Tests bestehen. Siehe
[S1-WM](S1WM_PPB1_STATISCHER_AUTORISIERUNGSVALIDATOR_PREFLIGHT.md).

S1-WL implementiert einen reinen privaten Validator fuer
injizierten Autorisierungstext und gebundene Digests. Exakte Uebereinstimmung
bleibt ausdruecklich ohne Frischepruefung, Freigabeverbrauch oder
Produktionsautorisierung. `12 von 12` neue und `276 von 276` aktuelle
fokussierte PPB-1-Tests bestehen. Siehe
[S1-WL](S1WL_PPB1_PRIVATER_AUTORISIERUNGSVALIDATORADAPTER.md).

S1-WK bestaetigt statisch acht private Strukturrollen
der S1-WJ-Root-/Ressourcenadapter. Exakt sechs Produktionsbindungen bleiben
offen; keine Adapter- oder Koordinatorfunktion wurde ausgefuehrt. `10 von
10` neue und `264 von 264` aktuelle fokussierte PPB-1-Tests bestehen. Siehe
[S1-WK](S1WK_PPB1_STATISCHER_ROOT_RESSOURCENADAPTER_PREFLIGHT.md).

S1-WJ implementiert private Rootspiegel- und
Ressourcenreceipts sowie reine H0B-/H0C-Adapter. Produktionswurzel und
Betriebssystemressourcen bleiben unberuehrt; vier Ressourcenrollen werden
nur injiziert. `12 von 12` neue und `254 von 254` aktuelle fokussierte
PPB-1-Tests bestehen. Siehe
[S1-WJ](S1WJ_PPB1_PRIVATE_ROOT_UND_RESSOURCENADAPTER.md).

S1-WI bestaetigt statisch Vertrag, S1-WH-Quelle, sechs
private Rollentypen, reine Adapter, nicht aufrufbaren Producer-Resolver und
H2-Sperre. Exakt sechs Produktionsintegrationen bleiben offen. `10 von 10`
neue und `242 von 242` aktuelle fokussierte PPB-1-Tests bestehen bei null
Runtimewirkung. Siehe
[S1-WI](S1WI_PPB1_STATISCHER_KOORDINATOR_PREFLIGHT.md).

S1-WH implementiert private Integrationsrollentypen und
eine reine In-Memory-H0A-bis-H1-Koordinatorhuelle. Sie stoppt zwingend vor
H2; der Producer-Resolver ist nicht aufrufbar und alle Produktionswirkungen
bleiben null. `11 von 11` neue und `232 von 232` aktuelle fokussierte
PPB-1-Tests bestehen. Siehe
[S1-WH](S1WH_PPB1_PRIVATE_IN_MEMORY_KOORDINATORHUELLE.md).

S1-WG bindet statisch sechs Produktionsintegrationsrollen
mit Vorbedingungen, Integrationswirkung und Stoppregel sowie die exakte
H0-H7-Reihenfolge. `8 von 8` neue und `221 von 221` aktuelle fokussierte
PPB-1-Tests bestehen; es wurde nichts implementiert oder ausgefuehrt. Siehe
[S1-WG](S1WG_PPB1_STATISCHER_PRODUKTIONSINTEGRATIONSDELTA_VERTRAG.md).

S1-WF bestaetigt statisch die privaten S1-WD- und
S1-WE-Rollen und bindet exakt sechs verbleibende Produktionsintegrationsblocker.
`10 von 10` neue und `213 von 213` aktuelle fokussierte PPB-1-Tests bestehen
bei null Ressourcen-, Dateisystem-, Autorisierungs- oder Producerwirkung.
Siehe
[S1-WF](S1WF_PPB1_STATISCHER_ROLLEN_UND_INTEGRATIONSPREFLIGHT.md).

S1-WE implementiert private kanonische Lock-, Erfolgs-
und Fehlerrollen mit exklusivem Dauer-Lock und atomarer, nicht ersetzender
Terminalpublikation. Die Dateiwirkung bleibt auf synthetische Fixtures unter
der Betriebssystem-Temporaerwurzel begrenzt. `12 von 12` neue und `203 von
203` aktuelle fokussierte PPB-1-Tests bestehen. Siehe
[S1-WE](S1WE_PPB1_PRIVATE_LOCK_UND_TERMINALROLLEN_MIT_TEMPORAERABNAHME.md).

S1-WD implementiert reale Speicher-, Datentraeger-,
Volume- und Atomaritaetsbeobachtung ausschliesslich unter einer dedizierten
Betriebssystem-Temporaerwurzel. `11 von 11` neue und `191 von 191` aktuelle
fokussierte PPB-1-Tests bestehen. Autorisierung, Producer,
Produktionsartefakte und Matrixausfuehrung bleiben gesperrt. Siehe
[S1-WD](S1WD_PPB1_PRIVATER_TEMPORAERER_H0_RESSOURCEN_UND_ATOMARITAETSBEOBACHTER.md).

S1-WC bestaetigt statisch Vertrag, Kalibrierung,
Ressourcen-/Autorisierungsfelder und bindet exakt sechs verbleibende
Produktionsblocker. `9 von 9` neue und `195 von 195` kombinierte Tests
bestehen, ohne Ressourcenprobe oder Produceraufruf. Siehe
[S1-WC](S1WC_PPB1_STATISCHER_POST_IMPLEMENTIERUNGS_PREFLIGHT_DER_PRODUKTIONSROLLEN.md).

S1-WB implementiert private injizierte
Ressourcenbeobachtung, deterministisches Gate und einen nicht autorisierenden
H0-Kandidaten. Der positive synthetische Fall stoppt exakt an H0D; Produktion
bleibt gesperrt. `12 von 12` neue und `186 von 186` kombinierte Tests
bestehen. Siehe
[S1-WB](S1WB_PPB1_PRIVATE_PRODUKTIONSROLLEN_UND_SYNTHETISCHE_H0_GATEABNAHME.md).

S1-WA bindet statisch Produktionsressourcen-, Gate-,
Autorisierungs-, Lock- und Terminalrollen sowie die feste H0A-bis-H0E-/
H1-bis-H7-Reihenfolge. Nur eine spaeter zu rendernde Autorisierungsvorlage
liegt vor; Produktion und reale Matrix bleiben gesperrt. Siehe
[S1-WA](S1WA_PPB1_STATISCHER_PRODUKTIONSBINDUNGS_RESSOURCEN_UND_AUTORISIERUNGSVERTRAG.md).

S1-VZ schliesst die private synthetische
Drei-Prozess-Ressourcenkalibrierung ab. Gebunden sind maximal rund
`188,15 MiB` zusaetzlicher RSS, rund `33,22 MiB` Erfolgs-/Temporaerartefakt
sowie Produktionsuntergrenzen von `2 GiB` freiem physischen Speicher und
`1 GiB` freiem Artefaktvolume. Produktion bleibt unautorisiert. Siehe
[S1-VZ](S1VZ_PPB1_PRIVATE_SYNTHETISCHE_RESSOURCENKALIBRIERUNG_UND_GATEABNAHME.md).

S1-VY bindet statisch drei frische synthetische
Ressourcenkalibrierungen, stufenweise RSS- und Artefaktmessungen,
Plattform-/Quellbindung sowie konservative Speicher- und Datentraegerreserven.
Es wurde noch keine Ressource abgefragt oder Pipeline ausgefuehrt. Siehe
[S1-VY](S1VY_PPB1_STATISCHER_PRODUKTIONS_RESSOURCENMESS_UND_GATEVERTRAG.md).

S1-VX bestaetigt statisch Plan, Runnerkoerper,
S1-VT-Pipeline und synthetische S1-VW-Handoffhuelle. Exakt fuenf
Produktionsrollen fehlen noch; deshalb bleiben Produktionsentry und reale
Autorisierung gesperrt. `9 von 9` neue und `164 von 164` kombinierte Tests
bestehen, ohne eine Runner-, Pipeline- oder Ressourcenfunktion auszufuehren.
Siehe
[S1-VX](S1VX_PPB1_STATISCHER_POST_INTEGRATIONS_UND_RESSOURCEN_PREFLIGHT.md).

S1-VW implementiert und prueft privat die feste
H0-bis-H7-Handoffkette mit injiziertem synthetischem Producer, dauerhaftem
Sperrmarker sowie atomaren Erfolgs- und Fehlerartefakten. `11 von 11` neue
und `155 von 155` kombinierte fokussierte Tests bestehen; null registrierte
Matrixpfade wurden ausgefuehrt. Produktionsentrypoint, API und Snapshot
bleiben gesperrt beziehungsweise unveraendert. Siehe
[S1-VW](S1VW_PPB1_PRIVATE_SYNTHETISCHE_EINMALLAUF_HANDOFF_UND_TERMINALHUELLEN_ABNAHME.md).

S1-VV bindet statisch die feste H0-bis-H7-
Handoffreihenfolge, dauerhaften Freigabeverbrauch vor dem ersten Aufruf,
prozessuebergreifende Wiederholungssperre und atomare terminale Erfolgs- oder
Fehlerartefakte ohne Teilresultat. Es wurden weder Code noch Tests oder
Matrixpfade ausgefuehrt. Siehe
[S1-VV](S1VV_PPB1_STATISCHER_EINMALLAUF_HANDOFF_ERGEBNIS_UND_FEHLERVERTRAG.md).

S1-VU bestaetigt Plan, Budget, Nullstand, Gate, Runnerkoerper und S1-VT-
Stufen. Die drei dort erkannten Anschlussluecken sind mit S1-VV auf
Vertragsniveau geschlossen. Siehe
[S1-VU](S1VU_PPB1_STATISCHER_REALER_HANDOFF_POST_IMPLEMENTIERUNGS_PREFLIGHT.md).

S1-VT implementiert privat die atomare 528-Receipt-Huelle, den reinen
48-Arm-Compositor mit Evidenzledger und den korrigierten v2-Auswerter. Die
Abnahme verwendet 75.808 konstruierte Schrittbeobachtungen, aber keinen PPB-,
Baseline- oder Matrixaufruf. Siehe
[S1-VT](S1VT_PPB1_PRIVATE_ERGEBNISHUELLE_COMPOSITOR_UND_V2_AUSWERTER_ABNAHME.md).

S1-VS bindet statisch die atomare Ergebnisversiegelung, den eindeutigen
48-Arm-Compositor, feste Diagnose- und Lebenszyklusrollen sowie getrennte
Zustands-, Identitaets- und Aufrufbudgets. Die Vertragsrollen sind mit S1-VT
privat synthetisch implementiert. Siehe
[S1-VS](S1VS_PPB1_STATISCHER_ERGEBNIS_PIPELINE_KORREKTURVERTRAG.md).

S1-VR bestaetigt statisch den korrigierten 528-Pfad-Plan, die Baseline-
Identitaeten und 144 R1-Frischwiederholungen. Von maximal 75.808 Aufrufen
wurden null ausgefuehrt. Die dort erkannten Ergebnis-Pipeline-Luecken sind
mit S1-VS auf Vertragsniveau geschlossen. Siehe
[S1-VR](S1VR_PPB1_ABSCHLIESSENDER_STATISCHER_KORRIGIERTER_VOLLMATRIX_PREFLIGHT.md).

S1-VQ implementiert den atomaren Baseline-Identitaetscarry und den
korrigierten 528-Pfad-Plan. Der neue Plan-Digest lautet
`f3073634...dcd1210`; von maximal 75.808 registrierten Aufrufen wurden null
ausgefuehrt. Siehe
[S1-VQ](S1VQ_PPB1_PRIVATE_IDENTITAETSROLLEN_UND_KORRIGIERTER_MATRIXPLANER.md).

S1-VP bindet statisch eindeutige Baseline-
Eintragsidentitaeten sowie je einen zweiten F04/F05/F06-Frischstartpfad. Der
korrigierte Plan wird 528 Faelle und maximal 75.808 Aufrufe umfassen. Der
bisherige 384-Pfad-Plan bleibt unveraenderter Elternstand; Implementierung
und Matrixausfuehrung sind noch gesperrt. Siehe
[S1-VP](S1VP_PPB1_STATISCHER_IDENTITAETS_UND_WIEDERHOLUNGSKORREKTURVERTRAG.md).

S1-VO implementiert den reinen 48-Arm-Auswerter und
stoppt den Vollmatrix-Preflight an zwei methodischen Luecken: fehlende
Baseline-Eintragsidentitaet und fehlende zweite F04/F05/F06-Pfade. Plan,
Budget, Kausalhistorien, Resultatrollen und Gate sind ansonsten konsistent.
`15 von 15` neue und `96 von 96` kombinierte Tests bestehen; null
registrierte Matrixaufrufe wurden ausgefuehrt. Siehe
[S1-VO](S1VO_PPB1_REINER_AUSWERTER_UND_STATISCHER_VOLLMATRIX_PREFLIGHT.md).

S1-VN implementiert privat die Fixturegeneratoren,
sieben Vergleichsadapter, den 384-Pfad-Plan und den internen Matrixrunner.
`19 von 19` neue und `81 von 81` kombinierte fokussierte Tests bestehen. Der
Vollmatrix-Einstieg bleibt hart gesperrt; null registrierte Matrixaufrufe
wurden ausgefuehrt. Siehe
[S1-VN](S1VN_PPB1_PRIVATE_FIXTURE_BASELINE_UND_MATRIXRUNNER_ABNAHME.md).

S1-VM bindet fuer das kontrollierte `12/72`-Profil drei
feste Parameterrecords, acht labelfreie numerische Verlaufstypen und sieben
faire Vergleichsadapter. Vorregistriert sind 48 PPB- und 336 Baselinefaelle
mit hoechstens 74.368 akzeptierten Aufrufen. Es wurde noch kein Runner
implementiert und kein Fall ausgefuehrt. Siehe
[S1-VM](S1VM_PPB1_STATISCHER_PARAMETERWAHL_BASELINE_UND_AUSFUEHRUNGSMATRIXVERTRAG.md).

S1-VL implementiert den privaten Profilbinder fuer vier
vorhandene reduzierte Rezeptorprofile. Die Geometrien `8/18`, `12/72`,
`48/240` und `48/288` werden aus den bestehenden Rezeptorklassen abgeleitet;
Parameter ausserhalb der S1-VK-Korridore werden fail-closed abgelehnt. Die
Abnahme besteht mit `14 von 14` neuen und `62 von 62` kombinierten
fokussierten Tests. Feldkern, API, Snapshot und Medienruntime bleiben
unveraendert. Siehe
[S1-VL](S1VL_PPB1_PRIVATER_REZEPTORPROFILBINDER_UND_DIMENSIONSSKALIERTE_SYNTHETISCHE_ABNAHME.md).

S1-VK bindet vier vorhandene Rezeptorprofile mit
`8/18`, `12/72`, `48/240` und `48/288` auditiven/visuellen Traegern statisch
an PPB-1. Maximal 32 auditive und 16 visuelle Slots sowie getrennte
Parameterkorridore sind zugelassen. Kein Adapter oder Medienlauf wurde
ausgefuehrt. Siehe
[S1-VK](S1VK_PPB1_STATISCHER_REZEPTORBINDUNGS_SKALIERUNGS_UND_PARAMETERKORRIDORAUDIT.md).

S1-VJ implementiert den privaten reinen PPB-1-Kern und
die 30 registrierten synthetischen Vertragspfade. `30 von 30` PPB-Pfade und
`18 von 18` Aktivkern-Grenztests bestehen. Feldkern, `current_api`,
Root-Exports und Snapshot bleiben unveraendert. Siehe
[S1-VJ](S1VJ_PPB1_PRIVATER_REINER_REFERENZKERN_UND_SYNTHETISCHE_VERTRAGSABNAHME.md).

S1-VI bindet fuer `PPB-1` getrennte private auditive und
visuelle Banken, normalisierte mittlere L1-Distanz, deterministische Slotwahl,
konvexe Aktualisierung, saettigende Stabilisierung, schrittbasiertes Vergessen
und LRU-Ersetzung. Eine synthetische 30-Pfade-Matrix ist vorregistriert, aber
nicht ausgefuehrt. Siehe
[S1-VI](S1VI_PPB1_STATISCHER_DATEN_DISTANZ_LEBENSZYKLUS_UND_TESTMATRIXVERTRAG.md).

S1-VH oeffnet `PPB-1` als transparente Engineeringlinie
fuer getrennte auditive und visuelle Prototypbanken. Nur reduzierte
Rezeptorzustaende sind zulaessig; Rohhistorie, Semantik und direkter
Feldzugriff bleiben ausgeschlossen. Zuordnung, Aktualisierung,
Stabilisierung, Vergessen und Kapazitaetskonflikt muessen begrenzt und
deterministisch sein. Siehe
[S1-VH](S1VH_PPB1_STATISCHER_ENGINEERING_FUNKTIONS_SICHERHEITS_UND_INTEGRATIONSVERTRAG.md).

S1-VG stoppt `MPZ-1` als eigenstaendigen
Forschungskandidaten. Seine Bildung, Stabilisierung, Aktualisierung,
Konkurrenz, Freigabe und spaetere Feldwirkung werden strukturell vollstaendig
durch eine begrenzte konkurrenzfaehige gemeinsame Prototypbank abgebildet.
Eine solche Bank bleibt eine moegliche Engineeringbaseline, ist aber nicht
implementiert und kein Funktionsbefund. Siehe
[S1-VG](S1VG_MPZ1_STATISCHER_UEBERGANGSQUELLEN_UND_BASELINE_NICHTDUPLIZIERUNGSAUDIT.md).

S1-VF bindet fuer `MPZ-1` eine feste private
Traegermenge an den vorhandenen Audio-Video-Dockgrenzmotiven. Die Rollen
verfuegbar, formend, stabilisiert und loesend sind lokal ausschliesslich und
vollstaendig bilanziert. Rohdaten, Folgen, Labels und Fernkanten bleiben
verboten. Die Anatomie ist nur bedingt zugelassen; Uebergangsursachen und die
Nichtreduzierbarkeit gegen eine konkurrenzfaehige gemeinsame Prototypbaseline
sind offen. Siehe
[S1-VF](S1VF_MPZ1_STATISCHER_ANATOMIE_URSACHEN_UND_BILANZVOLLSTAENDIGKEITSAUDIT.md).

S1-VE bindet `MPZ-1` als statischen Kandidaten fuer eine
modalitaetsuebergreifende perzeptive Zustandsbildung. Eine Paarungs- und
Vertauschungskontrolle muss bei identischen auditiven und visuellen
Einzelreizstatistiken nach Angleichung von Eingang, Einzelspuren und S/H eine
eigene spaetere Feldprognose tragen. Die staerkste unmittelbare Baseline ist
eine begrenzte gemeinsame gleitende Paarstatistik. Gleichung, Anatomie,
Implementierung, Test und Feldlauf bleiben aus. Siehe
[S1-VE](S1VE_MPZ1_STATISCHER_KANDIDATEN_UND_FALSIFIKATIONSVERTRAG.md).

S1-VD stoppt LCB-1 weiterhin mit `NO_ENDOGENOUS_CAUSE`. Der aktive
Feldfluss ist eine skalare Gradientendifferenz; die orientierte Summe um eine
elementare Schleife ist jederzeit exakt null. Eine zeitliche Rundfolge
benoetigt eine neue, in S1-VC nicht vorhandene Sequenzzustandsmechanik. Ein
gueltiges `H_CW/H_CCW`-Paar und ein fairer Angleichvergleich sind daher nicht
vorregistrierbar. Gleichung, Implementierung und Lauf bleiben aus. Siehe
[S1-VD](S1VD_LCB1_STATISCHER_KAUSALHISTORIEN_UND_ANGLEICHBARKEITSAUDIT.md),
[S1-VC](S1VC_LCB1_STATISCHER_ANATOMIE_UND_BILANZVOLLSTAENDIGKEITSAUDIT.md),
[S1-VB](S1VB_LCB1_STATISCHER_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG.md),
[S1-VA](S1VA_STATISCHER_KANDIDATENRAUMAUDIT_LOKALE_TECHNISCHE_URSACHEN.md),
[S1-UZ](S1UZ_STATISCHER_ABSCHLUSSAUDIT_AKTIVKERN_KONSOLIDIERUNG.md),
[S1-UY](S1UY_AKTIVKERN_REPRODUZIERBARKEITS_UND_DRIFTARTEFAKTAUDIT.md),
[S1-UX](S1UX_AKTIVKERN_KONSOLIDIERUNG_UND_DRIFTPRUEFUNG.md),
[S1-UW](S1UW_LRDE1_STATISCHER_ABSCHLUSS_UND_OBERFLAECHENKONSOLIDIERUNGSAUDIT.md),
[S1-UV](S1UV_LRDE1_STATISCHER_ENGINEERINGNUTZEN_UND_ZWEIGABSCHLUSSAUDIT.md),
[S1-UU](S1UU_LRDE1_STATISCHER_RICHTUNGS_UND_BASELINEREDUKTIONSAUDIT.md),
[S1-UT](S1UT_LRDE1_STATISCHER_BERECHENBARKEITSAUDIT.md),
[S1-US](S1US_LRDE1_LOKALER_KAUSAL_UND_LEBENSZYKLUSVERTRAG.md),
[S1-UR](S1UR_LRD1_ANATOMIE_BEGRENZUNGS_UND_BASELINEKOLLISIONSAUDIT.md),
[S1-UQ](S1UQ_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG_LOKALE_RUECKFUEHRUNGSDISPOSITION.md),
[S1-UP](S1UP_READONLY_REFERENZAUDIT_MCM_ABHANDLUNGEN_A_BIS_X.md),
[S1-UO](S1UO_REPOSITORYWEITER_MEMORY_ANHALTSPUNKTAUDIT.md) und
[S1-UN](S1UN_TECHNISCHER_KONSOLIDIERUNGSAUFTRAG_UND_WIEDEROEFFNUNGSTOR.md).

S1-VD ist fachlich abgenommen und LCB-1 terminal geschlossen. Ohne neue
Richtungsfreigabe bleibt die Kandidatenforschung pausiert. Eine Wiederaufnahme
erfordert erneut einen statischen Vertrag mit lokaler Ursache, Bilanz,
erreichbarer Geschichte, eigener Feldprognose, staerkster Gegenbaseline und
klarer Stoppbedingung.

Die nachfolgenden W7- und anderen historischen Registereintraege sind kein
aktueller Arbeitsauftrag.

- [W7-AP Rohdistanzkompositor](W7AP_ROHER_R1_R2_R2_R4_DISTANZKOMPOSITOR.md):
  privater Kompositor fuer 70 R1/R2- und R2/R4-Rohdistanzen sowie 105
  Same-Resolution-Nullkontrollen. Der schnelle Verbund besteht mit `54
  tests, OK`; ein reales numerisches W7-AP-Ergebnis steht noch aus.

- [W7-AQ numerischer Auswertungs- und Ergebnisvertrag](W7AQ_STATISCHER_NUMERISCHER_AUSWERTUNGS_UND_ERGEBNISVERTRAG.md):
  wertfreie Vorregistrierung der 70 Komponentenpruefungen, der zwei
  numerischen Ergebniszustaende und des nur nach Konvergenz zulaessigen
  Numerik- und Effektbodens. Keine Funktions- oder Memoryentscheidung.

- [W7-AR reiner numerischer Einmal-Auswerter](W7AR_REINER_NUMERISCHER_EINMAL_AUSWERTER.md):
  private Implementierung der 70 Komponentenpruefungen und der beiden
  numerischen Ergebniszustaende. Kein realer Zahlenlauf und keine
  Funktionsinterpretation.

- [W7-AS terminaler In-Memory-Handoff](W7AS_TERMINALER_IN_MEMORY_HANDOFF_W7AN_AP_AR.md):
  einmalige direkte Uebergabe eines fertig materialisierten W7-AN-Containers
  ueber W7-AP an W7-AR, ohne Persistenz, Runner oder zusaetzliche
  Integration.

- [W7-AT realer numerischer R1/R2/R4-Gesamtlauf](W7AT_REALER_NUMERISCHER_R124_GESAMTLAUF.md):
  36 reale Primaer-/Gegenlaufphasen und unmittelbare W7-AS-Auswertung. Alle
  70 Komponenten konvergieren; technischer Numerikbefund ohne Funktions-
  oder Memoryclaim.

- [W7-AU Bestands- und Anschlussaudit der W7-L-Baselines](W7AU_STATISCHER_BESTANDS_UND_ANSCHLUSSAUDIT_W7L_BASELINES.md):
  alle zehn Mechaniken existieren, aber ihre terminal W7-AT-vergleichbaren
  Ergebnisse fehlen. Trennt vorhandene Obserververlaeufe von fehlenden
  Feld- und Interventionstrajektorien.

- [W7-AV roher Observer-Siebenpfad-Kontrastbinder](W7AV_ROHER_OBSERVER_SIEBENPFAD_KONTRASTBINDER.md):
  bindet 24 rohe LEAK-/SAT-/NORM-Pfadkontrastkurven aus W7-AC und sperrt die
  dimensionswidrige Anwendung des W7-AT-Feldbodens auf Observerausgaben.

- [W7-AW Vertrag fuer Observer-eigenen Aufloesungs- und Profilvergleich](W7AW_VERTRAG_OBSERVER_EIGENER_AUFLOESUNGS_UND_PROFILVERGLEICH.md):
  registriert Wiederholungsboden, symmetrische Profilbildung, festen
  Erklaerungsgrenzwert und LEAK-/SAT-/NORM-Praezedenz ohne Ergebniswerte vor.

- [W7-AX reiner In-Memory-Observerprofilauswerter](W7AX_REINER_IN_MEMORY_OBSERVERPROFIL_AUSWERTER.md):
  bestaetigt 105 exakte Wiederholungskontrollen und bildet sechs aufgeloeste
  Observerprofile, ohne CAP-Vergleich oder Erklaerungsentscheidung.

- [W7-AY Vertrag fuer dimensionslose CAP-Feldprofile](W7AY_VERTRAG_DIMENSIONSLOSE_CAP_FELDPROFILE.md):
  bindet acht direkte W7-AG-Pfadkontraste, die gemeinsame S/H-Linf-Metrik,
  W7-AT-Nennergrenze und die reine Kontrollrolle von W7-AK.

- [W7-AZ reiner In-Memory-CAP-Feldprofilkompositor](W7AZ_REINER_IN_MEMORY_CAP_FELDPROFILKOMPOSITOR.md):
  bildet acht rohe CAP-Pfadkontrastkurven und zwei aufgeloeste CAP-Profile,
  ohne Observervergleich oder Funktionsentscheidung.

- [W7-BA Vertrag fuer dimensionslosen CAP-Observer-Profilvergleich](W7BA_VERTRAG_DIMENSIONSLOSER_CAP_OBSERVER_PROFILVERGLEICH.md):
  registriert Profil-Linf, AB-/BA-Maximum, Grenze `0.05` und feste
  LEAK-/SAT-/NORM-Praezedenz ohne Ergebniswerte.

- [W7-BB terminaler In-Memory-CAP-Observer-Profilauswerter](W7BB_TERMINALER_IN_MEMORY_CAP_OBSERVER_PROFILAUSWERTER.md):
  kanonisches Ergebnis `PROFILE_NOT_MATCHED`; keine der drei externen
  Observerbaselines erklaert beide CAP-Profilrichtungen innerhalb `0.05`.

- [W7-BC Vertrag fuer CONST-V-R1/R2/R4-Siebenpfad-Trajektorien](W7BC_VERTRAG_CONST_V_R124_SIEBENPFAD_TRAJEKTORIEN.md):
  wertfreie Vorregistrierung der ersten engen Feldbaseline mit eigener
  Konvergenzschwelle; noch kein Verbraucher, Lauf oder Funktionsbefund.

- [W7-BD privater CONST-V-Zustands- und Runtimeadapter](W7BD_PRIVATER_CONST_V_ZUSTANDS_UND_RUNTIMEADAPTER.md):
  setzt den CONST-V-Arm vor dem Safe-Step und bindet den bestehenden W7-N-
  Kern an die bestehende SSPRK33-Runtime, noch ohne Pfadverbrauch oder Lauf.

- [W7-BE CONST-V-AB/R1-Einpfadverbraucher](W7BE_CONST_V_AB_R1_EINPFADVERBRAUCHER.md):
  vollstaendige technische AB/R1-Hauptkette mit fuenf isolierten,
  fastzustandsausgerichteten Proben und rohen S/H/Skalar-Samples.

- [W7-BF Vertrag fuer AB/R1-Wiederholung und BA/R1](W7BF_VERTRAG_CONST_V_AB_R1_WIEDERHOLUNG_UND_BA_R1.md):
  bindet die exakte AB/R1-Reproduktion als Stoppschranke vor dem
  symmetrischen BA/R1-Gegenpfad, noch ohne Ausfuehrung oder Distanzen.

- [W7-BG CONST-V-AB/R1-Wiederholung und BA/R1-Executor](W7BG_CONST_V_AB_R1_WIEDERHOLUNG_UND_BA_R1_EXECUTOR.md):
  bestaetigt die exakte AB/R1-Reproduktion und materialisiert danach BA/R1;
  beide Rollen bleiben rohe technische Trajektorien ohne Auswertung.

- [W7-BH Vertrag fuer AB/BA-R2 und rohe D12-Vorbereitung](W7BH_VERTRAG_CONST_V_AB_BA_R2_WIEDERHOLUNG_UND_RAW_D12.md):
  bindet R2-Wiederholungen fuer beide Richtungen und erlaubt danach nur die
  wertfreie Vorbereitung einer rohen R1/R2-Struktur.

- [W7-BI CONST-V-AB/BA-R2 und rohe D12-Vorbereitung](W7BI_CONST_V_AB_BA_R2_D12_VORBEREITUNG.md):
  erzeugt beide R2-Rollen und bindet ihre R1/R2-Digests, ohne Distanz- oder
  Konvergenzauswertung.

- [W7-BJ Vertrag fuer AB/BA-R4 und Konvergenz](W7BJ_VERTRAG_CONST_V_AB_BA_R4_UND_KONVERGENZ.md):
  registriert R4 und die spaetere 70-fache R2/R4-S/H-Pruefung, noch ohne
  Ausfuehrung oder Zahlenwerte.

- [W7-BK CONST-V-AB/BA-R4-Executor](W7BK_CONST_V_AB_BA_R4_EXECUTOR.md):
  erzeugt beide R4-Rollen technisch; die getrennte 70-fache
  Konvergenzauswertung bleibt danach noch offen.
- [W7-BL CONST-V-Siebenpfad-Voraussetzung](W7BL_CONST_V_SIEBENPFAD_VORAUSSETZUNG.md):
  sperrt die 70-fache Auswertung, bis alle sieben Pfade in R1/R2/R4 gebunden
  sind.
- [W7-BM CONST-V-Siebenpfad-Executor](W7BM_CONST_V_SIEBENPFAD_EXECUTOR.md):
  erweitert den privaten Materialisierer; der Gesamt-Lauf muss wegen der
  Laufzeit in getrennten In-Memory-Shards erfolgen.
- [W7-BN CONST-V-Shard-Executor](W7BN_CONST_V_SHARD_EXECUTOR.md):
  materialisiert genau eine Pfad-/Aufloesungsrolle pro privatem Shard.
- [W7-BO CONST-V-Konvergenzauswerter](W7BO_CONST_V_KONVERGENZAUSWERTER.md):
  bildet die 70 gebundenen S/H-Rohvergleiche ohne funktionale Interpretation.
- [W7-BP CONST-V-Engineering-Uebergabe](W7BP_CONST_V_ENGINEERING_UEBERGABE.md):
  ordnet den Numerikbefund ein und haelt die Substratwiedereroeffnung gesperrt.
- [W7-BQ transparenter Baseline-Anschlussvertrag](W7BQ_TRANSPARENTER_BASELINE_ANSCHLUSSVERTRAG.md):
  bindet den passiven Snapshotvergleich im aktuellen Engineering-API-Pfad.
- [W7-BR kontrollierter Baseline-Testweltvertrag](W7BR_KONTROLLIERTER_BASELINE_TESTWELTVERTRAG.md):
  bindet die synthetische Audio-/Video-Testwelt, Digests und Snapshotpunkte.
- [W7-BR technischer Baseline-Lauf](W7BR_TECHNISCHER_ZWEIARM_LAUF.md):
  dokumentiert den numerischen Dreiarmvergleich und die Wiederholbarkeit ohne
  Memory- oder KI-Claim.
- [S1-AC Richtungsentscheid zur Substratentwicklung nach der Baseline](S1AC_RICHTUNGSENTSCHEID_SUBSTRATENTWICKLUNG_NACH_BASELINE.md):
  aktiviert die konzeptionelle Substratlinie, waehrend Runtimeimplementierung
  und Memory-Claims gesperrt bleiben.
- [S1-AD Kandidatenvertrag lokal feldvermittelte Umformbarkeit](S1AD_KANDIDATENVERTRAG_LOKALE_FELDVERMITTELTE_UMFORMBARKEIT.md):
  formuliert die erste konkrete Substratrolle `C_i` und weist die noch offene
  Naturursache aus.
- [S1-AE `C_i` als digitale Materialhypothese](S1AE_CI_DIGITALE_MATERIALHYPOTHESE.md):
  trennt das hypothetische MCM-Wirkprinzip von der entwickelbaren digitalen
  Traegerschicht `C_i`.
- [S1-AF Materialeigenschaft lokale feldvermittelte Akkommodation](S1AF_CI_MATERIALEIGENSCHAFT_LOKALE_AKKOMMODATION.md):
  bestimmt die erste konkrete `C_i`-Materialhypothese, ohne Gleichung oder
  Runtimefreigabe.
- [S1-AG Gemeinsame Ursache lokale Feldabweichung](S1AG_CI_GEMEINSAME_URSACHE_LOKALE_FELDABWEICHUNG.md):
  bindet die vorlaeufige gemeinsame Ursache fuer Bildung und Rueckwirkung von
  `C_i` und verlangt die Baseline-Reduktion vor Implementierung.
- [S1-AH Minimale Gleichungsform fuer `C_i`](S1AH_CI_MINIMALGLEICHUNG_FELDABWEICHUNG.md):
  formuliert die begrenzte Pruefform und haelt die Rueckwirkung `R` noch offen.
- [S1-AI Konjugierte Rueckwirkung des `C_i`-Substrats](S1AI_CI_KONJUGIERTE_RUECKWIRKUNG.md):
  bindet einen gemeinsamen lokalen Austauschterm fuer Substratbildung und
  Feldrueckwirkung.
- [S1-AJ Baseline-Reduktion des `C_i`-Austauschmodells](S1AJ_CI_BASELINE_REDUKTION_AUSTAUSCHTERM.md):
  reduziert die einfachste Form auf eine technische leaky-/Integratorbaseline
  und verhindert einen unbegruendeten Naturclaim.
- [S1-AK Passiver `C_i`-Substratpfad ueber synthetische AV-Testwelten](S1AK_CI_PASSIVER_AV_SUBSTRATPFAD.md):
  dokumentiert unterschiedliche technische `C_i`-Zustaende ohne Rueckwirkung
  auf das schnelle Feld.
- [S1-AL Passive `C_i -> S`-Rueckwirkungsablation](S1AL_CI_RUECKWIRKUNGSABLATION_PASSIV.md):
  dokumentiert die technische Rueckwirkungsprojektion ohne Rueckschreibung in
  den naechsten Feldschritt.
- [S1-AM Gekoppelte `C_i -> S`-End-to-End-Ablation](S1AM_CI_GEKOPELTES_END_TO_END_ABLATION.md):
  zeigt die technische spaetere Snapshotdifferenz bei aktivierter
  Rueckwirkungsbaseline.
- [S1-AN Dreiwegvergleich `C_i`, leaky und F3](S1AN_CI_DREIWEG_BASELINEVERGLEICH.md):
  vergleicht die gekoppelte `C_i`-Engineeringbaseline direkt mit leaky und F3.

- [Richtungsentscheid: Substrat vor Memorybefund](RICHTUNGSENTSCHEID_SUBSTRAT_VOR_MEMORYBEFUND.md):
  verbindliche operative Reihenfolge S0 bis S5. Zuerst werden Funktions- und
  Ressourcenvertrag sowie die minimale langsame lokale Substratrolle gebaut;
  erst danach duerfen Praegung, relative Feldzeit, Rekonstruktion, Cluster
  oder Abstraktion als moegliche Befunde untersucht werden.

- [S0-Funktions- und Ressourcenvertrag der langsamen Substratrolle L](S0_FUNKTIONS_UND_RESSOURCENVERTRAG_LANGSAME_SUBSTRATROLLE_L.md):
  bindet den ko-lokalisierten skalaren L-Traeger, trennt ihn von der
  vorhandenen M-Substratmasse und legt Atomaritaet, Bilanz, Baselines,
  technische Abnahme und Verwerfung fest. Die Gleichung ist nachfolgend in
  S1-A gebunden.

- [S1-A-Naturgleichung der kapazitaetsgewichteten reziproken S-L-Akkommodation](S1A_NATURGLEICHUNG_KAPAZITAETSGEWICHTETE_REZIPROKE_AKKOMMODATION.md):
  bindet die erste konkrete S-L-Gleichung, ihre lokale Austauschbilanz,
  Exaktintegration und den technischen Parameterzeugen. Sie ist ausdruecklich
  identisch mit der linearen B2-Referenzbaseline und kein Memory-Befund.

- [S1-B-Technische Implementierung der reziproken Akkommodation](S1B_TECHNISCHE_IMPLEMENTIERUNG_REZIPROKE_AKKOMMODATION.md):
  dokumentiert L-Zustand, Schema 3, exakte S/H/L-Integration, Nullarm,
  technische Interventionen und bestandene Invarianztests. Der Pfad ist noch
  an keinen S2-Forschungsversuch gebunden.

- [S2-A-Vorregistrierung Wiederholung gegen Dauerkontakt](S2A_VORREGISTRIERUNG_WIEDERHOLUNG_DAUERKONTAKT_REFERENZCHARAKTERISIERUNG.md):
  bindet die kontrollierte audiovisuelle Referenzcharakterisierung, die
  Fast-State-Angleichung, B0- bis B5-Pflichtbaselines und kausale
  Interventionen. Die Ausfuehrung bleibt gesperrt.

- [S2-B-Technischer Runnervertrag der Referenzcharakterisierung](S2B_TECHNISCHER_RUNNERVERTRAG_REFERENZCHARAKTERISIERUNG.md):
  bindet elf Weltplaene, 152 logische Aufgaben, dimensionskorrekte
  Modellarme, Interventionen, Digests, Stoppreihenfolge und ein rein skalares
  In-Memory-Paket. Implementierung und Vollmatrix bleiben gesperrt.

- [S2-C-Technische Kernimplementierung des Referenzrunners](S2C_TECHNISCHE_KERNIMPLEMENTIERUNG_REFERENZRUNNER.md):
  implementiert Weltplaene, B0- bis B5-Referenznumerik,
  Fast-State-Angleichung, Aufgabeninventar und Skalarpaket. Der transiente
  B0/B2-Einzelbatchpfad ist nachfolgend in S2-C2 gebunden; die Vollmatrix wird
  hart abgewiesen.

- [S2-C2-Transienter B0/B2-Einzelbatchpfad](S2C2_TRANSIENTER_B0_B2_EINZELBATCHPFAD.md):
  bindet die asynchrone S1-B-Fortschreibung zwischen Rezeptorabschluessen,
  B0/B2-Einzelbatches, Nullpfadgleichheit, unabhaengige B2-Referenz und
  Batchteilungsinvarianz. Der kanonische AV-Weltadapter ist nachfolgend in
  S2-C3 gebunden.

- [S2-C3-Kanonischer r1.a-AV-Weltadapter](S2C3_KANONISCHER_R1_AV_WELTADAPTER.md):
  reduziert erstmals genau `r1.a` prozedural und zeitversetzbar ueber die
  vorhandenen neutralen Audio-/Videorezeptoren und fuehrt die Welt ohne
  Persistenz durch B0/B2. Probe, N8 und Forschungsentscheidung bleiben
  gesperrt.

- [S2-C4-r1.a-Fast-State-Angleichung und Probe P](S2C4_R1_FASTSTATE_ANGLEICHUNG_UND_PROBE_P.md):
  bindet nach r1.a die externe S/H-Angleichung, erhaelt L unveraendert und
  fuehrt dieselbe kanonische Probe P durch B0 und B2. N8, Vollmatrix und
  Forschungsentscheidung bleiben gesperrt.

- [S2-C5-N8-Neutralbaseline und Probe P](S2C5_N8_NEUTRALBASELINE_UND_PROBE_P.md):
  bindet die einphasige N8-Bildung getrennt an B0/B2, denselben externen
  S/H-Abgleich und exakt dieselbe Probe P wie r1.a. Ein Vergleich, eine
  Probe-Verlaufsmetrik und die Vollmatrix bleiben gesperrt.

- [S2-C6-Passiver Probe-Verlaufsobserver](S2C6_PASSIVER_PROBE_VERLAUFSOBSERVER.md):
  bindet r1.a und N8 an dieselben 31 echten Probe-Abschlusszeitpunkte und
  liest nur fluechtige S/H-Kopien. Distanz, Entscheidung, Persistenz und
  Vollmatrix bleiben gesperrt.

- [S2-C7-Skalare r1.a-/N8-Einpaardistanzen](S2C7_SKALARE_R1_N8_EINPAAR_DISTANZEN.md):
  reduziert den identischen Probe-Support auf D_S und D_H sowie fuer B2 D_L.
  B0 bleibt exakt null; D_pair, Entscheidung und Vollmatrix bleiben
  gesperrt.

- [S2-C8-c1.a-Identitaetskontrolle D_pair(1)](S2C8_C1_IDENTITAETSKONTROLLE_D_PAIR_1.md):
  fuehrt die getrennte, aber wert- und zeitidentische C1-Welt durch B0/B2 und
  bindet `D_pair(1)=0` exakt. n=2, Entscheidung und Vollmatrix bleiben
  gesperrt.

- [S2-C9-R2/C2 erster Zeitstrukturkontrast](S2C9_R2_C2_ERSTER_ZEITSTRUKTURKONTRAST.md):
  bindet gleiche 0.8-s-Kontaktzeit bei getrennter gegen kontinuierliche
  Gliederung. B0 bleibt exakt null; B2 bleibt lineare Referenz ohne
  Forschungsentscheidung.

- [S2-C10-R4/C4 zweiter Zeitstrukturkontrast](S2C10_R4_C4_ZWEITER_ZEITSTRUKTURKONTRAST.md):
  bindet gleiche 1.6-s-Kontaktzeit bei vier getrennten gegen einen
  kontinuierlichen Kontakt. B0 bleibt exakt null; B2 bleibt lineare Referenz
  ohne Forschungsentscheidung.

- [S2-C11-R8/C8 dritter Zeitstrukturkontrast](S2C11_R8_C8_DRITTER_ZEITSTRUKTURKONTRAST.md):
  bindet gleiche 3.2-s-Kontaktzeit bei acht getrennten gegen einen
  kontinuierlichen Kontakt. B0 bleibt exakt null; B2 bleibt lineare Referenz
  ohne Trend- oder Forschungsentscheidung.

- [S2-C12 unveraenderliches skalares A-Paarprofil](S2C12_UNVERAENDERLICHES_SKALARES_A_PAARPROFIL.md):
  fuehrt die typisierten `D_pair(1/2/4/8)`-Ergebnisse in fester Reihenfolge
  und mit gemeinsamer Probe-Provenienz zusammen. Keine Trendlogik,
  Forschungsentscheidung oder Persistenz.

- [S2-C13 R8-B/C8-B kontrolliertes zweites Weltpaar](S2C13_R8B_C8B_KONTROLLIERTES_ZWEITES_WELTPAAR.md):
  bindet Kontakt B als getrennten n=8-Zeitstrukturkontrast durch B0/B2 und
  Probe P. Kein A/B-Vergleich und keine Weltspezifitaets- oder
  Semantikbehauptung.

- [S2-C14 unveraenderlicher n=8-A/B-Skalarcontainer](S2C14_UNVERAENDERLICHER_N8_AB_SKALARCONTAINER.md):
  bindet die getrennten A8- und B8-Paarergebnisse mit gemeinsamer
  Probe-Provenienz und getrennten Quell-Digests. Keine Differenzmetrik oder
  Weltspezifitaetsentscheidung.

- [S2-C15 skalare D_world_pair(8)-Observermetrik](S2C15_SKALARE_D_WORLD_PAIR_8_OBSERVERMETRIK.md):
  bindet den absoluten Abstand der A8- und B8-Paarskalare ohne Schwelle,
  Entscheidung, Runtime-Rueckwirkung oder Weltspezifitaetsbehauptung.

- [S2-C16 kanonische n=8-A/B-End-to-End-Komposition](S2C16_KANONISCHE_N8_AB_END_TO_END_KOMPOSITION.md):
  bindet die vorhandenen A8/B8-Welt-, Probe-, Paar-, Container- und
  Distanzbausteine in einer reproduzierbaren In-Memory-Referenzkette.

- [S2-Zwischenentscheid nach C16](S2_ZWISCHENENTSCHEID_NACH_C16.md):
  stoppt weitere Referenzcontainer und verschiebt Vollmatrix sowie restliche
  Pflichtbaselines bis ein konkreter neuer Substratkandidat vorliegt.

- [S1-C Zulassungsvertrag fuer einen minimalen nichtlinearen lokalen Substratkandidaten](S1C_ZULASSUNGSVERTRAG_MINIMALER_NICHTLINEARER_LOKALER_SUBSTRATKANDIDAT.md):
  bindet Zustandsrahmen, Nichtlinearitaetsgrenze, Pflichtreduktionen und
  Falsifikation, ohne eine unbegruendete Gleichung zu implementieren.

- [S1-D Audit einer feldspannungsabhaengigen reziproken Mobilitaet](S1D_AUDIT_FELDSPANNUNGSABHAENGIGE_REZIPROKE_MOBILITAET.md):
  prueft genau eine MCM-spezifische Nichtlinearitaet und verwirft sie als
  zustandsabhaengige Relaxationsbaseline ohne neue Organisationsbahn.

- [S1-E Audit der lokalen Skalardimension und verteilten Nichtseparierbarkeit](S1E_AUDIT_LOKALE_SKALARDIMENSION_UND_VERTEILTE_NICHTSEPARIERBARKEIT.md):
  verwirft eine unbegruendete zweite lokale Variable und bestimmt verteilte
  kausale Nichtseparierbarkeit als engste offene Feldanforderung.

- [S1-F Zulassungsvertrag fuer verteilte kausale Nichtseparierbarkeit](S1F_ZULASSUNGSVERTRAG_VERTEILTE_KAUSALE_NICHTSEPARIERBARKEIT.md):
  aktualisiert E0 bis E4, Interventionen und Pflichtbaselines fuer S/H/L und
  verhindert die Wiederaufnahme bereits geschlossener Traegerfamilien.

- [S1-G Richtungsentscheid Feldwahrnehmung aktiv, Substratimplementierung pausiert](S1G_RICHTUNGSENTSCHEID_FELDWAHRNEHMUNG_AKTIV_SUBSTRATIMPLEMENTIERUNG_PAUSIERT.md):
  trennt die aktive technische MCM-Feldwahrnehmung von der bis zu einer neuen
  Naturannahme pausierten Substratimplementierung.

- [W1-A Technischer Bestandsaudit der durchgaengigen Feldwahrnehmung](W1A_TECHNISCHER_BESTANDSAUDIT_DURCHGAENGIGE_FELDWAHRNEHMUNG.md):
  bestaetigt den allgemeinen Audio-/Videopfad bis zum gemeinsamen S/H-Feld
  und bestimmt die fehlende generische Browserausgabe-zu-Rezeptorsequenz-
  Bruecke als genau eine aktive Integrationsluecke.

- [W1-B Schnittstellenvertrag der generischen Browser-Rezeptorbruecke](W1B_SCHNITTSTELLENVERTRAG_GENERISCHE_BROWSER_REZEPTORBRUECKE.md):
  bindet geordnete PNG-/PCM-Eingaenge, gemeinsame indexbasierte Zeit,
  atomare Finalisierung, den allgemeinen Sequenzhandoff und die harte
  Abgrenzung von Z4-A vor der W1-C-Implementierung.

- [W1-C Implementierung der generischen Browser-Rezeptorbruecke](W1C_IMPLEMENTIERUNG_GENERISCHE_BROWSER_REZEPTORBRUECKE.md):
  implementiert die unmittelbare kamerafreie PNG-/PCM-Reduktion, den
  oeffentlichen allgemeinen Sequenzhandoff und den synthetisch geprueften Weg
  bis in das gemeinsame S/H-Feld ohne Z4-Reaktivierung.

- [W1-D Bestandsaudit und Vertrag der kamerafreien Browser-Payloadquelle](W1D_BESTANDSAUDIT_UND_VERTRAG_KAMERAFREIE_BROWSER_PAYLOADQUELLE.md):
  trennt den physischen allgemeinen Altpfad und die geparkte Z4-Kette von
  einer frischen parametrierten lokalen Canvas-/Offline-Audio-Quelle fuer die
  fertige W1-C-Bruecke.

- [W1-E Implementierung der kamerafreien Browser-Payloadquelle](W1E_IMPLEMENTIERUNG_KAMERAFREIE_BROWSER_PAYLOADQUELLE.md):
  implementiert allgemeine lokale Assets, Quellenvertraege, direkten
  Capture-Handoff und die Fake-Seiten-End-to-End-Abnahme bis in das gemeinsame
  S/H-Feld ohne Browserstart oder Z4-Reaktivierung.

- [W1-F Vertrag des minimalen realen Browser-Payload-Smokes](W1F_VERTRAG_MINIMALER_REALER_BROWSER_PAYLOAD_SMOKE.md):
  bindet eine kurze allgemeine Welt, die frische Runtimebindung, lokale
  Isolation, exakte Payload- und Rezeptorinventare, Pflichtabbrueche und den
  vollstaendigen spaeteren Browserlebenszyklus vor jeder realen Ausfuehrung.

- [W1-G Implementierung von Runtimebindung und Browser-Smoke-Lifecycle](W1G_IMPLEMENTIERUNG_RUNTIMEBINDUNG_UND_BROWSER_SMOKE_LIFECYCLE.md):
  implementiert den allgemeinen statischen Runtimebinder, injizierbaren
  Smoke, reines Konsolenwerkzeug und den vollstaendigen Fake-Lifecycle bis in
  das S/H-Feld, noch ohne realen Browserstart.

- [W1-H Einmaliger realer Browser-Payload-Smoke](W1H_EINMALIGER_REALER_BROWSER_PAYLOAD_SMOKE.md):
  dokumentiert die genau einmal bestandene reale technische PNG-/PCM-
  Durchgaengigkeit bis in das S/H-Feld, Rohpayloadfreiheit und den
  vollstaendigen Prozessschluss ohne Forschungslaufnummer oder Wirkungsclaim.

- [W1-I Vertrag einer zeitverschobenen AV-Gegenbaseline](W1I_VERTRAG_ZEITVERSCHOBENE_AV_GEGENBASELINE.md):
  bindet eine marginal angeglichene 300-ms-Verschiebung des Tons gegen eine
  unveraenderte Bildbewegung, Pflichtinvarianten und neutrale skalare
  Feldvergleiche, noch ohne Implementierung oder Ausfuehrung.

- [W1-J Implementierung des AV-Zeitverschiebungs-Paars](W1J_IMPLEMENTIERUNG_AV_ZEITVERSCHIEBUNGS_PAAR.md):
  implementiert A0/C0-Vertraege, skalare Energie- und Feldvergleiche sowie
  zwei getrennte Fake-Browserlebenszyklen, noch ohne reale Factory,
  Konsolenwerkzeug oder Forschungslauf.

- [W1-K Einmaliges reales AV-Zeitverschiebungs-Paar](W1K_EINMALIGES_REALES_AV_ZEITVERSCHIEBUNGS_PAAR.md):
  dokumentiert das genau einmal gestartete und wegen einer damals nicht
  einzeln protokollierten Eingangsinvariante verworfene Realpaar, den
  vollstaendigen Nachzustand und die gesperrte Wiederholung.

- [W1-L Statische und synthetische Invariantendiagnose](W1L_STATISCHE_UND_SYNTHETISCHE_INVARIANTENDIAGNOSE.md):
  grenzt den historischen Sammelfehler auf visuelle Sequenzgleichheit oder
  Audioenergie ein, quantifiziert Grenzsampleempfindlichkeit und implementiert
  einen rohpayloadfreien skalaren Fehlerbeleg.

- [W1-M Einmalige reale AV-Quellenpaar-Diagnose](W1M_EINMALIGE_REALE_AV_QUELLENPAAR_DIAGNOSE.md):
  lokalisiert ohne Feldhandoff die minimale reale Web-Audio-Energieabweichung
  als Ursache des W1-K-Abbruchs und bestaetigt exakt gleiche visuelle
  Rezeptorfolgen.

- [W1-N Kanonisches AV-Tonsegment unter Fakes](W1N_KANONISCHES_AV_TONSEGMENT_UNTER_FAKES.md):
  bindet getrennte kontrollierte Assets, setzt exakt dieselbe lokale
  Float32-Sampleform nur an verschiedene Zeitpositionen und behaelt die
  strenge Energiegrenze ohne realen Browserstart bei.

- [W1-O Einmalige reale kanonische Quellenpaar-Diagnose](W1O_EINMALIGE_REALE_KANONISCHE_QUELLENPAAR_DIAGNOSE.md):
  bestaetigt in genau einem realen Quellenpaar exakt gleiche visuelle
  Sequenzen und Audioenergien bei beabsichtigt verschiedenen auditiven
  Zeitfolgen, ohne Feldhandoff oder Rohpayloadhaltung.

- [W1-P Kanonischer AV-Feldpaarweg unter Fakes](W1P_KANONISCHER_AV_FELDPAARWEG_UNTER_FAKES.md):
  bindet die real bestaetigte kanonische Quelle getrennt an den vorhandenen
  skalaren Feldvergleich, bildet die lokale Sampleform im Fake nach und
  bewahrt den historischen Paarweg als Regression.

- [W1-Q Einmaliges reales kanonisches AV-Feldpaar](W1Q_EINMALIGES_REALES_KANONISCHES_AV_FELDPAAR.md):
  dokumentiert genau ein reales energieangeglichenes Zeitverschiebungspaar,
  seine skalare Feldendzustandsdifferenz, geschlossene Lifecycles und die
  enge technische Aussagegrenze.

- [W1-R Synthetische Feldbelastungs- und Erholungscharakterisierung](W1R_SYNTHETISCHE_FELDBELASTUNGS_UND_ERHOLUNGSCHARAKTERISIERUNG.md):
  misst 144 getrennte Belastungs-/Nullkontaktarme im gemeinsamen AV-Feld,
  bindet feste Gain-, Clipping- und Leaky-Gegenbaselines und laesst adaptive
  Regulation auf E0 geschlossen.

- [W1-S Raeumliche AV-Feldbelastungscharakterisierung](W1S_RAEUMLICHE_AV_FELDBELASTUNGSCHARAKTERISIERUNG.md):
  trennt lokale, auditive modalitaetsweite und vollstaendig verteilte
  Kontaktfolgen, misst lokale und modalitaetsfremde Feldausbreitung und macht
  die noch ungleiche gesamte Kontaktmasse als naechste Gegenbaseline sichtbar.

- [W1-T Massenangeglichene raeumliche Feldgegenbaseline](W1T_MASSENANGEGLICHENE_RAEUMLICHE_FELDGEGENBASELINE.md):
  gleicht fuenf Kontaktgeometrien auf Gesamtmasse 1.0 an, trennt erhaltene
  Feld-L1-Masse von geometrieabhaengigen Linf-Spitzen und korrigiert die
  W1-S-Grenzannaeherung auf ihre Kontaktmassenursache.

- [W1-U Lokaler Kontrast unter AV-Hintergrundbelastung](W1U_LOKALER_KONTRAST_UNTER_AV_HINTERGRUNDBELASTUNG.md):
  vergleicht 72 frische Feldpaare, zeigt Kontrasterhaltung im unveraenderten
  Feld und vollstaendigen Kontrastverlust in der statischen
  Clipping-Gegenbaseline, ohne adaptive Regulation freizugeben.

- [W1-V Ereignisdichte und technische Ressourcenlast](W1V_EREIGNISDICHTE_UND_TECHNISCHE_RESSOURCENLAST.md):
  trennt in Null- und Aktivarmen eine 100-fache technische Arbeitszunahme von
  der Feldamplitude, dokumentiert deskriptive Laufzeiten und findet im
  gebundenen Bereich weder Endpunktverfaelschung noch Ressourcenabbruch.

- [W1-W Abschluss der Regulationsvorpruefung auf E0](W1W_ABSCHLUSS_REGULATIONSVORPRUEFUNG_E0.md):
  fuehrt W1-R bis W1-V gegen Feldgrenze, Kontrasterhaltung, Erholung und
  Ressourcenlast zusammen, haelt beide Regulationsrollen geschlossen und
  bindet enge Wiedereroeffnungskriterien.

- [S1-H Ursachenentscheid fuer eine neue Substratnatur](S1H_URSACHENENTSCHEID_NEUE_SUBSTRATNATUR.md):
  findet im heutigen Feldstand keine neue unabhaengige lokale Naturursache,
  stoppt weitere blinde Gleichungssuche und trennt die pausierte
  Neuphysikfrage von einer moeglichen technischen Feldsubstratentwicklung.

- [S1-I Entwicklungsrichtung transparente Feldsubstrat-Engineeringlinie](S1I_ENTWICKLUNGSRICHTUNG_TRANSPARENTE_FELDSUBSTRAT_ENGINEERINGLINIE.md):
  oeffnet die technische Engineeringlinie, waehlt F3 nur als transparente
  Feldverlaufs-Referenz und bindet B2, P0 sowie Rueckwirkungsablation fuer den
  kleinsten synthetischen S1-J-Kompatibilitaetsprototyp.

- [S1-J Technische F3-AV-Kompatibilitaetsscheibe](S1J_TECHNISCHE_F3_AV_KOMPATIBILITAETSSCHEIBE.md):
  bindet F3, lineare gekoppelte Baseline, `eta=0` und P0 an die aktuelle
  26-Neuronen-AV-Geometrie und prueft Massenbilanz, Ereigniskausalitaet,
  exakten Nullpfad und Snapshot/Restore ohne funktionalen Claim.

- [S1-K Vorregistrierung minimale F3-Feldverlaufsfunktion](S1K_VORREGISTRIERUNG_MINIMALE_F3_FELDVERLAUFSFUNKTION.md):
  bindet zwei wertemultimengleiche ortsverschobene AV-Verlaeufe, exakte
  S/H-Angleichung, F3, lineare Baseline, `eta=0`, P0, M-Neutralisierung,
  Nachweisboden und Engineeringentscheidungen vor jeder Implementierung.

- [S1-L Implementierung In-Memory-F3-Feldverlaufspruefadapter](S1L_IMPLEMENTIERUNG_IN_MEMORY_F3_FELDVERLAUFSPRUEFADAPTER.md):
  implementiert Quellen, Armpfade, Nullkontrollen, Verfeinerungen,
  Wiederholung und externe Wiederbindung ohne Forschungsrunner, Report,
  Laufnummer oder Hauptentscheidung.

- [S1-M Passive Auswertung minimale F3-Feldverlaufsfunktion](S1M_PASSIVE_AUSWERTUNG_MINIMALE_F3_FELDVERLAUFSFUNKTION.md):
  berechnet Effektvektoren, Konvergenzboden und linearen Baselinefehler,
  bestaetigt alle Kontrollen und klassifiziert die technische Wirkung als
  transparenten, linear erklaerten Feldverlauf ohne Memoryclaim.

- [S1-N Vorregistrierung Expositions- und Erhaltungskurve](S1N_VORREGISTRIERUNG_EXPOSITIONS_UND_ERHALTUNGSKURVE.md):
  trennt Expositionsdosis, wiederholte gegen kontinuierliche Supports,
  Nullkontaktdauer und lineare Mechanikerlaerung mit zellbezogenen
  Nachweisboeden vor jeder Implementierung.

- [S1-O Implementierung In-Memory-Expositionsmatrixadapter](S1O_IMPLEMENTIERUNG_IN_MEMORY_EXPOSITIONSMATRIXADAPTER.md):
  implementiert das 32-Zellen-Inventar, exakt angeglichene Quellen,
  zellweise F3-/Baselinepfade und Sentinelnullen ohne automatische
  Vollmatrix oder Klassifikation.

- [S1-P Passive Vollmatrixauswertung Exposition und Erhaltung](S1P_PASSIVE_VOLLMATRIXAUSWERTUNG_EXPOSITION_UND_ERHALTUNG.md):
  wertet alle 32 Zellen aus, bestaetigt monotone Dosisgradation,
  nichtmonotone Nullkontaktantwort und Segmentierungssensitivitaet und ordnet
  alle nachweisbaren Zellen weiterhin der linearen Mechanikbaseline zu.

- [S1-Q Vorregistrierung Phasentrennung Feldverlauf](S1Q_VORREGISTRIERUNG_PHASENTRENNUNG_FELDVERLAUF.md):
  bindet Dosis 1/8, beide Quellenformen und acht feste Nullkontaktgrenzen,
  trennt Vorproben-M-Lage von spaeterer Probeantwort und verbietet eine
  nachtraegliche Peak- oder Phasengrenzenwahl.

- [S1-R Implementierung In-Memory-Phasentrennungsmatrix](S1R_IMPLEMENTIERUNG_IN_MEMORY_PHASENTRENNUNGSMATRIX.md):
  implementiert den zellweisen 32-Zellen-Adapter, getrennte Vorproben-M- und
  Probeeffektvektoren sowie technische Quellen-, Angleichungs-, Sentinel-,
  Kompatibilitaets- und Wiederholungskontrollen ohne Vollklassifikation.

- [S1-S Passive Vollmatrixauswertung Phasentrennung](S1S_PASSIVE_VOLLMATRIXAUSWERTUNG_PHASENTRENNUNG.md):
  klassifiziert 16 getrennte M-/Probe-Fenster, weist technische M-Bildung
  jenseits der festen Grenze aus und ordnet alle nachweisbaren Verlaeufe
  weiterhin der linearen Mechanikbaseline zu.

- [S1-T Statische F3-Beitragszerlegung und Observervertrag](S1T_STATISCHE_F3_BEITRAGSZERLEGUNG_UND_OBSERVERVERTRAG.md):
  zerlegt die implementierte M-Rate in massenausgleichenden und
  aktivierungsgetriebenen Beitrag, bindet eine exakte SSPRK-Stufenbilanz und
  trennt `kappa=0`-, `eta=0`-, lineare und Nullkontrollen vor Implementierung.

- [S1-U Implementierung passiver F3-Komponentenobserver](S1U_IMPLEMENTIERUNG_PASSIVER_F3_KOMPONENTENOBSERVER.md):
  implementiert einen zustandslosen SSPRK-Stufenhook und einen
  Einzelzellledger mit exaktem Komponentenabschluss, bitgleicher
  Observertransparenz sowie P0-, Uniformnull- und 2/4-Kontrollen.

- [S1-V Implementierung Vierkurven-Komponentenmatrixadapter](S1V_IMPLEMENTIERUNG_VIERKURVEN_KOMPONENTENMATRIXADAPTER.md):
  trennt fruehe kumulative von spaeten kausal geschachtelten Ledgerzellen,
  bindet F3, linear, `kappa=0` und `eta=0` zellweise und weist unzulaessige
  Fruehintervalle ohne Gesamtklassifikation ab.

- [S1-W Passive Vollmatrixauswertung F3-Komponentenledger](S1W_PASSIVE_VOLLMATRIXAUSWERTUNG_F3_KOMPONENTENLEDGER.md):
  weist `kappa` als notwendige feste Ursache der spaeten Anstiege und eine
  quantitative Wirkung der reziproken Rueckkopplung aus; ein knapper
  direkter Komponentenrest ueberschreitet die lineare 5-Prozent-Grenze und
  bleibt vor weiterer Deutung replizierungspflichtig.

- [S1-X Gezielte Komponentenrest-Replikation](S1X_GEZIELTE_KOMPONENTENREST_REPLIKATION.md):
  lokalisiert drei Aktivierungsantriebstreffer der wiederholten Dosis 8,
  repliziert sie geordnet bei Verfeinerung 4/8 und ordnet sie der bekannten
  nichtlinearen F3-Massengewichtung ohne Funktions- oder Memoryclaim zu.

- [S1-Y Architekturentscheid F3-Abschluss und Substratluecke](S1Y_ARCHITEKTURENTSCHEID_F3_ABSCHLUSS_UND_SUBSTRATLUECKE.md):
  schliesst die F3-Komponentenverfeinerung, ordnet F3 den technischen Rollen
  R1 bis R3 zu und bindet die offene R4-Luecke als lokal mitentwickelte
  Umformbarkeit ohne neue Gleichung oder Zustandsvorentscheidung.

- [S1-Z Bestandssichtung lokal mitentwickelter Umformbarkeit](S1Z_BESTANDSSICHTUNG_LOKAL_MITENTWICKELTE_UMFORMBARKEIT.md):
  prueft alle vorhandenen relevanten Kandidatenfamilien gegen das S1-Y-Tor,
  findet keinen vollstaendig zulaessigen Kandidaten und verhindert die
  Wiedereroeffnung geschlossener Mechaniken unter neuer Bezeichnung.

- [S1-AA Operativer Entwicklungsanschluss nach Substratstopp](S1AA_OPERATIVER_ENTWICKLUNGSANSCHLUSS_NACH_SUBSTRATSTOPP.md):
  trennt aktive Feldtechnik und pausierte Substratforschung, bindet ein hartes
  Wiedereroeffnungstor und bestimmt die Bereinigungskarte der oeffentlichen
  Paketoberflaeche als naechste Engineeringaufgabe W2-A.

- [W2-A Bestandsaudit der oeffentlichen Paketoberflaeche](W2A_BESTANDSAUDIT_OEFFENTLICHE_PAKETOBERFLAECHE.md):
  klassifiziert alle 1.267 Root-Reexporte, bestimmt den aktuellen
  kontrollierten Bestandskorridor und lokalisiert die geraeteneutrale
  Audioquellenrolle im inaktiven Live-Adapter als kleinste Trennungsaufgabe.

- [W2-B Implementierung der geraeteneutralen Audioquellengrenze](W2B_IMPLEMENTIERUNG_GERAETENEUTRALE_AUDIOQUELLENGRENZE.md):
  trennt Fehlervertrag, Quellenprotokoll und synthetische Audioquelle
  kompatibel vom Live-Adapter, erhaelt alle bisherigen Importidentitaeten und
  besteht mit `79 passed` sowie 18 Subtests.

- [W2-C Additive kuratierte current_api](W2C_ADDITIVE_KURATIERTE_CURRENT_API.md):
  stellt 114 neutrale kontrollierte Kern- und 16 getrennte F3-Referenzexporte
  bereit und schliesst Live-Geraete, Z4, Runner, Effektoren und pausierte
  Kandidaten per Manifesttest aus.

- [W2-D Transitiver Importgraphaudit der current_api](W2D_TRANSITIVER_IMPORTGRAPHAUDIT_CURRENT_API.md):
  verfolgt 35 lokale Module ueber 97 Kanten, findet keinen historischen oder
  pausierten Pfad und lokalisiert vier kompatibel trennbare gemischte
  Modulgrenzen.

- [W2-E Implementierung des geraeteneutralen Rezeptorzeitmodells](W2E_IMPLEMENTIERUNG_GERAETENEUTRALES_REZEPTORZEITMODELL.md):
  trennt Fehlervertrag, Timed-Frame und Sequenz kompatibel vom Capture- und
  Auditmodul, erhaelt bisherige Klassenidentitaeten und besteht mit
  `80 passed` sowie 301 Subtests.

- [W2-F Implementierung der kontrollierten Rezeptoraufnahmegrenze](W2F_IMPLEMENTIERUNG_KONTROLLIERTE_REZEPTORAUFNAHMEGRENZE.md):
  trennt die kontrollierte Sequenzaufnahme kompatibel vom Alignment-Audit,
  erhaelt die Funktionsidentitaet und entfernt das Auditmodul aus dem
  transitiven neutralen Kern.

- [W2-G Implementierung der operativen Handoffgrenze](W2G_IMPLEMENTIERUNG_OPERATIVE_HANDOFFGRENZE.md):
  trennt operative Handoff-Datenrollen und Gruppenuebergabe kompatibel von
  passiver Vergleichs- und Segmentierungsauswertung und entfernt das
  Auditmodul aus dem neutralen Kerngraphen.

- [W2-H Implementierung der neutralen AV-Dockgeometrie](W2H_IMPLEMENTIERUNG_NEUTRALE_AV_DOCKGEOMETRIE.md):
  trennt orthogonale Sample-Offsets und AV-Dockaufbau kompatibel vom
  Capturelauf und entfernt dessen private Captureabhaengigkeiten aus dem
  neutralen Kerngraphen.

- [W2-I Implementierung der neutralen Architekturvertraege](W2I_IMPLEMENTIERUNG_NEUTRALE_ARCHITEKTURVERTRAEGE.md):
  trennt Evidenz- und Laufzeitfreigabe-Enums kompatibel vom passiven
  Architekturplan und schliesst damit die vier in W2-D gefundenen gemischten
  Modulgrenzen.

- [W2-J Statischer Abschlussaudit des current_api-Importgraphen](W2J_STATISCHER_ABSCHLUSSAUDIT_CURRENT_API_IMPORTGRAPH.md):
  bestaetigt 36 neutrale beziehungsweise explizite Referenzmodule ueber 95
  Kanten ohne historische, private oder Live-/physische Pfade.

- [W3-A current_api End-to-End-Consumertest](W3A_CURRENT_API_END_TO_END_CONSUMERTEST.md):
  prueft die kontrollierte synthetische AV-Feld-Snapshot-Restore-Kette mit
  `current_api` als einzigem Projektimport und besteht im aktuellen Verbund
  mit `118 passed` sowie 350 Subtests.

- [W3-B current_api Restore-Fortsetzungspruefung](W3B_CURRENT_API_RESTORE_FORTSETZUNGSPRUEFUNG.md):
  prueft identische reduzierte AV-Fortsetzung auf ununterbrochenem und
  restauriertem Feld und bestaetigt denselben technischen Enddigest.

- [W3-C current_api JSON-Restore-Fortsetzung](W3C_CURRENT_API_JSON_RESTORE_FORTSETZUNG.md):
  bindet dieselbe Fortsetzung an die kanonische JSON-Snapshotgrenze und
  bestaetigt identische Snapshot- und Endfelddigests.

- [W3-D current_api Browserpayload-Consumertest](W3D_CURRENT_API_BROWSERPAYLOAD_CONSUMERTEST.md):
  fuehrt kontrollierte PNG- und PCM-Payloads ohne Browserstart oder
  Rohpayloadhaltung ueber die kamerafreie Bruecke in das neutrale Feld.

- [W3-E Browserpayload-Reproduktion und visuelle Gegenbaseline](W3E_BROWSERPAYLOAD_REPRODUKTION_VISUELLE_GEGENBASELINE.md):
  bestaetigt exakte Wiederholung und die isolierte Weitergabe einer einzelnen
  visuellen Payloadaenderung bei identischer auditiver Sequenz.

- [W3-F Browserpayload-Audio-Gegenbaseline](W3F_BROWSERPAYLOAD_AUDITIVE_GEGENBASELINE.md):
  spiegelt die Kontrolle mit einer einzelnen PCM-Amplitudenaenderung bei
  identischer visueller Sequenz.

- [W3-G Browserpayload visuelle Reihenfolge-Gegenbaseline](W3G_BROWSERPAYLOAD_VISUELLE_REIHENFOLGE_GEGENBASELINE.md):
  prueft bei identischem visuellen Werteinventar die technische Erhaltung der
  Frame-Zeitordnung bis in das neutrale gemeinsame Feld.

- [W3-H Browserpayload auditive Reihenfolge-Gegenbaseline](W3H_BROWSERPAYLOAD_AUDITIVE_REIHENFOLGE_GEGENBASELINE.md):
  spiegelt die endpunktkontrollierte Zeitordnungspruefung bei identischem
  PCM-Amplitudeninventar und unveraenderter visueller Sequenz.

- [W3-I Komponentenlokalisierung der Reihenfolgedifferenz](W3I_REIHENFOLGEDIFFERENZ_KOMPONENTENLOKALISIERUNG.md):
  lokalisiert beide Endfelddifferenzen in der schnellen Aktivierung; Nachhall
  ist nicht konfiguriert, Substrat und Entwicklung sind abwesend.

- [W3-J Kontrollierte Nachhall-Reihenfolgelokalisierung](W3J_KONTROLLIERTE_NACHHALL_REIHENFOLGELOKALISIERUNG.md):
  schaltet die bestehende neutrale schnelle Nachhallspur zu und lokalisiert
  darin beide kontrollierten Reihenfolgedifferenzen.

- [W3-K Nachhall-Kausalrichtung gegen die Nullbaseline](W3K_NACHHALL_KAUSALRICHTUNG_NULLABLATION.md):
  zeigt in vier Armen bitgenau gleiche Aktivierung mit und ohne Nachhall und
  ordnet die vorhandene schnelle Spur als einseitig ein.

- [W3-L Nachhallintervention vor identischer Fortsetzung](W3L_NACHHALL_INTERVENTION_IDENTISCHE_FORTSETZUNG.md):
  bestaetigt interventionsbasiert, dass ein isolierter Nachhallunterschied die
  spaetere Aktivierungsfortsetzung nicht veraendert.

- [W3-M Abschluss des Browser-Reihenfolge-/Nachhallkorridors](W3M_ABSCHLUSS_BROWSER_REIHENFOLGE_NACHHALLKORRIDOR.md):
  schliesst die schnelle Reihenfolge-/Nachhalllinie als technische Baseline
  und verhindert weitere Varianten ohne neue unabhaengige Frage.

- [W4-A Bestandsaudit kontrollierter Eingangsregulation](W4A_BESTANDSAUDIT_KONTROLLIERTE_EINGANGSREGULATION_FELDLAST.md):
  laesst adaptive Regulation geschlossen und bindet genau eine passive
  Browserpayload-Last-/Kontrastfrage als technischen Anschluss.

- [W4-B Browserpayload Last-/Kontrast-Nullpruefung](W4B_BROWSERPAYLOAD_LAST_KONTRAST_NULLPRUEFUNG.md):
  zeigt im gebundenen hohen Lastbereich weiterhin messbare kleine visuelle und
  auditive Unterschiede und liefert keinen Regulationsausloeser.

- [W4-C Abschluss der Regulations- und Lastlinie](W4C_ABSCHLUSS_REGULATIONS_UND_LASTLINIE.md):
  schliesst adaptive Regulation mangels Ausloeser und richtet den naechsten
  Schritt auf einen extern begruendeten Substratprinzip-Suchvertrag.

- [W5-A Primaerquellen-Suchvertrag fuer ein unabhaengiges Substratprinzip](W5A_PRIMAERQUELLEN_SUCHVERTRAG_UNABHAENGIGES_SUBSTRATPRINZIP.md):
  bindet Quellenstandard, Naturrollen, Ausschlussfamilien und Urteile vor der
  ersten externen Mechanismuskartierung.

- [W5-B Erste Primaerquellenkartierung von Substratprinzipien](W5B_ERSTE_PRIMAERQUELLENKARTIERUNG_SUBSTRATPRINZIPIEN.md):
  ordnet vier Originalarbeiten sofort gegen die Projektbaselines ein; drei
  sind baselinegleich, eine bleibt rollenunterbestimmt und keine erhaelt eine
  Kandidaten- oder Implementierungsfreigabe.

- [W5-C Suchlueckenentscheid zur geschichtsabhaengigen Umformbarkeit](W5C_SUCHLUECKENENTSCHEID_GESCHICHTSABHAENGIGE_UMFORMBARKEIT.md):
  isoliert die einzige noch unbelegte Rollenkombination und bindet eine zweite
  Suche auf hoechstens zwei neue Mechanismusfamilien, ohne Kandidaten-,
  Gleichungs- oder Implementierungsfreigabe.

- [W5-D Zweite Primaerquellenkartierung zur lokalen Umformbarkeit](W5D_ZWEITE_PRIMAERQUELLENKARTIERUNG_UMFORMBARKEIT.md):
  prueft gerichtetes Altern und mechanochemischen Polymerumbau; drei Rollen
  sind baselinegleich, eine bleibt lokal unterbestimmt und kein Kandidat wird
  zugelassen.

- [W5-E Richtungsentscheid fuer eine homogene Zweizeiten-MCM-Feldkomponente](W5E_RICHTUNGSENTSCHEID_HOMOGENE_ZWEIZEITEN_MCM_FELDKOMPONENTE.md):
  oeffnet einen konstruierten, homogenen und ergebnisoffenen
  Entwicklungsweg; Baselinegleichheit begrenzt Claims, verhindert aber nicht
  mehr einen transparenten technischen Referenzprototyp.

- [W6-A Minimaler Funktionsvertrag der langsamen MCM-Feldkomponente L](W6A_MINIMALER_FUNKTIONSVERTRAG_LANGSAME_MCM_FELDKOMPONENTE_L.md):
  bindet lokale Ursache, Gegenwirkung, Begrenzung, Nullpfad und Snapshotrolle
  an das bereits vorhandene, aber in der aktuellen API inaktive L-Geruest.

- [W6-B Statischer Kompatibilitaetsaudit des S1-B-Referenzpfads](W6B_STATISCHER_KOMPATIBILITAETSAUDIT_S1B_REFERENZPFAD.md):
  laesst die vorhandene reziproke Zweizeiten-Gleichung als technische
  Referenz zu und grenzt den noch fehlenden opt-in AV-Adapter sowie alle
  unzulaessigen Memory- und Feldzeitclaims ab.

- [W6-C Opt-in Adapter fuer den asynchronen S1-B-Referenzpfad](W6C_OPT_IN_ADAPTER_ASYNCHRONER_S1B_REFERENZPFAD.md):
  schliesst reduzierte Audio-/Video-Rezeptorsequenzen additiv an S1-B an und
  nimmt Nullarm, Schema 3, Zeitteilung, Restore und API-Trennung technisch ab.

- [W6-D Vorregistrierung der kausalen Zweistufenpruefung fuer L-Rueckwirkung](W6D_VORREGISTRIERUNG_KAUSALE_ZWEISTUFENPRUEFUNG_L_RUECKWIRKUNG.md):
  bindet Formation, L-Neutralisierung, vollstaendigen L-Tausch, gemeinsamen
  Probeverlauf, Nullarm, Metriken und Stopplinien vor jeder Ausfuehrung.

- [W6-E Implementierung des kausalen Zweistufen-Pruefadapters](W6E_IMPLEMENTIERUNG_KAUSALER_ZWEISTUFEN_PRUEFADAPTER.md):
  implementiert Vierarmablauf, passiven S/H/L-Observer, immutable
  Ergebnisrollen und den statisch digestgebundenen H_A/H_B/P-Weltvertrag.

- [W6-F Fake-Capture und Organismuszeit-Handoff](W6F_FAKE_CAPTURE_UND_ORGANISMUSZEIT_HANDOFF.md):
  reduziert drei deterministische Fake-Seiten durch echte Rezeptoren, bindet
  Formation und Probe an fortlaufende Organismuszeit und uebergibt P
  unveraendert an den Vierarmadapter.

- [W6-G Statischer einmaliger Browser-Ausfuehrungsvertrag](W6G_STATISCHER_EINMALIGER_BROWSER_AUSFUEHRUNGSVERTRAG.md):
  bindet Runtime, Assets, Isolation, Lifecycle und skalare Reportgrenze;
  sperrt die Ausfuehrung wegen des fehlenden Python-Playwright-Pakets.

- [W6-H Isolierter Python-Playwright-Runtimekorridor](W6H_ISOLIERTER_PYTHON_PLAYWRIGHT_RUNTIMEKORRIDOR.md):
  stellt die projektlokale Python-3.12-Umgebung her und hebt die rein
  technische Paketsperre durch eine READY-Vorabnahme auf, ohne Browserstart.

- [W6-I Einmaliger kausaler Browserlauf](W6I_EINMALIGER_KAUSALER_BROWSERLAUF.md):
  dokumentiert den genau einmal ausgefuehrten H_A/H_B/P-Lauf, den atomaren
  Skalarreport, bestandene Lifecyclekontrollen und die enge technische
  L-nach-S-Kausalentscheidung ohne Memoryclaim.

- [W7-A Vorregistrierung geschichtliche Funktion gegen lineare Spurbaselines](W7A_VORREGISTRIERUNG_GESCHICHTLICHE_FUNKTION_GEGEN_LINEARE_SPURBASELINES.md):
  reduziert den naechsten Vergleich auf R8/C8 unter B0, B1 und S1-B/B2 und
  bindet die vollstaendige lineare Erklaerung als begrenzende Entscheidung.

- [W7-B Implementierung des linearen R8/C8-Spurvergleichs](W7B_IMPLEMENTIERUNG_LINEARER_R8_C8_SPURVERGLEICH.md):
  implementiert B1 und die unabhaengige B2-Kontrolle im Arbeitsspeicher und
  begrenzt S1-B durch `LINEAR_RECIPROCAL_TRACE_SUFFICIENT` auf die lineare
  Referenzfunktion.

- [W7-C Funktions- und Ressourcenvertrag jenseits der linearen Spur](W7C_FUNKTIONS_UND_RESSOURCENVERTRAG_JENSEITS_LINEARER_SPUR.md):
  bindet den minimalen nachzuweisenden Abstand zu S1-B/B2, einschliesslich
  bilanzierter Verdichtung, funktionaler Loesung und Kapazitaetswiederverwendung,
  ohne eine Substratnatur oder Gleichung auszuwaehlen.

- [W7-D Statischer Vergleich dreier Substratfamilien](W7D_STATISCHER_VERGLEICH_DREIER_SUBSTRATFAMILIEN.md):
  ordnet alle drei W7-C-Familien vorhandenen engen Baselines zu und behaelt
  das konservierte Transportmedium nur als transparenten Engineering-Pfad,
  nicht als neue MCM-spezifische Substratnatur.

- [W7-E Engineeringentscheid fuer zielseitige freie Kapazitaet](W7E_ENGINEERINGENTSCHEID_ZIELSEITIGE_FREIE_KAPAZITAET.md):
  bindet genau eine abgeleitete Zielverfuegbarkeit als transparente
  Erweiterung der K2/F3-Baseline, einschliesslich direkter Gegenprognosen und
  ohne neue Zustandsdimension oder Implementierungsfreigabe.

- [W7-F Mathematischer Minimalvertrag fuer kapazitaetsbegrenzten Kantenaustausch](W7F_MATHEMATISCHER_MINIMALVERTRAG_KAPAZITAETSBEGRENZTER_KANTENAUSTAUSCH.md):
  bindet die gerichteten Raten, beweist Masse und lokale Kapazitaetsgrenzen,
  isoliert den einzigen neuen bilinearen Term und laesst Runtime sowie
  Forschungsausfuehrung unveraendert.

- [W7-G Implementierung der reinen kapazitaetsbegrenzten Kopplung](W7G_IMPLEMENTIERUNG_REINE_KAPAZITAETSBEGRENZTE_KOPPLUNG.md):
  implementiert die opt-in Ableitungsfunktion samt Kantenledger und
  Vertragstests, ohne Runtime, Zustandsschema, `current_api` oder
  Weltpfade zu veraendern.

- [W7-H Diskreter Integrationsvertrag fuer kapazitaetsbegrenzten Transport](W7H_DISKRETER_INTEGRATIONSVERTRAG_KAPAZITAETSBEGRENZTER_TRANSPORT.md):
  leitet eine gemeinsame Forward-Euler-Grenze fuer Masse und freie
  Kapazitaet her und bindet deren Vererbung durch SSPRK(3,3), Diagnosen,
  P0 und Ereignisausrichtung vor jeder Runtimeintegration.

- [W7-I Isolierte SSPRK-Vektorintegration](W7I_ISOLIERTE_SSPRK_VEKTORINTEGRATION.md):
  implementiert und prueft den gekoppelten S/M-Teil mit W7-G als einziger
  neuer Ableitungsquelle, weiterhin ausserhalb von `SharedMCMField`,
  `current_api` und Testwelten.

- [W7-J Adaptervertrag fuer kapazitaetsbegrenzte SharedMCMField-Runtime](W7J_ADAPTERVERTRAG_KAPAZITAETSBEGRENZTE_SHAREDMCMFIELD_RUNTIME.md):
  bindet die additive Stufen- und Commitvalidierung, den P0-Korridor und eine
  getrennte Restore-Kapazitaetsbindung vor der opt-in Runtimeimplementierung.

- [W7-K Implementierung des kapazitaetsbegrenzten SharedMCMField-Adapters](W7K_IMPLEMENTIERUNG_KAPAZITAETSBEGRENZTER_SHAREDMCMFIELD_ADAPTER.md):
  integriert W7-G opt-in in die gemeinsame Runtime, prueft Kapazitaet an
  allen Stufen- und Commitgrenzen und bindet Restore extern ohne neues
  Snapshot-Schema.

- [W7-L Vorregistrierung von Kapazitaetsfunktion und Gegenbaselines](W7L_VORREGISTRIERUNG_KAPAZITAETSFUNKTION_UND_GEGENBASELINES.md):
  bindet Quellen, Kapazitaet, regionale Ressourcenbilanz, direkte
  M-Interventionen, Quellentausch, numerischen Boden und Pflichtbaselines vor
  jeder funktionalen Auswertung.

- [W7-M In-Memory-Adapter der Kapazitaetsfunktionsmatrix](W7M_IMPLEMENTIERUNG_IN_MEMORY_KAPAZITAETSFUNKTIONSMATRIX_ADAPTER.md):
  implementiert den deterministischen Quellen-/Regionsaufbau, das kanonische
  Matrixinventar, regionale Kapazitaetsmessung und gebundene
  Observerinterventionen ohne Modellauswertung.

- [W7-N Implementierung reiner Kapazitaetsfunktions-Baselinekerne](W7N_IMPLEMENTIERUNG_REINER_KAPAZITAETSFUNKTIONS_BASELINEKERNE.md):
  implementiert LEAK, SAT und NORM als observerseitige lokale Kerne sowie
  LIN, F3, CONST-V und die konservative MOB-Gegenableitung ohne
  Hauptmatrixausfuehrung.

- [W7-O Messvertrag fuer Feldkausalitaet und Observerbaselines](W7O_MESSVERTRAG_FELDKAUSALITAET_UND_OBSERVERBASELINES.md):
  trennt S/H-/Substratmessungen und externe Observererklaerungen, bindet den
  gemeinsamen P0-S-Treiber und erlaubt zwischen beiden Flaechen nur
  dimensionslose Lebenszyklusprofile.

- [W7-P Implementierung des In-Memory-Messkompositors](W7P_IMPLEMENTIERUNG_IN_MEMORY_MESSKOMPOSITOR.md):
  implementiert atomare linksgehaltene P0-S-Treibersegmente, getrennte
  Messdatentypen, reine Observerkomposition und dimensionslose Profile ohne
  Feldpfad- oder Hauptmatrixausfuehrung.

- [W7-Q Vertrag des P0-S-Abschlusszustandsproduzenten](W7Q_VERTRAG_P0_S_ABSCHLUSSZUSTANDSPRODUZENT.md):
  bindet die verlustfreie Ereignisuebergabe, atomare P0-S-Beobachtung,
  unveraenderte Neuronenordnung und getrennte S/H-Endzustandsfortsetzung vor
  jeder Produzentenimplementierung.

- [W7-R Implementierung des P0-S-Abschlusszustandsproduzenten](W7R_IMPLEMENTIERUNG_P0_S_ABSCHLUSSZUSTANDSPRODUZENT.md):
  implementiert substratfreien P0-Zustand, digestgebundene
  Einzelquellsegmentproduktion, atomare S-Ereigniszustande, exakte
  S/H-Fortsetzung und direkten W7-P-Uebergang.

- [W7-S Vertrag der segmentuebergreifenden Observerfortsetzung](W7S_VERTRAG_SEGMENTUEBERGREIFENDE_OBSERVERFORTSETZUNG.md):
  bindet einmaligen Nullstart, getrennte LEAK-/SAT-/NORM-Zustandsketten,
  passive Checkpoints, kontrollierte Pfadkopien und lueckenlose
  Treiberdigestfortsetzung.

- [W7-T Implementierung der segmentuebergreifenden Observerfortsetzung](W7T_IMPLEMENTIERUNG_SEGMENTUEBERGREIFENDE_OBSERVERFORTSETZUNG.md):
  implementiert getrennte latente Zustandsketten, fortgesetzte
  Observermessungen, passive Checkpoints, Pfadkopien und lueckenlose
  W7-R-/W7-P-Digestbindung.

- [W7-U Audit der symmetrischen Pfadquellen-Suffizienz](W7U_AUDIT_SYMMETRISCHE_PFADQUELLEN_SUFFIZIENZ.md):
  weist vier vollstaendig registrierte und drei unvollstaendige Pfade nach
  und begrenzt die fehlende symmetrische Quellenfamilie auf B-Praefix und
  einzelne A-Fortsetzungsschritte.

- [W7-V Vertrag der additiven symmetrischen Quellenfamilie](W7V_VERTRAG_ADDITIVE_SYMMETRISCHE_QUELLENFAMILIE.md):
  bindet Identitaeten, Zeitrollen, technische Supportgleichheit,
  Inventardigest, vollstaendige Siebenpfadbelegung und explizite
  W7-R-Autorisierung vor jeder Implementierung.

- [W7-W Implementierung der additiven symmetrischen Quellenfamilie](W7W_IMPLEMENTIERUNG_ADDITIVE_SYMMETRISCHE_QUELLENFAMILIE.md):
  reduziert die fehlenden Quellenrollen frisch, bindet technischen Support,
  sieben Pfade und Inventardigests und oeffnet W7-R nur ueber eine explizite
  pfad- und intervallgenaue Autorisierung.

- [W7-X Vertrag fuer Siebenpfad-Quellplan und Checkpointkopien](W7X_VERTRAG_SIEBENPFAD_QUELLPLAN_UND_CHECKPOINTKOPIEN.md):
  bindet Hauptsegmentreihenfolge, Uniformstart, passive Checkpoints,
  getrennte Probeaeste und kanonische Plandigests vor jeder Ausfuehrung.

- [W7-Y Implementierung des nicht ausfuehrenden Siebenpfad-Planadapters](W7Y_IMPLEMENTIERUNG_NICHTAUSFUEHRENDER_SIEBENPFAD_PLANADAPTER.md):
  materialisiert und validiert alle Quellen-, Uniformstart-, Checkpoint- und
  Probeastrollen samt kanonischem Gesamtplandigest ohne Zustandsfortsetzung.

- [W7-Z Vertrag fuer P0-only-Siebenpfad-Planverbrauch](W7Z_VERTRAG_P0_ONLY_SIEBENPFAD_PLANVERBRAUCH.md):
  bindet getrennte substratfreie P0-Hauptketten, objektgetrennte
  Checkpointkopien, isolierte Probeaeste und Rueckwirkungsgegenkontrollen.

- [W7-AA Implementierung des P0-only-Siebenpfad-Verbrauchers](W7AA_IMPLEMENTIERUNG_P0_ONLY_SIEBENPFAD_VERBRAUCHER.md):
  verarbeitet sieben getrennte P0-Hauptketten und 35 tief kopierte
  Probeaeste samt Reihenfolge-Gegenkontrolle ausschliesslich im Arbeitsspeicher.

- [W7-AB Vertrag der Observeruebergabe fuer Haupt- und Probeketten](W7AB_VERTRAG_OBSERVERUEBERGABE_HAUPT_UND_PROBEKETTEN.md):
  bindet digestgleiche W7-P-Treiber, 21 getrennte LEAK-/SAT-/NORM-
  Hauptketten und 105 isolierte gleichpfadige Observerprobeaeste.

- [W7-AC Implementierung des Observer-Siebenpfad-Verbrauchers](W7AC_IMPLEMENTIERUNG_OBSERVER_SIEBENPFAD_VERBRAUCHER.md):
  verarbeitet 21 getrennte Observerhauptketten und 105 Probeaeste mit
  additiver W7-P-Autorisierung und technischen Rueckwirkungsgegenkontrollen.

- [W7-AD Vertrag fuer gekoppelten CAP-Siebenpfad-Verbrauch](W7AD_VERTRAG_GEKOEPPELTER_CAP_SIEBENPFAD_VERBRAUCH.md):
  bindet sieben getrennte CAP-Hauptketten, 35 tiefe S/H/M-Probekopien und
  snapshotgenaue Fortsetzungsbindungen bei unveraenderten Gegenbaselines.

- [W7-AE Implementierung des CAP-Siebenpfad-Verbrauchers](W7AE_IMPLEMENTIERUNG_CAP_SIEBENPFAD_VERBRAUCHER.md):
  verarbeitet 32 CAP-Hauptsegmente und 35 isolierte S/H/M-Probeproduktionen
  mit Mass-, Kapazitaets-, Geometrie- und Reihenfolgekontrollen.

- [W7-AF Vertrag fuer passive CAP-Messuebergabe](W7AF_VERTRAG_PASSIVE_CAP_MESSUEBERGABE.md):
  trennt technische Fortsetzungsproben von S/H-angeglichenen
  Kausalmesskopien und bindet passive Trajektorien- und Ressourcenrollen.

- [W7-AG Implementierung der passiven CAP-Messuebergabe](W7AG_IMPLEMENTIERUNG_PASSIVE_CAP_MESSUEBERGABE.md):
  erzeugt 35 angeglichene CAP-Messaeste, 3.185 echte S/H/M-Samples und
  rollenreine Feld- und regionale Ressourcenmessungen ohne Auswertung.

- [W7-AH Vertrag fuer P0-Nullstartmessreferenzen](W7AH_VERTRAG_P0_NULLSTART_MESSREFERENZEN.md):
  bindet 35 substratfreie S/H-Nullstarts, passive S/H-Samples und
  Endzustandsaequivalenz zum unveraenderten W7-R-Produzenten.

- [W7-AI Implementierung der P0-Nullstartmessreferenzen](W7AI_IMPLEMENTIERUNG_P0_NULLSTART_MESSREFERENZEN.md):
  materialisiert 35 getrennte P0-Messseiten mit 3.185 passiven S/H-Samples,
  weist W7-R-Aequivalenz nach und setzt nur technische Vergleichsbereitschaft.

- [W7-AJ Vertrag fuer CAP/P0-Messpaarung und Rohkontraste](W7AJ_VERTRAG_CAP_P0_MESSPAARUNG_UND_ROHKONTRASTE.md):
  bindet 35 exakt sampleausgerichtete CAP/P0-Paare und rohe S/H-Abstaende
  ohne Schwellen-, Pfad- oder Funktionsauswertung.

- [W7-AK Implementierung des CAP/P0-Rohkontrastkompositors](W7AK_IMPLEMENTIERUNG_CAP_P0_ROHKONTRASTKOMPOSITOR.md):
  materialisiert 35 Paare und 3.185 gerichtete S/H-Residualsamples mit
  Identitaets-, Symmetrie-, Reihenfolge- und Aggregatkontrollen.

- [W7-AL Audit des durchgaengigen 2n/4n-Verfeinerungspfads](W7AL_AUDIT_DURCHGAENGIGER_2N_4N_VERFEINERUNGSPFAD.md):
  bestaetigt Runtimeunterstuetzung, lokalisiert die fehlende W7-AE/AG/AK-
  Durchleitung und trennt die analytisch exakte gemeinsame P0-Referenz.

- [W7-AM Vertrag fuer den additiven R1/R2/R4-Aufloesungscontainer](W7AM_VERTRAG_ADDITIVER_R1_R2_R4_AUFLOESUNGSCONTAINER.md):
  bindet R1-Kompatibilitaet, getrennte R2/R4-CAP-Ketten, externe
  Integrationszeugen und die einmalige gemeinsame P0-Referenz.

- [W7-AN Zwischenstand Refinementbruecke und Laufzeitgrenze](W7AN_ZWISCHENSTAND_REFINEMENTBRUECKE_UND_LAUFZEITGRENZE.md):
  weist die private R1/R2/R4-Durchleitung am AB-Praefix nach, haelt den
  Vollcontainer nach kontrolliertem Zeitabbruch aber ausdruecklich offen.

- [W7-AN statische Laufzeit- und Gegenkontrollzerlegung](W7AN_STATISCHE_LAUFZEIT_UND_GEGENKONTROLLZERLEGUNG.md):
  trennt 306 zeugentragende Primaerintegrationen von 948
  Validierungsintegrationen und bindet 36 Batches mit hoechstens 67
  Integrationen, ohne eine Runtime auszufuehren.

- [W7-AN private Materialisierungs- und Audittrennstelle](W7AN_PRIVATE_MATERIALISIERUNGS_UND_AUDITTRENNSTELLE.md):
  implementiert die erste private Phasengrenze in W7-AE und W7-AG und
  bestaetigt die unveraenderte oeffentliche R1-Komposition mit der realen
  kanonischen W7-AG-Suite.

- [W7-AN vollstaendige private Auditbatchgrenzen](W7AN_VOLLSTAENDIGE_PRIVATE_AUDITBATCHGRENZEN.md):
  teilt W7-AE in 67+4 und W7-AG in 35+1 Kontrollintegrationen und bestaetigt
  danach erneut den unveraenderten realen R1-Digest.

- [W7-AN privater stufenweiser Aufloesungsexecutor](W7AN_PRIVATER_STUFENWEISER_AUFLOESUNGSEXECUTOR.md):
  verbindet die sechs Phasen einer Aufloesung einzeln im Arbeitsspeicher,
  finalisiert erst nach allen Audits und ist strukturell sowie real fuer R1
  geprueft.

- [W7-AN reale gestufte R1-Kompatibilitaet](W7AN_REALE_GESTUFTE_R1_KOMPATIBILITAET.md):
  weist alle sechs realen R1-Phasen, 67+35 Zeugen und die bitgleiche
  Reproduktion der kanonischen W7-AE-, W7-AG- und W7-AK-Digests nach.

- [W7-AN privater gestufter R1/R2/R4-Gesamtkoordinator](W7AN_PRIVATER_GESTUFTER_R124_GESAMTKOORDINATOR.md):
  bindet 36 einzelne Primaer- und Gegenlaufphasen, gemeinsame P0-Identitaet
  und den terminalen Stopp bei abweichenden Aufloesungsdigests; der spaetere
  reale Gesamtaufbau bestand vollstaendig.

- [W7-AN reiner globaler Containerfinalizer](W7AN_REINER_GLOBALER_CONTAINERFINALIZER.md):
  bindet die drei Primaerresultate nach 36 verifizierten Phasen ohne weitere
  Integration in die bestehende globale Containerlogik.

- [W7-AN realer vollstaendiger R1/R2/R4-Gesamtcontainer](W7AN_REALER_VOLLSTAENDIGER_R124_GESAMTCONTAINER.md):
  dokumentiert 36 reale Phasen, digestgleiche Primaer-/Gegenlaeufe, 306
  Primaerzeugen und den nicht ausgewerteten globalen Containerdigest.

- [W7-AO statischer Aufloesungsvergleichsvertrag](W7AO_STATISCHER_AUFLOESUNGSVERGLEICHSVERTRAG.md):
  bindet Rohresidualausrichtung, S/H-Linf-Metriken, rollenweise
  Konvergenzregel, numerischen Boden und Gegenbaselines vor jeder
  Wertauswertung.

- [Feldzeit, innerer Kontext und MCM-Memory-Substrat](FORSCHUNGSRICHTUNG_FELDZEIT_INNERER_KONTEXT.md):
  aktuelle manuelle Forschungsrichtung, Begriffsordnung, gekoppelte
  Zielarchitektur, bekannte Sackgassen, Forschungsphasen und Mindestnachweise.
  Die weitere Arbeit wird ausschliesslich manuell im MCM-Hauptchat gesteuert.

- [MINI_DIO-Zeitkontext-Uebertragungsvertrag](MINI_DIO_ZEITKONTEXT_UEBERTRAGUNGSVERTRAG.md):
  historische Herleitung der Zeitkontext-Uebertragung; ihre Evidenzreichweite
  wird durch den aktuellen Reaudit begrenzt.

- [MINI_DIO-Zeitkontext: funktionale Reduktion und Substratwege](MINI_DIO_ZEITKONTEXT_FUNKTIONALE_REDUKTION.md):
  rekonstruiert Eigenform und Rangzyklus, gleicht sie mit der heutigen Runtime
  ab und stellt drei falsifizierbare Substratwege gegenueber.

- [MINI_DIO-Zeitkontext-Reaudit nach Lauf 194](MINI_DIO_ZEITKONTEXT_REAUDIT_NACH_LAUF_194.md):
  begrenzt den historischen Befund auf passive relationale
  Trajektorienwiederkehr und leitet den Z1-Trajektorien-Kovarianzaudit ab.

- [Z1-Vorregistrierung des Feldtrajektorien-Kovarianzaudits](Z1_FELDTRAJEKTORIEN_KOVARIANZAUDIT_VORREGISTRIERUNG.md):
  bindet Quellenarme, Pfadmetrik, numerische Kontrollen, Entscheidungen und
  die lineare F3-Pflichtbaseline vor jeder Implementierung und Ausfuehrung.

- [Z1: technische Quellenarme und Pfadmetrik](Z1_TECHNISCHE_QUELLEN_UND_PFADMETRIK.md):
  dokumentiert die implementierten Quellenabbildungen, festen Digests, den
  passiven Observer, die reine Pfadmetrik und die weiterhin gesperrte
  Ausfuehrung von Lauf 195.

- [Z1: technischer F3/B3-Mehrarmrunner](Z1_TECHNISCHER_F3_B3_MEHRARMRUNNER.md):
  bindet 56 F3/B3-Aufgaben, prueft alle Quellen-Handoffs und dokumentiert die
  technische Trennung des Pakets von Lauf-ID und Forschungsentscheidung.

- [Z1: Entscheidung, Serialisierung und Lauf-195-Sperre](Z1_ENTSCHEIDUNG_SERIALISIERUNG_UND_LAUFSPERRE.md):
  fixiert numerische Huellen, Teilungsstopp, Zeit- und Ordnungsentscheidung,
  B3-Vergleich, JSON-Schema und den einmaligen one-shot Laufweg.

- [Lauf 195: Z1-Feldtrajektorien-Kovarianzaudit](forschung/LAUF_195_Z1_FELDTRAJEKTORIEN_KOVARIANZAUDIT.md):
  dokumentiert die technisch unentscheidbare Teilungsnullkontrolle und
  sperrt alle Zeit-, Ordnungs- und Baseline-Sachinterpretationen.

- [Z1-Korrekturvertrag gemeinsamer Observer-Support fuer Lauf 196](Z1_KORREKTURVERTRAG_GEMEINSAMER_OBSERVER_SUPPORT_LAUF_196.md):
  trennt leere technische Integrationsabschluesse von den echten
  Rezeptorabschluss-Stuetzpunkten der unveraenderten Sachpfadmetrik.

- [Z1: Implementierung des gemeinsamen Observer-Supports](Z1_GEMEINSAMER_OBSERVER_SUPPORT_IMPLEMENTIERUNG.md):
  dokumentiert die getrennte Voll- und Entscheidungstrajektorie, feste
  Supportinventare und die weiterhin unausgefuehrte Lauf-196-Matrix.

- [Z1: Lauf-196-Einstieg und Ausfuehrungssperre](Z1_LAUF196_EINSTIEG_UND_AUSFUEHRUNGSSPERRE.md):
  bindet Supportkontrollen, unveraenderte Auswertung, skalares JSON und den
  einmalig ausgefuehrten separaten one-shot Laufweg.

- [Lauf 196: Z1 mit gemeinsamem Observer-Support](forschung/LAUF_196_Z1_GEMEINSAMER_SUPPORT_FELDTRAJEKTORIEN.md):
  weist technische Teilungsinvarianz, Weltzeitbindung und
  Ordnungssensitivitaet der bestehenden F3/B3-Runtime nach und schliesst Z1.

- [Z2-Zulassigkeitsaudit lokaler ereignisgetragener Entwicklungsordnung](Z2_ZULASSIGKEITSAUDIT_LOKALE_EREIGNISGETRAGENE_ENTWICKLUNGSORDNUNG.md):
  prueft vor jeder neuen Mechanik, ob ein lokaler nichtzaehlender und nicht
  observerseitiger Traeger relativer Entwicklungsordnung ueberhaupt offen ist.

- [Z2-A-Bestandsaudit der S-, H- und M-Zeitdimensionen](Z2A_BESTANDSAUDIT_S_H_M_ZEITDIMENSIONEN_UND_REPARAMETRISIERUNG.md):
  entscheidet `NO_EXISTING_STATE_REPARAMETERIZATION`: Die Bestandszustaende
  enthalten keine von Weltsekunden unabhaengige lokale Entwicklungsordnung.

- [Z2-B-Kollisionsaudit lokaler Feldarbeit und lokalen Flussdurchgangs](Z2B_KOLLISIONSAUDIT_LOKALE_FELDARBEIT_UND_FLUSSDURCHGANG.md):
  entscheidet `NO_ADMISSIBLE_EVENT_ORDER_SOURCE` und schliesst Z2 fuer die
  aktuelle Runtime. Eine neue Entwicklungsrolle muss als offene
  physikalische Forschungsannahme begruendet werden.

- [Z3-Hypothesenvertrag lokaler konstitutiver Deformation](Z3_HYPOTHESENVERTRAG_LOKALE_KONSTITUTIVE_DEFORMATION.md):
  verengt die naechste Forschung auf genau eine hypothetische lokale
  Deformationsrolle Q und bindet Einheiten, Konjugation, Bilanz, Nullpfad,
  Ausschluesse und Pflichtbaselines vor jeder Gleichung.

- [Z3-A-Quellen- und Reduktionsaudit konstitutiver Deformation Q](Z3A_QUELLEN_UND_REDUKTIONSAUDIT_KONSTITUTIVER_DEFORMATION_Q.md):
  entscheidet `Q_ROLE_BASELINE_EQUIVALENT`. Viskoelastische,
  elastoplastische und energetisch rateunabhaengige interne Variablen liefern
  keine neue MCM-Rolle oberhalb der gebundenen Pflichtbaselines; Z3 ist
  geschlossen.

- [Z4-Richtungsentscheid fuer die strenge Feldlinie](Z4_RICHTUNGSENTSCHEID_STRENGE_FELDLINIE.md):
  setzt `STRICT_FIELD_SYSTEM_DEVELOPMENT`, ordnet P0, F3 und B3 und oeffnet
  als naechsten Schritt nur die statische Vorregistrierung einer
  Mehrwelt-Feldencoder-Charakterisierung.

- [Z4-A-Mehrwelt-Feldencoder-Vorregistrierung und Ausfuehrungssperre](Z4A_MEHRWELT_FELDENCODER_VORREGISTRIERUNG_UND_AUSFUEHRUNGSSPERRE.md):
  bindet vier Weltfamilien, Kausalarme, P0/F3/B3, Metrik und Entscheidungen.
  Der Zweig ist am Stand `Z4A2_OFFLINE_AUDIO_SMOKE_BOUND` als technische
  Wahrnehmungs- und Baseline-Infrastruktur geparkt. Die Vollmatrix und Lauf
  197 bleiben gesperrt und besitzen keinen Vorrang vor S0 und S1.

- [Z4-A1-Vertrag fuer reine Audio-Rezeptorsequenz und unabhaengige Kontrolle](Z4A1_REINE_AUDIO_REZEPTORSEQUENZ_UND_KONTROLLVERTRAG.md):
  bindet Referenz und frequenzverschobene Kontrolle, Rezeptorgeometrie und
  Abschluss-Supports. Adapter und Kontrolle sind implementiert, technisch
  reproduziert und final digestgebunden; ein Feldlauf fand nicht statt.

- [Z4-A2-Vertrag fuer die kamerafreie Browserwelt](Z4A2_KAMERAFREIER_BROWSERWELT_REZEPTORVERTRAG.md):
  bindet eine direkte v2-Capture-Welt fuer gerasterte Canvas-Pixel und
  browserinternes Offline-Audio sowie eine unabhaengige Kontrollwelt. Der
  physische v1-Server bleibt ausgeschlossen. v2-Assets und direkter
  PNG-/PCM-Rezeptoradapter sowie die Playwright-Capture-Schicht sind
  synthetisch abgenommen; auch der statische Runtime-Bindungsresolver liegt
  vor. Playwright 1.62.0 und Chromium 151.0.7922.34 sind real statisch
  gebunden; visueller Ein-Tick- und OfflineAudio-Grenzsmoke sind bestanden.
  Aktiver Quellenkontrast und echte Sequenzdigests bleiben offen, werden in
  der aktuellen Substrat-zuerst-Phase aber nicht fortgesetzt.

- [Z4-A3-Vertrag fuer den generischen P0/F3/B3-Trajektorienrunner](Z4A3_GENERISCHER_P0_F3_B3_TRAJEKTORIENRUNNERVERTRAG.md):
  bindet weltneutrale Eingaben, gemeinsamen Handoff, rollenvariable
  Trajektorien, Completion-Support und 42 Aufgaben je Welt. Alle drei
  Implementierungsscheiben einschliesslich des generischen Runners sind
  synthetisch abgenommen; die reale Vollmatrix und der Forschungslauf bleiben
  gesperrt.

- [Z4-A4-Vertrag fuer skalares Ergebnis, Entscheidung und Lauf-197-Sperre](Z4A4_SKALARES_ERGEBNIS_ENTSCHEIDUNG_UND_LAUF197_SPERRE.md):
  bindet reine Entscheidungslogik, konservative Restklasse,
  rohtrajektorienfreies JSON und atomaren one-shot Ablauf. Schema,
  Entscheidungsbaum, Messadapter und one-shot Sperre sind technisch
  abgenommen. Lauf 197 ist nur reserviert und nicht ausgefuehrt.

- [H1-Kausalvertrag und Kollisionsentscheidung](H1_LOKAL_DEFORMIERBARE_FELDAUFNAHME_KAUSALVERTRAG.md):
  ordnet die einfache Feldempfaenglichkeit dem abgeschlossenen C1-Befund zu
  und verschiebt die offene Lebenszyklusfunktion auf H2.

- [H2-Bestandsaudit des begrenzten umverteilbaren Feldmediums](H2_BEGRenztes_UMVERTEILBARES_FELDMEDIUM_BESTANDSAUDIT.md):
  fasst Ressourcen-, Material- und Morphologievorarbeiten zusammen und trennt
  die geschlossene automatische Herleitung von einer offenen deklarierten
  Materialhypothese.

- [H2-B-Vergleich passiver Materialklassen](H2B_VERGLEICH_PASSIVER_MATERIALKLASSEN.md):
  vergleicht Phasenfeld, Viskoelastik und memristive beziehungsweise
  Duhem-Hysterese und schliesst alle drei als direkte H2-Kandidaten.

- [H3-Quellenaudit der relationsabhaengigen Materialantwort](H3_LOKALE_RELATIONSABHAENGIGE_MATERIALANTWORT_QUELLENAUDIT.md):
  prueft lokale Differenz-, Fluss-, Zeitrichtungs- und MINI_DIO-Rangquellen,
  schliesst H3 als eigenstaendige Materialfamilie und leitet zwei gekoppelte
  MCM-Substratrollen innerhalb desselben gemeinsamen Feldes ab.

- [Zwei gekoppelte MCM-Substratrollen](ZWEI_MCM_SUBSTRATROLLEN_VERTRAG.md):
  trennt schnelle Wahrnehmungsdynamik und langsames Entwicklungssubstrat im
  selben Feld und bindet Kopplung, Feldzeit, Loesung und Wiederpraegung an
  kausale Baselines.

- [Vergleich der Kopplungsfamilien S-L](VERGLEICH_MCM_KOPPLUNGSFAMILIEN_S_L.md):
  ordnet gemeinsame Mitentwicklung, Aufnahme, Weiterleitung und Kapazitaet
  gegen die bisherigen Sackgassen und Baselines ein.

- [K1-Hypothese der reziproken lokalen Akkommodation](K1_HYPOTHESE_REZIPROKE_LOKALE_AKKOMMODATION.md):
  formuliert die erste bewusst deklarierte Naturannahme fuer gemeinsame
  schnelle und langsame MCM-Entwicklung, noch ohne Gleichung oder Runtime.

- [K1 konstitutiver Schliessungsaudit](K1_KONSTITUTIVER_SCHLIESSUNGSAUDIT.md):
  ordnet lineare, monotone nichtlineare und konservativ-dissipative Kopplung
  als Rekurrenz-, Fading-Memory-, Viskoelastik- oder Oszillatorbaselines ein.

- [Zulassungsvertrag fuer strukturveraendernde lokale MCM-Physik](ZULASSUNGSVERTRAG_STRUKTURVERAENDERNDE_LOKALE_MCM_PHYSIK.md):
  trennt erlaubte allgemeine Entwicklungsphysik von verbotener Vorgabe
  konkreter Organisation, Bedeutung und Zielstruktur.

- [Vergleich strukturveraendernder K1-Familien](VERGLEICH_STRUKTURVERAENDERNDER_K1_FAMILIEN.md):
  schliesst kontinuierliche Metastabilitaet und zustandsabhaengige Mobilitaet
  als Primaermechaniken und behaelt nur lokale nichtkontraktive
  S-L-Mitentwicklung unter Passivitaet bedingt offen.

- [F3-Minimalvertrag der nichtkontraktiven reziproken S-L-Mitentwicklung](F3_MINIMALVERTRAG_NICHTKONTRAKTIVE_REZIPROKE_SL_MITENTWICKLUNG.md):
  definiert Nichtkontraktivitaet als reine Verlaufseigenschaft, leitet globale
  Passivitaet nur aus lokalen Bilanzen ab und sperrt Gleichung sowie Runtime
  bis zu einem statischen Existenz- und Reduzierbarkeitsaudit.

- [F3-Existenz- und Reduzierbarkeitsaudit](F3_EXISTENZ_UND_REDUZIERBARKEITSAUDIT.md):
  weist die Vereinbarkeit von Passivitaet und zeitweiliger Nichtkontraktion
  nach, schliesst F3 aber als eigenstaendige Mechanik und identifiziert die
  zu breite Rekurrenzbaseline als methodischen Widerspruch.

- [Korrekturvertrag zur digitalen Naturrekurrenz](KORREKTURVERTRAG_DIGITALE_NATURREKURRENZ.md):
  trennt unvermeidbare inhaltsfreie lokale Updatephysik von verbotener
  vorprogrammierter Organismusfunktion und ersetzt die universelle
  Rekurrenzbaseline durch enge falsifizierbare Funktionsklassen.

- [Statischer Freiheitsgradaudit der bestehenden MCM-Runtime](STATISCHER_FREIHEITSGRADAUDIT_BESTEHENDE_MCM_RUNTIME.md):
  inventarisiert Activation und Afterimage, weist die fehlende
  Afterimage-zu-Activation-Rueckwirkung nach und bestimmt einen lokalen
  Skalar nur als kleinste noch ungepruefte Zustandserweiterung.

- [Skalarer L-Suffizienz- und No-Go-Audit](SKALARER_L_SUFFIZIENZ_UND_NO_GO_AUDIT.md):
  schliesst den isolierten Skalar als Registermechanik, behaelt einen Skalar
  pro Feldort aber als ko-lokalisiertes verteiltes Zustandsfeld innerhalb des
  gemeinsamen MCM-Feldes offen.

- [Zulassungsvertrag fuer ein ko-lokalisiertes skalares L-Feld](ZULASSUNGSVERTRAG_KOLOKALISIERTES_SKALARES_L_FELD.md):
  bindet L an dieselben Feldorte, dieselbe Geometrie, atomare S-L-Entwicklung
  und den normalen S-vermittelten Weltpfad, noch ohne eine raeumliche Familie
  oder Gleichung zu waehlen.

- [Vergleich raeumlicher L-Kopplungsfamilien](VERGLEICH_RAEUMLICHER_L_KOPPLUNGSFAMILIEN.md):
  schliesst eigenen L-Eigenfluss und reziproken Kreuzfluss als erste
  Kandidaten und behaelt nur ortsgebundenes L unter dem bestehenden
  raeumlichen S-Feldfluss bedingt offen.

- [R1-Naturfunktionsvertrag fuer ortsgebundene S-L-Mitentwicklung](R1_NATURFUNKTIONSVERTRAG_ORTSGEBUNDENE_SL_MITENTWICKLUNG.md):
  definiert lokale konstitutive Akkommodation als unteilbare beidseitige
  S-L-Kreuzwirkung und ersetzt die universelle Ein-Diffusor-Baseline durch
  enge konkrete Funktionsbaselines.

- [Vergleich lokaler R1-Schliessungsformen](VERGLEICH_R1_LOKALER_SCHLIESSUNGSFORMEN.md):
  schliesst dissipative reziproke und allgemein nichtgradientige Formen als
  Primaerkandidaten und behaelt nur ein additives konstitutives Gegenfeld fuer
  einen engeren statischen Reduzierbarkeitsvertrag bedingt offen.

- [Minimal- und Reduzierbarkeitsvertrag fuer ein additives Gegenfeld](MINIMALVERTRAG_ADDITIVES_KONSTITUTIVES_GEGENFELD.md):
  ordnet auch die letzte R1-Form als klassische interne Gegenvariable,
  dynamische Erholung, glatte Hysterese oder Oszillator ein und schliesst R1
  vor einer Gleichungswahl als primaeren Entwicklungsweg.

- [Funktionaler Anforderungsrang des Memory-Lebenszyklus](FUNKTIONALER_ANFORDERUNGSRANG_MEMORY_LEBENSZYKLUS.md):
  trennt vier notwendige Kausalrollen von der Zustandsdimension, weist nur
  einen zusaetzlichen erreichbaren und rueckwirkenden Zustand als Untergrenze
  aus und oeffnet die operationale Frage verteilter kausaler
  Nichtseparierbarkeit.

- [Evidenzvertrag fuer verteilte kausale Nichtseparierbarkeit](EVIDENZVERTRAG_VERTEILTE_KAUSALE_NICHTSEPARIERBARKEIT.md):
  bindet kontrollierte Audio-, Video- und AV-Geschichten an
  Zustandsangleichung, Tausch, Permutation, Neutralisierung, Rekonfiguration
  und enge lokale sowie raeumliche Pflichtbaselines, noch ohne Traeger oder
  Versuch.

- [Vergleich von Traegerfamilien fuer verteilte Nichtseparierbarkeit](VERGLEICH_TRAEGERFAMILIEN_VERTEILTE_NICHTSEPARIERBARKEIT.md):
  schliesst S-vermittelte Ortszustaende und nichtkonservativen L-Eigenfluss,
  behaelt konservative Umverteilung wegen ihrer eigenstaendigen begrenzten
  Ressourcenrolle fuer einen Minimalvertrag bedingt offen und laesst variable
  Beziehungen verboten.

- [Minimalvertrag fuer eine konservierte begrenzte Feldgroesse M](MINIMALVERTRAG_KONSERVIERTE_BEGRENZTE_FELDGROESSE_M.md):
  definiert M als die eine langsame Feldkomponente mit endlicher
  Neutralverteilung, lokal antisymmetrischer Mengenbilanz, unteilbarer
  S-M-Wechselwirkung und konservativen Forschungsinterventionen, noch ohne
  Transportgleichung oder Runtime.

- [Vergleich konservativer M-Transportfamilien](VERGLEICH_KONSERVATIVER_M_TRANSPORTFAMILIEN.md):
  schliesst passiven Eigenpotentialfluss und S-Drift mit separatem
  Pattern-Leser, behaelt aber eine unteilbare lokal konjugierte
  S-M-Kreuzwirkung fuer einen engen Schliessungsformen-Audit bedingt offen.

- [F3-Schliessungsformen-Audit fuer konservativen S-M-Austausch](F3_SCHLIESSUNGSFORMEN_AUDIT_KONSERVATIVER_SM_AUSTAUSCH.md):
  schliesst konstante lineare Kreuzmoden und M-abhaengige Mobilitaet, behaelt
  aber einen bilinearen Kraft-Fluss-Austausch mit an denselben M-Transport
  gebundener S-Rueckarbeit fuer einen mathematischen Minimalvertrag bedingt
  offen.

- [Mathematischer Minimalvertrag fuer bilinearen konservativen S-M-Austausch](MATHEMATISCHER_MINIMALVERTRAG_BILINEARER_KONSERVATIVER_SM_AUSTAUSCH.md):
  weist den No-Go zwischen aktivem neutralem M-Gleichzustand, weltbedingtem
  Fluss aus diesem Zustand und sofort gebundener S-Rueckarbeit nach, schliesst
  Form 3 unter dem aktuellen Vertrag und oeffnet die explizite
  Nullpfad-Korrekturfrage.

- [Nullpfad-Korrekturvertrag fuer gekoppelte Substratphysik](NULLPFAD_KORREKTURVERTRAG_GEKOPPELTE_SUBSTRATPHYSIK.md):
  waehlt K2 Parameterneutralitaet, fuehrt gleichfoermiges M nur als
  materiellen Referenzzustand und erhaelt die heutige S-H-Runtime durch eine
  pro Arm feste exakte Kopplungsablation.

- [K2-mathematischer F3-Minimalvertrag](K2_MATHEMATISCHER_F3_MINIMALVERTRAG.md):
  bestimmt eine kontinuierliche konservative Kantenform mit nichtnegativen
  M-Raten, flussgebundener additiver S-Rueckarbeit, analytischer Randhuelle
  und exaktem Nullparameterarm, noch ohne Parameter, Schema oder Runtime.

- [Statische K2/F3-Implementierungsspezifikation](K2_F3_STATISCHE_IMPLEMENTIERUNGSSPEZIFIKATION.md):
  bindet M als dritten ortsgleichen Zustand an die bestehende atomare Feld-
  und Snapshot-Grenze, haelt P0 auf dem bisherigen exakten S/H-Pfad und
  definiert die Integrations-, Restore- und Gegenbaseline-Grenzen fuer P1.

- [K2/F3-Implementierungs- und Falsifikationsscheiben](K2_F3_IMPLEMENTIERUNGS_UND_FALSIFIKATIONSSCHEIBEN.md):
  zerlegt den Umbau in Zustand/Snapshot/P0, reine C/R-Physik und erst danach
  aktive S/H/M-Integration; jede Scheibe besitzt eigene Eintritts-, Abnahme-
  und Abbruchkriterien.

- [Statischer K2/F3-Integratorfamilien-Audit](K2_F3_INTEGRATORFAMILIEN_AUDIT.md):
  vergleicht exakte, adaptive, implizite, Patankar-, Splitting- und
  SSP-Verfahren und waehlt bedingt ein ereignisausgerichtetes SSPRK(3,3) mit
  gemeinsamer Forward-Euler-Invariantengrenze.

- [K2/F3 Scheibe A: API- und Schema-2-Vertrag](K2_F3_SCHEIBE_A_API_SCHEMA2_VERTRAG.md):
  dokumentiert die implementierte ortsgleiche M-Substratkomponente,
  unveraendertes Schema 1, explizites Schema 2, Nullarm-Migration, Restore,
  P0-Projektionsgleichheit und die weiterhin aktive F3-Sperre.

- [K2/F3 Scheibe B: C/R-Implementierungsvertrag](K2_F3_SCHEIBE_B_CR_IMPLEMENTIERUNGSVERTRAG.md):
  dokumentiert die implementierte reine F3-Kantenbuchung, konservative
  M-Mengenrate und die ausschliesslich an dasselbe C gebundene additive
  S-Rueckarbeit samt algebraischen Gegenbaselines.

- [K2/F3 Scheibe C: SSPRK-Runtimevertrag](K2_F3_SCHEIBE_C_SSPRK_RUNTIME_VERTRAG.md):
  dokumentiert P0-Exaktbypass, aktive gemeinsame S/H/M-Integration,
  ereignisausgerichtetes SSPRK(3,3), Invariantendiagnose,
  Zeitverfeinerung und aktiven Schema-2-Restore.

- [K2/F3: gebundener Mehrarm-Runner](K2_F3_GEBUNDENER_MEHRARM_RUNNER.md):
  bindet P0, P1 n/2n/4n, eta-null, kappa-null und kappa-invertiert
  konstruktiv an denselben einmal validierten Rezeptor-Handoff und haelt
  Diagnosen ausserhalb des Feldsnapshots.

- [Vorregistrierung des ersten NASA-Kausallaufs](K2_F3_ERSTER_NASA_KAUSALLAUF_VORREGISTRIERUNG.md):
  bindet Quelle, Intervall, Rezeptordigests, Parameter, sieben Arme,
  Messrollen und Stopplinien vor dem ersten F3-AV-Ergebnis.

- [Lauf 188: K2/F3-NASA-Kausallauf](forschung/LAUF_188_K2_F3_NASA_KAUSALLAUF.md):
  dokumentiert konservative M-Umverteilung, kappa- und eta-Kausalkontraste
  sowie abnehmende n/2n/4n-Abweichung unter einer kontrollierten AV-Folge,
  ohne Memory- oder Organisationsclaim.

- [P2-Vorregistrierung des ersten Geschichtstraeger-Versuchs](K2_F3_P2_GESCHICHTSTRAEGER_VORREGISTRIERUNG.md):
  bindet zwei getrennte kontrollierte AV-Geschichten, eine einmal frisch
  reduzierte gemeinsame Probe, S/H-Angleichung, M-Neutralisierung, eta-null,
  M-Tausch und P0 vor dem Ergebnis.

- [Lauf 189: K2/F3-P2-Geschichtstraeger](forschung/LAUF_189_K2_F3_P2_GESCHICHTSTRAEGER.md):
  isoliert M nach exakter S/H-Angleichung als aus Weltgeschichte
  entstandenen, tauschbaren und eta-abhaengig rueckwirkenden kausalen
  Traeger, ohne daraus einen Memory-Claim abzuleiten.

- [E2-Vorregistrierung geometrischer M-Kausalitaet](K2_F3_E2_GEOMETRISCHE_M_KAUSALITAET_VORREGISTRIERUNG.md):
  bindet eine wertemultimengenerhaltende Zeilenspiegelung und zwei
  massenbilanzierte lokale Halbmasken vor dem Geometrieergebnis.

- [Lauf 190: technischer E2-Serialisierungsabbruch](forschung/LAUF_190_K2_F3_E2_TECHNISCHER_SERIALISIERUNGSABBRUCH.md):
  dokumentiert den reinen JSON-Abbruch ohne Ergebnisartefakt und ohne
  fachlichen Befund.

- [E2-Korrekturvertrag fuer Lauf 191](K2_F3_E2_KORREKTURVERTRAG_LAUF_191.md):
  beschraenkt die Korrektur auf native JSON-Boolwerte im passiven Observer.

- [Lauf 191: geometrische M-Kausalitaet](forschung/LAUF_191_K2_F3_E2_GEOMETRISCHE_M_KAUSALITAET.md):
  zeigt unter erhaltener M-Wertemultimenge und massenbilanzierten lokalen
  Interventionen eine von der konkreten Feldzuordnung abhaengige spaetere
  Wirkung und erfuellt damit E2 ohne Memory-Claim.

- [E3-Baseline-Audit und Vorregistrierung](K2_F3_E3_BASELINE_AUDIT_UND_VORREGISTRIERUNG.md):
  bindet lokale Leaky-Spur, lokale lineare Gegenvariable und die analytische
  lineare F3-Feldform mit identischem Zustands-, Geometrie-, Zeit- und
  Beobachtungsbudget sowie einer festen 5-Prozent-Grenze.

- [Lauf 192: E3-Baselinevergleich](forschung/LAUF_192_K2_F3_E3_BASELINEVERGLEICH.md):
  zeigt, dass die lineare gekoppelte Feldbaseline alle vorregistrierten
  F3-Effekttrajektorien mit maximal 4,923 Prozent Residuum erklaert, und
  schliesst diesen Korridor deshalb als primaeren E3-/Memory-Weg.

- [K2-Richtungsentscheid nach Lauf 192](K2_RICHTUNGSENTSCHEID_NACH_LAUF_192.md):
  trennt die weitere funktionale Charakterisierung von F3 als technischer
  Feld-Geschichtsbaseline von der weiterhin offenen, aber nicht
  implementierungsreifen Suche nach neuer MCM-Substratphysik.

- [K2-B-Vorregistrierung Funktionsverlust und Wiederverwendung](K2_B_F3_FUNKTIONSVERLUST_UND_WIEDERVERWENDUNG_VORREGISTRIERUNG.md):
  bindet A-, B-, Unterbrechungs- und Probequellen sowie die Trennung von
  konkurrenzbedingtem und passivem Wirkungsverlust.

- [Lauf 193: technischer Clock-Abbruch](forschung/LAUF_193_K2_B_TECHNISCHER_CLOCK_ABBRUCH.md)
  und [Korrekturvertrag fuer Lauf 194](K2_B_KORREKTURVERTRAG_LAUF_194.md):
  dokumentieren die vor jeder Messung erkannte Clock-Kollision und ihre
  ausschliesslich technische Korrektur.

- [Lauf 194: F3-Funktionsverlust und Wiederverwendung](forschung/LAUF_194_K2_B_F3_FUNKTIONSVERLUST_UND_WIEDERVERWENDUNG.md):
  klassifiziert die alte Wirkungsabnahme als passive Feldrelaxation und
  bestaetigt eine neue B-Wirkung, ohne konkurrierende Reorganisation oder
  Memory-Claim.

- [Bauplan und Anweisung](../BAUPLAN_UND_ANWEISUNG.md): Entwicklungsordnung,
  MINI_DIO-Kenntnisstand und Grenze zwischen technischer Naturbedingung und
  vorgegebener Bedeutung.
- [Vorarbeitsstand bis zum Forschungsstart](VORARBEITSSTAND.md): aktueller
  Bauzustand, Grundsystem-Freigabe und Regel gegen unnötige
  Versuchsdokumentation.
- [Gründungs- und Architekturvertrag](GRUENDUNGSVERTRAG.md): Ziel,
  Forschungsgrenzen und gesperrte Mechaniken.
- [Entwicklungsreihenfolge](ENTWICKLUNGSREIHENFOLGE.md): technische und
  funktionale Abhängigkeiten.
- [Offene Forschungsfragen](FORSCHUNGSFRAGEN.md): Fragen, die erst nach der
  notwendigen Vorarbeit untersucht werden dürfen.

## Aktuelle Ein-Feld-Architektur

- [Gemeinsames MCM-Feld](architektur/024_GEMEINSAMES_MCM_FELD_ARCHITEKTUR.md):
  verbindliche Zustandsgrenze des einen Organismusfeldes.
- [Rezeptorvertrag und Dockgrenze](architektur/025_REZEPTORVERTRAG_UND_DOCKGRENZE.md):
  neutrale, herkunftserhaltende Übergabe in offene Docks.
- [Gemeinsamer Audio-Video-Feldkontakt](architektur/026_GEMEINSAMER_AUDIO_VIDEO_FELDKONTAKT.md):
  technischer Weltkontakt in derselben MCM-Neuronenschicht.
- [Doppelte Selbstregulation](architektur/027_DOPPELTE_SELBSTREGULATION_GRENZE.md):
  spätere MCM-Rückführung und Eingangsregulation; derzeit geschlossen.
- [Hypothetische MCM-Memory-Entwicklungsrichtung](architektur/028_HYPOTHETISCHE_MCM_MEMORY_ENTWICKLUNGSRICHTUNG.md):
  offene Memory-Entwicklungsrichtung, nicht als Datenbank oder vorhandene
  Faehigkeit.
- [Minimaler Rezeptorprozessvertrag](architektur/029_MINIMALER_REZEPTORPROZESSVERTRAG.md):
  modalitätseigene Prozesse unter gemeinsamer Kausalitätsgrenze.
- [Weltkontakt, innerer Kontext und Feldrückwirkung](architektur/030_WELTKONTAKT_INNERER_KONTEXT_UND_FELDRUECKWIRKUNG.md):
  begriffliche Ordnung von Wahrnehmung, Verdichtung, innerem Dialog und Sprache.

Die Architekturverträge definieren technische Zustandsgrenzen. Sie behaupten
keine bereits entwickelte Topologie, Semantik, inneren Dialog oder organische
Memoryfunktion.

## Forschungs- und Evidenzgrenze

- [S1-AB Audit des endlichen lokal umverteilbaren Kopplungsmediums](S1AB_AUDIT_ENDLICHES_LOKAL_UMVERTEILBARES_KOPPLUNGSMEDIUM.md):
  ein technisch plausibler Substratvorschlag scheitert an der statischen
  Nichtreduktion gegen adaptive Mobilitaet und Standardmaterial; keine
  Implementierungsfreigabe.

- [Evidenzgrenze des gemeinsamen MCM-Feldes](EVIDENZGRENZE_GEMEINSAMES_MCM_FELD.md):
  trennt technische Reife, alte Komponentenevidenz und spätere
  Feldevidenz.
- [MINI_DIO-Mechanikabgleich](forschung/001_MINI_DIO_MECHANIKABGLEICH.md):
  wiederverwendbarer Kenntnisstand und nicht zu übertragende aktive Altmechanik.
- [Sättigungsgrenze des schnellen Feldes](forschung/002_SAETTIGUNGSGRENZE_DES_SCHNELLEN_FELDES.md):
  bekannte Grenze vor künstlicher Beziehungsspur.

### Historischer Zwischenstand 021 bis 029

Die Forschungsdokumentation 021 bis 029 ist im Workspace vorhanden. Sie bildet
einen historischen, abgeschlossenen Zwischenstand, erteilt aber keine
automatische Freigabe fuer weitere Forschung, Runtime- oder
Programmerweiterungen.

- [Aktuelle Feldreaktionen bei unveraenderter Runtime](forschung/021_AKTUELLE_FELDREAKTIONEN_UNVERAENDERTE_RUNTIME.md)
- [Gleichzeitige kontrollierte Weltkontakte](forschung/022_GLEICHZEITIGE_KONTROLLIERTE_WELTKONTAKTE_NULLBEFUND.md)
- [Vorregistrierung Geometrie, Amplitude und Additivitaet](forschung/023_VORREGISTRIERUNG_GEOMETRIE_AMPLITUDE_ADDITIVITAET.md)
- [Konzept reversible Feldnachwirkung](forschung/024_KONZEPT_RAHMEN_REVERSIBLE_FELDNACHWIRKUNG.md)
- [Kandidatenrolle und methodischer Stopp](forschung/025_KONZEPT_KANDIDATENROLLE_UND_METHODISCHER_STOPP.md)
- [Konzept Langzeitbeobachtung bestehender Feldwirkung](forschung/026_KONZEPT_LANGZEITBEOBACHTUNG_BESTEHENDER_FELDWIRKUNG.md)
- [Vorregistrierung Langzeitbeobachtung](forschung/027_VORREGISTRIERUNG_LANGZEITBEOBACHTUNG_BESTEHENDER_FELDWIRKUNG.md)
- [Langzeitbeobachtung bestehender Feldwirkung: Nullbefund](forschung/028_LANGZEITBEOBACHTUNG_BESTEHENDER_FELDWIRKUNG_NULLBEFUND.md)
- [Ordnungsdokument zum Konzeptabgleich 021 bis 028](forschung/029_ORDNUNGSDOKUMENT_KONZEPTABGLEICH_021_BIS_028.md)

Forschung 028 bleibt ein Nullbefund. Forschung 029 ordnet offene
Anschlussfragen, geschlossene Zweige, passive Baselines und harte Ausschluesse;
sie ist weder Forschungsfreigabe noch Grundlage fuer Memory-, Bedeutungs-,
Reward- oder Topologieableitungen. Die bestehende Browsergrenze bleibt
unveraendert: Browserwiedergabe wird nicht in Download, lokale Kopie,
Installation, Transcode oder einen dateibasierten Auswertungspfad umgedeutet.

## Historischer Bestand

- [Vorarbeiten bis zum Forschungsstart](archiv/vorarbeiten_bis_forschungsstart/README.md):
  frühere Methodiken, Befunde, technische Audits und die synthetische
  `GF_001`-Aufbauprobe.
- [Historische Architekturstände](architektur/HISTORISCHE_ARCHITEKTURSTAENDE.md):
  frühere Mehrfeld- und Verteilerarchitekturen.

Der historische Bestand bleibt nachvollziehbar, steuert aber nicht die aktuelle
Runtime und zählt nicht als laufende Versuchsserie.
Der aktuelle technische C_i-Robustheitsabgleich ist in
`S1AO_CI_PARAMETER_ZEITSCHRITT_ROBUSTHEIT.md` dokumentiert. Er bestaetigt nur
beschraenkte numerische Verlaeufe der Baseline, keinen Memory- oder
Organismusnachweis.

Der operative Abschluss der C_i-Linie und die Rueckkehr zur AV-
Engineeringlinie stehen in `S1AV_RICHTUNGSENTSCHEID_NACH_CI_BASELINE.md`.

Der statische Auswahlrahmen fuer neue Substratideen steht in
`S1AW_WIEDEROEFFNUNGSTOR_NEUE_SUBSTRATKANDIDATEN.md`.

Der anschliessende Bestandsaudit von S, H, M, L und MINI_DIO steht in
`S1AX_BESTANDSPRUEFUNG_S_H_M_L_MINIDIO.md`.

Die begrenzte aktuelle Primaerquellen-Vorpruefung und der methodische Stopp
weiterer offensichtlicher Materialanalogien stehen in
`S1AY_AKTUELLE_PRIMAERQUELLEN_VORPRUEFUNG.md`.

Die kompatible Ausgliederung der abgeschlossenen C_i-Baseline aus dem aktiven
Engineeringmanifest steht in
`S1AZ_TRENNUNG_AKTIVE_AV_OBERFLAECHE_UND_CI_REFERENZ.md`.

Der manifestgenaue Restaudit und die kompatible Trennung passiver
Snapshot-Vergleiche vom aktiven Kern stehen in
`S1BA_RESTAUDIT_AKTIVES_ENGINEERINGMANIFEST.md`.

Die AST-gesicherte Bindung des synthetischen AV-End-to-End-Consumers an die
aktive Kernmenge steht in
`S1BB_END_TO_END_CONSUMER_AKTIVE_KERNGRENZE.md`.

Die entsprechende Kernbindung der kontrollierten Browser-Testwelt-
Rezeptorbruecke steht in
`S1BC_BROWSER_TESTWELT_REZEPTORBRUECKE_KERNGRENZE.md`.

Der gemeinsame Zeit-, Handoff- und Feldpfad beider aktiven Weltzufuhren steht
in `S1BD_GEMEINSAME_ZEIT_HANDOFF_UND_FELDGRENZE.md`.

Die exakte neutrale Schema-1-Snapshotgrenze ohne implizite C_i-, F3- oder
S1B-Zustaende steht in
`S1BE_NEUTRALE_SNAPSHOTGRENZE_OHNE_REFERENZZUSTAND.md`.

Der synchronisierte aktuelle Wortlaut fuer Snapshot, Nachhall, neutrale
Feldkonfiguration, Referenzpfade und offene Memoryhypothese steht in
`S1BF_WORTLAUTAUDIT_AKTIVE_LEITSEITEN_UND_API.md`.

Die kompakte geraeteneutrale Beschreibung von Eingang, Uhr, Handoff, S/H-
Feld und neutralem Snapshot steht in
`S1BG_GERAETENEUTRALE_ZUSTANDSBESCHREIBUNG_AKTIVER_AV_FELDPFAD.md`.

Die daraus ohne zweiten Wahrheitskatalog erzeugte JSON-kompatible API-
Selbstauskunft steht in
`S1BH_MASCHINENLESBARER_AKTIVER_FELDZUSTANDSVERTRAG.md`.

Der deterministische SHA-256-Fingerabdruck dieser Vertragsausgabe steht in
`S1BI_DETERMINISTISCHER_VERTRAGSDIGEST.md`.

Der technische Abschlussaudit ohne offene Luecke in der erklaerten aktiven
AV-Engineeringstrecke steht in
`S1BJ_ABSCHLUSSAUDIT_AKTIVE_AV_ENGINEERINGSTRECKE.md`.

Die spaetere Benutzerfreigabe fuer eine bewusst konstruierte, aber nicht als
neue Natur behauptete lokale Plastizitaetslinie steht in
`S1BK_TECHNISCH_PRAGMATISCHE_SUBSTRATLINIE.md`.

Der erste statische Engineeringkandidat einer endlichen lokalen
Kopplungsressource steht in
`S1BL_E1_RESSOURCENBEGRENZTE_LOKALE_KOPPLUNGSPLASTIZITAET.md`.

Seine minimale Knoten-/Kantenanatomie und exakte lokale sowie globale
Erhaltungsidentitaet stehen in
`S1BM_E1_MINIMALE_RESSOURCENANATOMIE_UND_ERHALTUNGSIDENTITAET.md`.

S1-BN bindet die normierte lokale Feldspannung als einzige E1-Bindungsursache,
einen kontinuierlichen inhaltsfreien Rueckfluss und die symmetrische
Rueckwirkung der Bindung auf die Leitfaehigkeit derselben bestehenden Kante.
Noch keine Runtime und kein Memoryclaim. Siehe
`S1BN_E1_LOKALE_TRANSFERURSACHE_UND_KONJUGIERTE_RUECKWIRKUNG.md`.

S1-BO bindet die dimensionskonsistente kontinuierliche E1-Minimalgleichung,
eine symmetrische lokal zugeteilte Freigabe-Bindung-Freigabe-Integration und
die begrenzte Kantenleitfaehigkeit. Bilanz und Nichtnegativitaet werden ohne
nachtraegliches Clipping erhalten; noch keine Runtime. Siehe
`S1BO_E1_MINIMALGLEICHUNG_UND_BEREICHSERHALTENDE_INTEGRATION.md`.

S1-BP spezifiziert das isolierte opt-in E1-Modul mit unveraenderlichem
Vertrag, kanonischen Kantenbindungen, geometriegebundenem Zustand,
abgeleiteten freien Ressourcen und reiner zeitexpliziter Entwicklung.
`__init__`, `current_api`, S/H und Snapshots bleiben unberuehrt. Siehe
`S1BP_E1_ISOLIERTER_ZUSTANDSCONTAINER_UND_IMPLEMENTIERUNGSGRENZE.md`.

S1-BQ implementiert das isolierte E1-Modul und nimmt E0 mit 12 fokussierten
sowie 25 angrenzenden Regressionstests ab. Geometriebindung,
Nichtnegativitaet, Bilanz, Reihenfolgeinvarianz, analytische Freigabe,
Zeitverfeinerung und API-Isolation bestehen; noch keine Feldrueckwirkung.
Siehe `S1BQ_E1_ISOLIERTE_IMPLEMENTIERUNG_UND_E0_ABNAHME.md`.

S1-BR bindet den reinen ablatierbaren Adapter von E1-Bindungen zu
symmetrischen nichtnegativen internen Kantenraten und den daraus gebildeten
gewichteten Graphgenerator. Rezeptorgrenzen, H, Snapshots und APIs bleiben
unveraendert; noch keine Implementierung. Siehe
`S1BR_E1_ABLATIERBARER_KANTENRATENADAPTER.md`.

S1-BS implementiert den isolierten E1-Kantenratenadapter und den gewichteten
internen Generator. Neun fokussierte und insgesamt 46 Regressionstests
bestehen; noch keine Einbindung in einen S/H-Schritt. Siehe
`S1BS_E1_KANTENRATENADAPTER_IMPLEMENTIERUNG_UND_ABNAHME.md`.

S1-BT bindet den synchronen atomaren E1/S/H-Schritt als symmetrische
Halb-E1-/Ganz-S/H-/Halb-E1-Komposition. P0, A0 und A1 bleiben getrennt; der
transiente AV-Pfad wird noch nicht erweitert. Siehe
`S1BT_E1_ATOMARER_GEKOPELTER_S_H_SCHRITTVERTRAG.md`.

S1-BU implementiert und testet die synchrone atomare E1/S/H-Runtime. A0 ist
feldseitig bitgenau P0, A1 zeigt eine ablatierbare technische Feldwirkung;
acht fokussierte und insgesamt 62 Regressionstests bestehen. E2 und Memory
sind noch nicht nachgewiesen. Siehe
`S1BU_E1_SYNCHRONE_GEKOPELTE_RUNTIME_UND_ABNAHME.md`.

S1-BV bindet die eingefrorene identische E2-Probe nach zwei kontrollierten
gespiegelten E1-Geschichten. Historische S/H-Endfelder werden verworfen;
aktive Wirkung, Ablation, P0 und exakt passende feste Gainfelder bleiben
getrennt. Noch keine Implementierung und kein E2-Befund. Siehe
`S1BV_E1_EINGEFRORENER_IDENTISCHER_E2_PROBEVERTRAG.md`.

S1-BW implementiert den eingefrorenen E1-Probeoperator und die feste
Gain-Gegenbaseline. Acht fokussierte und insgesamt 70 Regressionstests
bestehen; Ablation ist bitgenau P0, aktive Probe und passender fester Gain
sind bitgenau gleich. Der L/R-Lauf steht noch aus. Siehe
`S1BW_E1_EINGEFRORENER_PROBEOPERATOR_UND_ABNAHME.md`.

S1-BX implementiert den gespiegelten Achtkontakt-Geschichtsproduzenten.
Gleiche Energie erzeugt zwei verschiedene, gleich starke und bis
`5.55e-17` gespiegelte E1-Kantenverteilungen; acht fokussierte und insgesamt
78 Tests bestehen. Auf dieser Vorstufe stand die E2-Probe noch aus; sie wurde
spaeter in S1-BZ ausgefuehrt. Siehe
`S1BX_E1_GESPIEGELTER_ACHTKONTAKT_GESCHICHTSPRODUZENT.md`.

S1-BY bindet die vollstaendige E2-Laufkomposition aus frischem neutral
vorbereitetem Probefeld, sieben Hauptarmen, n=2/n=4-Numerikkontrollen und
einem interpretationsfreien Rohmetrikcontainer. Die Toleranz `1e-12` ist vor
Ausfuehrung festgelegt; der spaetere Lauf steht getrennt in S1-BZ. Siehe
`S1BY_E1_E2_LAUFKOMPOSITION_UND_ERGEBNISCONTAINER.md`.

S1-BZ implementiert die vorregistrierte Komposition und fuehrt sie genau
einmal aus. Der gueltige begrenzte Befund lautet
`E2_TECHNICAL_CAUSAL_EFFECT`: `active_s_linf = 0.006046298243694848` und
`active_h_linf = 0.0038293104101744246`, waehrend Ablation und Fixed Gain
exakt null bleiben. Dies ist kein Memorybefund. Siehe
`S1BZ_E1_E2_EINMALLAUF_UND_TECHNISCHE_AUSWERTUNG.md`.

S1-CA registriert den noch unausgefuehrten E3-Korridor: analytisch
kontrollierte Nullkontaktfreigabe, rueckwirkungs-ablatierte konkurrierende
Wiederbindung und anschliessende identische eingefrorene Probe. Siehe
`S1CA_E1_E3_NULLKONTAKTFREIGABE_UND_RESSOURCENWIEDERVERWENDUNG.md`.

S1-CB implementiert und prueft die vier getrennten Zustandsarme vor der
Probe. Analytische Freigabe, Ressourcenbilanz, erneute Nettobindung,
Armtrennung und private API-Grenze bestehen; der relevante Verbund erreicht
`88 tests, OK`. Die interne Bereitschaft
`E3_STATE_ARMS_READY_FOR_PROBE` ist noch keine E3-Entscheidung. Siehe
`S1CB_E1_E3_ZUSTANDSARME_IMPLEMENTIERUNG_UND_ABNAHME.md`.

S1-CC registriert die noch unausgefuehrte identische E3-Probe. Zehn
Hauptarme trennen P0, HOLD, RELEASE, COMPETE, Ablation und feste Gains;
n=2/n=4 bindet den Numerikrest. Die Entscheidungen `INVALID_RUN`,
`E3_RELEASE_AND_RESOURCE_REUSE`, `E3_RELEASE_ONLY` und
`NO_E3_EFFECT_IN_FIRST_CORRIDOR` sind vorab festgelegt. Siehe
`S1CC_E1_E3_IDENTISCHE_PROBE_UND_ENTSCHEIDUNGSVERTRAG.md`.

S1-CD implementiert die Komposition und fuehrt sie genau einmal gueltig aus.
RELEASE unterscheidet sich von HOLD und COMPETE zusaetzlich von RELEASE
deutlich oberhalb des Numerikrests. Ablation und Fixed Gain bleiben exakt
null. Die begrenzte Entscheidung lautet
`E3_RELEASE_AND_RESOURCE_REUSE`, nicht Memory. Siehe
`S1CD_E1_E3_EINMALLAUF_FREIGABE_UND_RESSOURCENWIEDERVERWENDUNG.md`.

S1-CE auditiert die Pflichtbaselines und registriert E4 ohne Ausfuehrung.
Verglichen wird ein vorzeichenbehaftetes 72-Komponenten-S/H-Profil ueber
H8, drei Freigabe- und acht Konkurrenzcheckpoints. Fixed Gain ist direkt,
F3 geometrisch anschliessbar; S2-B2 und CONST-V benoetigen neue private
Handoffs. Alte Ergebnisdateien werden nicht gekreuzt. Siehe
`S1CE_E1_E4_BASELINE_BESTANDSAUDIT_UND_VERGLEICHSVERTRAG.md`.

S1-CF implementiert den geordneten 72-Komponenten-Profilcontainer sowie die
privaten S2-B2- und CONST-V-Handoffs. S2 verwendet unveraendert B2 und seine
B1-Ablation; CONST-V delegiert mit den kanonischen Parametern an W7-N. Zehn
fokussierte und 98 gemeinsame Tests bestehen. Noch kein E4-Gesamtlauf. Siehe
`S1CF_E1_E4_PROFILCONTAINER_UND_BASELINE_HANDOFFS.md`.

S1-CG registriert den vollstaendigen E4-Ausfuehrungs- und Ergebnisvertrag:
feste Modellreihenfolge, gemeinsame H/G/C-Welt, ausdrueckliche
Rueckwirkungsinterventionen, identische eingefrorene Probe, Numerik- und
Kontinuitaetskontrollen, private Ergebnisrollen sowie Abbruch- und
Entscheidungsreihenfolge. Es wurde kein E4-Lauf ausgefuehrt. Siehe
`S1CG_E1_E4_VOLLSTAENDIGER_AUSFUEHRUNGS_UND_ERGEBNISVERTRAG.md`.

S1-CH implementiert die privaten F3-Interventions- und Frozen-Probe-Wrapper,
die drei claimfreien Ergebnisrollen und einen streng geordneten,
runnerinjizierten Executorkern. 13 synthetische und 48 relevante
Verbundtests bestehen. Es wurde kein E4-Modelllauf ausgefuehrt. Siehe
`S1CH_E1_E4_EXECUTORKERN_F3_INTERVENTIONEN_UND_SYNTHETISCHE_ABNAHME.md`.

S1-CI bindet die konkreten B3- bis B6-Runner an H/G/C-Welt und identische
Frozen-Probe. Alle vier liefern isoliert vollstaendige, messbare und
checkpointvariable Profile; 9 fokussierte und 57 relevante Verbundtests
bestehen. Es wurde keine E4-Matrix komponiert und kein Profil gegen E1
verglichen. Siehe
`S1CI_E1_E4_F3_FAMILIENRUNNER_UND_ISOLIERTE_BEREITSCHAFT.md`.

S1-CJ bindet E1, das exakte B0-Nullprofil und einen einzigen statischen
H8-Gain B1 an denselben Vertrag. E1 ist messbar und checkpointvariabel, B1
checkpointkonstant. Alle 15 E1-Kontinuitaetswerte passen innerhalb `1e-12`
zu den gespeicherten S1-CD-Ankern, ohne dessen Einmallauf zu wiederholen.
9 fokussierte und 75 relevante Verbundtests bestehen. Siehe
`S1CJ_E1_E4_E1_B0_B1_RUNNER_UND_S1CD_KONTINUITAET.md`.

S1-CK bindet den konkreten S2-B2-Runner ueber den S1-CF-Handoff und bildet
ORACLE-G ausschliesslich aus einem Fixed-Gain-validierten E1-Profil. B2 ist
vollstaendig, messbar und checkpointvariabel; ORACLE-G ist komponentenweise
exakt E1 und bleibt reine Kontrollobergrenze. 6 fokussierte und 88 relevante
Verbundtests bestehen. Noch keine Gesamtmatrix oder E4-Entscheidung. Siehe
`S1CK_E1_E4_S2_B2_ORACLE_G_UND_EINZELRUNNERABSCHLUSS.md`.

S1-CL bindet alle neun Modellrollen als lazy, schreibgeschuetztes Inventar
in der festen E4-Reihenfolge. Inventardigest `e76d4154...c25c1`; 8
fokussierte und 96 relevante Verbundtests bestehen. Beim Aufbau wurde kein
Runner, keine Komposition und keine Entscheidung ausgefuehrt. Siehe
`S1CL_E1_E4_LAZY_RUNNERINVENTAR_UND_STATISCHE_MATRIXBEREITSCHAFT.md`.

S1-CM registriert den spaeteren E4-Gesamtlauf als genau einen Versuch. Der
Vertrag bindet Inventar- und Ausfuehrungsdigest, drei getrennte
Same-Directory-Pfade, kanonischen Ergebnisdigest, atomare Veroeffentlichung,
Fehlernachweis und Wiederholungsverbot. 7 fokussierte Tests bestehen. Es
wurde noch kein Runner ausgefuehrt und keine E4-Entscheidung erzeugt. Siehe
`S1CM_E1_E4_STATISCHER_EINMALLAUFVERTRAG.md`.

S1-CN fuehrt den gebundenen E4-Versuch genau einmal aus. Alle Kontrollen und
Kompatibilitaetspruefungen bestehen. Der kleinste relative Profilrest ist
B1 mit `0.9774918513` und liegt oberhalb der Grenze `0.05`; die technische
Entscheidung lautet `E4_RESIDUAL_AFTER_REGISTERED_BASELINES`. Dies ist kein
Memorybefund. Siehe
`S1CN_E1_E4_EINMALLAUF_UND_BASELINERESIDUAL.md`.

S1-CO registriert den ersten E1-Teilhinweiskorridor. Gespiegelte H8-
Geschichten, G4-Nullkontakt, energiegleiche Viertelhinweise,
Vollkontaktreferenzen sowie P0, statischer B1-Gain und gekreuzte Geschichte
sind fest gebunden. Noch keine Ausfuehrung und kein Rekonstruktions- oder
Memorybefund. Siehe `S1CO_E1_TEILHINWEIS_REKONSTRUKTIONSVERTRAG.md`.

S1-CP implementiert `left-g4`, `right-g4` und `neutral` sowie den privaten
Ergebniskern fuer exakt 36 injizierte Beobachtungen. Die gespiegelte
History-Hinweis-Interaktion, P0/B1-Boeden und n=2/n=4 sind synthetisch
abgenommen. 14 fokussierte und 44 relevante Verbundtests bestehen. Noch
keine reale Cue-Matrix oder Entscheidung. Siehe
`S1CP_E1_TEILHINWEIS_ZUSTANDSARME_UND_ERGEBNISKERN.md`.

S1-CQ implementiert isolierte E1-, P0- und B1-static-H8-Cue-Runner mit
frischen n=2/n=4-Feldkopien. P0 ist exakt null, B1 bleibt bei identischem
Hinweis ueber alle Geschichten wertgleich und gespiegelte E1-Arme bleiben
gespiegelt. 8 fokussierte und 52 relevante Verbundtests bestehen. Die
Viertelantwort ist isoliert proportional zur Vollantwort und daher noch
keine Rekonstruktion. Siehe `S1CQ_E1_ISOLIERTE_TEILHINWEISRUNNER.md`.

S1-CR bindet die 36 Modell-/Geschichte-/Hinweisrollen als lazy,
schreibgeschuetztes Inventar. Der Digest lautet `e91148ff...d34925`; 7
fokussierte und 59 relevante Verbundtests bestehen. Beim Aufbau wurde kein
Runner, Kompositor oder Evaluator aufgerufen. Siehe
`S1CR_E1_TEILHINWEIS_LAZY_RUNNERINVENTAR.md`.

S1-CS registriert die spaetere 36er-Ausfuehrung als genau einen Versuch.
Einmallauf-, Cue- und Inventardigest, drei getrennte Ergebnis-/Versuchs-/
Sperrpfade, atomare Veroeffentlichung und Wiederholungsverbot sind gebunden.
7 fokussierte und 66 relevante Verbundtests bestehen. Noch keine Matrix oder
Entscheidung. Siehe
`S1CS_E1_TEILHINWEIS_STATISCHER_EINMALLAUFVERTRAG.md`.

S1-CT fuehrt die gebundene 36er-Matrix genau einmal aus. Alle Kontrollen
bestehen; die Entscheidung lautet `HISTORY_SPECIFIC_PARTIAL_CUE_EFFECT`.
P0 und B1 besitzen keine Historyinteraktion. Die Teilinteraktion ist jedoch
exakt `0.25` der Vollinteraktion und zeigt daher lineare Historymodulation,
noch keine Mustervervollstaendigung oder Memory. Siehe
`S1CT_E1_TEILHINWEIS_EINMALLAUF_UND_HISTORYEFFEKT.md`.

S1-CU registriert die Cue-Amplituden `0.125, 0.25, 0.5, 1.0` gegen die
komponentenweise lineare Nullprognose `I(q)=q*I(1)`. P0, B1, Spiegelung,
n=2/n=4 und der unveraenderte S1-CT-Anker bleiben Pflichtkontrollen.
Vertragsdigest `88e56327...5cbe0`; 7 fokussierte und 77 relevante
Verbundtests bestehen. Siehe `S1CU_E1_CUE_AMPLITUDENKURVENVERTRAG.md`.

S1-CV implementiert den amplitudenparametrischen E1/P0/B1-Einzelrunner und
den interpretationsfreien 72er-Kurvenkern. Komponentenweise lineare und
nichtlineare Entscheidungen sind synthetisch abgenommen; real wurden nur
Einzelarme geprueft. 14 fokussierte und 84 relevante Verbundtests bestehen.
Siehe `S1CV_E1_CUE_AMPLITUDENRUNNER_UND_KURVENKERN.md`.

S1-CW bindet alle 72 Amplitudenrollen lazy und schreibgeschuetzt. Der
Inventardigest lautet `d3a40cbf...276cd9`; 7 fokussierte und 91 relevante
Verbundtests bestehen. Beim Aufbau wurde kein Runner, Kompositor oder
Evaluator aufgerufen. Siehe
`S1CW_E1_CUE_AMPLITUDEN_LAZY_RUNNERINVENTAR.md`.

S1-CX registriert die 72er-Amplitudenkurve als genau einen Versuch.
Kurven-, Inventar- und Einmallaufdigest, Ergebnis-/Versuchs-/Sperrpfade,
atomare Veroeffentlichung und Wiederholungsverbot sind gebunden. 7
fokussierte und 98 relevante Verbundtests bestehen. Siehe
`S1CX_E1_CUE_AMPLITUDEN_STATISCHER_EINMALLAUFVERTRAG.md`.

S1-CY fuehrt die gebundene 72er-Kurve genau einmal aus. Alle Kontrollen
bestehen; die Entscheidung lautet
`AMPLITUDE_CURVE_EXPLAINED_BY_LINEAR_SCALING`. Die Interaktion folgt bei
allen vier Staerken komponentenweise exakt `I(q)=q*I(1)`. Damit ist der
Teilhinweis-Rekonstruktionszweig beendet, nicht das Gesamtprojekt. Siehe
`S1CY_E1_CUE_AMPLITUDEN_EINMALLAUF_LINEARBEFUND.md`.

S1-CZ bilanziert die vorhandene E1-Evidenz statisch. Lokaler langsamer
Zustand, endliche Ressourcenwiederverwendung und spaetere
history-spezifische Feldwirkung sind technisch belegt; Rekonstruktion,
MCM-Memory und AV-weite Wirksamkeit sind es nicht. Der isolierte
Drei-Knoten-Rekonstruktionszweig bleibt gestoppt. Als naechstes wird in
S1-DA ausschliesslich der statische Vertrag fuer eine private, ablatierbare
E1-Integration in den kontrollierten Audio-/Video-Feldpfad gebunden. Siehe
`S1CZ_EVIDENZAUDIT_UND_AV_INTEGRATIONSENTSCHEID.md`.

S1-DA bindet den privaten E1-Anschluss hinter dem gemeinsamen
`TransientNeuronInputSet`-Handoff. Die E1-Zeitentwicklung folgt den
geordneten AV-Kontaktabschluessen; Gleichung und Parameter bleiben
unveraendert. P0, A0 und A1 sowie neutrale, Audio-, Video- und kombinierte
AV-Quellenarme bleiben getrennt. Der oeffentliche neutrale Pfad und seine
Snapshots werden nicht erweitert. Als naechstes implementiert S1-DB nur den
privaten transienten Schritt und asynchronen Kompositor mit synthetischer
In-Memory-Abnahme. Siehe `S1DA_E1_KONTROLLIERTER_AV_INTEGRATIONSVERTRAG.md`.

S1-DB implementiert den privaten transienten E1/S/H-Schritt und den
asynchronen Kompositor. A0 bleibt bitgenau P0, Nullgain-A1 bleibt bitgenau
A0, und aktive E1-Rueckwirkung folgt denselben geordneten
Kontaktabschlusszeiten. Ressourcenbilanz, genau einmalige Source-Supports,
simultane Modalitaeten und API-Isolation bestehen in 76 relevanten
`unittest`-Tests. Der begrenzte Befund lautet
`E1_TRANSIENT_AV_INTEGRATION_READY`, nicht Memory. Als naechstes bindet
S1-DC statisch die zweiphasige AV-Probe mit angeglichener S/H-Grenze und
eingefrorenem F0-Adapter. Siehe
`S1DB_E1_TRANSIENTE_AV_INTEGRATION_UND_ABNAHME.md`.

S1-DC registriert ein reines AB/BA-Permutationspaar desselben bereits
reduzierten AV-Frame-Multisets. E1 entsteht waehrend der Geschichte ohne
Rueckwirkung; historisches S/H wird vor der identischen Probe verworfen.
P0, neutraler E1-Zustand, AB/BA-Ablation, aktive eingefrorene AB/BA-
Zustaende und ihre festen Adapterbaselines sind getrennt. Als naechstes
implementiert S1-DD nur den privaten eingefrorenen transienten Probeoperator
mit synthetischer Abnahme, noch keine Gesamtmatrix. Siehe
`S1DC_E1_ZWEIPHASIGER_AV_HISTORY_PROBEVERTRAG.md`.

S1-DD implementiert den privaten eingefrorenen transienten E1-Probeoperator
und seine feste Adapterbaseline. Ablation, neutraler Zustand und Nullgain
sind bitgenau P0; aktiver E1-Ausgang und passender fester Adapter sind
bitgenau gleich. E1 bleibt waehrend der Probe objekt- und wertidentisch.
Der relevante Verbund besteht mit 92 `unittest`-Tests. Als naechstes
implementiert S1-DE nur den reduzierten AB/BA-Sequenz-Permutator und seine
Quellenidentitaeten, noch keine E1-Historie. Siehe
`S1DD_E1_EINGEFRORENER_TRANSIENTER_PROBEOPERATOR.md`.

S1-DE implementiert die private reduzierte AB/BA-Quellenpermutation. Nach
einer verworfenen neutralen Audio-Aufwaermphase enthalten A und B je 100
auditive und je 10 visuelle Frames. Payload, Carrier, Source-Supports,
Organismus-Zeitslots, Masse und Energie bleiben beim Blocktausch exakt
identisch; nur die geordnete Folge ist verschieden. 7 fokussierte und 107
relevante `unittest`-Tests bestehen. Es wurde keine E1-Historie, kein Feld
und keine Probe ausgefuehrt. Als naechstes bindet S1-DF den privaten
A0-History-Produzenten statisch. Siehe
`S1DE_E1_REDUZIERTE_AV_HISTORY_PERMUTATION.md`.

S1-DF bindet den privaten A0-History-Produzenten statisch. AB-P0, AB-A0,
BA-P0 und BA-A0 starten auf objektgetrennten, wertidentischen frischen
84-Knoten-Feldern; beide E1-Arme besitzen getrennte neutrale E1-Zustaende
und deaktivierte Rueckwirkung. Historische S/H-Felder duerfen nicht in den
Ausgabecontainer gelangen. Es wurde keine E1-Historie und kein Feldlauf
ausgefuehrt. Als naechstes implementiert S1-DG den Produzenten mit kleiner
synthetischer Abnahme. Siehe
`S1DF_E1_A0_AV_HISTORY_PRODUKTIONSVERTRAG.md`.

S1-DG implementiert den privaten A0-History-Produzenten. Vier frische
P0-/A0-Arme bleiben intern; nur zwei E1-Endzustaende und technische Audits
duerfen ausgegeben werden. Ein Frischfelddigest ersetzt keinen Runtime-
Snapshot, sondern bindet den noch kontaktfreien Startzustand. 7 fokussierte
und 114 relevante `unittest`-Tests bestehen. Der kanonische Einstieg wurde
ohne Ausfuehrung des E1-Kerns vorgeprueft; es existieren noch keine
kanonischen `b_AB`-/`b_BA`-Zustaende. Als naechstes registriert S1-DH genau
eine kanonische History-Produktion statisch. Siehe
`S1DG_E1_A0_AV_HISTORY_PRODUZENT_UND_ABNAHME.md`.

S1-DH registriert genau eine spaetere kanonische History-Produktion. Die
drei S1-DE-Digests, der normalisierte S1-DG-Quellcodedigest, die feste
Konfiguration und drei unbenutzte Zielpfade sind gebunden. Nur `D_state` und
`D_total_binding` duerfen ohne Schwelle berichtet werden. 8 fokussierte und
122 relevante `unittest`-Tests bestehen; es wurde keine History ausgefuehrt
und keine Datei angelegt. Als naechstes implementiert S1-DI den
Einmalexecutor mit synthetischer Abnahme. Siehe
`S1DH_E1_A0_AV_HISTORY_STATISCHER_EINMALLAUFVERTRAG.md`.

S1-DI implementiert und prueft den Einmalexecutor synthetisch und fuehrt
danach den kanonischen History-Produzenten genau einmal aus. Beide Arme
verarbeiten 220 Supports, A0 bleibt bitgenau P0, Ressourcenfehler sind null
und die E1-Endzustaende unterscheiden sich mit
`D_state = 0.000830161044915372`. Die Ergebnisdatei sperrt eine Wiederholung.
Dies ist kein Memorybefund. Da kein S1-DC-Verfeinerungsrest erhoben wurde,
bleibt die Probe bis zum statischen S1-DJ-Anschlussaudit gesperrt. Siehe
`S1DI_E1_A0_AV_HISTORY_EINMALLAUF_UND_ZUSTANDSDIFFERENZ.md`.

S1-DJ auditiert den veroeffentlichten Report und die relevanten
Implementierungsquellen statisch. Eine globale analytische Fehlerobergrenze
fuer den fehlenden S1-DC-Verfeinerungsrest existiert nicht. Der volle
S1-DC-Befund ist deshalb gestoppt und S1-DI darf nicht wiederholt werden.
Zulaessig bleibt eine enger benannte Transferpruefung, die `b_AB` und `b_BA`
nur als gegebene eingefrorene Inputs behandelt. 5 fokussierte und 132
relevante `unittest`-Tests bestehen. Als naechstes bindet S1-DK diesen
Transfervertrag statisch. Siehe
`S1DJ_E1_A0_AV_HISTORY_EVIDENZ_UND_ANSCHLUSSAUDIT.md`.

S1-DK bindet den engen eingefrorenen Zustandstransfer statisch: die
veroeffentlichten Zustandsdigests, eine identische 110-Support-AV-Probe,
sieben Kontrollarme und einen eigenen Probe-Partitionsvergleich. Der
Builder fuehrt keinen Feld- oder Probelauf aus. 6 fokussierte Tests bestehen.
Der volle S1-DC-Befund bleibt gestoppt. Als naechstes implementiert S1-DL
nur den privaten Transferpfad und nimmt ihn synthetisch ab; die reale Probe
bleibt gesperrt. Siehe
`S1DK_E1_EINGEFRORENER_ZUSTANDSTRANSFERVERTRAG.md`.

S1-DL implementiert den privaten digestgebundenen Zustandsloader und einen
siebenarmigen Kompositor mit strikt synthetischer Provenienz. Die
kanonischen Zustaende koennen den Kompositor nicht erreichen; die reale
Probe bleibt gesperrt. 8 fokussierte und 146 relevante `unittest`-Tests
bestehen. Der volle S1-DC-Befund bleibt gestoppt. Als naechstes registriert
S1-DM statisch genau einen kanonischen Transferlauf, ohne ihn auszufuehren.
Siehe
`S1DL_E1_ZUSTANDSLOADER_UND_SYNTHETISCHER_SIEBENARMKOMPOSITOR.md`.

S1-DM registriert statisch genau einen kanonischen Zustandstransferlauf. Es
bindet Evidenz, S1-DL-Implementierung, beide Partitionen, sieben Arme und
drei neue unbenutzte Einmalpfade. Es wurde keine Datei erzeugt und keine
Probe gestartet. 9 fokussierte und 155 relevante `unittest`-Tests bestehen.
Der volle S1-DC-Befund bleibt gestoppt. Als naechstes implementiert S1-DN
den Einmalexecutor und nimmt ihn zuerst synthetisch ab. Siehe
`S1DM_E1_EINGEFRORENER_ZUSTANDSTRANSFER_STATISCHER_EINMALLAUFVERTRAG.md`.

S1-DN implementiert den privaten Einmalexecutor und prueft ihn nur mit
synthetischen Ergebnisproduzenten. Der Status folgt deterministisch aus
aktiver Distanz und Probe-Partitionsrest; gestartete Fehler sperren jede
Wiederholung. Die kanonischen Projektpfade bleiben unbenutzt. 7 fokussierte
und 162 relevante `unittest`-Tests bestehen. Der volle S1-DC-Befund bleibt
gestoppt. Als naechstes implementiert S1-DO die kanonische
Zwei-Partitions-Produzentenbruecke, ohne sie aufzurufen. Siehe
`S1DN_E1_ZUSTANDSTRANSFER_EINMALEXECUTOR_UND_SYNTHETISCHE_ABNAHME.md`.

S1-DO implementiert die kanonische Zwei-Partitions-Produzentenbruecke und
prueft nur ihren nichtausfuehrenden Preflight. Probequelle, Zustaende,
Geometrie, Partitionen und sieben Arme sind vollstaendig verdrahtet; der
Produzent wurde nicht aufgerufen. 7 fokussierte und 169 relevante
`unittest`-Tests bestehen. Der volle S1-DC-Befund bleibt gestoppt. Als
naechstes bindet S1-DP Produzenten- und Executordigest in einem letzten
statischen Freigabetor. Siehe
`S1DO_E1_KANONISCHE_ZWEIPARTITIONS_PRODUZENTENBRUECKE.md`.

S1-DP bindet den projektgebundenen Einmallaufvertrag, Produzent, Executor,
Evidenz und freie Zielpfade in einem letzten statischen Freigabetor. Jede
Validierung rekonstruiert das Gate vollstaendig. Produzent und Executor
blieben unaufgerufen. 8 fokussierte und 177 relevante `unittest`-Tests
bestehen. Der volle S1-DC-Befund bleibt gestoppt. Als naechstes validiert
S1-DQ erneut und fuehrt den engen kanonischen Transfer genau einmal aus.
Siehe `S1DP_E1_FINALES_STATISCHES_ZUSTANDSTRANSFER_FREIGABETOR.md`.

S1-DQ validiert das Gate und fuehrt den engen kanonischen Zustandstransfer
genau einmal aus. Die gegebenen eingefrorenen E1-Zustaende erzeugen unter
derselben AV-Probe S/H-Differenzen von `6.0604584716517085e-06` und
`6.506083701604548e-06` bei einem Probe-Partitionsrest von
`9.71445146547012e-17`. Ablation ist exakt P0; aktive und passende feste
Adapterarme sind bitgenau gleich. Der Status lautet
`REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE`. Der Ergebnisbericht ist
statisch nachauditiert und 309 E1-Verbundtests bestehen. Das ist ein enger
technischer Zustandstransfer, kein History-, Rekonstruktions- oder
Memorybefund. Der volle S1-DC-Befund bleibt gestoppt. Als naechstes
klassifiziert S1-DR den erreichten Substratbaustein statisch, ohne neuen
Lauf. Siehe
`S1DQ_E1_KANONISCHER_ZUSTANDSTRANSFER_EINMALLAUF_UND_TECHNISCHER_BEFUND.md`.

S1-DR klassifiziert den digestgebundenen S1-DQ-Befund statisch. Der Status
`GIVEN_STATE_TRANSFER_MILESTONE_ONLY` bestaetigt nur die ablatierbare
spaetere Feldwirkung gegebener E1-Zustaende. Da aktive und feste
zustandsabgeleitete Adapter bitgenau gleich sind, bleiben kontrollierte
Weltkontaktbildung, Rekonstruktion und Memory-Lebenszyklus offen. 6
fokussierte und 12 gemeinsame Nachlauftests bestehen; der vollstaendige
E1-Verbund besteht mit 315 Tests. Der alte S1-DC-Zweig
bleibt gestoppt; S1-DS darf als neuer statischer, dreifach zeitverfeinerter
Weltkontakt-Bildungsvertrag folgen. Siehe
`S1DR_E1_STATISCHE_SUBSTRATMEILENSTEIN_KLASSIFIKATION.md`.

S1-DS bindet den neuen Weltkontakt-Bildungskorridor vor jeder
Implementierung und Ausfuehrung. AB/BA, Identitaetswiederholung,
Bildungsablation, identische Probe, Probeablation und feste Adapter werden
unter drei completion-aligned Zeitverfeinerungen `r1/r2/r4` verglichen.
Physischer Horizont, Supports und integrierter lokaler Eingang bleiben
identisch. Signal und passender feiner Rest sind mit vorab gebundenem Faktor
acht getrennt. 6 fokussierte und 321 vollstaendige E1-Verbundtests bestehen;
kein Lauf wurde gestartet.
Als naechstes implementiert S1-DT nur den synthetischen
Verfeinerungsplaner. Siehe
`S1DS_E1_VERFEINERTER_WELTKONTAKT_BILDUNGSVERTRAG.md`.

S1-DT implementiert den privaten completion-aligned Verfeinerungsplaner.
Rezeptorkontakte bleiben punktfoermig an ihrer gemessenen Abschlusszeit;
nur die kontaktfreie Entwicklung zwischen Abschluessen wird in `r1/r2/r4`
unterteilt. Horizont, Supports und signiertes, absolutes sowie quadratisches
Kontaktintegral bleiben in der synthetischen Abnahme exakt identisch. 7
fokussierte und 328 vollstaendige E1-Verbundtests bestehen; kein E1- oder
Feldlauf wurde gestartet. Als
naechstes bindet S1-DU einen nichtausfuehrenden kanonischen AB-/BA-Preflight.
Siehe `S1DT_E1_COMPLETION_ALIGNED_VERFEINERUNGSPLANER.md`.

S1-DU prueft die kanonischen AB-/BA-Quellen nichtausfuehrend mit dem
S1-DT-Planer. Beide Reihenfolgen besitzen 220 Supports, 200 identische
Abschlussgrenzen, `200/400/800` Schritte und exakt gleiche signierte,
absolute sowie quadratische Kontaktintegrale. Ihre geordneten Kontakt-,
Handoff- und Plandigests bleiben verschieden. 7 fokussierte und 335
vollstaendige E1-Verbundtests bestehen; kein E1- oder Feldlauf wurde
gestartet. Als naechstes implementiert S1-DV
nur den synthetisch abgenommenen E1-Bildungsrunner. Siehe
`S1DU_E1_KANONISCHER_AB_BA_VERFEINERUNGSPREFLIGHT.md`.

S1-DV implementiert den privaten verfeinerten Bildungsrunner und nimmt ihn
nur synthetisch ab. Je `r1/r2/r4` werden AB, BA, eine zweite AB-Identitaet
und zwei Bildungsablationsarme aus frischen Objekten gebildet. Identitaet,
neutrale Ablation, Supports, Ressourcen und deaktivierte History-
Rueckwirkung bestehen. Historische Felder verlassen den Kern nicht;
kanonische Quellen werden vor Ausfuehrung abgewiesen. 8 fokussierte und 343
vollstaendige E1-Verbundtests bestehen. Als naechstes bindet S1-DW den
statischen Einmallaufvertrag fuer
die verfeinerte Bildungs- und Transferkette. Siehe
`S1DV_E1_VERFEINERTER_SYNTHETISCHER_BILDUNGSRUNNER.md`.

S1-DW registriert statisch genau einen spaeteren kanonischen Lauf der
verfeinerten Bildungs- und Transferkette. S1-DS, S1-DU, Bildungsrunner,
Transferkern, Quellen, Verfeinerungen, Arme, Metriken, Kontrollen,
Entscheidungen, Berichtsfelder und drei freie Einmalpfade sind gebunden.
Kanonischer Produzent und Executor fehlen noch; `execution_permitted` bleibt
deshalb falsch. 8 fokussierte und 351 vollstaendige E1-Verbundtests bestehen;
keine Bildung oder Probe wurde ausgefuehrt. Als naechstes implementiert
S1-DX nur den synthetisch
abgenommenen Einmalexecutor. Siehe
`S1DW_E1_VERFEINERTE_BILDUNGS_TRANSFERKETTE_STATISCHER_EINMALLAUFVERTRAG.md`.

S1-DX implementiert Ergebniscontainer und atomare Einmal-Persistenz. Die
synthetische Abnahme prueft alle Verfeinerungsarme, 13 Metriken, elf
Kontrollen, vier Entscheidungen, Vorstart- und gestartete Fehler,
Veroeffentlichung und Wiederholungsschutz. Der kanonische Projektordner wird
von dieser Oberflaeche abgewiesen; alle S1-EA-Pfade bleiben frei. 8
fokussierte und 359 vollstaendige E1-Verbundtests bestehen. Als naechstes
implementiert S1-DY nur die
kanonische Produzentenbruecke und ihren nichtausfuehrenden Preflight. Siehe
`S1DX_E1_VERFEINERTER_KETTENERGEBNISKERN_UND_SYNTHETISCHER_EINMALEXECUTOR.md`.

S1-DY bindet Quellen, `r1/r2/r4`-Plaene, Probe, frische Geometrie, neutralen
E1-Anfang und den privaten kanonischen Produzenteneinstieg in einem
nichtausfuehrenden Preflight. Der Einstieg bleibt bis S1-DZ geschlossen.
6 fokussierte und 365 vollstaendige E1-Verbundtests bestehen; die S1-EA-
Pfade bleiben frei. Als naechstes implementiert S1-DZ die numerische
Produzentenkomposition ohne kanonischen Aufruf. Siehe
`S1DY_E1_KANONISCHE_PRODUZENTENBINDUNG_UND_PREFLIGHT.md`.

S1-DZ komponiert drei synthetische verfeinerte Bildungsresultate mit je
einem siebenarmigen Probe-Ergebnis zum S1-DX-Container. Zustandsfreeze,
Ablationen, Verfeinerungsreste, 13 Metriken und elf Kontrollen werden
deterministisch gebildet. 5 fokussierte und 370 vollstaendige
E1-Verbundtests bestehen; der kanonische Einstieg bleibt geschlossen. Als
naechstes implementiert S1-EA0 den siebenarmigen kanonischen Probe-Runner
ohne Freigabe des Einmallaufs. Siehe
`S1DZ_E1_VERFEINERTE_PRODUZENTENKOMPOSITION.md`.

S1-EA0 implementiert und prueft den siebenarmigen eingefrorenen Probe-Runner
auf synthetischen Zustaenden. E1-Freeze, Supportzuordnung, Probeablation,
feste Adapter und die Komposition aller drei Verfeinerungen bestehen. 5
fokussierte und 375 vollstaendige E1-Verbundtests sind gruen; der kanonische
84-Knoten-Lauf bleibt gesperrt. Als naechstes implementiert S1-EA1 den
kanonischen Bildungsadapter. Siehe
`S1EA0_E1_SIEBENARMIGER_EINGEFRORENER_PROBERUNNER.md`.

S1-EA1 implementiert den kanonisch gebundenen Fuenfarm-Bildungsadapter. Der
Kern ist mit ersetzten synthetischen Eingaben fuer `r1/r2/r4`, Identitaet
und Bildungsablation abgenommen; die kanonische 84-Knoten-Bildung wurde
nicht gestartet. 6 fokussierte und 381 vollstaendige E1-Verbundtests
bestehen. Als naechstes bindet S1-EA2 Bildung, Probe und Komposition ohne
Einmalfreigabe. Siehe
`S1EA1_E1_KANONISCHER_VERFEINERTER_BILDUNGSADAPTER.md`.

S1-EA2 verdrahtet Bildung, geometrieneutralen siebenarmigen Probekern und
S1-DZ zum privaten Gesamtproduzenten. Der Preflight bindet 110 Supports,
100 Abschluesse, `100/200/400` Probeschritte und alle Implementierungsdigests.
Die Gesamtfolge wurde nur mit ersetzten synthetischen Eingaben abgenommen.
5 fokussierte und 386 vollstaendige E1-Verbundtests bestehen. Als naechstes
bindet S1-EA3 Produzent, Einmalexecutor und Zielpfade statisch. Siehe
`S1EA2_E1_KANONISCHE_GESAMTPRODUZENTENVERDRAHTUNG.md`.

S1-EA3 bindet statisch Gesamtproduzent, S1-DX-Executor-Kern,
Berichtsfelder, Upstream und freie Zielpfade. Der kanonische Executor fehlt
noch; Ausfuehrung und Persistenz bleiben gesperrt. 5 fokussierte und 391
vollstaendige E1-Verbundtests bestehen. Als naechstes implementiert S1-EA4
den kanonischen Exactly-once-Adapter mit temporaeren Spiegelpfaden. Siehe
`S1EA3_E1_KANONISCHER_RELEASE_PREFLIGHT.md`.

S1-EA4 implementiert den kanonischen Exactly-once-Executoradapter und prueft
ihn ausschliesslich an temporaeren Spiegelpfaden. Markerpolitik, gestarteter
Fehler, Wiederholungsschutz und atomare Veroeffentlichung bestehen. Der
produktive Einstieg bleibt gesperrt. 5 fokussierte und 396 vollstaendige
E1-Verbundtests sind gruen. Als naechstes implementiert S1-EA5 das letzte
statische Freigabegate. Siehe
`S1EA4_E1_KANONISCHER_EXACTLY_ONCE_EXECUTORADAPTER.md`.

S1-EA5 schliesst das finale statische Gate. Alle Vertraege,
Implementierungsdigests, Einstiege, Berichtsfelder und freien Zielpfade sind
gebunden; technische Bereitschaft ist wahr, Ausfuehrung bleibt falsch. 5
fokussierte und 401 vollstaendige E1-Verbundtests bestehen. Der naechste
Schritt S1-EA6 waere der tatsaechliche kanonische Einmallauf. Siehe
`S1EA5_E1_FINALES_STATISCHES_EINMALLAUFGATE.md`.

S1-EA6 wurde kanonisch genau einmal ausgefuehrt und atomar veroeffentlicht.
Alle Kontrollen bestehen; beide feinen Probensignale verfehlen den
vorregistrierten Achtfachboden knapp. Die Entscheidung lautet
`NUMERICALLY_UNDECIDABLE`. 411 post-run E1-Verbundtests bestehen. S1-EA6
darf nicht wiederholt oder nachparametriert werden. Ein neuer S1-EB-
Bestaetigungskorridor kann statisch folgen. Siehe
`S1EA6_E1_KANONISCHER_VERFEINERTER_EINMALLAUF.md`.

S1-EB registriert einen neuen `r2/r4/r8`-Bestaetigungskorridor mit
unveraenderter Mechanik, Achtfachschwelle und neuen freien Exactly-once-
Pfaden. S1-EA6 bleibt terminal. 6 fokussierte und 417 vollstaendige
E1-Verbundtests bestehen; nur die Plannerimplementierung darf als naechstes
folgen. Siehe
`S1EB_E1_UNABHAENGIGER_VERFEINERUNGSBESTAETIGUNGSVERTRAG.md`.

S1-EB1 implementiert den getrennten completion-aligned `r2/r4/r8`-Planer.
Supports, Abschlusszeiten, Horizont und Kontaktintegrale bleiben in der
synthetischen Abnahme exakt. 7 fokussierte und 424 vollstaendige E1-
Verbundtests bestehen; kein kanonischer Plan oder Feldlauf entstand. Als
naechstes bindet S1-EB2 AB, BA und Probe nichtausfuehrend. Siehe
`S1EB1_E1_COMPLETION_ALIGNED_R8_PLANER.md`.

S1-EB2 bindet die kanonischen AB-, BA- und Probeplaene an `r2/r4/r8`, ohne
Feld- oder E1-Ausfuehrung. Die kontrollierten Inventare, Abschlusszeiten,
Kontaktintegrale und refinementsinvarianten Handoffs bestehen. Nur die
Implementierung eines privaten synthetischen S1-EB3-Bildungsrunners ist als
naechster Schritt freigegeben. Siehe
`S1EB2_E1_KANONISCHER_R2_R4_R8_PREFLIGHT.md`.

S1-EB3 implementiert den privaten synthetischen `r2/r4/r8`-Bildungsrunner.
Identitaet, Bildungsablation, Supportzuordnung, Ressourcenbilanz,
Wiederholbarkeit und die Ablehnung kanonischer Quellen bestehen. Neun
fokussierte und 439 vollstaendige E1-Verbundtests sind gruen; Probe und
Einmallaufpfade blieben unberuehrt. Als Naechstes wird nur die vollstaendige
Bestaetigungskette statisch gebunden. Siehe
`S1EB3_E1_SYNTHETISCHER_R2_R4_R8_BILDUNGSRUNNER.md`.

S1-EB4 bindet die vollstaendige Bestaetigungskette statisch an alle
vorregistrierten Quellen, Mechaniken, Kontrollen, Metriken und
Entscheidungen. Acht fokussierte und 447 vollstaendige E1-Verbundtests
bestehen. Produzent, Executor und Ausfuehrung bleiben gesperrt; die
Exactly-once-Pfade sind frei. Als Naechstes folgt nur der synthetische
`r2/r4/r8`-Ergebnis- und Entscheidungskern. Siehe
`S1EB4_E1_STATISCHER_BESTAETIGUNGSKETTENVERTRAG.md`.

S1-EB5 implementiert den privaten `r2/r4/r8`-Ergebnis- und
Entscheidungskern. Alle vier Entscheidungen und die strikte Achtfachgrenze
sind mit synthetischen Resultaten abgenommen. Neun fokussierte und 456
vollstaendige E1-Verbundtests bestehen; kanonische Ausfuehrung und
Persistenz blieben gesperrt. Als Naechstes folgt ein synthetischer
siebenarmiger Probeadapter fuer die neuen Bildungsergebnisse. Siehe
`S1EB5_E1_R2_R4_R8_ERGEBNIS_UND_ENTSCHEIDUNGSKERN.md`.

S1-EB6 implementiert den privaten siebenarmigen Probeadapter fuer die neuen
`r2/r4/r8`-Bildungsergebnisse. Eingefrorene Zustaende, Ablation,
Fixed-Adapter und Supportzuordnung sind mit einer kleinen synthetischen AV-
Quelle kontrolliert. Acht fokussierte und 464 vollstaendige E1-Verbundtests
bestehen; kanonische Probe, Entscheidung und Persistenz bleiben gesperrt.
Als Naechstes folgt die synthetische End-to-End-Komposition. Siehe
`S1EB6_E1_SYNTHETISCHER_SIEBENARMIGER_R2_R4_R8_PROBEADAPTER.md`.

S1-EB7 komponiert Bildung, Probe, Metriken, Kontrollen und Entscheidung fuer
`r2/r4/r8` durchgaengig im Speicher. Sieben fokussierte und 471
vollstaendige E1-Verbundtests bestehen. Die synthetische Fixture endet wegen
null Probensignal korrekt `NUMERICALLY_UNDECIDABLE`; dies ist kein
kanonischer Befund. Als Naechstes folgt nur ein synthetischer Exactly-once-
Executor in einem temporaeren Testverzeichnis. Siehe
`S1EB7_E1_SYNTHETISCHE_R2_R4_R8_END_TO_END_KOMPOSITION.md`.

S1-EB8 implementiert den synthetischen Exactly-once-Executor fuer die
S1-EB4-Berichtsoberflaeche. Atomare Publikation, Wiederholungssperre,
Attempt-Erhalt und Ablehnung registrierter Zielpfade sind temporaer
abgenommen. Sechs fokussierte und 477 vollstaendige E1-Verbundtests
bestehen; alle S1-EB-Pfade bleiben frei. Als Naechstes wird der kanonische
Produzent nur statisch gebunden. Siehe
`S1EB8_E1_SYNTHETISCHER_EXACTLY_ONCE_EXECUTOR.md`.

S1-EB9 bindet den kanonischen Produzenten nichtausfuehrend an Quellen,
`r2/r4/r8`-Plaene, Geometrie, frisches Feld, neutralen E1-Startzustand und
alle neuen Kettenrollen. Sieben fokussierte und 484 vollstaendige E1-
Verbundtests bestehen. Runtime, Persistenz und Claims bleiben gesperrt. Als
Naechstes folgt nur der kanonisch gebundene Bildungsadapter mit synthetisch
ersetztem Rechenkern. Siehe
`S1EB9_E1_KANONISCHE_PRODUZENTENBINDUNG_UND_PREFLIGHT.md`.

S1-EB10 bindet den privaten `r2/r4/r8`-Bildungsadapter an die unveraenderte
S1-EB9-Produzentenbindung. Der kanonische Resolver prueft die gebundenen
Eingaben ohne Feldlauf; der fuenfarmige Rechenkern wurde nur mit
synthetischen Ersatzinputs abgenommen. Sechs fokussierte und 490
vollstaendige E1-Verbundtests bestehen. Kanonische Bildung, Probe,
Entscheidung und Persistenz bleiben gesperrt. Als Naechstes wird nur die
Bildung-zu-Probe-Uebergabe statisch gebunden. Siehe
`S1EB10_E1_KANONISCH_GEBUNDENER_R2_R4_R8_BILDUNGSADAPTER.md`.

S1-EB11 bindet die S1-EB10-Bildungsergebnisse statisch an die kanonische
Probequelle und die `r2/r4/r8`-Probeplaene. Die Uebergabe verbindet nur
Resultat-, Zustands-, Quellen- und Plandigests und fuehrt keinen Feldschritt
aus. Sechs fokussierte und 496 vollstaendige E1-Verbundtests bestehen.
Probe, Entscheidung, Persistenz und Claims bleiben geschlossen. Als
Naechstes folgt ein kanonisch gebundener siebenarmiger Probeadapter mit
synthetisch ersetzter Rechenabnahme. Siehe
`S1EB11_E1_STATISCHE_BILDUNG_ZU_PROBE_UEBERGABE.md`.

S1-EB12 implementiert den kanonisch gebundenen siebenarmigen Probeadapter.
Der Rechenkern ist nur mit synthetischer Audio-/Video-Probe und synthetischen
E1-Zustaenden abgenommen; der kanonische Einstieg stoppt vor der
Inputaufloesung. Acht fokussierte und 504 vollstaendige E1-Verbundtests
bestehen. Entscheidung, Persistenz und Claims bleiben gesperrt. Als
Naechstes wird die Probe-zu-Ergebniskern-Uebergabe statisch gebunden. Siehe
`S1EB12_E1_GESPERRTER_KANONISCHER_SIEBENARMIGER_PROBEADAPTER.md`.

S1-EB13 bindet drei geordnete `r2/r4/r8`-Proberesultate statisch an das
vorregistrierte Metrik-, Kontroll-, Entscheidungs- und Regelinventar. Der
Ergebniskern wird nicht aufgerufen. Sieben fokussierte und 511 vollstaendige
E1-Verbundtests bestehen. Entscheidung, Persistenz und Claims bleiben
geschlossen. Als Naechstes folgt ein gesperrter kanonischer Ergebnis-
Kompositor mit synthetisch unterlegter Rechenabnahme. Siehe
`S1EB13_E1_STATISCHE_PROBE_ZU_ERGEBNISKERN_UEBERGABE.md`.

S1-EB14 implementiert den gesperrten kanonischen Ergebnis-Kompositor. Nur
synthetisch unterlegte Ersatzresultate wurden verarbeitet; sie reproduzieren
den bekannten Fixture-Digest und `NUMERICALLY_UNDECIDABLE`. Sieben
fokussierte und 518 vollstaendige E1-Verbundtests bestehen. Der kanonische
Einstieg stoppt vor der Komposition. Als Naechstes wird ein spaeteres
kanonisches Ergebnis statisch an die Exactly-once-Berichtsoberflaeche
gebunden. Siehe
`S1EB14_E1_GESPERRTER_KANONISCHER_ERGEBNIS_KOMPOSITOR.md`.

S1-EB15 bindet ein spaeteres Ergebnis statisch an die vollstaendige
Exactly-once-Berichtsoberflaeche und die drei freien Zielpfade. Kein Executor
oder Dateischreibpfad wurde aufgerufen. Sieben fokussierte und 525
vollstaendige E1-Verbundtests bestehen. Als Naechstes folgt ein weiterhin
gesperrter kanonischer Exactly-once-Executor mit nur temporaerer
synthetischer Schreibabnahme. Siehe
`S1EB15_E1_STATISCHE_ERGEBNIS_ZU_BERICHTSOBERFLAECHE_UEBERGABE.md`.

S1-EB16 implementiert den gesperrten kanonischen Exactly-once-Einstieg. Die
Schreibmechanik wurde nur temporaer mit dem synthetisch unterlegten Ergebnis
abgenommen. Sieben fokussierte und 532 vollstaendige E1-Verbundtests
bestehen. Der kanonische Einstieg stoppt vor jeder Dateioperation; alle
registrierten Pfade bleiben frei. Als Naechstes folgt ein statisches
Gesamtfreigabe-Audit der Kette S1-EB9 bis S1-EB16. Siehe
`S1EB16_E1_GESPERRTER_KANONISCHER_EXACTLY_ONCE_EXECUTOR.md`.

S1-EB17 auditiert die vollstaendige gesperrte Kette S1-EB9 bis S1-EB16.
Sieben fokussierte und 539 vollstaendige E1-Verbundtests bestehen. Der
Status lautet `TECHNICALLY_BOUND_AWAITING_EXPLICIT_RESEARCH_RELEASE`:
technisch vollstaendig vorbereitet, fachlich und operativ weiterhin
gesperrt. Weitere Adapterstufen sind nicht sinnvoll; als Naechstes folgt die
fachliche Pruefung von Forschungsfrage, Kontrollen, Aussagegrenze,
Einmallauf, Ressourcenrahmen und Fehlerpolitik. Siehe
`S1EB17_E1_STATISCHES_GESAMTFREIGABE_AUDIT.md`.

S1-EB18 bewertet Forschungsfrage, Kontrollen, Entscheidungsregel und
Aussagegrenze mit `KORREKTUR`, nicht `STOPP`. Der enge technische
Bestaetigungslauf ist fachlich sinnvoll. Vor einer Freigabe fehlen jedoch
eine statische Vertragspruefung, feste Laufzeit- und
Speicherobergrenzen sowie die ausdrueckliche Einmallauf-Autorisierung. Als
Naechstes wird nur ein unveraenderlicher Releasevertrag vorbereitet. Siehe
`S1EB18_FACHLICHE_FREIGABEPRUEFUNG.md`.

S1-EB19 bindet den unveraenderlichen Releasevertragsentwurf mit 23800
Feldschritten, 30 Minuten und 4 GiB als harte Obergrenzen. Sieben fokussierte
und 546 vollstaendige E1-Verbundtests bestehen. Der Vertrag bleibt ein
Entwurf; Vertragspruefung, Projekteigner-Autorisierung, Same-session-
Preflight und Ressourcendurchsetzung sind offen. Als Naechstes muss der
Benutzer mit `FREIGABE`, `KORREKTUR` oder `STOPP`
entscheiden. Siehe
`S1EB19_UNVERAENDERLICHER_RELEASEVERTRAG_ENTWURF.md`.

S1-EB20 dokumentiert die bestandene statische Vertragspruefung fuer den
Releasevertragsentwurf. Sie ist keine Laufautorisierung. Offen bleiben
die ausdrueckliche Projekteigner-Autorisierung, technisch gebundene Zeit-
und Speicher-Abbruchgates sowie der Same-session-Preflight. Siehe
`S1EB20_STATISCHE_RELEASEVERTRAGSPRUEFUNG.md`.

S1-EB21 bindet die Projekteigner-Autorisierung genau eines S1-EB-Laufs an
den freigegebenen Releasevertrag. Sieben fokussierte und 553 vollstaendige
E1-Verbundtests bestehen. Der Lauf startet noch nicht: Zeit-/Speicher-
Abbruchgates und Same-session-Preflight bleiben offen. Als Naechstes wird
nur die Ressourcendurchsetzung synthetisch abgenommen. Siehe
`S1EB21_PROJEKTEIGNER_EINMALLAUF_AUTORISIERUNG.md`.

S1-EB22 implementiert native Windows-Job-Object-Gates fuer Wandzeit,
Speicher und Prozessbaumabbruch. Sieben fokussierte und 560 vollstaendige
E1-Verbundtests bestehen. Nur synthetische Unterprozesse wurden gestartet;
der kanonische Lauf bleibt bis zum Same-session-Preflight gesperrt. Siehe
`S1EB22_NATIVE_RESSOURCEN_ABBRUCHGATES.md`.

S1-EB23 implementiert den fluechtigen Same-session-Preflight. Das Receipt ist
an den aktuellen Prozess gebunden, hoechstens fuenf Sekunden gueltig und
bindet Freigabe, Autorisierung, Ressourcenlimits, kanonische Digests, S1-EA6
und die freien Zielpfade erneut. Sechs fokussierte und 566 vollstaendige E1-
Verbundtests bestehen; Lauf und Persistenz wurden nicht gestartet. Als
Naechstes folgt ein Einmal-Worker mit rein synthetischer
Ablaufkoordinationsabnahme. Siehe
`S1EB23_FLUECHTIGER_SAME_SESSION_PREFLIGHT.md`.

S1-EB24 implementiert den geschuetzten synthetischen Einmal-Worker. Ein
Child-Prozess laeuft unter dem S1-EB22-Job-Object, erzeugt S1-EB23 in derselben
Sitzung und konsumiert es unmittelbar vor genau einem synthetischen Marker.
Parent und Child binden Marker, Prozessidentitaet und Preflight-Digest;
Wiederholung und `reports/` werden abgelehnt. Sieben fokussierte und 573
vollstaendige E1-Verbundtests bestehen. Kanonische Runtime und Persistenz
blieben gesperrt. Als Naechstes folgt das statische S1-EB25-Releasekettenaudit. Siehe
`S1EB24_GESCHUETZTER_SYNTHETISCHER_EINMAL_WORKER.md`.

S1-EB25 bindet die Releaseevidenz S1-EB19 bis S1-EB24 an alle acht
kanonischen Rollen S1-EB9 bis S1-EB16 und registriert die exakte Reihenfolge
von Same-session-Preflight, Markern, Bildung, Probe, Komposition und atomarer
Publikation. Sieben fokussierte und 580 vollstaendige E1-Verbundtests
bestehen. Der Auditstatus haelt den kanonischen Worker ausdruecklich als noch
nicht implementiert fest; Lauf und Persistenz bleiben geschlossen. Als
Naechstes folgt S1-EB26 mit synthetisch ersetzten Rechenkernen. Siehe
`S1EB25_STATISCHES_RELEASEKETTEN_UND_WORKERVERTRAG_AUDIT.md`.

S1-EB26 implementiert die gebundene Workerform mit sechs synthetischen
Digestkernen. Der Erfolgsweg prueft atomare Publikation und entfernt den
Attempt erst nach Verifikation; der Fehlerweg behaelt den Attempt und sperrt
jeden Retry. Acht fokussierte und 588 vollstaendige E1-Verbundtests bestehen.
Der kanonische Einstieg stoppt weiterhin vor Markern und Rechenkernen. Als
Naechstes bindet S1-EB27 die vorhandenen kanonischen Funktionen statisch an
die Workerrollen. Siehe
`S1EB26_KANONISCHE_WORKERFORM_MIT_SYNTHETISCHEN_RECHENKERNEN.md`.

S1-EB27 bindet die sechs realen kanonischen Funktionen ueber Modul,
Funktionsname, Signatur, Rueckgabetyp und Quellhash. Datenfluss und
`r2/r4/r8` bleiben fest. Acht fokussierte und 596 vollstaendige E1-
Verbundtests bestehen; keine Funktion, kein Marker und kein Writer wurde
aufgerufen. Als Naechstes folgt der statische S1-EB28-Datenflussvertrag. Siehe
`S1EB27_STATISCHE_BINDUNG_DER_KANONISCHEN_WORKERFUNKTIONEN.md`.

S1-EB28 bindet sechs Artefakttypen, zwoelf Parameterkanten, acht
Digestkontinuitaeten, `r2/r4/r8` und zwoelf geschlossene Handoff-Gates. Neun
fokussierte und 605 vollstaendige E1-Verbundtests bestehen; weder Objekte noch
Runtime, Marker oder Writer wurden aufgerufen. Als Naechstes folgt der statische S1-EB29-
Freischaltungsvertrag. Siehe
`S1EB28_STATISCHER_KANONISCHER_DATENFLUSSVERTRAG.md`.

S1-EB29 bindet vier minimale spaetere Gateuebergaenge und haelt zehn Rollen,
darunter Retry, Claims, S1-EA6-Rerun und Posthoc-Tuning, dauerhaft
geschlossen. Neun fokussierte und 614 vollstaendige E1-Verbundtests bestehen;
aktuell wurde kein Gate geoeffnet. Als Naechstes folgt ein finales
S1-EB30-Go/No-Go-Audit, nicht eine weitere Adapterkette. Siehe
`S1EB29_STATISCHER_MINIMALER_GATE_TRANSITIONSVERTRAG.md`.

S1-EB30 entscheidet
`GO_FOR_FINAL_CANONICAL_WORKER_IMPLEMENTATION`. Alle 14 Voraussetzungen sind
erfuellt und weitere Adapterstufen sind verboten. Neun fokussierte und 623
vollstaendige E1-Verbundtests bestehen. Lauf und Persistenz wurden nicht
gestartet. Als einziger naechster Schritt folgt S1-EB31 als kombinierte finale
Implementierungs- und Einmallaufeinheit. Siehe
`S1EB30_FINALES_GO_NO_GO_AUDIT.md`.

**STOPP:** S1-EB31 wurde genau einmal gestartet und brach nach Lock und
Attempt, aber vor dem ersten Feldschritt ab. Die Bildungsfunktion
rekonstruiert einen alten Vertrag, der freie Zielpfade verlangt und damit dem
Pflicht-Attempt widerspricht. Kein Bericht und keine Forschungsdaten
entstanden. Der Attempt bleibt erhalten; No-Retry gilt. Siehe
`S1EB31_TERMINALER_EINMALLAUF_ABBRUCH.md`.

S1-EB32 bestaetigt statisch, dass derselbe Lebenszykluswiderspruch in
Formation, Probe-Uebergabe und Probe vorliegt. Fuer eine neue Identitaet
muessen Vertrag und kanonische Eingaben vor Lock/Attempt einmalig in einem
unveraenderlichen Ausfuehrungsbundle gebunden und danach nur konsumiert
werden. S1-EB31 bleibt terminal; ein neuer kanonischer Lauf ist nicht
autorisiert. Siehe
`S1EB32_STATISCHE_URSACHENPRUEFUNG_UND_NEUER_LAUFLEBENSZYKLUS.md`.

S1-EC1 implementiert die neue private Bundle-Lebenszyklusoberflaeche. Sie
loest konkrete Laufzeitobjekte genau einmal vor Lock/Attempt auf, prueft ihre
Digests vor und nach dem synthetischen Consumer und besitzt danach keinen
Resolverpfad. Sechs fokussierte Tests bestehen. Die kanonische S1-EB-Kette
wurde nicht ausgefuehrt und bleibt gesperrt. Siehe
`S1EC1_VORBEREITETES_AUSFUEHRUNGSBUNDLE_SYNTHETISCHER_LEBENSZYKLUS.md`.

S1-EC2 bindet die acht konkreten Rollen Korridor, AV-Permutation,
AB-/BA-/Probeplaene, Probesequenzen, Anfangsfeld und E1-Anfangszustand vor
den Markern. Typen, Quellkontakt, Refinements, Geometrie, Neutralzustand und
Digests werden geprueft. Elf gemeinsame S1-EC1/S1-EC2-Tests bestehen; kein
Feld- oder kanonischer Lauf fand statt. Siehe
`S1EC2_TYPISIERTE_VORBEREITETE_E1_EINGABEN.md`.

S1-EC3 trennt die Forschungsbedingungen in einen pfadunabhaengigen
Deskriptor und Identitaet, Exactly-once-Pfade sowie No-Retry in einen
separaten synthetischen Laufvertrag. Der Deskriptor kann trotz real
vorhandenem terminalem S1-EB31-Attempt normal gebaut werden. 17 gemeinsame
S1-EC1-bis-S1-EC3-Tests bestehen; kein Feldlauf fand statt. Siehe
`S1EC3_PFADUNABHAENGIGER_FORSCHUNGSKORRIDOR_UND_LAUFVERTRAG.md`.

S1-EC4 bindet den Refinementplaner direkt an den S1-EC3-Deskriptor. AB-, BA-
und Probeplaene sind in allen Plan-, Zeit-, Handoff- und Integralfeldern
exakt zur Legacy-Ausgabe aequivalent; nur die Plan-Set-Bindung wechselt auf
den Deskriptordigest. 21 gemeinsame Tests bestehen, ohne Feld- oder
kanonischen Lauf. Siehe
`S1EC4_DESKRIPTORGEBUNDENER_REFINEMENTPLANER.md`.

S1-EC5 komponiert den vollstaendigen typisierten Eingangssatz direkt aus
S1-EC3-Deskriptor, kanonischer AV-Permutation, S1-EC4-Plaenen, frischem
Anfangsfeld und neutralem E1-Zustand. Der alte S1-EB-Korridorkonstruktor wird
nicht mehr verwendet. 26 gemeinsame Tests bestehen; kein Feldlauf. Siehe
`S1EC5_VOLLSTAENDIGER_DESKRIPTORGEBUNDENER_EINGABERESOLVER.md`.

S1-EC6 bindet S1-EC1, S1-EC2 und S1-EC5 an den separaten
S1-EC3-Laufvertrag. Im neuen Pfad ist dieser Vertrag die einzige Quelle fuer
Ausfuehrungs-ID und alle drei Exactly-once-Pfade; Bundle und Receipt tragen
denselben Laufvertragsdigest. 30 gemeinsame Tests bestehen, ohne Feldlauf.
Siehe `S1EC6_LAUFVERTRAGSGEBUNDENES_BUNDLE_UND_EXECUTOR.md`.

S1-EC7 bindet den ersten nach dem Attempt liegenden Formation-Consumer an das
vorbereitete Bundle. Fuer `r2/r4/r8` werden die fuenf Formationsrollen in 15
synthetischen Digest-Kernen mit denselben gebundenen Objektinstanzen
aufgerufen. 35 gemeinsame Tests bestehen; kein Feldlauf. Siehe
`S1EC7_VORBEREITETER_SYNTHETISCHER_FORMATION_CONSUMER.md`.

S1-EC8 setzt den realen `_run_arm`-Kern hinter die S1-EC7-Schnittstelle und
nimmt ihn auf einer minimalen Zwei-Dock-In-Memory-Fixture mit zwei
Zeitschritten ab. Aktiver Zustand, neutrale Ablation, Kopienisolierung und
Wiederholbarkeit bestehen. 39 gemeinsame Tests sind gruen; kein kanonischer
Lauf. Siehe `S1EC8_KLEINER_REALER_FORMATIONSKERN_IN_MEMORY.md`.

S1-EC9 komponiert auf derselben kleinen Fixture alle fuenf realen
Formationsarme. Identitaetswiederholung, neutrale Ablationen,
Objekttrennung, Feldgleichheit ohne Rueckwirkung, Ressourcenbudget und
Determinismus bestehen. 43 gemeinsame Tests sind gruen; kein kanonischer
Lauf. Siehe `S1EC9_KLEINE_REALE_FUENF_ARM_FORMATION.md`.

S1-EC10 fuehrt die reale Fuenf-Arm-Komposition mit kleinen echten
`r2/r4/r8`-Schrittfolgen aus. Alle Kontrollen bestehen; der maximale
stufengleiche Verfeinerungsrest sinkt von `0.039194601584206512` auf
`0.019481843726620207`. 48 gemeinsame Tests sind gruen. Dies ist kein
kanonischer Lauf und kein Memory-Nachweis. Siehe
`S1EC10_KLEINE_REALE_R2_R4_R8_REFINEMENTMATRIX.md`.

S1-EC11 fuehrt diese kleine reale Matrix innerhalb des korrigierten
temporaeren Exactly-once-Lebenszyklus aus. Alle 15 Feldarme laufen nach dem
Attempt; der Bericht wird vor Attempt-Entfernung verifiziert und der Lock
anschliessend freigegeben. 52 gemeinsame Tests sind gruen. Keine Probe, kein
kanonischer Lauf und kein Memory-Nachweis. Siehe
`S1EC11_TEMPORAERER_REALER_KLEINFORMATION_LEBENSZYKLUS.md`.

S1-EC12 inventarisiert die vollstaendige vorbereitete AV-Formation ohne
Ausfuehrung: 15 Armlaeufe, 14.000 Armschritte, 1.176.000 Knoten-Schritt- und
2.030.000 Kanten-Schritt-Einheiten. Alle festen Grenzen bestehen; der
pfadunabhaengige Digest lautet `236f7d6a...fb75`. 56 gemeinsame Tests sind
gruen. Kein Attempt, Bericht, Feldlauf oder Memory-Nachweis. Siehe
`S1EC12_STATISCHER_RESSOURCENPREFLIGHT_VOLLSTAENDIGE_AV_FORMATION.md`.

S1-EC13 fuehrte die 15-armige Vollformation genau einmal temporaer aus. Alle
Kontrollen bestanden; der Verfeinerungsrest sank von
`3.4885390053043374e-05` auf `1.736313599644745e-05`. Der Bericht besitzt
SHA-256 `15932c1f...e48a`; 59 Post-Run-Tests sind gruen. **STOPP fuer
Wiederholung und direkten Probe-Handoff**, weil der generische Bericht nur
den Formation-Digest und nicht die gebildeten E1-Zustaende persistiert. Siehe
`S1EC13_TEMPORAERER_VOLLFORMATIONS_EINMALLAUF.md`.

S1-EC14 bindet den vollstaendigen spaeteren Ergebnis- und Zustandshandoff mit
15 E1-Zustaenden, 2.175 Bindungswerten, allen Audits, Kontrollen und
Rohmetriken. JSON-Roundtrip und Manipulationsabwehr bestehen;
Vertragsdigest `db97af62...2b90`, 64 Tests gruen. Keine Publikation, keine
neue Formation und keine Probe. Der S1-EC13-STOPP bleibt bestehen. Siehe
`S1EC14_VOLLSTAENDIGER_ERGEBNIS_UND_ZUSTANDSHANDOFF_VERTRAG.md`.

S1-EC15 nimmt die atomare Publikation des vollstaendigen 15-Zustands-
Fixture-Payloads ab. Finales Reread, Digestpruefung, typisierter Reload,
Exactly-once-Sperre und erhaltener Fehler-Attempt bestehen.
Publisher-Policy-Digest `96617801...314f`; 70 Tests gruen. Keine neue
Vollformation oder Probe. Siehe
`S1EC15_ATOMARER_FIXTURE_PUBLISHER_VOLLSTAENDIGER_ZUSTANDSHANDOFF.md`.

S1-EC16 bindet fuer eine neue Identitaet 13 Uebergaenge und 15 Pflichtgates
vom Preflight bis zum typisierten Reload aller 15 Zustaende. Das statische
Audit bestaetigt nur die Vertragsvollstaendigkeit, keine zukuenftigen
Laufzeitergebnisse. Policy-Digest `54b1b5c5...b026`; 75 Tests gruen. Keine
Marker, Formation, Publikation oder Probe. Siehe
`S1EC16_STATISCHER_GESAMTLEBENSZYKLUS_VERTRAG_NEUE_IDENTITAET.md`.

S1-EC17 fuehrt alle 13 Uebergaenge mit einer realen kleinen
Vollgeometrie-Fixture Ende-zu-Ende aus und publiziert sowie laedt alle 15
Zustaende. 82 Tests sind gruen; Policy-Digest `e145102b...cae3`. Die
Fixture-Konvergenz ist `false` und daher keine Forschungsevidenz. Keine
Vollformation oder Probe. Siehe
`S1EC17_SYNTHETISCHE_END_TO_END_ABNAHME_GESAMTLEBENSZYKLUS.md`.

S1-EC18 prueft Ressourcen, neue Zielpfade und den vollstaendigen
Publikationsvertrag statisch. Alle 15 Schranken bestehen; die Entscheidung
lautet `FREIGABE` fuer die Vorbereitung der neuen S1-EC19-Identitaet. Fuenf
fokussierte Tests sind gruen. S1-EC18 selbst autorisiert oder erzeugt keinen
Feldlauf, Marker, Bericht oder Probe. Siehe
`S1EC18_STATISCHE_FREIGABEPRUEFUNG_NEUER_TEMPORAERER_VOLLFORMATIONSLAUF.md`.

S1-EC19 fuehrt die neue Vollformation genau einmal aus und publiziert alle 15
Zustaende mit 2.175 Bindungswerten. Atomarer Reread und typisierter Reload
bestehen; Bericht-SHA-256 `93cc94dd...1fcc`. Die Rohwerte reproduzieren
S1-EC13 exakt, diesmal bleibt jedoch der vollstaendige Zustandssatz erhalten.
Keine Probe und kein Memory-Claim. Siehe
`S1EC19_VOLLSTAENDIGER_PUBLIZIERTER_VOLLFORMATIONS_EINMALLAUF.md`.

S1-EC20 inventarisiert den S1-EC19-Handoff statisch: 15 Rollen, sieben
erwartete Zustandsdigestklassen, sechs aktive `r2/r4/r8`-AB/BA-Zustaende und
die beiden `r8`-Entscheidungskandidaten. Der bereits vorbereitete AV-
Probequellendigest, drei Plaene, sieben Arme, Ablation und feste
Adapterbaseline sind gebunden. Audit-Digest `3524e973...6c2a`; 6 Tests
gruen. Keine Probe oder Entscheidung. Siehe
`S1EC20_STATISCHER_PROBE_HANDOFF_AUDIT.md`.

S1-EC21 fuehrt den neuen Probe-Consumer mit kleinen synthetischen
Vollgeometrie-Zustaenden und `2/4/8`-Fixture-Plaenen aus. Alle 21 Arme und
Kontrollen bestehen. Der feine Fixture-Rest ist nach einem praktisch nullen
groben Rest groesser; die Fixture ist daher keine Numerikevidenz.
Ergebnisdigest `1b328220...e11f`; 5 Tests gruen. S1-EC19-Zustaende und die
registrierte Vollprobe bleiben unverbraucht. Siehe
`S1EC21_SYNTHETISCHE_SIEBENARM_PROBE_CONSUMER_ABNAHME.md`.

S1-EC22 bindet die spaetere Vollprobe statisch an die tatsaechlichen
`200/400/800`-Plaene, 110 Supports je Plan, sieben Arme und damit 9.800
Feldarm-Schritte. Die fruehere Schaetzung von 19.600 Schritten ist
korrigiert. Alle 17 Gates bestehen; Policy-Digest `493df3be...f487`, 5 Tests
gruen. Keine Probe, Marker, Publikation oder Ergebnisentscheidung. Siehe
`S1EC22_STATISCHE_RESSOURCEN_UND_EXACTLY_ONCE_FREIGABE_VOLLPROBE.md`.

S1-EC23 fuehrt die persistente Vollprobe genau einmal aus. Alle 9.800
Feldarm-Schritte, Ablations-, Adapter-, Freeze- und Supportkontrollen
bestehen; der feine Rest sinkt auf `4.0517124277883454e-07`. Der
27.906-Byte-Rohbericht wurde atomar publiziert und typisiert reloaded;
SHA-256 `85a114b9...b50e`. Keine Ergebnisentscheidung oder Claims. Siehe
`S1EC23_PERSISTENTER_VOLLPROBEN_EINMALLAUF_ROHMETRIKEN.md`.

S1-EC24 auditiert den geschuetzten S1-EC23-Bericht rein statisch. Beide
r8-Aktivsignale liegen mit etwa `15.50x` ueber dem feinen Rest und damit
strikt ueber dem registrierten Achtfachboden; alle Kontrollgates bestehen.
Die begrenzte Entscheidung bestaetigt eine numerisch klare persistente
Zustands-Probedifferenz, jedoch kein Memory und keine KI. Siehe
`S1EC24_STATISCHER_ENTSCHEIDUNGSAUDIT_PERSISTENTE_VOLLPROBE.md`.

S1-EC25 trennt sechs Memory-Funktionsrollen und waehlt
wiederholungsabhaengige Bildung als kleinste naechste Kausalfrage. Erst ein
kontrollierter Unterschied zwischen getrennten `1/2/4/8`-Kontakten und
einem angeglichenen Dauerkontakt darf die spaetere Abschwaechungsfrage
oeffnen. Keine Ausfuehrung und kein Memory-Claim. Siehe
`S1EC25_STATISCHER_MEMORY_FUNKTIONSLUECKEN_AUDIT.md`.

S1-EC26 bindet eine vorhandene 110-Support-AV-Episode in expositionsgleiche
getrennte und kontinuierliche `1/2/4/8`-Kontaktarme ueber denselben
15-Millionen-Tick-Horizont. Baselines und Entscheidung sind vorregistriert;
nur die Plannerimplementierung ist freigegeben. Siehe
`S1EC26_STATISCHER_VERTRAG_WIEDERHOLUNGSABHAENGIGE_E1_BILDUNG.md`.

S1-EC27 materialisiert alle acht Quellenarme und r2/r4/r8-Handoffs. Eine
ungleiche kontaktfreie Nachzeit im ersten Entwurf wurde erkannt, gestoppt
und korrigiert. Je Paar stimmen nun auch letzter Kontaktabschluss und
Schrittzahl; alle Supports sind genau einmal zugeordnet. Kein Feldlauf oder
Claim. Siehe
`S1EC27_QUELLEN_UND_SCHEDULE_PLANNER_WIEDERHOLUNGSBILDUNG.md`.

S1-EC28 fuehrt eine kleine reale n2/r2-Consumer-Fixture aus. Sie deckt zuerst
doppelte technische Quellsupports auf; nach gemeinsamer Verschiebung von
Quell- und Organismuszeit bestehen drei Kopie-Arme, neutrale Ablation,
Snapshot/Restore und atomarer Fehlerpfad. Fixture-Digest
`1b36c259...dff6`; keine Forschungsentscheidung. Siehe
`S1EC28_SYNTHETISCHE_REALE_FORMATION_CONSUMER_ABNAHME.md`.

S1-EC29 bindet die nichtkanonische n1/n2-Pilotmatrix mit sechs getrennten
P0-, Bildungsablations- und Aktivarmen je r2/r4/r8-Batch. Gesamtlast 25.368
Feldarm-Schritte; nur Runnerimplementierung ist erlaubt. Pilotlauf,
Persistenz und Forschungsentscheidung bleiben gesperrt. Siehe
`S1EC29_STATISCHER_N1_N2_PILOTVERTRAG.md`.

S1-EC30 koordiniert alle sechs Batches mit 36 typisierten synthetischen
Receipts. Reihenfolge, Rollentrennung, Receipt-Ausrichtung und Fail-fast
bestehen; ausgefuehrte Feldschritte bleiben exakt null. Rohdigest
`700b0296...97c0`; keine Entscheidung. Siehe
`S1EC30_SYNTHETISCHE_SECHSARM_PILOTRUNNER_ABNAHME.md`.

S1-EC31 auditiert den realen Anschluss der sechs n1/n2-Pilotrollen statisch.
Die technischen Gates bestehen, aber Rollenadapter und ausdrueckliche
Ausfuehrungsfreigabe fehlen absichtlich. Entscheidung
`VORBEREITET_NICHT_FREIGEGEBEN`, Digest `3be17db1...7f3c`; kein Feldlauf,
keine Persistenz und kein Claim. Siehe
`S1EC31_STATISCHER_REAL_PREFLIGHT_N1_N2_PILOT.md`.

S1-EC32 implementiert die reale Sechs-Rollen-Abbildung und nimmt sie nur auf
der kleinen n2/r2-Fixture ab. P0, Bildungsablation und aktive E1-Bildung sind
jeweils doppelt getrennt; insgesamt werden 48 Feldschritte ausgefuehrt.
Ergebnisdigest `04ae0494...2d12`; der Vollpilot, Persistenz, Entscheidung und
Claims bleiben gesperrt. Siehe
`S1EC32_REALE_SECHSROLLEN_ADAPTER_FIXTURE.md`.

S1-EC33 prueft den Zustand nach der Adapterabnahme erneut statisch. Neun von
zehn Gates bestehen; offen ist nur die ausdrueckliche Projekteignerfreigabe
fuer den nichtkanonischen 25.368-Schritte-Pilot. Entscheidung
`ADAPTER_BESTAETIGT_FREIGABE_FEHLT`, Digest `77922b78...6d3b8`; kein Feldlauf
und keine Ergebnisentscheidung. Siehe
`S1EC33_STATISCHER_POST_ADAPTER_PREFLIGHT.md`.

S1-EC35 auditiert ohne neuen Lauf die P0-Messgrenze des EC34-Schemas. Die
Zeitlagen sind bei n1 identisch und bei n2 trotz gleicher Exposition
verschieden. P0 behaelt nur Digest-Gleichheit, keine quantitativen
Aktivierungs-, Nachhall- oder Verfeinerungsdistanzen. Entscheidung
`P0_MAGNITUDE_NOT_IDENTIFIABLE_FROM_EC34_SCHEMA`, Digest
`9423c442...e290b`; kein Claim. Siehe
`S1EC35_STATISCHER_P0_IDENTIFIZIERBARKEITSAUDIT.md`.

S1-EC36 implementiert ohne Feldlauf das quantitative P0-Snapshot-Schema. Es
behaelt vorzeichenbehaftete Aktivierungs- und Nachhallkontraste sowie deren
komponentenweise r2/r4/r8-Reste. 21 Tests bestehen; synthetischer
Profildigest `e15b511d...20912`. Keine EC34-Rekonstruktion oder Entscheidung.
Siehe `S1EC36_QUANTITATIVES_P0_ERGEBNISSCHEMA.md`.

S1-EC37 bindet je n1/n2-r2/r4/r8-Batch zwei frische P0-Snapshots an EC36,
insgesamt zwoelf. EC34-Ergebnis und verbrauchte Autorisierung sind explizit
ausgeschlossen. Vertragsdigest `ad9200e9...7502e`; nur
Runnerimplementierung, kein Feldlauf oder Claim. Siehe
`S1EC37_STATISCHER_P0_INTEGRATIONSVERTRAG.md`.

S1-EC38 nimmt den Handoff-Pfad synthetisch ab. Zwoelf getrennte Snapshots
werden zu sechs EC36-Paaren und zwei n1/n2-Profilen verarbeitet. 34 Tests
bestehen; Fixture-Digest `e8f6b0d4...3b53e`. Keine Autorisierung,
Felddynamik, Persistenz oder Entscheidung. Siehe
`S1EC38_SYNTHETISCHE_QUANTITATIVE_P0_RUNNERABNAHME.md`.

S1-EC39 bestaetigt zehn von zwoelf Gates des korrigierten Realpfads. Offen
sind die reale unmittelbare P0-Snapshot-Uebergabe und eine neue
Einmallauffreigabe. Entscheidung `VORBEREITET_REAL_HANDOFF_FEHLT`, Digest
`9a0d128b...18313`; kein Feldlauf oder Claim. Siehe
`S1EC39_STATISCHER_QUANTITATIVER_REAL_PREFLIGHT.md`.

S1-EC40 nimmt die reale P0-Snapshot-Uebergabe auf der kleinen n2/r2-Fixture
ab. Zwei P0-Arme laufen insgesamt 16 Schritte; Aktivierungs-Linf
`0.004439790780415592`, Nachhall-Linf `0.008155675046400305`.
Fixture-Digest `489bbebc...8d26e`; keine Vollpilot- oder Memory-Evidenz. Siehe
`S1EC40_KLEINE_REALE_QUANTITATIVE_P0_HANDOFF_FIXTURE.md`.

S1-EC41 bestaetigt die kleine reale Handoff-Funktion mit acht von zehn Gates.
Vollrunnerintegration und neue Einmallauffreigabe fehlen. Entscheidung
`SMALL_HANDOFF_CONFIRMED_FULL_RUNNER_MISSING`, Digest
`2015d171...771b6`; kein Feldlauf. Siehe
`S1EC41_STATISCHER_POST_HANDOFF_PREFLIGHT.md`.

S1-EC42 integriert synthetisch alle sechs Batches mit 36 Arm-Receipts,
zwoelf unmittelbaren P0-Snapshots, sechs Paaren und zwei Profilen. 25.368
Schritte sind geplant, null ausgefuehrt. Integrationsdigest
`9073aa10...eafc9`; keine Autorisierung oder Entscheidung. Siehe
`S1EC42_SYNTHETISCHE_QUANTITATIVE_VOLLRUNNER_INTEGRATION.md`.

S1-EC43 bestaetigt alle elf technischen Gates des quantitativen Realpfads.
Offen bleibt nur eine neue ausdrueckliche Einmallauffreigabe. Entscheidung
`TECHNISCH_BEREIT_NEUE_FREIGABE_FEHLT`, Digest `d5ec3541...f4046`; kein
Feldlauf. Siehe `S1EC43_ABSCHLIESSENDER_QUANTITATIVER_REAL_PREFLIGHT.md`.
