# NASA Weltwiederkehr - Replikation mit kausalen Gegenbaselines

## Pruefentscheidung

Die begrenzte Replikation des vollstaendigen zweistufigen NASA-Weltwiederkehrlaufs ist vorregistriert. Es wird noch kein Runner implementiert und keine Replikation ausgefuehrt.

## Ausgangsbefund

Der vorangegangene Einzelvergleich zeigte eine technische zustandsabhaengige spaetere Feldantwort:

```text
stage_two_activation_linf_between_arms: 0.017293651956615398
stage_two_afterimage_linf_between_arms:  0.017580295681599252
```

Dieser Befund trennt noch nicht, ob die Differenz aus linearer Restaktivierung, Nachhall oder sequenzspezifischer Weltwiederkehr stammt. Daraus folgt keine Memory-, Bedeutungs- oder Organisationsaussage.

## Vorregistrierte Arme

```text
return.continued.full_state
return.fresh_stage_two
control.activation_only_carry
control.afterimage_only_carry
control.stage_two_order_permuted
control.stage_two_sequence_withheld
```

Die Gegenbaselines trennen:

- Fortsetzung des vollstaendigen Zustands gegen frisches Feld;
- lineare Restaktivierung gegen Nachhall;
- gleiche Stufe-zwei-Sequenz gegen permutierte Stufe-zwei-Reihenfolge;
- Weltwiederkehr gegen kontaktfreie Fortsetzung ohne Stufe-zwei-Rezeptorsequenz.

## Fixierte Bedingungen

```text
Quelle:                  public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20
Takt:                    public.media.pts_ns
Stufe-1-Dauer:           500000000 Ticks
Aufloesungsdauer:        100000000 Ticks
Feldparameter:           unveraendert
Dockgeometrie:           identisch
Rohdaten im Ergebnis:    nein
Medienmetadaten im Feld: nein
```

## Messrollen

Vorregistriert sind ausschliesslich technische Messungen:

- Snapshot- und Layer-Digests;
- nullable Digests fuer Arme ohne abgeschlossenen rezeptorgetriebenen Zustand;
- Aktivierungs- und Nachhallvektoren;
- paarweise L-inf-Differenzmatrizen;
- Gleichheitsmatrizen fuer Layer- und Snapshot-Digests;
- Kontaktanzahl des withheld-Arms.

Es wird kein positiver Mindestabstand, keine Memory-Schwelle und keine Organisationsschwelle definiert.

## Sperren

```text
replication_run_allowed:       false
runner_implementation_allowed: false
memory_threshold_defined:      false
organization_threshold_defined:false
positive_effect_required:      false
memory_claim_allowed:          false
meaning_claim_allowed:         false
organization_claim_allowed:    false
ai_claim_allowed:              false
```

## Grenze des Befunds

Diese Vorregistrierung belegt selbst keinen neuen Forschungsbefund. Sie legt nur fest, wie eine spaetere Replikation die kausalen Rollen von Restzustand, Nachhall und sequenzspezifischer Weltwiederkehr trennen soll.

## Naechster ausfuehrbarer Auftrag

Pruefe separat, ob ein Replikationsrunner fuer diese sechs Arme ohne Sonderregeln, ohne kuenstliche Medienereignisse und mit unveraenderten Feldparametern implementierbar ist. Noch keinen Replikationslauf ausfuehren.
