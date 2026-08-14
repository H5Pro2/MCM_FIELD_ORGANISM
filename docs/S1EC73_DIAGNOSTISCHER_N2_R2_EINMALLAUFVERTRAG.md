# S1-EC73: Diagnostischer n2/r2-Einmallaufvertrag

## Zweck

S1-EC73 definiert die feste Huelle eines moeglichen diagnostischen
Folgeversuchs nach dem EC69-Teilabbruch. Der Vertrag ist kein Retry-Befehl und
keine Freigabe. Er beschreibt genau einen geplanten Versuch, dessen
autorisierte Ausfuehrungszahl weiterhin null ist.

## Gebundene Grenze

- Quelle ist ein technisch bereiter, aber nicht freigegebener EC72-Preflight;
- ein geplanter Folgeversuch, null autorisierte Ausfuehrungen;
- n2/r2 mit vier Bildungsarmen, acht Fresh Fields und acht Proben;
- maximal 1.608 Bildungs-, 1.600 Probe- und 3.208 Gesamtfeldschritte;
- der erste Bildungsarm umfasst 402 Schritte;
- maximale Laufzeit 900 Sekunden;
- alle fuenf benannten EC70-Bildungsdiagnosegates gebunden;
- Abbruch beim ersten fehlgeschlagenen Diagnosegate;
- fehlgeschlagene Gate-Namen muessen berichtet werden;
- erneuter EC72-Preflight unmittelbar vor einer moeglichen Ausfuehrung;
- neue ausdrueckliche Besitzerfreigabe erforderlich;
- kein automatischer Retry und keine Nachparametrierung;
- keine Rohoutput-Persistenz oder Aenderung geschuetzter Artefakte;
- keine Forschungsentscheidung oder Claims.

Der technische Bericht nach einem spaeter autorisierten Versuch muss strikt
trennen:

1. Messung
2. technische Interpretation
3. Nichtnachweis
4. offene Annahmen

## Synthetische Abnahme

Vier eigene fokussierte Tests bestehen:

- korrekte geschlossene Einmallaufhuelle;
- exakte EC70-Gates und getrennte Berichtspflicht;
- unbereiter EC72-Preflight wird abgelehnt;
- keine Autorisierungsschnittstelle, Realpfadaufrufe oder Schreiboperationen.

## Aktueller geschlossener Vertragsentwurf

Der aktuelle nicht ausfuehrende Snapshot enthaelt:

- freier Arbeitsspeicher: `7.019.069.440` Byte;
- freier Datentraeger: `234.953.109.504` Byte;
- EC72-Preflight-Digest:
  `da4e06372b0b0658cb4672fc3433255fad84b6145fa8c7c2ab0f345a825225bb`;
- EC73-Vertragsdigest:
  `464df04203e016cb0f86bb2e1417652ad6119e63bd6b512f466d558401e7a4e1`.

Entscheidung:

`DIAGNOSTIC_ONE_SHOT_CONTRACT_BOUND_AWAITING_EXPLICIT_OWNER_AUTHORIZATION`

Der Ressourcen-Snapshot ist zeitabhaengig. Deshalb muss EC72 vor einer
moeglichen Ausfuehrung erneut gebildet und der dazugehoerige EC73-Vertrag
erneut gebunden werden.

## Aussagegrenze

EC73 plant nur einen diagnostischen technischen Folgeversuch. Der Vertrag
belegt weder Fehlerfreiheit noch die Ursache des EC69-Abbruchs und liefert
keinen Memory-, Feldzeit-, Organisations- oder KI-Nachweis.

**STOPP fuer reale Ausfuehrung.** `authorized_execution_count = 0` und
`execution_permitted = False`. Ein allgemeines `ok weiter` ist keine
Einmallauffreigabe.

Am besten geht es erst nach einer ausdruecklichen Besitzerentscheidung mit
S1-EC74 weiter: Autorisierung fuer genau einen nicht persistenten
diagnostischen n2/r2-Folgeversuch mit maximal 3.208 Feldschritten binden. Ohne
diese Entscheidung bleibt der Realpfad geschlossen.
