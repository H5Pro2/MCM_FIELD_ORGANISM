# W7-J: Adaptervertrag fuer kapazitaetsbegrenzte SharedMCMField-Runtime

Stand: 2026-08-09

Entscheidung: `ADDITIVE_CAPACITY_RUNTIME_ADAPTER_CONTRACT_BOUND`

Arbeitsart: statischer Integrationsvertrag

Runtimeaenderung: nein

Forschungslauf: nein

## Zweck

W7-J bindet den kleinsten technischen Weg, auf dem die in W7-G
implementierte kapazitaetsbegrenzte Kopplung spaeter in die vollstaendige
`SharedMCMField`-Runtime eingesetzt werden kann. W7-J implementiert diesen
Weg noch nicht.

Der neue Pfad bleibt ausdruecklich opt-in. Die bestehende K2/F3-Runtime, ihre
oeffentlichen Funktionen, `current_api`, Snapshot-Schemata und neutrale
Ergebnisse duerfen durch die spaetere Umsetzung nicht veraendert werden.

## Bestehende Anschlussstelle

Die Runtime besitzt bereits eine private Einspeisestelle fuer eine alternative
Kopplungsberechnung. Eine gebundene Closure kann dort W7-G mit einer festen
Ortskapazitaet aufrufen. Die vorhandene Schrittgrenze bleibt hinreichend:

```text
rho_M = 2 * lambda_sm * d_max
h_safe = 0.5 / max(rho_S, rho_H, rho_M)
```

Der freie Zielanteil liegt im zulaessigen Zustand in `[0,1]`. Deshalb wird
keine groessere gerichtete Abgaberate als im bestehenden K2/F3-Korridor
eingefuehrt.

Die vorhandene Stufenpruefung bindet jedoch nur `M_i >= 0` und die
Gesamtmasse. Ein blosser Austausch der Kopplungsfunktion reicht deshalb nicht:
`M_i <= C_site` muss nach jeder gemeinsamen SSPRK-Stufe und unmittelbar vor
dem Commit separat geprueft werden.

## Minimaler Runtimeeingriff fuer W7-K

Die spaetere Umsetzung darf in `mcm_f3_runtime.py` genau eine additive private
Pruefstelle einfuehren:

```text
_stage_validator: Callable[..., None] | None = None
```

Verbindlich ist:

- `None` behaelt den bisherigen Kontrollfluss und alle bisherigen Ergebnisse;
- die Zusatzpruefung laeuft erst nach der bestehenden Stufenvalidierung;
- sie erhaelt keine mutierbaren Runtimearrays und darf keinen Zustand
  korrigieren;
- sie wird fuer den Eingangszustand und nach jeder SSPRK-Stufe aufgerufen;
- unmittelbar vor `_commit` wird die Kapazitaetsgrenze erneut gebunden;
- Fehler brechen vor dem Commit ab und hinterlassen das Feld unveraendert;
- Observer bleiben rein beobachtend und sind keine Ersatzvalidierung.

Der direkte P0-Pfad fuehrt weiterhin keine SSPRK-Stufe aus. Der opt-in Adapter
prueft dort Eingang und Ergebnis gegen dieselbe Kapazitaet. M bleibt exakt
unveraendert; die bestehende exakte S/H-Projektion muss erhalten bleiben.

## Getrennter opt-in Adapter

W7-K soll ein neues Modul
`mcm_field_organism/capacity_limited_mcm_f3_runtime.py` anlegen. Es darf die
bestehende Runtime nur aufrufen und konfigurieren, nicht kopieren.

Der Adapter bindet:

- eine unveraenderliche technische Konfiguration aus Gleichungskennung und
  `site_capacity`;
- eine Closure auf `compute_capacity_limited_mcm_f3_coupling` aus W7-G;
- den kapazitaetsspezifischen Stufenvalidator;
- passive Diagnosen fuer maximale Belegung, minimale freie Kapazitaet und
  maximale Obergrenzenverletzung;
- je eine opt-in Funktion fuer kontinuierliche und transiente Fortschreibung.

Das Adapterergebnis darf das vorhandene `MCMF3AdvanceResult` zusammen mit den
Kapazitaetsdiagnosen und dem Konfigurationsdigest kapseln. Es darf keine
Memory-, Bedeutungs- oder Organisationsauswertung enthalten.

## Fortsetzungs- und Restorebindung

`site_capacity` ist technische Gleichungskonfiguration und kein dynamischer
Organismuszustand. Deshalb wird sie nicht in `SharedMCMFieldSnapshot`
eingeschrieben und erzeugt kein neues Snapshot-Schema.

Fuer eine gebundene Fortsetzung verwendet der Adapter einen separaten
Fortsetzungsnachweis aus:

```text
snapshot_digest + configuration_digest
```

Nach Restore muss dieselbe Gleichungskennung und dieselbe Ortskapazitaet
vorgelegt werden. Eine fehlende oder geaenderte Bindung wird vor der ersten
Stufe abgewiesen. Eine Fortsetzung mit identischer Bindung muss dasselbe
Ergebnis liefern wie eine ununterbrochene Fortsetzung.

Der Nachweis ist weder Memory noch Feldzustand und wird nicht als
Forschungsergebnis gespeichert.

## Transienter Pfad

Der vorhandene ereignisausgerichtete Lauf bleibt massgeblich. Punktfoermige
Rezeptorereignisse duerfen S beeinflussen, aber weder M noch `C_site` direkt
schreiben. Jedes ereignisfreie Teilintervall verwendet denselben
kapazitaetsbegrenzten Kopplungsadapter und dieselbe gemeinsame Schrittgrenze.

Kapazitaetspruefungen gelten auch direkt nach Ereignisgrenzen und vor dem
abschliessenden Commit. Es entsteht kein eigener Takt und keine Feldzeitmetrik.

## Verbindliche W7-K-Pruefungen

W7-K muss mindestens nachweisen:

1. Die unveraenderte Default-Runtime liefert weiterhin ihre bestehenden
   Resultate und Digests.
2. P0 behaelt M exakt und entspricht fuer S/H dem vorhandenen Exaktpfad.
3. Der aktive kontinuierliche Pfad erhaelt `S,H in [-1,1]`,
   `M in [0,C_site]` und die Gesamtmasse.
4. Der transiente Pfad bleibt ereignisausgerichtet und wahrt dieselben
   Grenzen nach jeder Stufe und vor Commit.
5. Ein unzulaessiger Eingang oder eine erzwungene Obergrenzenverletzung wird
   vor Commit abgewiesen.
6. Restore mit identischer Bindung ist deterministisch identisch; fehlende
   oder geaenderte Bindung wird abgewiesen.
7. Deterministische Wiederholung und geordnete n/2n/4n-Verfeinerung bestehen.
8. `current_api`, Browserpfade, Reports und Snapshot-Schemata bleiben
   unveraendert.

## Aussagegrenze

W7-J ist ein technischer Adaptervertrag. Er belegt weder Praegung noch
Verdichtung, Vergessen, Rekonstruktion, Feldzeit, inneren Kontext, Memory,
Organisation, Semantik, Selbstregulation oder KI.

Insbesondere wird aus lokaler Kapazitaetsinvarianz kein funktionaler
Memorybefund abgeleitet. Ein spaeterer Welt- oder Forschungsversuch benoetigt
weiterhin einen eigenen vorregistrierten Vergleich mit Gegenbaselines.

## Naechster Schritt

W7-K darf den getrennten opt-in Runtimeadapter und die minimale private
Stufenpruefstelle implementieren und ausschliesslich technisch testen. Kein
Browser, kein Report und kein Forschungslauf ist Bestandteil von W7-K.
