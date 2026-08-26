# W5-C: Suchlueckenentscheid zur geschichtsabhaengigen Umformbarkeit

Stand: 2026-08-09

Entscheidung: `ONE_NARROW_SOURCE_GAP_JUSTIFIES_SECOND_SEARCH`

Auditart: statisch

Runtimeaenderung: nein

Formaler Forschungslauf: nein

## Entscheidungsfrage

Laesst sich aus W5-B eine fachlich bestimmte, noch unbelegte Naturrolle
ableiten, die eine zweite engere Primaerquellensuche rechtfertigt, ohne einen
Mechanismus fuer das gewuenschte Ergebnis zu konstruieren?

## Nicht die Suchluecke

Folgende Einzelrollen sind bereits bekannt und begruenden keine weitere
Suche:

- ein Zustand, der von vergangenem Eingang abhaengt;
- eine Leitfaehigkeit oder Empfindlichkeit, die sich an Fluss anpasst;
- Hysterese oder ein Schwelleneffekt;
- eine Trainingsamplitude, die spaeter ausgelesen werden kann;
- eine nichtreziproke oder aktive Feldkopplung allein;
- ein endlicher Materialvorrat allein;
- Vergessen als Leck, Relaxation oder besondere Loeschphase.

Diese Rollen werden durch die W5-B-Quellen oder bestehende Projektbaselines
bereits abgedeckt.

## Isolierte Suchluecke

Die noch unbelegte Kombination lautet:

> Eine lokale materielle Wechselwirkung besitzt eine unabhaengige technische
> Funktion. Normale lokale Feldteilnahme veraendert geschichtlich die spaetere
> Umformbarkeit genau dieser Wechselwirkung. Der veraenderte Zustand wirkt
> ueber denselben Austausch auf das tragende Feld zurueck. Die dafuer
> verfuegbare Kapazitaet ist begrenzt und kann durch konkurrierende normale
> Geschichte ihre alte Wirkung verlieren sowie fuer eine anders verteilte
> Wirkung erneut verfuegbar werden, ohne Reset-, Trainings-, Lese- oder
> Loeschphase.

Die entscheidende Rolle ist damit nicht blosse Zustandsbehaftung, sondern eine
**geschichtsabhaengige Aenderung spaeterer lokaler Transformierbarkeit bei
konjugierter Rueckwirkung und wiederverwendbarer Kapazitaet**.

## Warum die Kombination eigenstaendig gesucht werden darf

W5-B hat die Bestandteile getrennt gefunden:

| Bestandteil | W5-B-Beispiel | Grenze |
|---|---|---|
| lokale gegenseitige Zustandskopplung | Memristor | Hystereseelement, keine verteilte Wiederverwendung |
| verteilte Rekonfiguration | adaptives Transportnetz | adaptive Leitfaehigkeit und gespeicherte Kanten |
| geschichtsabhaengige materielle Antwort | zyklisch getriebene Materie | vorgeschriebene Trainings- und Ausleseordnung |
| eigenstaendige nichtreziproke Feldfunktion | ungerade Elastizitaet | keine veraenderte Transformierbarkeit oder Kapazitaetsfreigabe belegt |

Keine Quelle untersucht die gebundene Kombination. Deshalb ist die Luecke
nicht nur ein anderes Wort fuer einen bereits ausgeschlossenen Mechanismus.
Das begruendet eine zweite Recherche, aber noch keinen Kandidaten.

## Gebundener Umfang der zweiten Suche

W5-D darf hoechstens zwei klar verschiedene Mechanismusfamilien und je
hoechstens drei Primaerarbeiten kartieren. Eine Arbeit kommt nur in das Ledger,
wenn ihr primaerer Befund mindestens Folgendes explizit untersucht:

1. eine lokale materielle oder Feld-Medium-Wechselwirkung;
2. eine durch normale Geschichte veraenderte spaetere lokale Suszeptibilitaet,
   Umformbarkeit oder Kopplungsantwort;
3. eine Rueckwirkung dieser Aenderung auf denselben physikalischen Austausch;
4. eine erkennbare Ressourcen-, Erhaltungs- oder Dissipationsgrenze;
5. konkurrierende Geschichte, Umlagerung oder Funktionsverlust ohne externen
   Reset als Teil des untersuchten Naturverlaufs.

Fehlt Punkt 2 oder 3, wird die Quelle nicht aufgenommen. Fehlt Punkt 4 oder 5
bei sonst passender Rolle, lautet das Urteil hoechstens
`SOURCE_ROLE_UNDERDETERMINED`.

## Ausgeschlossene Wiederholungen

W5-D darf nicht erneut allgemein suchen nach:

- Memristoren oder resistivem Switching;
- adaptiven Transport- und Schleimnetzwerken;
- Hebb-, Gain-, Mobilitaets- oder Metaplastizitaetsregeln;
- allgemeinen Hysterese-, Plastizitaets- oder Viskoelastizitaetsmodellen;
- zyklischem Training mit nachgeschaltetem Amplitudensweep;
- ungerader Elastizitaet ohne veraenderlichen Materialzustand;
- Reaktions-Diffusion, Musterbildung, Attraktoren oder variabler Topologie;
- biologischer Analogie ohne vollstaendige lokale Mechanik.

Schlagworte wie `material memory`, `learning material`, `adaptive matter` oder
`self-organizing` sind kein Aufnahmegrund.

## Abbruchkriterien fuer W5-D

Die zweite Suche endet sofort mit `SECOND_SOURCE_SEARCH_NO_ROLE_FOUND`, wenn:

- keine Primaerarbeit alle Punkte 1 bis 3 explizit traegt;
- die aufgenommenen Rollen vollstaendig auf W5-A-Ausschlussfamilien
  reduzieren;
- Wiederverwendung nur durch Reset, Schaltprotokoll oder vorgegebene
  Lebenszyklusphase entsteht;
- die angenommene endliche Kapazitaet nur nachtraeglich aus dem Projektziel
  ergaenzt werden koennte.

Nur ein Urteil `SOURCE_ROLE_POTENTIALLY_ADMISSIBLE` duerfte danach einen
eigenen statischen Kandidatenaudit vorschlagen. Auch dann bleiben Gleichung,
Implementierung und Test gesperrt.

## Verwendete Quellen

- [W5-A Primaerquellen-Suchvertrag](W5A_PRIMAERQUELLEN_SUCHVERTRAG_UNABHAENGIGES_SUBSTRATPRINZIP.md)
- [W5-B erste Primaerquellenkartierung](W5B_ERSTE_PRIMAERQUELLENKARTIERUNG_SUBSTRATPRINZIPIEN.md)
- [S1-AA hartes Wiedereroeffnungstor](S1AA_OPERATIVER_ENTWICKLUNGSANSCHLUSS_NACH_SUBSTRATSTOPP.md)
- [S1-F verteilte kausale Nichtseparierbarkeit](S1F_ZULASSUNGSVERTRAG_VERTEILTE_KAUSALE_NICHTSEPARIERBARKEIT.md)
- [S1-AB Audit des umverteilbaren Kopplungsmediums](S1AB_AUDIT_ENDLICHES_LOKAL_UMVERTEILBARES_KOPPLUNGSMEDIUM.md)

## Aussagegrenze

W5-C begruendet nur einen engen Recherchekorridor. Es existiert weiterhin
kein zugelassener Substratkandidat und kein Befund zu MCM-Memory, Lernen,
Feldzeit, innerem Kontext, Organisation, Semantik, Selbstregulation oder KI.
Es wurde keine Gleichung, Variable, Runtime, Testmatrix oder Ausfuehrung
vorbereitet. Lauf 197 bleibt reserviert und unberuehrt.

## Bester naechster Schritt

W5-D fuehrt die zweite begrenzte Primaerquellensuche exakt gegen die fuenf
Aufnahmekriterien dieses Entscheids durch. Sie umfasst hoechstens zwei
Mechanismusfamilien mit je hoechstens drei Originalarbeiten und beginnt mit
der Suche nach experimentell belegter geschichtsabhaengiger Aenderung lokaler
Transformierbarkeit, nicht mit dem Begriff `Memory`.
