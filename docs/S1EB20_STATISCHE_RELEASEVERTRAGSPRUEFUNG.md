# S1-EB20: Statische Releasevertragspruefung

Stand: 2026-08-11

Status: `STATIC_RELEASE_CONTRACT_CHECK_PASSED`

## Ergebnis

Der S1-EB19-Releasevertragsentwurf ist gegen die gebundenen technischen und
wissenschaftlichen Grenzen statisch konsistent.

Geprueft wurden:

- die enge Forschungsfrage;
- die Pflichtkontrollen;
- die strikte Achtfachregel;
- die claimfreie Aussagegrenze;
- maximal 23800 Feldschritte;
- maximal 30 Minuten Wandzeit;
- maximal 4 GiB Peak RSS;
- No-Retry, No-Rerun und No-Tuning.

## Grenze

Diese statische Vertragspruefung ist keine Laufautorisierung. Sie startet
keinen Runner, veraendert keine Parameter und erzeugt keinen Forschungsbefund.
Projekteigner-Autorisierung, technische Ressourcendurchsetzung und
Same-session-Preflight bleiben getrennte Voraussetzungen.

Kein Memory-, Feldzeit-, Organisations- oder KI-Nachweis.
