# A1: eindeutiger Teilhinweis als Anlass zur Erhaltung einer Originalspur

Status: **KONZEPTVORSCHLAG – NICHT IMPLEMENTIERT, NICHT AUSGEFÜHRT**.
Genau eine Regel gegenüber unverändertem U. K1 ist abgeschlossen und bleibt
deaktiviert; seine zusätzliche Kandidatenfrist wird nicht übernommen.

## Entscheidung und Bedeutung

Ein bereits vorhandener Kandidat darf aufgrund eines neuen, eindeutig
berechtigten Teilhinweises in einen der zwei vorhandenen Erhaltungsplätze
übernommen werden. Das bestätigt ausschließlich die beobachtete Abrufrelevanz
dieser Originalspur. Es bestätigt weder die Wiederkehr ihres ganzen Viererblocks
noch die Richtigkeit ihres noch unbekannten Nachfolgers.

Die beiden bisher durch vollständige Wiederkehr belegten Retained-Plätze
werden damit zu **höchstens zwei zur Erhaltung zugelassenen Originalspuren**.
Ihre Zulassungsgründe können vollständige Wiederkehr oder A1-Teilhinweis sein.
Diese geänderte Bedeutung ist eine ausdrückliche Konzeptänderung; vorhandene
Retained-Rolle allein dürfte unter A1 nicht mehr als Beweis vollständiger
Wiederholung bezeichnet werden. Wer zwei ausschließlich vollständig bestätigte
Spuren zusätzlich zu A1 erhalten wollte, verlangte einen dritten Platz; das
wäre mit diesem Vertrag unvereinbar und ist nicht vorgeschlagen.

Die Autorisierung betrifft nur diesen Konzepttext. Ein beobachteter externer
Teilhinweis ist neue Wahrnehmung; bloßes internes Abrufen, Wiederlesen eines
Receipts oder Beobachterwissen ist niemals ein Bestätigungsereignis. Die
Projektorientierung in der Konzeptnotiz zu Wahrnehmungsverläufen bleibt gewahrt.

## Exakte Auslösebedingung

Bezug ist der unveränderte U-Pfad: Vierersegmente, zwei neue Hinweisframes je
Prognose, exakter Abruf, bisherige Berechtigung, EMA und Auswahl. Ein Abschluss
ohne A1-Auslösung verhält sich wie U, nicht wie K1.

An jedem regulären Prognosezeitpunkt, nachdem beide Hinweisframes tatsächlich
eingetroffen sind, aber **vor Einfrieren der neuen Prognose und vor Aufnahme
dieser Hinweisframes in den Spurbestand**, wird einmal der bisherige lebende
Bestand gelesen. Früheres Feedback muss wie bisher verarbeitet und freigegeben
sein. Kein zweites noch offenes Ticketpaket ist zulässig.

Eine Originalhypothese ist das Tupel aus Scope, vier Originalordinalen und
Offset. Für A1 müssen gleichzeitig gelten:

1. Nach der unveränderten Berechtigung existiert **genau eine** Hypothese über
   alle Retained-Spuren und den Kandidaten: exakter Faktor ausschließlich1,
   Offset0 oder1, vorhandener Originalnachfolger. Kein Zählen bloß unterschiedlicher
   Ausgabewerte statt unterschiedlicher Hypothesen.
2. Diese einzige Hypothese gehört zum aktuell lebenden Kandidaten.
3. Beide neuen Hinweisordinalen liegen strikt nach dessen letztem Originalordinal
   im selben Scope. Keine Selbstbestätigung, keine Überschneidung und kein
   archivierter beziehungsweise nur noch eingefrorener Altbestand.
4. Steht mit der anschließenden Aufnahme gerade ein vollständiger Viererabschluss
   an und stimmen dessen bereits beobachtete vier Werte exakt mit irgendeiner
   lebenden Retained-Spur oder dem Kandidaten überein, **unterbleibt A1**.
   Die vorhandene vollständige Bestätigung hat Vorrang und läuft unverändert.
   Diese Prüfung benutzt ausschließlich schon beobachtete Werte des bildenden
   Blocks und des aktuellen Hinweispaars, niemals einen zukünftigen Frame.

Bei null oder mehreren berechtigten Hypothesen unterbleibt A1 vollständig.
Das gilt auch für zwei Offsets derselben Spur oder zwei Originalspuren mit
identischem Nachfolger. Bei genau einer Retained-Hypothese unterbleibt A1
ebenfalls: kein Aktualisieren ihrer Erhaltungsreihenfolge allein durch Abruf.
Unberechtigte Matches ohne Nachfolger oder mit anderem Faktor begründen weder
eine Zulassung noch eine Auswahl einer widersprüchlichen Fortsetzung.

Weder Fehlerwert, Wärme, Auswahlentscheidung, tatsächlicher Zielwert noch
Modalwert/Beobachterlabel entscheiden über A1. Die vollständige Kandidatenspur
bleibt unverändert; Teilspuren werden nicht ergänzt oder zusammengeführt.

## Einzige neue Zustandsänderung und Reihenfolge

Bei erfüllter Bedingung wird vor dem Einfrieren atomar ausgeführt:

1. Scope, Originalidentität, Kapazität und Generationsgrenze prüfen. Bei Fehler
   bestehender Fehlerabschluss; keine Teilveröffentlichung und kein Notfallslot.
2. Sind beide Retained-Plätze belegt, die nach bestehender Reihenfolge älteste
   Retained-Spur samt zugehörigen Fehlerzellen entfernen. Sind Plätze frei,
   wird keiner zusätzlich verdrängt. Keine zielwertabhängige Opferwahl.
3. Genau die vier vorhandenen Kandidatenframes in den frei gewordenen oder
   freien Retained-Platz verschieben und als neuesten Eintrag einordnen.
   Neue Retained-Generation, Kandidat leeren; keine neue Kandidatengeneration,
   keine Kopie der Originalframes, keine zweite Erhaltung desselben Kandidaten.
4. Vorhandene Fehlerzellen beider Offsets unter Beibehaltung ihrer ec/ep-Werte
   auf die neue Rolle/Generation übertragen; kalt bleibt kalt. Keine neuen
   Fehlerwerte aus dem Hinweis erzeugen. Vorher gelöschte Zellen bleiben gelöscht.
5. Den neuen Zustand veröffentlichen; für diese Zustandsänderung die Revision
   einmal erhöhen. Anschließend regulärer Abruf und Auswahl auf diesem Zustand,
   dann neue Prognose und neue Feedbacktickets einfrieren. Diese Tickets tragen
   von Anfang an die neue Retained-Generation. Keine Umschreibung offener Tickets.
6. Die beiden Hinweisframes normal aufnehmen und einen eventuell vollständigen
   bildenden Block nach U verarbeiten. Der Kandidatenplatz ist jetzt frei.
   Ein neuer abweichender Viererblock kann dort aufgenommen werden; er wird
   nicht wie bei K1 allein zum Schutz des alten Kandidaten verworfen.

Die erste lesende Bestandsprüfung ist eine Zulassungsprüfung, keine bereits
veröffentlichte Prognose. Der spätere Prognosereceipt muss die neue Revision
und die tatsächliche Retained-Herkunft abbilden. Die alte arithmetische Formel
für Revisionen allein aus Aufnahme-/Segmentzahlen gilt unter A1 deshalb nicht
mehr unverändert. Das ist ausdrücklich Teil einer späteren Umsetzung und
Referenzprüfung, kein angeblich unveränderter bestehender Aufrufpfad.

Da die einzige berechtigte Vorhersagehypothese vor der Änderung der Kandidat
war, konnte die eventuell verdrängte Retained-Spur zu diesem Zeitpunkt keine
weitere berechtigte Alternative liefern. Das sagt nichts über ihren späteren
Wert. Rohmatches und Status können sich mit dem Bestand ändern; keine Behauptung
identischer Receipts zwischen U und A1.

Für den vorhandenen Ordnungswert `_observation_end` erhält die neue Retained-Spur
zunächst das Ende ihrer ursprünglichen Viereraufnahme. Der Hinweiszeitpunkt
wird dort **nicht** als beobachtetes vollständiges Viererwiederauftreten
eingetragen. Eine spätere echte vollständige Bestätigung aktualisiert diesen
Wert und die Reihenfolge nach der bisherigen Regel.

Der externe Zulassungsbeleg muss den Grund `PARTIAL_RETRIEVAL_ADMISSION`,
Originalordinalen, Offset, Hinweisordinalen, alte/neue Schlüssel und das Opfer
benennen. Er darf nicht als `FULL_TRACE_RECONFIRMED` ausgegeben werden. Kein
zusätzlicher persistenter Herkunftstag ist für die Policy erforderlich: Ihre
spätere Behandlung hängt nicht vom Zulassungsgrund ab. Der externe Beleg
bleibt Diagnose, nicht neuer Policy-Eingang.

## Vollständiger Erfahrungszyklus

Sei C ein lebender Kandidat und h das Ende eines passenden neuen Hinweises.
A1 verschiebt C vor der Prognose für h+1 in einen Retained-Platz. Der unmittelbar
anschließende Viererabschluss kann C deshalb nicht mehr als Kandidaten ersetzen.
Er kann den freigewordenen Kandidatenplatz mit neuer Erfahrung belegen.

Trifft h+1 regulär ein, erhält das bereits unter dem neuen Schlüssel eingefrorene
Ticket sein Feedback vor der Aufnahme dieses Zieles. Die Retained-Spur ist bis
dahin nicht durch einen weiteren Kandidatenpromotionsvorgang verdrängt worden:
Es lagen nur die beiden gerade aufgenommenen Hinweisframes und höchstens ein
Abschluss bei zuvor leerem Kandidatenplatz dazwischen. Scopefehler oder Storyende
bleiben reguläre Abbruch-/Zensierungsgründe; kein Feedback wird erfunden.

Danach verbleibt die Spur nach der normalen Zweiplatzregel. Spätere echte
Bestätigungen aktualisieren sie wie bisher; spätere Zulassungen oder Promotionen
können sie verdrängen. Weitere bloße Abrufe verlängern oder verjüngen sie nicht.
Es gibt keine Garantie einer bestimmten Zeitspanne oder einer späteren Wiederkehr.

Erfolg erfordert einen **späteren weiteren berechtigten Abruf desselben
Originalspur-Offsets**, solange dessen verarbeitete Rückmeldung noch vorhanden
ist. Erst dann kann die unveränderte Fehlerauswahl diese Erfahrung nutzen.
Das erste kalte Feedback, ein Retained-Status oder eine erhaltene Zelle allein
sind kein Nutzenbeleg. Auch warme Erfahrung kann falsch vorhersagen.

Eine Promotion nach dem Einfrieren wäre hier kein gleichwertiger Ersatz:
Sie könnte erneut ein totes Ticket hinterlassen. A1 legt deshalb genau die
oben definierte Vorhersagegrenze fest; keine zweite zeitliche Variante.

## Budget und Verlustseite

| Ressource | A1-Vertrag |
| --- | --- |
| Retained-Spuren | Höchstens2 ×4 vorhandene Originalframes; gegebenenfalls älteste Spur vorher entfernen |
| Kandidat | Höchstens1 ×4; verschobener Kandidat wird sofort aus diesem Platz entfernt |
| Originalframes insgesamt | Unverändert höchstens18 einschließlich bildender Frames, Hinweise und eingefrorener Referenzen |
| Ausgaben / kombiniert | Höchstens2 /20 |
| Fehler-/Ticketbank |416 Byte, weiterhin höchstens6 Fehlerzellen und6 Tickets; In-place-Schlüsselwechsel, keine Zusatzzelle |
| Zusatzheap | Höchstens16.384 Byte einschließlich temporärer Zulassungsprüfung |
| Receipt / UTF8 | Höchstens16.384 /32.768 Byte einschließlich Zulassungsbeleg im geregelten Ausgabeumfang |
| Neue persistente Armmetadaten | Keine Zähler, Fristen, Schutzbits, zusätzlichen Spurlisten oder Historien |

Zählung der Berechtigten kann bei zwei abbrechen; für den eindeutigen Fall
genügen vorhandener Kandidatenverweis und Offset als temporäre Skalare.
Vorprüfung des vollständigen Blocks liest vorhandene Werte, ohne neue Frames
anzulegen. Move und In-place-Umschlüsselung brauchen keinen zusätzlichen
Speicherplatz für eine Spur. Allein daraus folgt keine gemessene Heap- oder
Laufzeitfreigabe. Eine spätere Implementierung muss auch temporäre Referenzen,
neue Receipts, Revision und Fehlerpfade innerhalb dieser Grenzen qualifizieren.
Falls das nicht gelingt, ist A1 technisch nicht abnehmbar; kein Grenzzuschlag.

Der unmittelbare Preis bei vollem Bestand ist **die älteste bislang erhaltene
Viererspur einschließlich ihrer möglicherweise warmen zwei Fehlerzellen**.
Sie hätte unter U ohne vollständige Wiederkehr des Kandidaten weiterbestehen
können. Neue eingehende Erfahrung darf im Kandidatenplatz zwar aufgenommen
werden; künftige Promotionen und Verdrängungen können dennoch anders ausfallen.
Keine Behauptung, dass A1 alte und neue Erfahrung gleichzeitig verlustfrei erhält.

Wird ein irreführender Kandidat zugelassen, kann er einen wertvollen Platz
belegen, bis reguläre Verdrängung eintritt. Auch ohne Abruf-Verjüngung kann das
lange dauern, wenn keine weiteren Zulassungen entstehen. Begrenzte Kapazität
bedeutet nicht begrenzte Verweildauer. Es gibt keinen zusätzlichen Vergessens-
oder Reparaturmechanismus innerhalb dieses Vorschlags.

## Nutzenprognose und Gegenprognose

Vergleich ist genau **U mit vollständiger Bestätigung gegen A1**, jeweils frisch
und mit identischen Eingaben, kompletter Zielmenge, Fehlerbewertung und Grenzen.
Keine Kombination mit K1 und keine Auswahl nur erfolgreich zugelassener Ziele.
Ein späterer Versuch benötigt vorab gebundene Quellen, Masken, Nenner und eigene
Referenzen; dieser Konzeptauftrag definiert keinen ausführbaren Lauf.

**Mechanistische Prognose:** Wenn ein eindeutiger neuer Teilhinweis einen noch
lebenden Kandidaten vor dessen sonstiger Ersetzung erreicht, kann A1 dessen
Rückmeldung unter einem gültigen Schlüssel verarbeiten und über den Kandidaten-
wechsel hinaus erhalten. Bei einer späteren Wiederkehr desselben Offsets vor
Retained-Verdrängung entstehen zusätzliche lebende Hypothesen mit vorherigem
Feedback gegenüber U. Zu zählen sind solche vollständigen Zyklen und tatsächliche
zusätzliche warme Wiederabrufe, nicht nur Zulassungen oder verarbeitete Updates.
Kein strikter Zuwachs widerlegt die erwartete mechanistische Verbesserung im
vorab gebundenen Vergleich.

**Nutzenprognose:** Der vollständige gleich gewichtete Fallvergleich muss
strikt niedrigeren MAE liefern, nicht bloß mehr Kontextwahl. Bei einem später
erneut beauftragten Vergleich der bisherigen T1/F-Fallmengen gelten die bereits
strengen getrennten Bedingungen: T1 strikt besser, F nicht schlechter und
Gesamtmittel strikt besser; Fall-Schadensgrenze1/32 und T1-G_w nicht schlechter.
Die Daten wären weiterhin bekanntes Entwicklungsmaterial. Diese Bedingungen
werden durch den Konzeptvorschlag nicht abgeschwächt oder neu freigegeben.

**Überprüfbare symbolische Konstellation, nicht materialisierte Quelle:**
Ein Kandidat A=(a,b,c,d) entsteht, danach B=(x,y,a,b), danach C=(c,z,a,b).
Alle Symbole stehen für getrennte beobachtbare Framewerte; x,y,z erzeugen
keine weiteren berechtigten Matches. Bei Abschluss von B ist (a,b) die einzige
berechtigte Kandidatenhypothese aus A, während B nicht gleich A ist.
U ersetzt A durch B. A1 übernimmt A vor dem Ticket für den ersten Wert von C.
Dieser Wert c liefert erstmals einen günstigen Fehlerwert. Der abschließende
Hinweis (a,b) von C erlaubt dann die spätere warme Nutzung von A. B bietet
(a,b) nur an Offset2 ohne Nachfolger und ist keine berechtigte Konkurrenz.
Folgt erneut c, ist der A-Nachfolger richtig; U hat weiterhin keinen
berechtigten A-Nachfolger und fällt auf Persistenz b zurück.

**Gegenfall mit häufigem irreführendem Hinweis:** Derselbe Verlauf bis
einschließlich C, aber nach dessen abschließendem (a,b) folgt a statt c.
Für beispielsweise auf allen Koordinaten a=1/4, b=1/2 und c=3/4 hatte A1
zuvor ec=0 und ep=1/4. Es wählt deshalb c; jetzt beträgt sein Fehler1/2
gegenüber Persistenzfehler1/4 bei U. Die Erhaltungsentscheidung konnte die
beiden möglichen Zukünfte nicht unterscheiden und darf das auch nicht.
Weitere Blöcke (a,z_i,a,b) mit jeweils anderen z_i lassen denselben Teilhinweis
häufig wiederkehren, ohne den ursprünglichen Viererblock A zu wiederholen.
EMA kann die Kontextwahl nach widersprüchlichem Feedback unterdrücken; daraus
folgt weder Rücknahme der Zulassung noch Rückgabe eines verdrängten Platzes.

Sind vor A bereits zwei andersartige vollständig bestätigte Spuren R und S
vorhanden, verliert A1 bei seiner Zulassung die ältere R. U behält R. Eine
spätere passende R-Abfrage kann daher zusätzlich eine zuvor warme Erfahrung
verlieren. R und S seien bei (a,b) nicht berechtigt, sodass der Gegenfall
die Eindeutigkeitsbedingung nicht umgeht. Diese Verlustseite muss in einem
späteren vollständigen Vergleich enthalten sein. Gemeinsame Teilhinweise mit
mehreren berechtigten Fortsetzungen lösen dagegen überhaupt kein A1 aus.

## Bezug zum Befund und Abnahmekriterien

Die abgeschlossene Diagnose begründet die notwendige Verbindung zwischen
Aufnahme, lebendigem Feedback und erneuter Nutzung. Sie belegt A1 nicht.
Insbesondere können die27 K1-Kandidaten am Zeitpunkt c+8 unter U längst
gelöscht sein. A1 darf sie dann nicht retten. Aus den31 K1-Zusatzvorkommen
wird keine A1-Erfolgszahl oder garantierte Zielmenge abgeleitet.

Vor einer Implementierungsabnahme wären mindestens eindeutige/kollidierende
Teilhinweise, mehrere Offsets, vollständige Bestätigung mit Vorrang,
Vorhersagegrenze und Revision, neue Tickets, Zellmitnahme, volles Zweiplatz-
Opfer, Scope-/Generationfehler, Ressourcen und der vollständige warme
Wiederabrufzyklus neutral zu prüfen. Eigene Referenzregel erforderlich;
das unveränderte U darf nicht als A1-Sollbestand verwendet werden.

**Empfehlung:** Diesen einen A1-Konzeptvorschlag einschließlich der geänderten
Retained-Bedeutung, der Vorhersagegrenze und der Verdrängungskosten prüfen.
Strukturell ist er innerhalb der vorhandenen Slots darstellbar; tatsächliche
Ressourceneinhaltung und Nutzen bleiben offen. Erst eine ausdrückliche weitere
Beauftragung darf die Implementierung und neutrale Qualifikation beginnen.
Kein Code geändert, keine Quelle erzeugt und kein Replay ausgeführt.
