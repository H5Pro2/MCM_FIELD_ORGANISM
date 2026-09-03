# S2-KI - TwoAreaPerceptualContext336

## Status und Zweck

`S2KI_STATIC_TWO_AREA_MODAL_CONTEXT_336_CONTRACT_COMPLETE`

S2-KI bindet eine kleine unveraenderliche read-only Kontextansicht fuer das
qualifizierte Default-Live-Profil mit `48` auditiven und `288` visuellen
Rezeptorwerten. Die Ansicht ist keine neue Memorymechanik und erzeugt keine
Entscheidung ueber die Verwendung eines Kontextes.

Grundlage ist Commit
`55d1b1a358ff7103a31eec8f31142ff0e25aef7e`.

| Quelle | SHA-256 |
| --- | --- |
| 336-Werte-read-only-Adapter | `efd3dad03810811acc3fc124543bf8aa524ad1de4585210f2852f7048dbf93e7` |
| atomarer 336-Werte-Koordinator | `c9676ea9a740bfb82d66a91c00c559d1ff4d3759bd7bfed12c55afb9820dea81` |
| bestehende Zwei-Bereich-Referenz | `21bc206dc37f8a9f477c02eac7d14ff22e6924bbdb54eb5153122ec296cdd587` |
| S2-KH-Befund | `dab63e6cec9cfd6c5d3f8ab762ebd4a352c2524945a7086b550a2b20e0ed1d67` |
| unveraenderter S2-KG-Primaerbeleg | `f780b44dc366212e0d076b66545df8b1d02db124673a32fa5bff81ddc7e062c8` |

## Architekturgrenze

```text
TwoAreaPerceptualContext336
  A_RECENT
    B4_RECENT       interner AV-Befund
    TSPM_FAST       interner AV-Befund
  B_STABLE
    AUDITORY        stabiler 48-Werte-Kandidat oder ABSENT_VALID
    VISUAL          stabiler 288-Werte-Kandidat oder ABSENT_VALID
```

`B4_RECENT` und `TSPM_FAST` bleiben interne Rollen desselben logischen
Bereichs `A_RECENT`. Sie werden weder zu einer dritten Memoryebene noch
automatisch miteinander verschmolzen. Abweichende interne A-Befunde bleiben
getrennt sichtbar; es gibt keine Prioritaet und keinen Fallback.

## Einziger Eingang

Die reine Projektion akzeptiert exakt einen bereits validierten
`ValidatedPerceptualFinding336V1`. Dieser entsteht prospektiv am bestehenden
read-only Probeweg und enthaelt:

- `config_digest`, `composite_state_digest`, `probe_digest` und
  `source_digest`;
- getrennte auditive und visuelle Quelldigests sowie Geometrie- und
  Zeitbindung;
- identische `prestate_digest` und `poststate_digest`;
- den Digest des bestehenden `S2JVReadOnlyFindingV1`;
- je einen typisierten Rollenbefund fuer `B4_RECENT`, `TSPM_FAST`,
  `B_STABLE_AUDITORY` und `B_STABLE_VISUAL`;
- den gebundenen 336-Werte-Probedigest und ein endliches Ressourcenledger.

Der bestehende `S2JVReadOnlyFindingV1` enthaelt ausgewaehlte Slot-, Distanz-
und Zustandsbelege, aber keine Kandidatenwerte. Deshalb darf die neue
Eingangsform die Werte nur waehrend desselben validierten read-only
Probevorgangs aus dem bereits geprueften Zustand uebernehmen. Eine spaetere
Rekonstruktion aus Slot-, Ergebnis- oder Erwartungsdigests ist verboten.

Nach Bildung dieses Eingangs darf die Kontextprojektion keine Memory-,
Rezeptor-, Koordinator-, Kontextauswahl- oder Feldfunktion aufrufen.

## Unveraenderliche Datenformen

### RoleFinding336V1

Jeder Rollenbefund bindet:

```text
role
status = AVAILABLE | ABSENT_VALID
absence_reason | candidate
observed_state_digest
probe_digest
source_finding_digest
finding_digest
```

Ein `AVAILABLE`-Befund besitzt genau einen Kandidaten. `ABSENT_VALID`
besitzt keinen Kandidaten und genau einen neutralen Grund aus:

```text
NO_OCCUPIED_SOURCE
NO_FUNCTIONAL_MATCH
NO_STABLE_MATCH
```

Fehlende, beschaedigte oder widerspruechliche Evidenz ist niemals
`ABSENT_VALID`.

### AVContextCandidate336V1

Die internen A-Rollen verwenden je einen AV-Kandidaten mit:

- exakt `48` auditiven und `288` visuellen Werten im Rezeptorbereich
  `0.0...1.0`;
- getrennten Wertedigests und einem gemeinsamen AV-Wertedigest;
- Slot-ID und Slotdigest;
- B4-Bildungsindex beziehungsweise Fast-Support und letzten Auswahlschritt;
- getrennten auditiven und visuellen Distanzen;
- `mechanical_match = true`;
- Quellen-, Probe- und Zustandsbindung.

Die beiden A-Kandidaten duerfen inhaltlich gleich oder verschieden sein.
Gleiche Inhalte werden nicht verschmolzen, verschiedene nicht aufgeloest.

### StableModalityCandidate336V1

Die B-Rollen verwenden getrennte Kandidaten:

```text
B_STABLE_AUDITORY: modality=AUDITORY, dimension=48
B_STABLE_VISUAL:   modality=VISUAL,   dimension=288
```

Jeder Kandidat bindet Werte, Wertedigest, Slot-ID, Slotdigest, Support,
Stabilitaet, native Distanz, Probe-, Quellen- und Zustandsdigest. Zulaessig
ist nur `stable = true`, `support >= 3` und `mechanical_match = true`.

### TwoAreaPerceptualContext336

Das Ausgabeobjekt bindet in kanonischer Reihenfolge:

```text
schema
contract_digest
input_finding_digest
config_digest
composite_state_digest
probe_digest
source_digest
A_RECENT
B_STABLE
B_stability_status
context_presence
resource_ledger_digest
prestate_digest
poststate_digest
automatic_selection = null
bundle_digest
```

`B_stability_status` besitzt genau vier deskriptive Werte:

```text
AUDITORY_AND_VISUAL_STABLE
AUDITORY_STABLE_ONLY
VISUAL_STABLE_ONLY
NO_STABLE_CONTEXT
```

`context_presence = NO_CONTEXT` ist nur zulaessig, wenn beide A-Rollen und
beide B-Modalitaeten `ABSENT_VALID` sind. Ein
`B_STABLE_AUDITORY`-Befund mit Grund `NO_FUNCTIONAL_MATCH` darf als
`AUDITORY_NO_MATCH` dargestellt werden, erzeugt allein aber niemals
`NO_CONTEXT`.

## Projektion

Die Projektion besitzt exakt sechs logische, rein lokale Schritte:

1. Eingang, Quellenrelation und Read-only-Gleichheit validieren.
2. `B4_RECENT` nach `A_RECENT` projizieren.
3. `TSPM_FAST` getrennt nach `A_RECENT` projizieren.
4. den auditiven Slow-Befund nach `B_STABLE.AUDITORY` projizieren.
5. den visuellen Slow-Befund nach `B_STABLE.VISUAL` projizieren.
6. Status, Ledger und finalen Bundledigest bilden und den Eingangsdigest
   erneut unveraendert bestaetigen.

Die Reihenfolge ist nur kanonisch. Sie ist keine Rangfolge. Es entstehen
keine Gesamtentscheidung, keine gemeinsame AV-Slow-Erinnerung und kein
Feldinput.

## Ressourcenbindung

Pro Projektion gelten folgende harte Obergrenzen:

| Ressource | Maximum |
| --- | ---: |
| validierte Eingangsfindings | 1 |
| Rollenbefunde | 4 |
| Kandidaten | 4 |
| referenzierte Rezeptorwerte | 1.008 |
| logische Projektionsschritte | 6 |
| neu gebildete Digests | 9 |
| serialisierte kanonische Ausgabe | 65.536 Byte |

Die `1.008` Werte sind das Maximum aus zwei internen AV-Kandidaten
`2 x 336` sowie einem auditiven und einem visuellen Slow-Kandidaten
`48 + 288`. Roh-RGB-, PCM-, Feld- oder Memoryzustandsobjekte duerfen nicht
in Eingang oder Ausgabe serialisiert werden.

## Fail-Closed-Regeln

Ohne Ausgabe abzubrechen ist bei:

- falschem Typ, Schema oder Profil sowie Dimensionen ungleich `48/288`;
- ungueltigem, fremdem oder widerspruechlichem Quellen-, Probe-,
  Konfigurations- oder Zustandsdigest;
- ungleichen Vor-/Nachzustandsdigests;
- doppelter, fehlender oder falsch zugeordneter Rolle;
- Kandidat bei `ABSENT_VALID` oder fehlendem Kandidaten bei `AVAILABLE`;
- instabilem beziehungsweise nicht passendem B-Kandidaten;
- nachtraeglicher Werterekonstruktion oder ungebundener Wertquelle;
- Kapazitaets-, Operations-, Digest- oder Byteueberschreitung;
- irgendeinem Versuch einer Auswahl, Verschmelzung oder Feldwirkung.

Gueltige Abwesenheit bleibt ein regulaerer Rollenbefund. Beschaedigte
Evidenz erzeugt dagegen weder Teilbundle noch Abwesenheitsstatus.

## Gebundene S2-KG-Abbildung

Die spaetere neutrale Qualifikation muss mindestens diese beiden bereits
belegten Formen ohne Verwendung ihrer fachlichen Labels nachbilden:

```text
H final:
  A_RECENT.B4_RECENT       = ABSENT_VALID
  A_RECENT.TSPM_FAST       = ABSENT_VALID
  B_STABLE.AUDITORY        = AVAILABLE, Support 3
  B_STABLE.VISUAL          = AVAILABLE, Support 3
  B_stability_status       = AUDITORY_AND_VISUAL_STABLE

N final:
  A_RECENT.B4_RECENT       = ABSENT_VALID
  A_RECENT.TSPM_FAST       = ABSENT_VALID
  B_STABLE.AUDITORY        = ABSENT_VALID / AUDITORY_NO_MATCH
  B_STABLE.VISUAL          = AVAILABLE, Support 3
  B_stability_status       = VISUAL_STABLE_ONLY
  context_presence         != NO_CONTEXT
```

Diese Abbildung korrigiert S2-KG nicht und erzeugt keinen neuen
Memorybefund. Sie prueft spaeter nur, dass eine modalitaetsgetrennte
Kontextansicht den vorhandenen Zustand wahrheitsgemaess darstellen kann.

## Falsifikation und Aussagegrenze

Die Projektionshypothese ist falsifiziert, wenn ein gueltiger
336-Werte-Befund nicht ohne Informationsverlust in die vier Rollen
abgebildet werden kann oder wenn H/N nur durch Verschmelzung, Priorisierung
oder erfundene Abwesenheit die gebundenen Statusformen erreichen.

Ein Bestehen bestaetigt ausschliesslich eine transparente, unveraenderliche
Kontextdarstellung. Es bestaetigt weder Kontextnutzen noch automatische
Auswahl, Semantik, Lernen, Feldrueckwirkung oder eine neue Memoryebene.
Nach diesem Vertrag duerfen die private Eingangsbindung, Projektion und
fokussierte neutrale Tests unmittelbar und ohne neue Infrastrukturkaskade
implementiert werden.
