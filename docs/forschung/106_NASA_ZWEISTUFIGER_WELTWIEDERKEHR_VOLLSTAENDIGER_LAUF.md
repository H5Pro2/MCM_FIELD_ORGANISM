# NASA: vollstaendiger zweistufiger Weltwiederkehrlauf

## Ausfuehrung

Der korrigierte und separat vorabgenommene Lauf wurde genau einmal ausgefuehrt. Beide Arme verarbeiteten in Stufe eins und Stufe zwei jeweils 56 reduzierte Audio-/Video-Rezeptorereignisse.

```text
stage_duration_ticks:      500000000
resolution_duration_ticks: 100000000
clock_id:                  public.media.pts_ns
```

## Vorregistrierte Messungen

```text
stage_two_activation_linf_between_arms: 0.017293651956615398
stage_two_afterimage_linf_between_arms:  0.017580295681599252
stage_two_layer_digest_equal:            false
stage_two_snapshot_digest_equal:         false
```

Fortsetzungsarm:

```text
stage_one_snapshot_digest:      e987feafce00699b1945e666d9d954716df53a935ecd9a005bf9573cb13c4c51
post_resolution_snapshot_digest: aa72b3f06051dfb8b9cd253369ba838ae0b039ca3eb7ae7ba105a7819c7a97b9
stage_two_layer_digest:          c9a5d0fb4bf88f975a5d35eda11a473f159e8812c0aa7f3646666ed2c73b68ce
stage_two_snapshot_digest:       f1600c73655b04ffe68d83c4b7b43939ffcf7215ea82cebd4262200147e78988
```

Frische Stufe-zwei-Baseline:

```text
stage_one_snapshot_digest:       e987feafce00699b1945e666d9d954716df53a935ecd9a005bf9573cb13c4c51
post_resolution_snapshot_digest: null
stage_two_layer_digest:          98e017ef50d98c2178ef6b5d43376d46ee2e2e3c6a7353c774e82ff605adc477
stage_two_snapshot_digest:       2144b71530756e149b0e2efa026a9cd0e3cbd4b636c2d89eb26abb4505992535
```

Die identischen Stufe-eins-Digests bestaetigen fuer diesen Lauf identische Anfangsbedingungen und dieselbe erste reduzierte Weltsequenz. Die Stufe-zwei-Unterschiede zeigen technisch, dass der uebernommene Feldzustand nach der kontaktfreien Aufloesungsphase die spaetere Feldantwort gegenueber einem frischen Feld veraendert hat.

## Forschungsgrenze

Der Lauf isoliert eine zustandsabhaengige spaetere Feldantwort im vorhandenen linearen Feldpfad. Er definiert weder eine Memory- noch eine Organisationsschwelle und prueft keine Bedeutung, Handlung oder eigenstaendige KI. Aus dem Einzelvergleich darf keine solche Behauptung abgeleitet werden.

Rohdaten wurden nicht im Ergebnis behalten und Medienmetadaten wurden nicht als Feldeingang verwendet.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabeauftrag;
- `mcm_field_organism/public_av_two_stage_return_execution.py`;
- `mcm_field_organism/public_av_two_stage_return_rerun_preflight.py`;
- lokale Datei `sources/media/NASA Earthrise Realtime Apollo 8.mp4`.

Externe Quellen wurden nicht verwendet. Eine Zielabweichung ist nicht erkennbar.
