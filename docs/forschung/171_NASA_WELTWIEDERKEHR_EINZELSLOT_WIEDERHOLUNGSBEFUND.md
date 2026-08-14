# NASA-Weltwiederkehr: Einzelslot-Wiederholungsbefund

## Ausfuehrungsgrenze

Der freigegebene Einzelslot wurde genau einmal ueber den bestehenden One-shot-Einstiegspunkt ausgefuehrt. Der Einstiegspunkt erzeugte eine neue Vorabnahme, einen frischen Runner und frische Feldzustaende. Es gab keine automatische Wiederholungsschleife und keinen Zustandsuebertrag aus einem frueheren Lauf.

```text
source_id:                public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20
clock_id:                 public.media.pts_ns
stage_duration_ticks:     500000000
resolution_duration_ticks:100000000
authorized_repeat_count:  1
execution_completed:      true
```

## Technischer Befund

Alle sechs Stufe-eins-Snapshot-Digests waren gleich:

```text
e987feafce00699b1945e666d9d954716df53a935ecd9a005bf9573cb13c4c51
```

Die Arm-, Layer- und Snapshot-Digests sowie die vollstaendigen Aktivierungs- und Nachhall-L-inf-Matrizen stimmen bitgenau mit dem dokumentierten Lauf 116 ueberein. Insbesondere wurden erneut gemessen:

```text
full_state vs fresh_stage_two:
  activation_linf: 0.017293651956615398
  afterimage_linf:  0.017580295681599252

full_state vs activation_only:
  activation_linf: 0.0
  afterimage_linf:  0.003527301811182163

full_state vs permuted_stage_two:
  activation_linf: 0.012491996276939484
  afterimage_linf:  0.009650827900181767

full_state vs withheld_stage_two:
  activation_linf: 0.021061313972438742
  afterimage_linf:  0.0017208269679413624
```

Damit ist die technische Reproduzierbarkeit dieses deterministischen Medien- und Feldpfads fuer einen frischen Einzelslot belegt. Der Befund widerlegt fuer diesen Slot einen einmaligen Rechen- oder Verdrahtungsausreisser.

## Forschungsgrenze

Die bitgenaue Wiederholung mit derselben Mediendatei zeigt keine unabhaengige Weltvariation. Sie trennt insbesondere nicht zwischen linearer Restaktivierung, endlichem Nachhall und einer ueber diese schnellen Zustaende hinausgehenden veraenderten Feldorganisation.

```text
memory_threshold_defined:       false
organization_threshold_defined: false
memory_claim_allowed:           false
meaning_claim_allowed:          false
organization_claim_allowed:     false
ai_claim_allowed:               false
```

## Naechster ausfuehrbarer Forschungsauftrag

Die Sperr- und Abnahmekette wird nicht weiter verlaengert. Als naechster Versuch ist auf Basis des vorhandenen sechsarmigen Ausfuehrungspfads eine vorregistrierte Aufloesungsdauer-Variation zu implementieren:

- mehrere vorab fixierte kontaktfreie Aufloesungsdauern;
- je Dauer frischer Vollzustands-, Aktivierungs-, Nachhall- und Frischfeldvergleich;
- danach dieselbe Stufe-zwei-Weltsequenz;
- Messung der Aktivierungs- und Nachhall-L-inf-Abstaende sowie Layer- und Snapshot-Digests;
- keine nachtraegliche Schwelle und kein Memory-, Bedeutungs-, Organisations- oder KI-Claim.

Der Versuch soll feststellen, ob die reproduzierten Unterschiede vollstaendig und erwartbar mit den schnellen linearen Zustaenden abklingen. Vollstaendige Angleichung falsifiziert diese Architektur als Traeger einer ueber den schnellen Zustand hinausgehenden Veraenderbarkeit. Ein verbleibender reproduzierbarer Funktionsunterschied muesste anschliessend durch getrennte Ablationen isoliert werden.

## Verifikation

```text
19 relevante Tests bestanden
Einzelslot-Runner: exit 0
Laufdauer: 45.4 s
```

## Tatsaechlich verwendete Quellen

- `PRIO_UMSETZUNGSPLAN.md`
- `docs/forschung/116_NASA_WELTWIEDERKEHR_REPLIKATION_EINMALIGER_LAUF.md`
- `docs/forschung/117_NASA_WELTWIEDERKEHR_REPLIKATION_KAUSALKONTRAST_ANALYSE.md`
- `mcm_field_organism/public_av_return_replication_repeatability_runner.py`
- `mcm_field_organism/public_av_return_replication_execution.py`
- `mcm_field_organism/public_av_return_replication_entrypoint.py`
- `tools/run_public_av_return_replication.py`
- lokale Datei `sources/media/NASA Earthrise Realtime Apollo 8.mp4`

Externe Quellen wurden nicht verwendet. Eine Zielabweichung ist nicht erkennbar.
