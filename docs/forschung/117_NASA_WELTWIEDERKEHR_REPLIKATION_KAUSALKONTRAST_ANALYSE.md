# NASA-Weltwiederkehr: technische Analyse der vorregistrierten Kausalkontraste

## Analysegrenze

Diese Analyse verwendet ausschließlich den Ergebnisvertrag des einmaligen Laufs aus Dokument 116 und die vier vorregistrierten Kontrollfragen. Sie definiert keine nachträgliche Schwelle und erhebt keinen Memory-, Bedeutungs-, Organisations- oder KI-Claim.

Alle sechs Arme begannen mit demselben Stufe-eins-Snapshot. Damit ist die technische Ausgangsgleichheit innerhalb dieses Laufs dokumentiert.

## 1. Vollzustand gegen frische Stufe zwei

`return.continued.full_state` gegen `return.fresh_stage_two`:

```text
activation_linf: 0.017293651956615398
afterimage_linf: 0.017580295681599252
layer_digest_equal: false
snapshot_digest_equal: false
```

Die spätere technische Feldantwort ist unter Vollzustandsfortsetzung und frischem Feld nicht gleich. Dieser Kontrast belegt keine Erinnerung; er zeigt nur Zustandsabhängigkeit der implementierten Dynamik.

## 2. Aktivierungs- und Nachhallkomponenten

`control.activation_only_carry` gegen `control.afterimage_only_carry`:

```text
activation_linf: 0.017293651956615398
afterimage_linf: 0.010867382684156419
layer_digest_equal: false
snapshot_digest_equal: false
```

Zusätzliche komponentenspezifische Abgrenzungen:

```text
full_state vs activation_only:
  activation_linf: 0.0
  afterimage_linf: 0.003527301811182163

fresh_stage_two vs afterimage_only:
  activation_linf: 0.0
  afterimage_linf: 0.0035273018111821545
```

Damit sind die Aktivierungsvektoren in diesen beiden Paaren jeweils gleich, während Nachhall und Digests verschieden sind. Der Befund ist daher komponentenspezifisch und darf nicht als vollständige Verschiedenheit aller Messgrößen formuliert werden.

## 3. Gleiche Sequenz gegen Rangpermutation

`return.continued.full_state` gegen `control.stage_two_order_permuted`:

```text
activation_linf: 0.012491996276939484
afterimage_linf: 0.009650827900181767
layer_digest_equal: false
snapshot_digest_equal: false
```

Bei gleichem Stufe-eins-Ausgang und vollständiger Zustandsfortsetzung unterscheidet sich die technische Stufe-zwei-Antwort zwischen Originalreihenfolge und vorregistrierter Rangumkehr. Das grenzt Reihenfolgeempfindlichkeit technisch ab, ohne Bedeutung oder Sequenzverständnis zu behaupten.

## 4. Weltkontakt gegen kontaktfreie Fortsetzung

`return.continued.full_state` gegen `control.stage_two_sequence_withheld`:

```text
activation_linf: 0.021061313972438742
afterimage_linf: 0.0017208269679413624
layer_digest_equal: false
snapshot_digest_equal: false
stage_two_event_counts: 56 vs 0
```

Der rezeptorgetriebene Rückkehrpfad und die kontaktfreie Feldzeitfortsetzung enden technisch verschieden. Dies trennt erneuten Weltkontakt von bloßer kontaktfreier Fortsetzung innerhalb der vorhandenen linearen Feldmechanik.

## Methodischer Gesamtbefund

Die vier vorregistrierten Kontraste sind im einmaligen Lauf technisch messbar. Der Lauf zeigt Zustands-, Komponenten-, Reihenfolge- und Kontaktabhängigkeit. Er beweist weder einen eindeutigen kausalen Mechanismus noch Veränderbarkeit über wiederholte Weltteilnahme, da nur ein Lauf autorisiert war und keine vorregistrierte Funktionsschwelle existiert.

```text
thresholds_defined:          false
causal_mechanism_proven:     false
memory_claim_allowed:        false
meaning_claim_allowed:       false
organization_claim_allowed:  false
ai_claim_allowed:            false
```
