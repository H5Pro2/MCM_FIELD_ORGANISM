# S1-EC74: Autorisierter Diagnoselauf mit Handoff-Digest-Schemaabweichung

## Freigabe und Vorpruefung

Der Projekteigentuemer gab genau einen nicht persistenten diagnostischen
n2/r2-Folgelauf unter EC73 mit maximal 3.208 Feldschritten frei. Retry und
Nachparametrierung waren ausgeschlossen.

Unmittelbar vor dem Start wurden im selben Prozess EC72, EC73 und EC74 neu
gebunden:

- EC72-Preflight-Digest:
  `5eeab2e2942109c7f1260b383bc76c69cca9423b7814b3fc6d817e40c6ef9148`
- EC73-Vertragsdigest:
  `1d247ecf292f5d1a7d97725ab4fd7e5ee65d2dc29d8caecf6b29a57687055886`
- EC74-Autorisierungsdigest:
  `cddaffb747083b0c8d2a9307cd6a120823e7fd57401ae73843bac86c607e8b19`
- freier Arbeitsspeicher: `7.033.008.128` Byte
- freier Datentraeger: `235.030.564.864` Byte

Quellintegritaet, technische Gates und alle fuenf geschuetzten Artefakte
waren exakt.

## Messung

Der EC67-Realmodus-Koordinator wurde genau einmal gestartet.

- Der erste Bildungsarm `active-ab`, `n2/r2`, wurde mit 402 Feldschritten
  verarbeitet.
- Beim unmittelbar folgenden EC70-Diagnosegate brach die Kette ab.
- Benanntes fehlgeschlagenes Gate:
  `formation-handoff-digest-exact`
- Exception:
  `E1CommonProbeN2R2RealOutputConverterError`
- Die drei weiteren Bildungsarme, acht Fresh Fields und acht Proben wurden
  nicht gestartet.
- Tatsaechlicher Umfang: 402 Bildungs-, 0 Probe-, insgesamt 402
  Feldschritte.
- Es existiert kein Gesamtergebnis-Digest.

Die einmalige EC74-Freigabe ist durch diesen Start verbraucht. Es erfolgte
kein Retry.

## Technische Interpretation

Die statische Quellpruefung zeigt einen Digest-Schemavergleich zwischen zwei
unterschiedlichen Funktionen:

1. Der reale Bildungsrunner erzeugt `output.audit.handoff_digest` mit
   `e1_refined_formation_runner._handoff_digest`. Dieses Schema hasht nur die
   geordnete Folge aus Abschlusszeit und Frame-Identitaeten.
2. Der EC70-Konverter vergleicht diesen Wert mit
   `resolved.formation_plan.handoff_digest`.
3. Der Planwert stammt aus
   `e1_completion_aligned_refinement._handoff_digest`. Dieses Schema hasht
   zusaetzlich Clock-ID, Modalitaeten, Quell- und Zuweisungszahlen sowie den
   Assigned-once-Status.

Die beiden SHA-256-Werte repraesentieren daher nicht dasselbe serialisierte
Schema. Das Gate kann trotz konsistentem Handoff nicht bestehen. Der Befund
ist eine technische Vertragsinkompatibilitaet zwischen Plan und Runner, kein
Hinweis auf eine Abweichung der AV-Zeitordnung.

## Nichtnachweis

- kein vollstaendiger n2/r2-Lauf;
- keine AB/BA- oder Ablationsauswertung;
- keine Probeantwort;
- kein Memory-, Feldzeit-, Organisations- oder KI-Nachweis;
- keine Aussage ueber E1-Wirkung oder MCM-Memory.

## Offene Annahmen

Vor einer weiteren Ausfuehrung muss festgelegt werden, welches Handoff-Schema
kanonisch ist oder ob beide Digests mit eindeutigen Rollen separat getragen
werden. Ein blosses Entfernen des Gates waere nicht zulaessig.

Alle fuenf geschuetzten Artefakte sind nach dem Lauf unveraendert.

**STOPP fuer weitere reale Ausfuehrung.** Die EC74-Freigabe ist verbraucht.

Am besten geht es mit S1-EC75 weiter: die zwei Handoff-Digest-Schemata
typisieren, einen gemeinsamen kanonischen Vergleich definieren und die
Korrektur ausschliesslich synthetisch gegen beide bisherigen Schemata testen.
Danach muessen EC71 bis EC73 wegen der Quellaenderung neu gebunden werden.
