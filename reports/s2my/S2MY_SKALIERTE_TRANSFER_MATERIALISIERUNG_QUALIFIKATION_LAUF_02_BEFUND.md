# S2-MY: Skalierte S2-MT-Materialisierungsqualifikation Lauf 02

## Entscheidung

Die fokussierte Einmalqualifikation unter der ID
`s2my-scaled-transfer-materialization-20260906-02` ist vollstaendig
bestanden.

Der prospektive, einheitlich skalierte S2-MT-Quellenplan ist fuer die
vollstaendige 28-Ereignis-Materialisierung und die bestehende
Geometrieprojektion technisch qualifiziert. Ein dritter Transferlauf wurde
nicht ausgefuehrt und benoetigt weiterhin eine getrennte Freigabe.

## Enge Fixturekorrektur

Gegenueber dem historischen `7/9`-Versuch wurden ausschliesslich zwei
Attributzugriffe in der Qualifikationsdatei korrigiert:

```text
field_input.frames -> field_input.timed_frames
```

Zusaetzlich wurde nur die Qualifikations-ID auf die neue Laufidentitaet
gesetzt. Produktcode, Quellenplan, Faktor, Payloads, Schwellen, Rezeptoren
und fachliche Fixtures blieben unveraendert.

## Vorbindungen

Vor dem Testaufruf galten folgende SHA-256-Quellhashes:

- S2-MT-Runner:
  `e2e5a2f0d7b1bff4231c4e88daf1fbac1431e19ed5e9ad34b97b8cb8dc5f9ec4`;
- skalierter Quellenplan:
  `56ac39b47e9df7cab424943a66636de80200c925035d4328521c90500dd92674`;
- korrigierte Qualifikation:
  `70248f622336fc0cbc1a66a586d7950b4b080863619dfe17c059eaa885c4f34d`;
- unveraenderter S2-MW-Ergebnisbeleg:
  `b1ca1ad9d11e29c6d5b547d166741f1afbf40fb3e8f240ea6eb07d3f4e7d87ef`.

## Einmalqualifikation

Genau ein Testaufruf wurde ausgefuehrt; es gab keinen Retry:

```text
python -m unittest -v tests.test_s2my_private_scaled_transfer_materialization
```

Ergebnis:

- `9/9` Tests bestanden;
- Exit-Code `0`;
- terminales `OK`;
- Laufzeit `3.418 s`;
- keine Memoryformation, kein Feldschritt und keine Runtimeausfuehrung;
- kein Hauptlauf.

Qualifiziert sind:

1. der neue prospektive Plan und seine unveraenderte Ereignisfolge;
2. exakt 28 skalierte Materialisate, davon 20 Vollereignisse und je vier
   auditive beziehungsweise visuelle Teilhinweise;
3. alle materialisierten auditiven Werte innerhalb der Kontakt-Normalform;
4. alle 78 aus `S2LOFieldInputV1.timed_frames` gewonnenen auditiven
   Rezeptpaardistanzen bitgleich zum gebundenen S2-MW-Beleg;
5. alle vier visuellen Cue-Quelldigestbindungen fuer `e22`, `e24`, `e26`
   und `e28`;
6. alle acht erwarteten auditiven und visuellen Cue-Treffermengen;
7. unveraenderte Fast-Grenzen `0,2` und Slow-Grenzen `0,02` beziehungsweise
   `0,01`;
8. `S2MT_GEOMETRY_MATERIALIZED` und der kanonische Geometriedigest;
9. geschlossenes und unverbrauchtes Hauptgate.

## Aussagegrenze

Die Qualifikation bestaetigt ausschliesslich Quellenplan,
Rezeptormaterialisierung und Geometrieprojektion. Sie ist kein Memory-,
Feld-, Runtime- oder Transferbefund. Der fruehere `7/9`-Versuch bleibt
unveraendert dokumentiert.

Ein dritter S2-MT-Transferlauf ist durch diesen Befund technisch
freigabefaehig, aber noch nicht ausgefuehrt oder autorisiert.
