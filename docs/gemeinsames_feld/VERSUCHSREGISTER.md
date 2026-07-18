# Versuchsregister des gemeinsamen MCM-Feldes

| Nummer | Status | Forschungsgrenze | Runtimefreigabe |
|---|---|---|---|
| `GF_001` | geschlossen | Gemeinsame Feldtakte und lokale Wirkung aufeinanderfolgender auditiver und visueller Rezeptorzustände im selben Feld | keine |

## Bedeutung des Status

- `geschlossen`: noch keine verbindliche Methodik und kein Lauf,
- `vorregistriert`: Methodik vollständig, aber noch kein Ergebnis,
- `gelaufen`: Messung abgeschlossen, Auswertung noch offen,
- `befundet`: Befund mit begrenzter Evidenzaussage dokumentiert,
- `gestoppt`: Abbruchkriterium erreicht; keine Erweiterung freigegeben.

## Grenze von GF_001

`GF_001` darf erst geöffnet werden, wenn der technische Zeitvertrag einzelne
auditive und visuelle Rezeptorzustände auf derselben Organismusuhr abbildet.

Der [Technische Zeitaudit 001](TECHNISCHER_ZEITAUDIT_001.md) erfüllt den ersten
Teil, zeigt aber null eindeutige 1:1-Zustandspaare. Vor `GF_001` fehlt deshalb
weiterhin ein gemeinsamer Feldtaktvertrag.

Der [Technische Fensteraudit 002](TECHNISCHER_FENSTERAUDIT_002.md) legt reale
Fenster vor den Sensor-Reads fest. In jedem Ein-Sekunden-Fenster treten jedoch
viele auditive und mehrere visuelle native Zustände auf. Damit fehlt weiterhin
eine begründete Trennung zwischen Rezeptorereignis und Feldfortschritt.

Der [Technische Ereigniszeitaudit 003](TECHNISCHER_EREIGNISZEITAUDIT_003.md)
bewahrt alle nativen Zustände, zeigt aber bei einem Ereignis pro möglichem
Feldschritt einen auditiven Anteil von rund 95 %. Vor `GF_001` fehlt deshalb
eine Rateninvarianzprüfung der passiven Feldzeit.

Die [Technische Rateninvarianzprüfung 004](TECHNISCHE_RATENINVARIANZPRUEFUNG_004.md)
zeigt für die bekannte B1-Baseline: Reale verstrichene Dauer beseitigt reine
Segmentratenabhängigkeit, rekonstruiert aber keinen ausgelassenen Kontakt. Vor
`GF_001` fehlt nun ein passiver Zeitspannenvertrag im MCM-Neuronenantrieb.

Der [Technische Zeitspannenvertrag 005](TECHNISCHER_ZEITSPANNENVERTRAG_005.md)
übergibt optional dieselbe gemessene Dauer an alle atomaren
Neuronenvorschläge, ohne Zustand oder Baselines zu verändern. Offen bleibt die
technische Bildung einer lückenlosen Feldzeitfolge aus asynchronen
Rezeptorabschlüssen.

Die [Technische Feldzeitpartition 006](TECHNISCHE_FELDZEITPARTITION_006.md)
deckt drei reale Sekunden lückenlos ab, enthält aber 324 ereignistragende
Grenzen und bleibt damit ratenbestimmt. Offen ist nun die tatsächliche
zeitliche Stütze jedes reduzierten Rezeptorzustands auf der Organismusuhr.

Der Versuch darf nicht:

- Gleichzeitigkeit aus bloß überlappenden Gesamtaufnahmen ableiten,
- eine Beziehung zwischen Docks voraussetzen,
- eine Kopplungs- oder Lernregel ergänzen,
- Semantik, Objekte oder Sprache einführen,
- Aktivität bereits als Feldorganisation interpretieren.
