# W6-I: Einmaliger kausaler Browserlauf

Stand: 2026-08-09

Entscheidung: `LOCAL_L_STATE_CAUSALLY_ALTERS_LATER_S_TRAJECTORY_IN_S1B_REFERENCE`

Arbeitsart: genau einmalige kontrollierte Browserausfuehrung

Browser gestartet: ja, genau einmal

Formaler Memory-Forschungslauf: nein

## Ausfuehrungsfrage

Veraendert ein durch kontrollierten H_A-Weltkontakt erzeugter L-Zustand die
spaetere S-Trajektorie unter derselben Probe P, wenn S und H vor P gleich
gehalten und L vollstaendig erhalten, neutralisiert oder gegen L_B getauscht
wird?

## Gebundene Ausfuehrung

Ausgefuehrt wurde ausschliesslich
`s1b.causal.browser.w6i.once.v1` mit dem in W6-G gebundenen Weltset,
Playwright 1.62.0, der vorhandenen Chromium-Headless-Shell und drei frischen
isolierten Kontexten. Der Attemptmarker wurde vor dem Browserstart gesetzt.
Der Report wurde atomar publiziert; Attemptmarker und Lock wurden danach
entfernt. Der vorhandene Report sperrt jede Wiederholung.

```text
Report: reports/s1b_causal_browser_w6i_once_v1.json
SHA-256: 6480ede15cb783c24de34d6dfa57b3351e7571264de80619ef0a712f7a7746ad
Vertragsdigest: 094558b988103ad1ed75e708b3a0961b62963f74896411dd1e381afeac81387d
```

Lauf 197 und seine reservierten Attempt-/Lockpfade blieben unberuehrt.

## Kontrollen

```text
formation_support_count_a: 108
formation_support_count_b: 108
probe_support_count:       108
fast_r_n_equal:            true
fast_r_x_equal:            true
null_formation_equal:      true
null_probe_equal:          true
raw_payloads_retained:     false
audio_buffers_released:    true
pages_closed:              true
contexts_closed:           true
browser_closed:            true
```

Die Formation war informativ:

```text
l_a_linf:  0.0013898494692739269
l_b_linf:  0.0014124356777130461
l_ab_linf: 0.0003549252112082364
```

## Vorregistrierte Distanzen

```text
d_rn_s: 0.00015754602515355431
d_rx_s: 0.0000206194528247217
d_xn_s: 0.0001604238888009979
d_rn_h: 0.0000981830158535979
d_rx_h: 0.0000148219886825438
Toleranz: 0.000000000001
```

Mindestens `d_rn_s` und `d_rx_s` liegen ueber der festen Toleranz. Weil die
S/H-Ausgangsprojektionen gleich waren und beide Nullkontrollen bestanden,
ist der vollstaendige L-Zustand innerhalb des S1-B-Referenzpfads eine
technische Ursache der spaeteren S-Trajektorie.

## Aussagegrenze

S1-B wurde als reziproke Zweizeitenmechanik konstruiert. W6-I bestaetigt ihre
beabsichtigte L-nach-S-Wirkung unter real gerenderten, kontrollierten
Browserwelten. Der Lauf belegt nicht:

- Praegung durch Wiederholung;
- Unterscheidung von Wiederholung und Dauerkontakt;
- Rekonstruktion durch Teilhinweise;
- feldinternes Vergessen oder Wiederverwendung;
- relative Feldzeit;
- Organisation, Semantik, Selbstregulation, Memory oder KI.

## Bester naechster Schritt

W7-A registriert einen minimalen geschichtlichen Funktionsvergleich vor.
Wiederholter Weltkontakt wird gegen einen in Gesamtstuetze und
Rezeptorwirkung angeglichenen zusammenhaengenden Kontakt unter identischer
Probe gestellt. Der S1-B-Pfad muss dabei mindestens gegen eine lokale
Leaky-Spur und eine langsame Feldkopie bestehen. W7-A fuehrt noch keinen
Browserlauf aus.
