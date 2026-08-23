# S1-WL: Privater PPB-1-Autorisierungsvalidatoradapter

## Auftrag und Grenze

S1-WL implementiert einen reinen Validator fuer bereits injizierten
Autorisierungstext und bereits gebundene Digestrollen. Er erzeugt keine
Produktionsautorisierung und liest den Text aus keiner Datei oder externen
Quelle.

Nicht ausgefuehrt werden:

- Instanziierung von `S1WAProductionAuthorization`;
- Pruefung oder Reservierung einer realen Ausfuehrungs-ID;
- Verbrauch oder Speicherung einer Freigabe;
- Datei-, Betriebssystem- oder Ressourcenoperation;
- Lock-, Terminal-, Producer- oder Matrixfunktion;
- Feld-, Rezeptor- oder Medienruntime.

## Reine Text- und Digestpruefung

Das unveraenderliche Receipt bindet:

- Format der injizierten Ausfuehrungs-ID;
- SHA-256-Digest des injizierten Textes, nicht den Text selbst;
- exakte Uebereinstimmung mit der gebundenen Textvorlage;
- Vertrags-, Kalibrierungs- und Ressourcengatedigest;
- Parent- und korrigierten Plandigest;
- Fallzahl, maximales Aufrufbudget und privaten Entrybezeichner;
- null Frischepruefungen, Autorisierungsinstanziierungen und Runtimewirkungen.

`ok weiter`, ein zusaetzliches Leerzeichen, eine abweichende Ausfuehrungs-ID
oder Digestdrift lassen die jeweilige Pruefung fail-closed scheitern.

## H0D-Testadapter

Aus dem Receipt kann ein privater S1-WH-H0D-Testadapter entstehen. Dessen
`passed`-Rolle bedeutet ausschliesslich, dass injizierter Text, ID-Format und
Digestrollen uebereinstimmen. Sie bedeutet nicht, dass die ID frisch ist,
dass eine Freigabe verbraucht wurde oder dass Produktion autorisiert ist.

Deshalb bleibt immer gebunden:

```text
production_authorization_instantiated = false
ready_for_production_authorization = false
authorization_instantiation_count = 0
execution_id_freshness_check_count = 0
```

Der Produktionsblocker
`PRODUCTION_AUTHORIZATION_INSTANTIATION_LOCKED` ist damit nicht geschlossen.

## Abnahme

Die zwoelf neuen Tests bestaetigen exakte Text- und Digestbindung,
deterministisches Receipt, getrennte Abweisung von allgemeinem Befehl,
Textdrift, ID-Abweichung, ID-Formatfehler und vier Digestrollen, einen rein
synthetischen H0D-Adapter, acht Nullzaehler, gesperrten Produktionseinstieg
sowie private API- und Snapshotneutralitaet.

S1-WL-Quellcodedigest:

```text
a61d4bfe66e2195f24f022c95b8d70c7aa5909dec94e0815f67351215718e857
```

Kanonischer Testreceiptdigest:

```text
ac2ac30f22d1772cd612d85b85f528b21e5cbfd4b3834e0b1098d2f46780da7c
```

Zusammen bestehen `276 von 276` aktuelle fokussierte PPB-1-Tests.

## Genau ein naechster Schritt

S1-WM auditiert S1-WL ausschliesslich statisch: Quellcodedigest,
Receiptfelder, exakte Text- und Digestbindung, H0D-Testbruecke,
Runtimefreiheit und weiterhin gesperrte Produktionsautorisierung. Keine
S1-WL-, S1-WH- oder Produktionsfunktion darf dabei ausgefuehrt werden.

## Grundlagen

- [S1-WK statischer Root-/Ressourcenadapterpreflight](S1WK_PPB1_STATISCHER_ROOT_RESSOURCENADAPTER_PREFLIGHT.md)
- [S1-WG statischer Integrationsdelta-Vertrag](S1WG_PPB1_STATISCHER_PRODUKTIONSINTEGRATIONSDELTA_VERTRAG.md)
- [S1-WA Produktionsbindungs- und Autorisierungsvertrag](S1WA_PPB1_STATISCHER_PRODUKTIONSBINDUNGS_RESSOURCEN_UND_AUTORISIERUNGSVERTRAG.md)
