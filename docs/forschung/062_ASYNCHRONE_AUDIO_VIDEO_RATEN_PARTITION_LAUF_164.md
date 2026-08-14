# Lauf 164: Asynchrone Audio-Video-Raten und Zeitpartitionen

## Forschungsfrage und Auftrag

Untersucht wurde die in Forschung 030 benannte Luecke: Bleibt die aktuelle
synthetische Audio-Video-Feldantwort bei unterschiedlichen nativen Raten,
grober oder feiner Zeitteilung und vertauschter Sequenzdeklaration erhalten?

## Verwendete Quellen

Tatsaechlich verwendet wurden ausschliesslich der aktuelle freigegebene
Uebergabeeingang, `AGENTS.md`, Forschung 030 und 061 sowie:

- `audio_video_neutral_field_runtime.py`;
- `asynchronous_receptor_events.py`;
- `asynchronous_audio_video_partition_probe.py`;
- `controlled_audio_video_test_world.py`;
- die vorhandenen asynchronen Tests und Runner.

Externe Quellen und Projektdatenbanken wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Neu angelegt wurden:

- `mcm_field_organism/asynchronous_audio_video_rate_probe.py`;
- `tests/test_asynchronous_audio_video_rate_probe.py`;
- `tools/run_asynchronous_audio_video_rate_probe.py`;
- dieser Bericht.

Die vorhandene Partitionierungsprobe wurde um explizite Ratenparameter und
Layer-/Snapshot-Digests erweitert. Die Feldmechanik blieb unveraendert.

## Durchgefuehrte Schritte

Vorab festgelegt wurden die Ratepaare `50/5`, `100/10` und `200/20` Hz fuer
Audio/Video. Je Ratepaar wurden frisch ausgefuehrt:

- ein grober Zeitschritt ueber den gesamten Horizont;
- verlustfreie feine Teilung an allen Abschlusszeitpunkten;
- frische Reproduktion der feinen Teilung;
- feine Teilung mit vertauschter Sequenzdeklaration.

Gemessen wurden Aktivierung, `afterimage`, Layer-Digest, Snapshot-Digest,
Ereigniszahl, Teilungsschritte und Determinismus.

## Messergebnisse und Gegenbaselines

```text
Audio/Video  Ereignisse  feine Schritte  activation L-inf  afterimage L-inf
50/5 Hz      51          46              2.0903e-15        2.4156e-15
100/10 Hz   101          91              4.6352e-15        4.6144e-15
200/20 Hz   201         182              9.7145e-15        1.0976e-14
```

Fuer alle drei Ratepaare galt:

```text
frische Reproduktion exakt:                 ja
vertauschte Sequenzdeklaration Layer-gleich: ja
grob/fein Aktivierung bitgleich:             nein
grob/fein afterimage bitgleich:              nein
grob/fein Layer-Digest gleich:               nein
grob/fein Snapshot-Digest gleich:            nein
```

Der kombinierte Test der neuen und bestehenden Partitionierungsprobe ergab:

```text
6 passed
```

## Einordnung

**Beobachtetes Ergebnis:** Grobe und feine Teilung liefern nicht bitgleiche
Vektoren. Die maximalen Unterschiede liegen zwischen `2.1e-15` und
`1.1e-14`. Frische Reproduktion und vertauschte Deklarationsreihenfolge sind
exakt invariant.

**Technische Interpretation:** Die grob/fein-Abweichung waechst mit der Zahl
der Integrationsschritte und liegt im Bereich der Gleitkomma-Summation. Die
Digest-Abweichung folgt daraus, dass Digests die exakten Floatwerte und bei
Snapshots zusaetzlich technische Zeit- und Verteilungsmetadaten abbilden.

**Nicht beobachtet:** Es gibt keine nichtdeterministische Abweichung und
keine Wirkung der Sequenzdeklarationsreihenfolge.

## Grenzen und nicht gepruefte Annahmen

- Verschiedene native Raten erzeugen verschieden viele Rezeptorzustaende;
  ihre Endvektoren sind daher keine bitidentische Quellenpayload-Baseline.
- Numerische Aequivalenz wurde aus Fehlergroesse und Schrittzahl abgeleitet,
  nicht durch alternative Praezisionsarithmetik bewiesen.
- Keine Geraete, Medien, Browser oder Streams wurden verwendet.
- Keine Memory-, Bedeutungs-, Organisations- oder Topologieauswertung wurde
  vorgenommen.

Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Die asynchrone Runtime ist gegen frische Wiederholung und vertauschte
Sequenzdeklaration exakt stabil. Grobe und feine Zeitteilung sind numerisch
bis maximal `1.1e-14`, aber nicht bitweise oder digestseitig gleich. Die
beobachtete Abweichung ist durch vorhandene Gleitkommanumerik und technische
Partitionierung erklaerbar und begruendet keine neue Feld- oder
Memory-Mechanik.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Vor realen Langzeitgeraetelaeufen sollte ein letzter technischer
Praezisionskontrolllauf die grob/fein-Abweichung gegen eine feste
hochpraezise oder analytisch komponentenweise Summationsbaseline pruefen.
Ziel ist nur, die `1e-14`-Abweichung eindeutig der Summationsreihenfolge
zuzuordnen. Neue Feldmechanik, Geraete und Memory-Auswertung bleiben
ausgeschlossen.
