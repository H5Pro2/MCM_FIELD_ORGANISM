# Lauf 187

## Forschungsfrage und Auftrag

Geprueft wurde, ob zwei unterschiedliche kontrollierte audiovisuelle
Vorgeschichten bei spaeter identischem audiovisuellem Holdout einen
reproduzierbaren und kausal dem schnellen Feldvorzustand zuordenbaren
Unterschied der spaeteren Feldaufnahme erzeugen.

Freigegeben waren sechs Kombinationen aus zwei Vorgeschichten und den
Operatoren `None`, `identity` und `zero`. Jede Kombination sollte mit frischem
Feld zweimal ausgefuehrt werden; der zweite Durchgang verwendete die
umgekehrte Armreihenfolge.

## Verwendete Quellen

- aktueller freigegebener Uebergabeauftrag;
- `AKTUELLER_FORSCHUNGSWEG.md`;
- `AGENTS.md`;
- `controlled_audio_video_test_world.py`;
- `audio_video_neutral_field_runtime.py`;
- `previous_state_contribution_hook.py`;
- vorhandene Tests der kontrollierten AV-Welt und des Vorzustands-Hooks.

Externe Quellen, Netzwerk, Kamera, Mikrofon und oeffentliche Medien wurden
nicht verwendet.

## Verwendete Dateien und Schnittstellen

- `controlled_history_holdout_world_family()`;
- `_scheduled_phase_sequences()`;
- `_advance_captured_audio_video_sequences()`;
- `apply_previous_state_operator()` als private Intervention unmittelbar vor
  dem Holdout;
- `tools/run_controlled_av_previous_state_probe.py`;
- Ergebnisartefakt
  `reports/controlled_av_previous_state_probe_lauf_187.json`.

Der Produktionspfad wurde nicht um einen Operator erweitert. Die Intervention
blieb auf den privaten Forschungsadapter begrenzt.

## Durchgefuehrte Schritte

1. Der private Operator wurde mit fuenf fokussierten Tests geprueft. Alle
   Tests bestanden.
2. Das vorbenannte Ergebnisartefakt war vor dem Lauf nicht vorhanden.
3. Zwei Startversuche endeten vor einer Feldoperation: einmal vor dem
   Projektimport, einmal beim Lesen eines falsch benannten reinen
   Sequenzmetadatenfelds. Beide erzeugten kein Ergebnisartefakt und keinen
   abgeschlossenen Arm.
4. Nach Korrektur des Metadatenzugriffs berechnete der begrenzte Unterprozess
   alle zwoelf Arme und wertete die festgelegten Kontrollen aus.
5. Der Prozess stoppte bei der Kontrollentscheidung. Es wurde keine
   ergebnisabhaengige Aenderung der Arme, Schwellen oder Hypothese vorgenommen
   und keine Wiederholung des Effektlaufs gestartet.

## Beobachtete Messung und Gegenbaselines

```text
arm_count_completed_before_control_evaluation: 12
holdout_receptor_sequences_exactly_equal:       false
none_identity_exactly_equal:                    true
reverse_order_repetition_exactly_equal:         true
zero_same_changed_exactly_equal:                false
none_same_changed_different:                    true
decision:                                       TECHNICALLY_UNDECIDABLE
```

Die `identity`-Gegenbaseline war bitgleich zu `None`. Die Wiederholung in
umgekehrter Ausfuehrungsreihenfolge war ebenfalls bitgleich. Die zwingende
Eingangskontrolle scheiterte jedoch: Die reduzierten Holdout-Rezeptorfolgen
beider Vorgeschichten waren nicht exakt gleich. Entsprechend konnte auch die
`zero`-Gegenbaseline nicht zusammenfallen.

Der Unterprozess lag innerhalb des gesetzten 60-Sekunden-Zeitlimits. Das
vollstaendige Ergebnisartefakt wurde wegen des Kontrollfehlers nicht vom
Runner geschrieben; deshalb sind keine numerischen `L2`-/`Linf`-Kontraste als
persistierte Messung verfuegbar. Das nachtraeglich angelegte Abbruchartefakt
enthaelt ausschliesslich die vom Prozess ausgegebenen Kontrollwerte.

## Technische Interpretation

Die kontrollierten Rohmedien des letzten Weltabschnitts sind laut bestehendem
Welttest identisch. Der auditive Rezeptor ist jedoch zustandsbehaftet und wird
im bisherigen Phasenlauf ueber die jeweilige Vorgeschichte fortgefuehrt.
Damit kann dieselbe spaetere Rohquelle unterschiedliche reduzierte
Rezeptorfolgen erzeugen. Lauf 187 trennt diese Rezeptorvorgeschichte nicht von
der Feldvorgeschichte.

Die Unterschiede im `None`-Arm koennen daher nicht kausal allein dem schnellen
Feldvorzustand zugeordnet werden. Das fehlende Zusammenfallen der `zero`-Arme
ist mit den ungleichen aktuellen reduzierten Eingaben vereinbar.

## Grenzen, Nichtnachweise und offene Annahmen

- Kein kausal isolierter schneller Vorzustandsbeitrag wurde nachgewiesen.
- Kein Nullbefund zum schnellen Vorzustandsbeitrag wurde nachgewiesen.
- Nicht geprueft wurde, ob bei einer einzigen, fuer beide Vorgeschichten
  wiederverwendeten reduzierten Holdout-Sequenz die `zero`-Arme zusammenfallen.
- Thread- und Handlewerte des abgeschlossenen Fehlers wurden wegen des
  Kontrollabbruchs nicht persistiert.
- Kein Befund zu Memory, Organisation, Topologie, Bedeutung, Semantik,
  Bewusstsein, Eigenstaendigkeit oder KI.

## Konkrete Schlussfolgerung

Lauf 187 ist technisch unentscheidbar. Reproduzierbarkeit und
Reihenfolgeunabhaengigkeit waren gegeben, aber der erforderliche identische
aktuelle Rezeptoreingang war nicht gegeben. Der Lauf darf weder positiv noch
negativ als Evidenz fuer einen schnellen Feldvorzustandsbeitrag verwendet
werden.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Der kleinste naechste Lauf soll den Holdout genau einmal mit einem frischen
Audio- und Videorezeptor in eine feste reduzierte AV-Sequenz ueberfuehren und
diese bytegleiche Sequenz unveraendert an beide bereits getrennt aufgebauten
Feldvorgeschichten uebergeben. Die sechs Operatorarme und die umgekehrte
Wiederholungsreihenfolge bleiben unveraendert. Vor jeder Feldmessung muss der
Digest dieser einen Holdout-Sequenz in allen Armen gleich sein.

Erst dieser korrigierte Lauf kann entscheiden, ob ein Unterschied nach
identischem aktuellem Rezeptoreingang durch `zero` verschwindet. Vor einer
Ausfuehrung ist dieser einzelne Korrekturlauf der statischen Gegenpruefung zur
Entscheidung vorzulegen.
