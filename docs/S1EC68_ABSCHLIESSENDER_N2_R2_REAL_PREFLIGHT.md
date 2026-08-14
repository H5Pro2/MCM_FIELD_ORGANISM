# S1-EC68: Abschliessender n2/r2-Real-Preflight

## Zweck

S1-EC68 prueft die vollstaendige vorbereitete n2/r2-Kette, ohne eine
Besitzerfreigabe anzunehmen und ohne Koordinator, Adapter, Wrapper oder
Feldkern aufzurufen.

## Gepruefte Kette

- EC59: objekttragender Handoff exakt und nullschrittig
- EC65: reale Aufrufadapter exakt und nicht freigegeben
- EC66: positive 4/8-Synthetikfixture exakt und null real ausgefuehrte
  Schritte
- EC67: Realmodus-Koordinator exakt, Freigabesperre vor jedem Adapteraufruf
- vier Bildungs-, acht Fresh-Field- und acht Proberouten
- exakt 1.608/1.600/3.208 geplante Feldschritte
- maximale Laufzeit 900 Sekunden
- in-memory, keine Persistenz
- keine EC46- oder Forschungsentscheidung und keine Claims
- alle fuenf geschuetzten Artefakthashes exakt

Zum Pruefzeitpunkt standen `7.186.976.768` Byte Arbeitsspeicher und
`235.421.171.712` Byte freier Plattenspeicher zur Verfuegung.

## Entscheidung

Alle technischen Gates bestehen. Der Preflight akzeptiert absichtlich keine
Autorisierung und setzt deshalb weiterhin:

- `owner_execution_authorized = False`
- `coordinator_execution_permitted = False`
- `adapter_execution_permitted = False`

Entscheidung:

`TECHNISCH_BEREIT_NEUE_EINMALLAUFFREIGABE_FEHLT`

Preflight-Digest:

`d49687451c8f3612e34e66ea6d43124cd5e1ff71b7cdab51c47bd1b19ab071d7`

## Erforderliche Freigabe

Ein allgemeines Fortsetzungssignal ist keine Einmallauffreigabe. Vor einer
Ausfuehrung ist eine neue ausdrueckliche Freigabe fuer genau einen
nicht-persistenten n2/r2-Lauf mit exakt 3.208 Feldschritten erforderlich.

Die Freigabe darf keine Wiederholung, keinen Retry, keine Nachparametrierung,
keine Persistenz und keine Ergebnis- oder Memory-Entscheidung einschliessen.

Am besten geht es erst nach dieser ausdruecklichen Einmallauffreigabe mit
S1-EC69 weiter: genau einen in-memory n2/r2-Lauf ausfuehren und danach nur den
technischen Rohbefund getrennt von Interpretation, Nichtnachweis und offenen
Annahmen berichten.
