# S1-CK: E1 E4 S2-B2, ORACLE-G und Einzelrunnerabschluss

## Status

Der konkrete S2-B2-Runner und ORACLE-G sind implementiert und isoliert
technisch abgenommen. Damit existieren fuer alle neun registrierten
E4-Modellrollen konkrete Einzelrunner oder gueltige technische
Ergebnisrollen.

Die neun Rollen wurden noch nicht gemeinsam in den E4-Executor eingesetzt.
Es wurde keine Gesamtmatrix materialisiert, kein Profilabstand gegen E1
berechnet und keine E4-Entscheidung erzeugt. S1-BZ und S1-CD wurden nicht
erneut ausgefuehrt.

## Implementierung

```text
mcm_field_organism/e1_e4_s2_oracle_runners.py
tests/test_e1_e4_s2_oracle_runners.py
```

Alle Rollen bleiben privat und fehlen im Paketexport sowie in `current_api`.

## S2-B2-Runner

Der Runner verwendet unveraendert den S1-CF-Handoff:

```text
H: B2 mit Rueckwirkung, 8 linke Kontakte
G: B2 mit Rueckwirkung, Nullkontakt bis G1/G4/G8
C: vorhandenes B1, L-Entwicklung aktiv, L-zu-S-Rueckwirkung aus
Probe: L fest, vorhandener Frozen-B2-Reader
```

Die festen Parameter bleiben:

```text
capacity_ratio           = 8.0
coupling_rate_per_second = 0.25
afterimage_time_seconds  = 0.5
leak_rate_per_second     = 0.0
gain_reference_seconds   = 1.0
rk4_substeps             = 16
```

Das primaere Profil verwendet n=4, die Kontrolle n=2. Ablation verwendet
den vorhandenen B0-Pfad. In der aktiven Frozen-Probe bleibt L an jedem
Teilintervall exakt der Checkpointvektor.

Das B2-Profil ist vollstaendig, messbar und ueber die Checkpoints nicht
konstant. Seine Invarianten, B2/B1-Zuordnung, Frozen-L-Kontrolle und
Refinementgrenze bestehen.

## ORACLE-G

ORACLE-G wird nur aus einem bereits technisch gueltigen E1-Run aufgebaut,
dessen checkpointweise Fixed-Gain-Kontrollen bestanden haben. Fuer jeden
Checkpoint werden die bestaetigten E1-Wirkungskomponenten unter der
eigenstaendigen Modellidentitaet `oracle-g` uebernommen.

Das ORACLE-G-Profil ist dadurch komponentenweise exakt gleich E1, besitzt
aber einen eigenen Parameterdigest. Es ist nur Kontrollobergrenze und bleibt
von der Baselineentscheidung ausgeschlossen. ORACLE-G entwickelt keinen
eigenen Zustand.

## Technische Abnahme

Fokussiert:

```text
python -m unittest -v tests.test_e1_e4_s2_oracle_runners

6 tests
OK
```

Gemeinsam mit S2-Referenzmodell, E1/B0/B1, E1-Historie und Probe,
Executorkern, Handoffs und B3-B6, jedoch ohne die Einmallauf-Suiten:

```text
88 tests
OK
```

Geprueft wurden:

- vollstaendiges, messbares und checkpointvariables B2-Profil;
- B2/B1-Intervention und Frozen-L-Identitaet;
- endliche und begrenzte S/H/L-Zustaende;
- n=2/n=4-Profilgrenze;
- exakte ORACLE-G-Reproduktion von E1;
- Ablehnung eines ungueltigen oder fremden Oracle-Quellprofils;
- unveraenderte Eingaben und private API-Grenze.

## Aussagegrenze

S1-CK zeigt nur die isolierte technische Lauffaehigkeit von B2 und die
Korrektheit der Oracle-Kontrolle. Es wurde nicht entschieden, ob B1 bis B6
das E1-Profil erklaeren. Es folgt kein Memory-, Lern-, Organisations-,
Semantik- oder KI-Befund.

## Anschluss

S1-CL baut das vollstaendige lazy Runnerinventar und prueft Reihenfolge,
Digest, Eingaben und Ankerlieferant ohne Runnerausfuehrung, Komposition oder
Entscheidung.

## Bester naechster Schritt

S1-CM registriert den atomaren E4-Einmallauf und seine Ergebnisablage
statisch. S1-CM fuehrt den Lauf noch nicht aus.
