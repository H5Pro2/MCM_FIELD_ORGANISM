# NASA zweistufiger Weltwiederkehrlauf - Ausfuehrungsvorabnahme

## Pruefentscheidung

Die Ausfuehrungsvorabnahme ist als eigenes Gate umgesetzt. Sie prueft Quelle, lokale Dateiintegritaet, Runner-Identitaet, Gap-Audit, feste Intervalle und unveraenderte Feldparameter gemeinsam. Der tatsaechliche Feldlauf wird durch dieses Dokument nicht ausgefuehrt.

## Gepruefter Laufumfang

```text
Quelle:        public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20
Stufe 1:       [0, 500000000)
Aufloesung:    [500000000, 600000000)
Stufe 2:       [600000000, 1100000000)
Freigabe:      genau ein begrenzter zweistufiger Lauf
```

## Gate-Bedingungen

Die Vorabnahme verlangt:

- positiven lokalen Quellen-Audit mit Groesse und SHA-1;
- gleiche `source_id` in Quellenvertrag, Vorregistrierung und Runner-Wiring;
- gleiche `runner_id` zwischen Runner-Wiring und Gap-Audit;
- gleiche `preregistration_id` zwischen Vorregistrierung, Runner-Wiring und Gap-Audit;
- festen `public.media.pts_ns`-Takt;
- feste Intervalle fuer Stufe 1, Aufloesungsphase und Stufe 2;
- kontaktfreien `no_input_gap.step_time_only`;
- unveraenderte Feldparameter aus der Vorregistrierung.

## Sperren

```text
field_run_started:          false
raw_payload_retained:       false
metadata_used_by_field:     false
memory_claim_allowed:       false
meaning_claim_allowed:      false
organization_claim_allowed: false
ai_claim_allowed:           false
```

## Grenze des Befunds

Die Vorabnahme decodiert kein Medium, speist keine Rezeptoren und startet keinen Feldlauf. Sie erlaubt nur, dass ein nachfolgender Agent genau den begrenzten zweistufigen Lauf mit den festgelegten Vertragen starten darf, sofern das Gate positiv ist.

Der Befund belegt kein Memory, keine Bedeutung, keine innere Organisation und keine eigenstaendige KI.

## Naechster ausfuehrbarer Auftrag

Fuehre genau einen begrenzten zweistufigen NASA-Weltwiederkehrlauf mit dem vorabgenommenen Runner aus. Danach sind ausschliesslich die vorregistrierten technischen Differenzmessungen zu berichten; Memory-, Bedeutungs-, Organisations- und KI-Claims bleiben weiterhin ausgeschlossen.
