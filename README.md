# MCM_FIELD_ORGANISM

`MCM_FIELD_ORGANISM` entwickelt ein technisches audiovisuelles
MCM-Wahrnehmungssystem mit gemeinsamen Rezeptoren, einem dynamischen Feld und
einer davon getrennten perzeptiven Zwei-Bereich-Memory.

Faehigkeiten werden nur benannt, wenn sie durch vorab gebundene,
reproduzierbare Befunde gestuetzt sind. Bekannte Engineeringverfahren bleiben
der verbindliche Vergleichsmassstab.

## Systemstand

```text
kanonische RGB-/PCM-Quelle
-> auditive und visuelle Rezeptoren
-> 336 reduzierte Wahrnehmungswerte
   |-> MCM-Feldkontakt
   `-> atomare Zwei-Bereich-Memory
       -> read-only Teilhinweisabruf
       -> Kontexthypothese oder Enthaltung
```

Das Default-Live-Profil erzeugt `288` visuelle und `48` auditive Werte.
Feld und Memory erhalten unabhaengige Geschwisterprojektionen desselben
Wahrnehmungszustands. Rohbilder, PCM-Fenster und Feldsnapshots werden nicht als
Memoryinhalt gespeichert.

Die Memory besitzt genau zwei oeffentliche Bereiche:

- `A_RECENT`: B4-Inhalte und Kurzfolge mit interner Fast-Spur;
- `B_STABLE`: getrennte auditive und visuelle stabile Prototypen.

Bestaetigt sind ein nichttrivialer AV-Feldpfad, wiederholungsabhaengige
Verdichtung, kontrolliertes Vergessen, begrenzte Holdout-Generalisation sowie
visueller und auditiver Teilhinweisabruf. Rollenfreie AV-Stroeme koennen mehrere
Erfahrungen bilden und bei fehlendem, unpassendem oder mehrdeutigem Kontext
kontrolliert enthalten. Alle Abruf- und Kontextoperationen bleiben read-only;
Kontext wirkt nicht in Feld oder Memory zurueck.

Die Funktionen werden durch Slotscans, L1-Vergleiche, adaptive Prototypbildung
und transparente Entscheidungstabellen erklaert. Das ist ein technischer
Memory- und Kontextnutzen, aber kein Nachweis besonderer MCM-Speicherphysik.

## Abgeschlossen: auditive Reihenfolgenempfindlichkeit S2-NU

Der [einmalige NU-Vergleich](reports/s2nu/s2nu-temporal-comparison-20260909-01/BEFUND.md)
verarbeitet sechs vorversiegelte Fuenferfolgen aus gespeicherten Halbprofilwerten.
Im kontrollierten s02/s03-Gegenpaar sind Randvektoren und vollstaendige
ungeordnete Multisets bitgleich, waehrend die festgelegte totale Variation
streng unterschiedlich ist: `0.0018286359991568396 < 0.003657297305254732`.
Die Primaerbedingung besteht; vier beschreibende Kontrollen bestehen getrennt.
Direktnachrechnung und einmalige read-only Verifikation sind baselinegleich.

Das belegt ausschliesslich Reihenfolgenempfindlichkeit dieser Kennzahl auf
diesem Gegenpaar, keine Quellenfortsetzung, Kategorieerkennung oder sichere
Lernbindung. Keine neue Memory-, Feld- oder Runtimefunktion; ME/MI bleiben
gesperrt. Keine Rezeptorwiederholung oder nachtraegliche Parameterwahl.
NU bleibt unveraendert geschlossen: keine weiteren Permutationsversuche
und kein Einsatz von T als Memory- oder Zulassungsregel. T ist kein Mass
fuer Identitaet, Praegung oder Bedeutung.

Der naechste [statische NV-Plan](docs/S2NV_STATISCHER_PLAN_PROSPEKTIVE_AUDITIVE_VERLAUFSVORHERSAGE.md)
fragt nach prospektivem Vorhersagenutzen: eine feste Zwei-Zustands-
Extrapolation gegen Persistenz auf vier neuen Fuenferfolgen. Gewinne und
Wechselverluste werden getrennt geprueft. Die [rezeptorfreie Vorversiegelung](reports/s2nv/s2nv-source-preseal-20260909-01/BEFUND.md)
ist nach 16/16 neutralen Quellenpruefungen einmal abgeschlossen und einmal
read-only verifiziert: 20 getrennte Fenster, gemeinsame Praefixe und alle
Bytegleichheiten sind gebunden. Der [praefixgebundene Prognoseanschluss](reports/s2nv/s2nv-prediction-qualification-20260909-01/BEFUND.md)
ist anschliessend einmal neutral 20/20 qualifiziert: Prognosen werden vor
Zielfenstererzeugung/-analyse gebunden, Aenderungen und vorzeitiger Zugriff
abgewiesen. Direktbaseline, Gesamtbeleg und getrennte Bewertung sind angebunden.
Der danach separat freigegebene [NV-Einmallauf](reports/s2nv/s2nv-prospective-prediction-20260909-01/BEFUND.md)
ist `RECORDING_COMPLETE`, einmal read-only verifiziert und anschliessend
getrennt ausgewertet: 20 Analysen/NJ-Projektionen, zwoelf Prognosestellen.
LINEAR gewinnt alle drei Fortsetzungsprognosen. Bei Umkehr, Stillstand und
Quellenwechsel verliert es jeweils am ersten Wechsel; nach Quellenwechsel
auch im Folgefenster. Die drei Primaer- und drei getrennten Verlustprognosen
bestehen; Gewinne kompensieren keine Verluste. Gemeinsame Praefixe sind
keine unabhaengigen Replikate. Keine separate Zielmaterialisierung, kein
Lernen oder Identitaetsnachweis durch feste Extrapolation; Gates `False`.
Die Offline-Pruefung beweist allein keine historische CPU-Aufrufreihenfolge;
die Zukunftssperre beruht auf dem qualifizierten unveraenderten Aufrufpfad.

NV ist unveraendert geschlossen. LINEAR wird nicht als bevorzugte
Systemprognose integriert. Gleiche Praefixe verraten keinen zukuenftigen
Zweig; Vorhersagefehler sind weder Quellenwechselnachweis noch Stress.
Der [statische NW-Lernplan](docs/S2NW_STATISCHER_PLAN_GELERNTE_AUDITIVE_VERLAUFSVORHERSAGE.md)
bindet genau einen aus beobachteten Uebergaengen gelernten skalaren
Fortsetzungskoeffizienten: vier Updates, dann eingefrorene Pruefung gegen
unveraenderte Persistenz und LINEAR auf neuen Quellen. Gewinne und Verluste
gegen beide Baselines bleiben getrennt. Die [rezeptorfreie Vorversiegelung](reports/s2nw/s2nw-source-preseal-20260909-01/BEFUND.md)
ist nach 20/20 neutralen Quellenpruefungen einmal abgeschlossen und einmal
read-only verifiziert: 26 getrennte Fenster, vier dokumentierte
Bytegleichheitsgruppen und getrennte Lern-/Pruef-/Evaluationsbindungen.
Dabei keine Rezeptor-/NJ-, Koeffizienten- oder Prognoseberechnung.
Der anschliessende [private Lern-/Prognoseanschluss](reports/s2nw/s2nw-learning-qualification-20260909-01/BEFUND.md)
ist einmal neutral **28/28 qualifiziert**: vier Updates nach beobachteten
Zielen, Prognosebindung vor Zielverarbeitung und ein eingefrorener Zustand
fuer zwoelf Pruefprognosen. Unabhaengiger Direktlerner, Fehlerabschluesse
und gueltige negative Ergebnisse sind geprueft. Sechs neutrale Analysen/NJ-
Projektionen prueften den Adapter, keine versiegelten NW-Quellen.
Der danach separat freigegebene [NW-Einmallauf](reports/s2nw/s2nw-learned-prediction-20260909-01/BEFUND.md)
ist `RECORDING_COMPLETE`, einmal read-only verifiziert und getrennt
ausgewertet. 26 Analysen/NJ-Projektionen, vier Updates und zwoelf eingefrorene
Pruefprognosen; gelerntes alpha `0.49999999812324286`, Direktlerner identisch.
Alle sechs Fortsetzungsbedingungen gegen PERSIST und LINEAR bestehen.
Gegen Persistenz verliert der gelernte Arm aber bei allen drei ersten
Wechseln und nach Gruppenwechsel auch im Folgefenster. Diese Verluste werden
nicht mit Gewinnen verrechnet. Bestaetigt ist nur gelernter Vorhersagenutzen
innerhalb der gebundenen Dynamikklasse, keine Objekt-/Quellenidentitaet oder
allgemeines Sequenzlernen. Keine Memory-/Feldintegration, ME/MI gesperrt,
Gates `False`.

NW ist unveraendert geschlossen: keine Wiederholung und keine Integration.
Offen bleibt, ob unterschiedliche Lernerfahrungen aufgabengerecht wirken
oder eine feste Daempfung bereits genuegt. Der [statische NX-Plan](docs/S2NX_STATISCHER_PLAN_GEKREUZTE_LERNHISTORIEN.md)
kreuzt zwei unabhaengig gelernte, eingefrorene Zustaende mit denselben vier
Pruefverlaeufen. PERSIST, LINEAR und ein vorab festes `0.5` bleiben getrennte
Kontrollen. Kreuzhistoriengewinn, Zusatznutzen gegen die feste Daempfung und
Wechselverluste sind eigene Befunde. Die [rezeptorfreie NX-Vorversiegelung](reports/s2nx/s2nx-source-preseal-20260909-01/BEFUND.md)
ist nach einer neutralen 24/24-Quellenqualifikation einmal abgeschlossen und
einmal unabhaengig read-only geprueft: 32 getrennte Fenster, Nenner 1024,
sieben Bytegleichheitsgruppen, zwei Lern-/Freeze-Bindungen, zwoelf
Pruefstellen und 28 getrennte Kriterien. Keine Deduplizierung; historische
NW-Bindungen unveraendert. Die [private Zwei-Lerner-Anbindung](reports/s2nx/s2nx-learning-qualification-20260909-01/BEFUND.md)
ist anschliessend genau einmal neutral **32/32 qualifiziert**: eigene
Historienketten, Prognosen vor Zielverarbeitung, Updates nach Fehlerbindung,
beide Freezes vor Test und zwoelf gemeinsame Pruefstellen ohne Nachlernen.
Gleiche/initiale Koeffizienten bleiben technisch gueltige negative Befunde;
alle 28 Kriterien sind getrennt angebunden. Sechs neutrale Adapteranalysen,
keine NX-Payloads in dieser Qualifikation.
Der anschliessend separat freigegebene [NX-Einmallauf](reports/s2nx/s2nx-crossed-learning-20260909-01/BEFUND.md)
ist `RECORDING_COMPLETE`, einmal unabhaengig read-only verifiziert und
getrennt ausgewertet: 32 Analysen/NJ-Projektionen, je vier eigene Updates,
beide Freezes vor zwoelf gemeinsamen Pruefstellen. H1 lernt
`0.2500000003063012`, H2 `0.7500000008868464`; Direktlerner identisch.
Kreuzhistorienvorteil 6/6, Vorteil gegen festes 0.5 separat 6/6 und weitere
Fortsetzungsbaselines 12/12 bestaetigt. Die vier vorgebundenen Wechselverluste
treten ebenfalls ein; nach Gruppenwechsel verlieren beide auch im Folgefenster
gegen Persistenz. Keine Verrechnung dieser Verluste. Das belegt kontrollierten
Einfluss der Lerngeschichte, keine automatische Auswahl einer passenden
Historie oder allgemeines Sequenzlernen. **S2-NX ist unveraendert geschlossen.**
Keine Wiederholung oder Integration; Gates `False`, ME/MI gesperrt.
Die unpassende Historie verschlechtert Ergebnisse; der Vorteil gegen das
gepruefte `0.5` schliesst nicht jeden denkbaren Festfaktor aus.

Der [einzelne statische NY-Plan](docs/S2NY_STATISCHER_PLAN_PRAEFIXGEBUNDENE_ANWENDBARKEIT.md)
fragt nach praefixgebundener Anwendbarkeit: Empfehlung anhand des Fehlers
am letzten beobachteten Uebergang, ausschliesslich fuer die naechste Prognose.
Beide eingefrorenen NX-Historien und PERSIST bleiben Kontrollen; eine lokale
Schaetzung aus demselben Praefix prueft den Mehrwert gespeicherter Erfahrung.
Fehlende Evidenz und Gleichstand ergeben keine Empfehlung. Die private
[rezeptorfreie Quellen-/Freeze-Anbindung](reports/s2ny/s2ny-source-binding-qualification-20260909-01/BEFUND.md)
ist einmal neutral 24/24 qualifiziert; danach wurden sechs neue Fuenferfolgen
[einmal vorversiegelt und read-only geprueft](reports/s2ny/s2ny-source-preseal-20260909-01/BEFUND.md).
30 getrennte Quellen, fuenf Bytegleichheitsgruppen, 18 Prognose-/zwoelf
LOCAL-Stellen und 20 Kriterien wurden vor der Ausfuehrung gebunden.
Historische NX-Freeze-Payloads nur gelesen, keine Lernwiederholung.
Empfehlungserfolg, Folgefehler und Wechselverluste bleiben getrennt;
absolute MAE/Gewinne gegen LOCAL sind erforderlich. Die danach freigegebene
[private Empfehlungs-/LOCAL-Anbindung](reports/s2ny/s2ny-prediction-qualification-20260909-01/BEFUND.md)
ist einmal neutral **30/30 qualifiziert**: unmittelbare Fehlerherkunft,
Prognosebindung vor Zielverarbeitung, Enthaltung ohne Ersatzwerte, frische
LOCAL-Schaetzung und unveraenderliche Freeze-Eingaenge. Fuenf echte neutrale
Nullfenster prueften Audio/NJ, keine NY-Payloads. Vollstaendige neutrale
Gesamthuelle 585.190 Byte; keine erneute NX-Lernrechnung oder Systemintegration.
Offline-Bindungen beweisen allein keine historische Aufrufordnung.

Der separat freigegebene [reale NY-Einmallauf](reports/s2ny/s2ny-prefix-recommendation-20260909-01/BEFUND.md)
ist technisch vollstaendig, einmal read-only verifiziert und getrennt
ausgewertet: 30 Analysen/NJ, 18 Prognosestellen, zwoelf LOCAL-Fits pro
Implementierung. 10/18 Empfehlungen: 9 NEXT_BEST, 1 NEXT_WRONG; sechs
Enthaltungen wegen fehlenden Praefixes und zwei wegen Gleichstands.
R/L/P jeweils 4/4, aber LOCAL-Fortsetzungsgewinne nur etwa 4.61e-14 bis
2.49e-12. Bei beschleunigtem Verlauf verliert die Empfehlung zweimal gegen
LOCAL; Umkehrziel und beide Gruppenwechselfenster verlieren gegen PERSIST.
W-Verlustprognosen 3/8, nicht eingetretene Verluste separat berichtet.
D=0 bei Stillstand bleibt ungepruefter Empfehlungsnutzen. Alle absoluten
Einzelwerte sind im Befund verlinkt. Kein Nachweis allgemeiner Robustheit
oder sicherer Wechselerkennung, keine Integration oder Wiederholung.
**S2-NY bleibt unveraendert als begrenzter Mischbefund geschlossen.**
Kein ueberzeugender praktischer LOCAL-Zusatznutzen, keine bevorzugte
Empfehlungsregel, keine Wiederholung und keine nachtraegliche Fehlerschwelle.
Gates `False`, ME/MI und Systemintegration unveraendert gesperrt.

Der [einzige statische NZ-Stoerungsvergleich](docs/S2NZ_STATISCHER_PLAN_BELASTBARKEIT_GESPEICHERTER_VORHERSAGEN.md)
bindet drei saubere/gestoerte Kontrollpaare mit neuen PCM-Rezepten und
unveraenderten Vorhersagearmen. Ausschliesslich Diagnose: absolute MAE,
Gewinne/Verluste gegen LOCAL und Abdeckung getrennt fuer sauber/gestoert.
Alle vier gestoerten Fortsetzungsstellen bleiben erhalten, auch bei
Enthaltung. Keine praktische Mindestverbesserung oder Ersatzschwelle;
die Nutzungsanforderung bleibt offen. Kein Robustheits-/Integrationsbeleg,
keine weitere Stoerparametersuche. Die separat freigegebene
[Quellen-/Stoerqualifikation](reports/s2nz/s2nz-source-binding-qualification-20260909-01/BEFUND.md)
besteht einmal neutral 24/24. Danach wurden
[30 PCM-Fenster einmal rezeptorfrei vorversiegelt](reports/s2nz/s2nz-source-preseal-20260909-01/BEFUND.md)
und einmal read-only geprueft, ohne Regeneration. Vier Bytegleichheitsgruppen,
getrennte Quellen-/Zeitbindungen, historische Freeze-Payloads unveraendert.
Die danach separat freigegebene [diagnostische Anbindung](reports/s2nz/s2nz-diagnostic-qualification-20260909-01/BEFUND.md)
besteht einmal neutral 24/24: Zukunftssperre, Kontrolltrennung, unveraenderte
Freeze-Eingaenge und N=4 auch bei Enthaltung. NY-Arithmetik unveraendert;
feste Historien und Empfehlungen getrennt. Fuenf echte Null-PCM-Analysen
samt NJ nur neutral, keine NZ-Payloads. Vollstaendige neutrale Huelle
609.371 Byte. Der danach separat freigegebene
[einmalige reale NZ-Diagnoselauf](reports/s2nz/s2nz-diagnostic-disturbance-20260909-01/BEFUND.md)
ist technisch vollstaendig, einmal verifiziert und getrennt ausgewertet:
30 Analysen/NJ, 18 Stellen, zwoelf LOCAL-Fits pro Rechnung.
Schwerpunkt N=4/D=4: drei Empfehlungsgewinne gegen LOCAL, ein Verlust;
absolute Gewinne ca. 8.37e-10, 3.70e-7, 3.29e-7, Verlust ca. 2.34e-9.
Feste Historien bleiben separat. Beide ersten Wechselziele werden falsch
empfohlen; auch beide Folgefenster verlieren gegen PERSIST. Keine
Verlustverrechnung oder praktische Robustheitsbehauptung. Vollstaendige
Einzelwerte dokumentiert; keine Integration/Parametersuche, Gates False,
ME/MI unveraendert.

**S2-NZ ist unveraendert geschlossen; der Prognosezweig ruht.** NW/NX
belegen gelerntes Vorhersagewissen mit begrenztem Transfer, NY/NZ jedoch
keine verlaessliche Anwendbarkeit durch den letzten Fehler. Keine bevorzugte
Integration und keine weiteren Stoer-, Koeffizienten- oder Auswahlvarianten.
Die [statische Aufgabenklaerung](docs/S2NZ_ABSCHLUSS_UND_AUFGABENKLAERUNG_SYSTEMNUTZEN.md)
benennt keinen begruendeten Vorhersageverbraucher im bestehenden Grundpfad.
Ohne dessen Aufgabe und Fehlerfolgen bleibt auch eine sachliche
MAE-Anforderung offen. Kein kuenstlicher Anschluss; Gates False, ME/MI
gesperrt. Der Stopp betrifft den Prognosezweig, nicht das Grundsystem.

## Abgeschlossen: auditive L1-Ordnungsdiagnose S2-NT

[S2-NT](reports/s2nt/s2nt-diagnostic-comparison-20260908-01/BEFUND.md)
ist technisch vollstaendig und unveraendert geschlossen. Die primaere
Trennprognose ist widerlegt: nur 2/8 Bedingungen bestehen, sechs sind
umgekehrt. Bei beiden Referenzen ist die Partialaddition naeher als jede
zugelassene Variante. Die getrennten Eigenreferenzbedingungen bestehen 4/4,
die Abstandskontrollen 12/12; sie kompensieren den primaeren Gegenbefund nicht.

Alle vier Varianten veraendern Roh- und Halbwerte. Auf den 25 geprueften
Paaren gibt es ausser den zwei beabsichtigten Exaktkontrollen keine
Bitkollision und keine erst durch Halbierung entstandene Kollision.
Damit ist eine Grenze dieser L1-Bewertung belegt, kein nachgewiesener
Informationsverlust des Rezeptors. Unterschiedliche Vektoren beweisen
umgekehrt nicht, dass die Repraesentation fuer die Aufgabe ausreicht.

Keine weitere Masken-, Schwellen- oder Distanzsuche auf NT; der Korpus bleibt
diagnostische Evidenz, kein Optimierungsbestand. Keine Produktionsaenderung.
Der [statische Ansatzvergleich](docs/S2NT_ABSCHLUSS_UND_STATISCHER_ANSATZVERGLEICH.md)
stellt ausschliesslich bestehende Prototyp-/Abstandsbewertung und eine
erfahrungsgebundene Variationsbeschreibung gegenueber, ohne Algorithmuswahl.
Letztere bleibt durch die fehlende beobachtbare Lernbindung begrenzt:
ME/MI werden weder durch NT noch durch eine neue Huelle entsperrt.
Keine neue Ausfuehrung; Gates bleiben `False`.

## Abgeschlossen: auditive Zwei-Sichten-Bestaetigung S2-NS

[S2-NS](reports/s2ns/s2ns-real-two-view-memory-20260908-01/BEFUND.md)
ist technisch gueltig und fachlich gemischt abgeschlossen. In allen 15
Faellen ist LOWER eine Teilmenge von UPPER; die generationstreue Konjunktion
liefert exakt LOWER, keine zusaetzliche Unterscheidungsleistung.

- Gegen LOWER bleiben sechs richtige Abrufe erhalten, darunter vier
  Variantenfaelle; kein Zusatznutzen, zwei Fehlzulassungen bleiben bestehen.
- Gegen UPPER entstehen sechs richtige Abrufe und fuenf verhinderte
  Fehlzulassungen, aber zwei neue Fehlzulassungen derselben Mischquelle in
  zwei Geschichten. Gewinne werden nicht gegen Fehler verrechnet.
  Oeffentliches `D=0` bleibt Erhaltung nicht geprueft.
- Die tatsaechliche Aufloesung beidseitig widerspruechlicher Sichten bleibt
  ungeprueft. Die nachgewiesene Speicherbildung wird dadurch nicht widerlegt.

**Keine Integration und keine bevorzugte Konjunktionskonfiguration.** Weniger
Kandidaten bedeuten nicht automatisch weniger Fehlzulassungen: Hier entfernt
die Konjunktion gegen UPPER Mehrdeutigkeit und laesst einen fachlich falschen
Kandidaten uebrig. Korrekte Speicherherkunft und eindeutige Anwendbarkeit
beweisen keinen richtigen Bezug der gesamten Wahrnehmung.

**Offene Forschungsfrage:** Welche beobachtbare Evidenz unterscheidet einen
passenden gespeicherten Inhalt von einer Mischwahrnehmung, die dieselben
Anwendbarkeitspruefungen besteht? Eine Mischquelle kann reale Bestandteile
eines bekannten Inhalts enthalten. Deren Wiedererkennung und die eindeutige
Zuordnung der gesamten Wahrnehmung sind verschiedene Aufgaben. NS belegt
damit noch keine eigenstaendige Bestandteilserkennung; seine vorgebundenen
Erwartungen bleiben der unveraenderte Bewertungsmassstab dieses Laufs.
Auch ein spaeteres Semantikziel rechtfertigt keine Umdeutung der Fehler.

Dieser Abschluss verwendet nur vorhandene Befunde. Keine Wiederholung,
Quellenoptimierung, neue Regel, Schwelle oder weitere Vertragsserie.
Historische Defaults, Versiegelung und Belege bleiben unveraendert;
Gates bleiben `False`. Die naechste fachliche Aufgabe bedarf einer gesonderten
Entscheidung.

## Abgeschlossen: auditiver Maskenvergleich NP/NQ/NR

Der Vergleich der festen zusammenhaengenden und verteilten 24-Band-Sicht
ist geschlossen. Die folgenden Zahlen stammen ausschliesslich aus den
vorhandenen Befunden; fuer diese Konsolidierung wurde nichts neu berechnet.

- [S2-NP: Rezeptorevidenz ohne Memory](reports/s2np/s2np-coverage-corpus-comparison-20260907-01/BEFUND.md):
  begrenzter, regelabhaengiger Vorteil der verteilten Sicht. Eine falsche
  Quellenbeziehung entfiel in zwei Panels, bekannte Beziehungen blieben
  erhalten. Die getrennte 48-Band-Diagnose war keine garantierte Obergrenze;
  insbesondere beeinflusst auch die Mittelung die Slow-Anwendbarkeit.
- [S2-NQ: Transfer an real gebildeter Memory](reports/s2nq/s2nq-real-mask-memory-transfer-20260908-01/BEFUND.md):
  Wiederverwendung der bereits untersuchten NP-Quellen, keine unabhaengige
  Korpusbestaetigung. Je vier richtige A- und B-Abrufe blieben erhalten,
  darunter jeweils drei variierte Hinweise. Zwei Fehlzulassungen derselben
  Kontrollquelle in zwei Geschichten entfielen, nicht zwei unabhaengige
  Kontrollquellen. Beziehungserhaltung und richtige oeffentliche Abrufe
  hatten getrennte Nenner.
- [S2-NR: unabhaengig vorversiegelter neuer Runtime-Strom](reports/s2nr/s2nr-mask-runtime-transfer-20260908-01/BEFUND.md):
  technisch gueltig, funktional negativer Transfer. Zielspuren blieben
  gespeichert und anwendbar. Zusaetzliche Konkurrententreffer verhinderten
  zwei richtige eindeutige Abrufe; A- und B-Erhaltung jeweils
  `N/D/R/L = 1/1/0/1`. Hinzu kam eine Fehlzulassung vor Zielbildung.
  Bei e18 traf auch der stabile Zielslot; die Enthaltung wegen Mehrdeutigkeit
  belegt keine Unbekanntheitserkennung. Feld und Memory waren zwischen den
  Armen identisch. Gescheitert ist hier die Selektivitaet der Sicht, nicht
  die Speicherbildung oder technische Runtime.

**Keine allgemeine Ersatzregel:** Der NP/NQ-Vorteil bleibt quellenbegrenzt;
NR beweist umgekehrt keine allgemeine Ueberlegenheit der zusammenhaengenden
Sicht. Beide Masken bleiben untersuchte Forschungskonfigurationen. Keine
bevorzugte verteilte Runtimekonfiguration, keine Aenderung historischer
Defaults. Keine Wiederholung, Maskenoptimierung, Schwellenanpassung oder
B-Priorisierung. Gates bleiben `False`; historische Belege unveraendert.

**Offene Evidenzfrage:** Wie laesst sich ausreichende auditive Evidenz fuer
einen eindeutigen Abruf bestimmen, ohne relevante Konkurrenz durch eine
feste Teilansicht zu uebersehen? Dies ist noch keine Freigabe fuer Vollsicht,
Maskenvereinigung, automatische Sichtwahl oder einen neuen Versuch.

## Private Minimalruntime: konsolidierter Stand nach S2-NG

Dieser Abschnitt bewahrt die damalige Regelentscheidung im historischen
Ausgangsprofil; er begruendet keine bevorzugte verteilte Maske. Fuer den
abgeschlossenen Halbprofil-Maskenvergleich gilt die Einordnung oben.

Die ausfuehrbare private Oberflaeche ist
[`MinimalMCMRuntime336`](tools/_s2mr_private_minimal_mcm_runtime.py):
`process_once`, `snapshot`, `close`. S2-MS bestaetigte den gemeinsamen
Ereignispfad. Vollstaendige AV-Ereignisse erzeugen unabhaengigen Feldkontakt
und genau eine atomare B4-/TSPM-Formation; Teilhinweise erzeugen Feldkontakt
und read-only Abruf. Nur B4/TSPM ist atomar, nicht Feld und Memory gemeinsam.
Kontext bleibt eine getrennte auditive oder visuelle Hypothese.

[`RuntimeComparison`](tools/_s2ng_private_runtime_comparison.py) komponiert
zwei getrennte Runtime-, Feld-, Memory- und Ownerinstanzen mit denselben
unveraenderlichen Eingaben. `AudioRuleBindingV1` bindet Regel-ID, Bandplan,
Konfiguration und Implementierungshashes vor dem ersten Ereignis.

**Bevorzugte Forschungskonfiguration fuer kommende begrenzte Versuche:**
ausdruecklich vorab gebundenes `ALL_BANDS_24`, ausschliesslich fuer auditive
B4-/Fast-Anwendbarkeit (`max(delta_0..23) <= 0.2`). Der unveraenderte
Referenzarm bleibt `HISTORICAL_SUM_L1_24` mit historischem `sum(...)/24`,
nicht `statistics.mean`. Auditory-Slow, Visualpfad, Memorybildung und
Feldkontakt bleiben unveraendert. Keine automatische Regelwahl, kein
Fallback, keine B-Bevorzugung und keine Aenderung historischer Defaults.
Das ist keine allgemeine Produktumstellung oder neue Lernregel.

Zwei getrennte Belege tragen diese private Forschungsentscheidung:

- [S2-NF: Erhaltung unter realer Konkurrenz](reports/s2nf/s2nf-real-retention-under-competition-20260906-01/BEFUND.md):
  `D/R/L = 4/4/0`, davon drei tatsaechlich veraenderte Hinweise;
  eine Fehlzulassung verhindert. Die Partialaddition verliert dagegen ihre
  Zielanwendbarkeit bei bereits mehrdeutiger Referenz. Keine allgemeine
  Verlustfreiheit.
- [S2-NG: Runtime-Transfer](reports/s2ng/s2ng-real-runtime-comparison-20260906-01/BEFUND.md):
  zwei neue richtige auditive B-Abrufe, keine Fehlzulassung; Feld und Memory
  armweise identisch. Auditiv `D=0`: Erhaltung nicht geprueft. Visuell
  `D/R/L = 2/2/0`. Die unbekannte auditive Probe bleibt mehrdeutig; dies ist
  keine nachgewiesene Unbekanntheitserkennung. Direktbaselines erklaeren alles.

S2-NG ist abgeschlossen; kein weiterer NG-Lauf. Der archivierte
[Einmalaufrufer](reports/s2ng/run_runtime_comparison_once.py) dokumentiert die
ausgefuehrte Anbindung, ist aber kein wiederzuverwendender Startbefehl.
Der [S2-NH-Plan fuer unabhaengige Quellen](docs/S2NH_UNABHAENGIGER_AV_RUNTIME_TRANSFERPLAN.md)
ist inzwischen rezeptorfrei vorversiegelt. Seine private Materialisierungs-
und Runtime-Anbindung ist [neutral mit 20/20 qualifiziert](reports/s2nh/s2nh-runtime-binding-qualification-20260906-01/BEFUND.md).
Ein fortgefuehrter HearingPath, native Zeitbindungen, die explizite NH-Felduhr,
fruehe Read-only-Hinweise und getrennte Auswertung sind technisch geprueft.
Keine versiegelten NH-Payloads wurden dabei materialisiert. Der danach
einmalig freigegebene [reale NH-Lauf](reports/s2nh/s2nh-runtime-comparison-20260907-01/BEFUND.md)
stoppte bei e02/`nh-a01` mit `ReceptorContractError` in der Materialisierung:
`NOT_EVALUABLE`, bevor Runtimes, Memoryformationen oder Feldkontakte
gestartet wurden. Der Fehlerbeleg wurde einmal read-only verifiziert;
kein Retry und keine Quellenanpassung. Alle Hauptgates sind geschlossen.
Ein NH-Transfer- oder Erhaltungsbefund liegt weiterhin nicht vor.

## Forschungsgrenze

Ein vorab versiegeltes, unabhaengig erzeugtes AV-Korpus zeigt, dass der Pfad
noch nicht robust auf ungefilterte Varianten uebertraegt:

- Blockmittelung komprimiert unterschiedliche visuelle Texturen unter die
  bestehende Slow-Schwelle und vermischt ihre Prototypen.
- Vollvektorvergleich und exakter maskierter Positionsscan besitzen dort keine
  kompatible visuelle Anwendbarkeitsgrenze.
- Audio trennt die Familien besser, bleibt durch breite B4-/Fast-Treffermengen
  und einzelne Druckaktualisierungen jedoch mehrdeutig.

Das System enthaelt sich dabei korrekt. Ein breiterer Formenvergleich zeigt,
dass die bestehenden 288 Blockmittelwerte raeumliche Struktur tragen. Der
maskenkonditionierte Pose-/Formvergleich verbessert eine verteilte 96-Werte-
Sicht deutlich. Zwei zeitlich getrennte 96er-Sichten reduzieren
Fehlzulassungen durch Konsens und ihre 192er-Vereinigung erreicht auf dem
prospektiven Formkorpus die Vollform-Obergrenze. Ein getrennter Open-Set-
Vergleich weist unbekannte, zwischenliegende und quellinkompatible Evidenz
ohne Fehlzulassung ab. Diese Zwei-Blick-Evidenz ist als fluechtige interne
`A_RECENT`-Funktion qualifiziert; sie wird nach der Auswertung verworfen und
nicht an `B_STABLE` uebergeben. Gegen real gebildete visuelle `B_STABLE`-Slots
liess sie auf dem versiegelten Korpus `5/6` bekannte Holdouts zu und wies alle
`14` unbekannten, mehrdeutigen oder inkompatiblen Faelle ohne Fehlzulassung ab.
In einem rollenfreien Lebenszyklus enthielt derselbe Teilhinweis vor der
Erfahrung und wurde nach realer Stabilisierung kontrolliert aus `B_STABLE`
zugelassen; unbekannte und widerspruechliche Hinweise enthielten weiterhin.
Diese Zwei-Blick-/Formbefunde bleiben extern kalibrierte Versuche; sie sind
keine selbst erlernte allgemeine Anwendbarkeitshuelle der Minimalruntime.
S2-ME/S2-MI werden durch die auditive Regelanbindung nicht entsperrt.

## Aussagegrenzen

Nicht belegt sind semantisches Verstehen, automatische Erinnerungsauswahl,
offene Welt, allgemeine Langzeit-Memory, autonome Handlung oder Feldrueckwirkung
innerer Kontexte. Die Simulation ist als Quellenreferenz qualifiziert;
Quellengleichheit zwischen zwei realen digitalen oder physischen Quellen ist
noch nicht nachgewiesen.

## Dokumentation

- [Gemeinsames MCM-Feld](docs/architektur/024_GEMEINSAMES_MCM_FELD_ARCHITEKTUR.md)
- [Rezeptorvertrag und Dockgrenze](docs/architektur/025_REZEPTORVERTRAG_UND_DOCKGRENZE.md)
- [336-Werte-Memorybefund](docs/S2JX_DEFAULT_LIVE_MEMORY_FUNKTIONSBEFUND.md)
- [Rollenfreier Wahrnehmungsstrom](docs/S2LL_ROLLENFREIER_WAHRNEHMUNGSSTROM_PROZESSOR_VERTRAG.md)
- [Vorab versiegeltes AV-Korpus](docs/S2LS_VORAB_EINGEFRORENES_AV_TRAIN_HOLDOUT_KORPUS_VERTRAG.md)
- [Read-only Ursachenbefund](docs/S2LS_READONLY_URSACHENBEFUND.md)
- [Fluechtige A_RECENT-Zwei-Blick-Integration](docs/S2MA_FLUECHTIGE_A_RECENT_ZWEI_BLICK_INTEGRATION.md)
- [Zwei-Blick-Abruf gegen B_STABLE](docs/S2MB_BSTABLE_ZWEI_BLICK_KONTEXTABRUF.md)
- [Rollenfreier Lernlebenszyklus](docs/S2MC_ROLLENFREIER_LERNLEBENSZYKLUS_VERTRAG.md)

Historische Vertraege und Laufbelege bleiben unter `docs/` und `reports/`.
Die README ist eine kompakte Projektuebersicht, kein Forschungsjournal.

Vorarbeiten aus [MINI_DIO](https://github.com/H5Pro2/MINI_DIO) und der
[Mental-Core-Matrix](https://github.com/H5Pro2/Mental-Core-Matrix-MCM) sind
Forschungsreferenzen und gelten nicht automatisch als Evidenz dieses Projekts.
