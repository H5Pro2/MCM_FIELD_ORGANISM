# S2-SP: identitätserhaltender PPB-Präfixvergleich

Auftragskennung: `S2SP-IDENTITY-PREFIX-COMPARE-20260919-01`  
Technischer Abschluss: `RECORDING_COMPLETE`, unabhängig verifiziert.

Beide getrennten Arme verarbeiten denselben Präfix `e01` bis `e06` mit vier
gemeinsam materialisierten Formationen und zwei read-only Cues. Sie haben
dieselben Fast-Ereignisse, Fast-Supports und visuellen PPB-Schrittzahlen:
e01 erstellt Fast, e03-e05 matchen Fast und schreiben die PPB bis Schritt 3
fort. Feldkontakte finden nicht statt.

| Arm | Updatebindung | visueller Slow-Kandidat bei e06 | Exakthinweis bei e06 |
| --- | --- | --- | --- |
| Historisch | `historical.v1` | vorhanden | keiner |
| Privat | `identity-preserving.v1` | vorhanden | genau einer |

Der private Arm bewahrt bei bitgleichen Komponenten den gespeicherten Wert;
dadurch ist der Slow-Prototyp gegenüber der identischen e06-Cue bitstabil und
besteht die unveränderte Exakt- sowie Teilstrukturprüfung. Der historische Arm
bleibt unverändert und zeigt die zuvor nachgewiesene Rechendrift.

Dieser Befund betrifft nur den gebundenen Präfix und nur die private
Updatevorschrift. Er löst weder den separaten Randvarianten-Fehlhinweis noch
begründet er eine öffentliche Regeländerung, Videoanbindung oder Integration.
