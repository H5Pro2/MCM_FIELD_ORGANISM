# S1-WE: Private PPB-1-Lock- und Terminalrollen mit Temporaerabnahme

## Auftrag und Grenze

S1-WE implementiert genau die drei im S1-WA-Vertrag benannten Rollen:

```text
S1WAProductionLockMarker
S1WAProductionSuccessOutcome
S1WAProductionErrorOutcome
```

Die Namen bilden den spaeter vorgesehenen Vertrag ab. Die aktuelle
Konstruktion und Dateiwirkung ist dennoch ausschliesslich
`TEMPORARY_TEST_ONLY`. S1-WE instanziiert keine Produktionsautorisierung und
oeffnet keinen Produktionsablauf.

Ausgeschlossen bleiben:

- reale oder gerenderte Produktionsautorisierung;
- Produktionsartefaktwurzel und Produktionsentry;
- privater S1-VQ-Producer, Pipeline und Matrix;
- Feld-, Rezeptor- und Medienruntime;
- oeffentliche API oder Snapshotaenderung.

## Kanonische Rollen

Alle drei Typen binden Ausfuehrungs-ID, Autorisierungs- und
Ressourcengatedigest, den S1-WA-Vertrag, Kalibrierung, Plaene, kalibrierte
Quellen, `528` Faelle und maximal `75.808` registrierte Aufrufe.

Der Lock bindet zusaetzlich:

- `authorization_consumed = true` nur als synthetische H1-Fixturerolle;
- `retry_permitted = false`;
- einen kanonischen Markerdigest.

Der Erfolg bindet drei synthetische Resultatdigests, exakt `75.808`
akzeptierte Aufrufe, abgeschlossenen Einmallauf, ausgeschlossenen Retry und
ausgeschlossene Teilresultate.

Der Fehler bindet eine Stufe H2 bis H7, ihren exakten Vorgaenger, Fehlercode,
Fehlerdetaildigest und optional bekannte Aufrufzahl. Er enthaelt keine
Matrix-, Kompositions- oder Auswertungsresultate.

## Dateisystemverhalten

Akzeptiert wird nur ein existierendes Verzeichnis namens
`s1we-lock-terminal-fixtures` unter der Betriebssystem-Temporaerwurzel. Die
Produktionswurzel, gleichnamige Workspace-Verzeichnisse und falsch benannte
Temporaerverzeichnisse werden abgelehnt.

Der Lock wird mit exklusiver Neuerstellung geschrieben. Jede bereits belegte
Lock-, Erfolgs-, Fehler- oder Temporaerrolle stoppt vor einer Aenderung. Es
existiert bewusst keine Funktion zum Loeschen oder Umschreiben des Locks.

Ein Terminal setzt einen lesbaren, kanonisch unveraenderten und zum Ausgang
passenden Lock voraus. Der vollstaendige Terminalinhalt wird zuerst exklusiv
in derselben Wurzel geschrieben und synchronisiert. Die anschliessende
atomare Verschiebung besitzt kein Ersetzungsrecht. Dadurch kann bei
konkurrierender Publikation hoechstens ein Ausgang entstehen; ein vorhandener
Erfolg oder Fehler bleibt unveraendert.

## Abnahme

Die zwoelf neuen Tests bestaetigen:

- kanonische und deterministische Lock-, Erfolgs- und Fehlertypen;
- exklusiven Lock ohne Umschreiben;
- Blockade durch jede bereits belegte Artefaktrolle;
- atomaren Erfolg bei unveraendertem Lock;
- atomaren Fehler ohne Teilresultatrollen;
- Pflicht eines passenden und unveraenderten Locks;
- gegenseitigen Ausschluss von Erfolg und Fehler;
- No-Replace-Verhalten auch bei bereits vorhandenem Ziel;
- Ablehnung falscher Temporaer-, Workspace- und Produktionswurzeln;
- Fail-Closed fuer ungueltige synthetische Rollen;
- weiterhin gesperrten Produktionsentry und null Runtimeabhaengigkeiten;
- private API- und Snapshotneutralitaet.

Ergebnis:

```text
S1_WE_BOUND_PRIVATE_LOCK_SUCCESS_AND_ERROR_TYPES_IMPLEMENTED
S1_WE_TEMPORARY_TEST_ONLY_CONSTRUCTION_AND_PUBLICATION_ACCEPTED
S1_WE_EXCLUSIVE_DURABLE_LOCK_WITHOUT_DELETE_OR_REWRITE_ACCEPTED
S1_WE_ATOMIC_NO_REPLACE_TERMINAL_EXCLUSIVITY_ACCEPTED
S1_WE_PRODUCTION_AUTHORIZATION_PRODUCER_PATH_AND_ENTRY_BLOCKED
S1_WE_ZERO_MATRIX_FIELD_AND_MEDIA_CALLS
S1_WE_12_OF_12_NEW_TESTS_PASS
S1_WE_203_OF_203_CURRENT_FOCUSED_PPB1_TESTS_PASS
```

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-WF - statischer Post-S1-WD/S1-WE-Rollen- und Integrationspreflight
```

S1-WF darf nur Quelltext, Typfelder und Vertragsdigests lesen. Er muss exakt
trennen, welche technischen Rollen nun privat vorhanden und synthetisch
abgenommen sind und welche Produktionsbindungen weiterhin fehlen. Keine
Ressourcenabfrage, Dateisystemprobe, Autorisierung, Producer-, Matrix-, Feld-
oder Medienfunktion darf ausgefuehrt werden.

## Grundlagen

- [S1-WD temporaerer H0-Ressourcenbeobachter](S1WD_PPB1_PRIVATER_TEMPORAERER_H0_RESSOURCEN_UND_ATOMARITAETSBEOBACHTER.md)
- [S1-WA Produktionsbindungs- und Autorisierungsvertrag](S1WA_PPB1_STATISCHER_PRODUKTIONSBINDUNGS_RESSOURCEN_UND_AUTORISIERUNGSVERTRAG.md)
- [S1-VW synthetische Einmallauf-Handoffabnahme](S1VW_PPB1_PRIVATE_SYNTHETISCHE_EINMALLAUF_HANDOFF_UND_TERMINALHUELLEN_ABNAHME.md)
