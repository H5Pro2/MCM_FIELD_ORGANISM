# S2-MT: Transferlauf 05

## Entscheidung

Der einmalige Lauf `s2mt-presealed-transfer-runtime-20260906-05` ist
technisch unabhaengig verifiziert: `RECORDING_COMPLETE`.
Die vorgebundene fachliche Gesamtvorhersage ist `S2MT_FUNCTION_FALSIFIED`.
Es handelt sich um einen auswertbaren Funktionsbefund.

Die erwarteten auditiven Hypothesen fuer A und B fehlen bei e21/e23.
Beide Hinweise enden mit `ABSTAIN_INTERNAL_AMBIGUITY`. Die sechs anderen
Hypothese-/Enthaltungsentscheidungen entsprechen ihrer Vorhersage.
Es gab genau einen Hauptaufruf, genau eine anschliessende read-only
Verifikation, keinen Retry und keinen Parameterwechsel.

## Vorbindung und Ausfuehrung

- Quellcommit: `bb450a955a432cddc7e782130bce409540270d4b`.
- Ausschliesslich die autorisierte Lauf-ID wurde in Runner und Verifikator
  von Lauf 04 auf Lauf 05 geaendert.
- Das neue Ergebnisverzeichnis existierte vor dem Hauptaufruf nicht.
- Skalierungsfaktor: `0.989912331104279`, unveraendert.
- Skalierter Plandigest:
  `3b749837273f9cfb1af4ac50659881c48a4a113384d65999dc90e922b46fd26c`.
- Quellenplanmodul-SHA-256:
  `56ac39b47e9df7cab424943a66636de80200c925035d4328521c90500dd92674`.
- S2-MR-Runtime-SHA-256:
  `da7699b6ef2a17c3b241f257a8aa9c954439e8a2b5cc37dab2a372a7691cf49f`.
- Runner-SHA-256:
  `8f9690e566af9b8a783cf0aaba3c50aa857a34370b5b0f7ce278e32b3716d383`.
- Verifikator-SHA-256:
  `e26ffe7d7538796b58663b64c625732f8556b3debc2ab9c423d60379efadfc32`.

Alle 14 gebundenen Quellhashes waren vor und nach dem Hauptlauf identisch.
Der Hauptaufruf endete mit Exit-Code `0`; das Gate war danach `False`,
der Einmalverbrauch `True`. Der Lauf verwendete CPython `3.14.4`, Windows x64.

Aufgerufen wurde genau einmal:

```python
runner.run_main_once(
    workspace_root=root,
    output_root=root / "reports/s2mt",
    run_id="s2mt-presealed-transfer-runtime-20260906-05",
)
```

Das Gate wurde nur fuer diesen Aufruf im Prozess geoeffnet. Die vollstaendige
Hashbindung und die Prozessausgabe stehen in
`s2mt-presealed-transfer-runtime-20260906-05/main_call.txt`.

## Technischer Abschluss

- 28 vollstaendige Runtimeereignisse, 20 erfolgreiche Formationen.
- Acht spaetere Teilhinweise; jeweils `READ_ONLY_UNCHANGED`.
- 28 erfolgreiche Feldzweige, `8064` gebundene Feldkontakte.
- Keine Runtimefehlercodes.
- Beide Slow-Banken mit Supportinventar `[2, 3, 3]`.
- A, B und C aus `A_RECENT` verdraengt.
- Runtime nach `close()` geschlossen; Schlusszustand konsistent.
- Keine Hypothesenanwendung und keine Vervollstaendigung.

Der atomare Ergebnisbeleg besitzt `149416` Byte und bindet:

- Record-Digest:
  `d450a63eed0fde352f7e9d4e82132f56a7af68203ae835ff0407f762b490fafd`.
- Datei-SHA-256:
  `2de06dfc17728fd1c9aa7793e616e5a530cbf716306431117ce9dce4325d886f`.

Anschliessend wurde `verify_result_file(result_path, workspace_root)` genau
einmal in einem getrennten Python-Prozess aufgerufen. Exit-Code `0`,
`verification_status = RECORDING_COMPLETE`, `read_only = True`.
Der Ergebnisdateihash blieb vor und nach der Verifikation identisch.
Verifikationsdigest:
`fa7d4ddfb5aa8b90cf886ea1fbccda5fd478212ed5627fdabb10ee9b5920990d`.
Die Ausgabe steht in
`s2mt-presealed-transfer-runtime-20260906-05/verification_call.txt`.

## Fachliche Auswertung

Erst nach erfolgreicher Verifikation wird die aufgezeichnete Evaluation
uebernommen. Rollen in der folgenden Tabelle sind Auswerterrollen.

| Ereignis | Rolle | Modalitaet | Erwartung | Beobachtung | Vorhersage |
| --- | --- | --- | --- | --- | --- |
| e21 | A | Audio | Hypothese | `ABSTAIN_INTERNAL_AMBIGUITY` | abweichend |
| e22 | A | Video | Hypothese | `B_STABLE`-Hypothese | erfuellt |
| e23 | B | Audio | Hypothese | `ABSTAIN_INTERNAL_AMBIGUITY` | abweichend |
| e24 | B | Video | Hypothese | `B_STABLE`-Hypothese | erfuellt |
| e25 | C | Audio | Enthaltung | `ABSTAIN_INTERNAL_AMBIGUITY` | erfuellt |
| e26 | C | Video | Enthaltung | `ABSTAIN_NO_APPLICABLE_CONTEXT` | erfuellt |
| e27 | unbekannt | Audio | Enthaltung | `ABSTAIN_INTERNAL_AMBIGUITY` | erfuellt |
| e28 | unbekannt | Video | Enthaltung | `ABSTAIN_NO_APPLICABLE_CONTEXT` | erfuellt |

Die Stabilisierung und Verdraengung sind im aufgezeichneten Inventar
nachvollziehbar: In beiden Slow-Banken besitzen Slot 000/001 Support 3,
Slot 002 Support 2. B4 enthaelt nur Formationen 12 bis 20; Fast enthaelt
zuletzt ausgewaehlte Schritte 18 bis 20. Der Auswerter bestaetigt die
Abwesenheit der drei Lerninhalte n00/n01/n02 aus A_RECENT.

Damit ist die gesamte auditive/visuelle Transferprognose falsifiziert,
obwohl Bildung, Feldkontakt, Lifecycle und visuelle Hypothesenausgabe
funktionieren. Alle vier auditiven Hinweise enthalten sich wegen interner
Mehrdeutigkeit. Fuer C und den unbekannten Inhalt erfuellt dies die
vorgebundene Enthaltungserwartung; es belegt keine spezifische auditive
Erkennung ihrer Instabilitaet beziehungsweise Unbekanntheit.

Der Record lokalisiert die Funktionsabweichung auf die auditive
Hypothesenausgabe. Welche konkreten Slot-Treffermengen die Mehrdeutigkeit
verursachen, wird mit diesem Bericht nicht neu diagnostiziert.
Schwellen, Quellen und fachliche Bewertung wurden nicht nachgebessert.

## Historische Integritaet und Grenze

Lauf 04 bleibt dauerhaft `NOT_EVALUABLE`, mit unveraendertem Datei-SHA-256
`a5c16ef89e7059cd358f82fc25422607b5405572d21a86b18b4f80c90d3e11c5`.
Er wurde nicht erneut verifiziert oder bewertet. Die anderen historischen
Laeufe wurden ebenfalls nicht veraendert.

S2-MS bleibt der bestehende Reproduktionsbefund. Lauf 05 liefert einen
gemischten Transferbefund mit formal falsifizierter Gesamtvorhersage,
keinen technischen Abbruch. Ein weiterer Hauptlauf ist nicht ausgefuehrt.
