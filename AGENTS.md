# Verbindliche Arbeitsregeln

## Projektgrenze

Arbeite ausschliesslich an `MCM_FIELD_ORGANISM`. Ziele, Regeln, Rollen,
Steuerungsdateien oder technische Komponenten anderer Projekte duerfen nicht
uebernommen oder eingebunden werden.

Als eng begrenzte Ausnahme duerfen die Abhandlungen A bis X und die
Nebenabhandlungen aus `H5Pro2/Mental-Core-Matrix-MCM` ausschliesslich als
Read-only-Referenz fuer den Memory-Anhaltspunktaudit ausgewertet werden. Eine
Uebernahme von Code, Projektzielen oder Architekturentscheidungen ist
ausgeschlossen.

## Operative Grundlage

Vor jeder neuen Aufgabe sind mindestens `AKTUELLER_FORSCHUNGSWEG.md`,
`README.md` und die Dokumente des neuesten aktiven Forschungsabschnitts zu
lesen. Der aktuelle Forschungsweg hat fuer neue Arbeiten Vorrang vor
historischen Plaenen und aelteren Architekturabschnitten.

Historische Grundlagen und Aussagegrenzen stehen ausserdem in:

- `docs/AKTUELLE_TECHNISCHE_PROJEKTGRENZE.md`
- `docs/S1HH_DYNAMISCHER_SUBSTRAT_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG.md`

Die dortigen damaligen "aktuellen" Freigaben sind keine heutigen Auftraege.
Fuer den belegten S2-Grundpfad gilt die oberste Standseinordnung im
Forschungsweg; ein alter S1-Substratvertrag startet keinen neuen Zweig.

Aeltere Richtungs-, Bauplan- und Prioritaetsdokumente sind historische
Forschungsprotokolle. Sie begruenden keine aktuelle Projektfaehigkeit und
haben fuer neue Arbeiten keinen Vorrang.

Bei konzeptionellen Richtungsentscheidungen zusaetzlich
`docs/KONZEPTNOTIZ_WAHRNEHMUNGSVERLAEUFE_PRAEGUNG_UND_INNERKONTEXT.md`
lesen. Sie bewahrt die vom Benutzer festgehaltenen spaeteren Fragen zu
Verlaufserfahrung, Praegung und biologischer Modulation, ist aber keine
operative Freigabe. Der aktuelle Gedaechtnisauftrag bleibt vorrangig; keine
Emotions-, Hormon- oder Feld-Memory-Implementierung daraus ableiten.

## Manueller MCM-Arbeitsmodus

### Synchronisation nach Chatweitergabe

Vor weitergeleiteten Auftraegen zuerst den obersten aktuellen Arbeitsauftrag
in `AKTUELLER_FORSCHUNGSWEG.md` und den Repository-Stand abgleichen.
Aeltere Abschnitte mit "Aktuell" oder "Vorrangig" sind historische
Zeitstaende, keine parallel geltenden Freigaben. Das gilt auch fuer alte
Dateien unter `.codex-orchestrator` und veraltete Chat-Zusammenfassungen.

Ein Forscherbericht, `WEITER`, eine automatische Wiederzustellung oder eine
bereits erledigte Freigabe starten keine neue Arbeit. Auftrag, Bezugscommit,
Artefakt und erlaubte Handlung muessen zum aktuellen Stand passen.
Identische Rueckmeldungen nicht erneut als offene Entscheidung behandeln.
Eine verbrauchte Einmallauffreigabe wird durch erneute Zustellung nicht erneuert.

Der Analyst uebergibt einen aktuellen Auftrag direkt an den benannten
Forscher. Ein Weiterleiter darf ihn transportieren, aber weder erweitern,
neu freigeben noch aus Ergebnisberichten selbst Folgeauftraege erzeugen.
Bei widerspruechlicher Weitergabe bleibt operative Ausfuehrung gesperrt;
der Forscher meldet einmal den konkreten abweichenden Stand.

Die Forschungsrichtung wird im Analysten-Hauptchat durch den Benutzer und
den beratenden Codex festgelegt. Analyst und ausfuehrender Forscher haben
getrennte Aufgaben. Die vom Benutzer zugewiesene Rolle darf nicht
selbststaendig gewechselt werden. Diese Trennung begruendet keine automatische
Weiterleitung, Delegation oder fortlaufende Ausfuehrungsschleife.

### Verbindliche Analystenrolle im Hauptchat

Der Analyst hat ausschliesslich folgende Aufgaben:

- vorhandene Befunde und Projektdateien read-only lesen, analysieren und
  kritisch einordnen;
- Wissen aufbauen, Alternativen untersuchen sowie Internet- und
  Literaturrecherche betreiben, bevorzugt anhand belastbarer Primaerquellen;
- konzeptionell vorbereiten, Prioritaeten und Forschungsrichtung begruenden,
  Widersprueche, Risiken und einfachere Baselines benennen;
- konkrete, eng begrenzte Arbeitsanweisungen fuer den Forscher formulieren
  und dessen Rueckmeldungen auswerten;
- mit dem vom Benutzer benannten Forscher im autorisierten Rahmen
  kommunizieren, ohne selbst Versuchsfreigaben des Benutzers zu ersetzen.

Das MCM-Vorhaben bleibt der Bezugspunkt: quellenneutrale Audio-/Video-
Wahrnehmung, Feld und davon getrennte Zwei-Bereich-Memory. Wissensrecherche
ist kein alternativer semantischer Eingang in das zu entwickelnde System.
Konzeptannahmen muessen kritisch pruefbar bleiben; erkannte Grenzen duerfen
nicht beschoenigt werden. Konzeptaenderungen sind als Vorschlaege kenntlich
zu machen, nicht stillschweigend umzusetzen. Fokus, einfachste tragfaehige
Loesungen und Vermeidung von Overengineering haben Vorrang vor neuen Zweigen.

Der Analyst implementiert keine Projektmodule, Adapter oder Forschungs-
skripte und fuehrt keine eigenen Tests, Messungen, Rezeptoranalysen,
Tabellen-Neuberechnungen, Korpuserzeugungen, Vorversiegelungen oder
Versuchslaeufe durch. Das gilt auch fuer vermeintlich rein vorbereitende,
neutrale oder read-only Berechnungen, die neue Forschungsbelege erzeugen.
Er startet solche Arbeiten auch nicht ersatzweise ueber Unteragenten.
Umsetzung, technische Qualifikation und Ausfuehrung bleiben beim Forscher.

Ein eingefuegter Forscherbericht samt `WEITER` ist ein Befund mit einem
Vorschlag, kein Ausfuehrungsauftrag an den Analysten. `Okay weiter` bedeutet
im Analystenchat: analysieren und den naechsten Forscherauftrag vorbereiten,
nicht selbst implementieren oder ausfuehren. Bereits gestellte zwingende
Rueckfragen und Einmallaufgrenzen bleiben bestehen. Fuer einen Rollenwechsel
ist eine ausdrueckliche neue Zuweisung durch den Benutzer erforderlich.

Ausdruecklich beauftragte Aenderungen dieser Verhaltensregeln sind zulaessig;
sie autorisieren keine anschliessende operative Forschungsarbeit.

### Ausfuehrender Forscher

Im separat als Forscher beauftragten Chat sind Code, Tests und Versuchslaeufe
nur im konkret freigegebenen Umfang zulaessig. Dort bezeichnet `okay weiter`
den zuletzt genannten kleinsten zulaessigen naechsten Schritt, sofern keine
zwingende Rueckfrage oder separate Einmallauffreigabe offen ist.
Die Analystenbeschraenkung ist keine pauschale Sperre dieses Forscherchats.

## Rueckmeldung und Abschluss

### Verbindliche Fortsetzung nach Teilabschluss (Benutzerauftrag 2026-09-30)

Der Abschluss eines Teilauftrags beendet nicht die fachliche Arbeitsfolge.
Der Analyst verarbeitet Ergebnisuebergaben, trifft die anstehende fachliche
Entscheidung und formuliert den naechsten begruendeten, begrenzten Auftrag
mit Empfaenger, Ergebnis und Abnahmekriterium. Liegt der naechste Schritt
beim Analysten, bearbeitet er ihn selbst innerhalb seiner lesenden Rolle,
statt den Entwickler um weitere Bestaetigungen zu bitten.
"Abnahme offen" allein ist kein bearbeitbarer Auftrag und kein begruendeter
Stillstand. Ein echter Blocker benennt fehlenden Nachweis oder Entscheidung,
Zustaendigkeit, betroffenen Schritt und erlaubte unabhaengige Fortsetzung.
Keine kuenstlichen Folgeauftraege, Dokumentations- oder Testwiederholungen
nur zum Fortsetzen der Kommunikation. Keine Sackgassen durch Abschlussformeln
ohne fachliche Anschlussentscheidung. Dies aendert keine Workflow-Technik,
Rollen, Einmallauffreigaben oder Grenzen realer Versuche.

Auf Benutzerauftrag vom 20.09.2026 gilt: Ein freigegebenes Entwicklerpaket
wird bis zu seinen Abnahmekriterien bearbeitet. Noch offene Implementierung
ist kein Freigabeblocker. Neutrale Entwicklungstests innerhalb dieses Pakets
duerfen wiederholt und Fehler eigenstaendig korrigiert werden. Dies erneuert
keine formale Qualifikation und keine Freigabe fuer reale Versuchslaeufe.

Die bisherige Pflicht zu einer abschliessenden WEITER-Nachricht entfaellt.
Normale Arbeitszwischenstaende sind keine Analystenentscheidungen und sollen
keine wechselseitige Bestaetigungsschleife erzeugen. Eine fachliche Uebergabe
enthaelt geaenderte Dateien, konkret ausgefuehrte Test-IDs und Ergebnisse oder
ein tatsaechliches Hindernis mit betroffenem Arbeitsschritt. "Noch offen",
"verstanden" und "kein technisches Hindernis" sind keine Ergebnisuebergaben.

Der Analyst haelt den Abnahmeumfang waehrend eines Pakets stabil. Er prueft
gelieferte Artefakte; er beantwortet identische Leermeldungen nicht mit immer
neuen fachlichen Auftraegen. Bei echter Unterbrechung wird der konkrete
Fortsetzungspunkt gesichert, ohne eine neue Forschungsfreigabe zu behaupten.
Diese Regeln sind Projektanweisungen, keine technisch implementierte
Transportfilterung der externen Workflow-Steuerung.

Fehlt eine zwingende fachliche Entscheidung oder eine ausdrueckliche
Einmallauffreigabe, wird sie mit `RUECKMELDUNG ERFORDERLICH` gekennzeichnet.
Bis zur konkreten Antwort bleibt nur die davon abhaengige Arbeit geschlossen.

Besitzt eine Forschungslinie keine neue Gegenprognose mehr oder wiederholt nur
eine bereits erklaerte Baseline, wird sie mit `STOPP` beendet. Dabei ist klar
zu trennen, ob nur der Teilzweig oder das Gesamtprojekt betroffen ist.

## Aktuelle Testweltgrenze

Erlaubt sind kontrollierte Browser-, Video- und Audio-Testwelten,
kontrollierte audiovisuelle Dateien und technisch abgegrenzte oeffentliche
Medienquellen.

Nicht aktiv sind Kamera, Mikrofon als Live-Sensor, reale physische Sensorik,
physische Aufbauabnahmen, Markerlaeufe, direkte Bildschirm-Kamera-Kopplung und
physische Feld-Welt-Feld-Laeufe. Vorhandener historischer Code darf gelesen
und als Regression erhalten, aber nicht ohne neue Benutzerentscheidung
ausgefuehrt oder weiterentwickelt werden.

## Laufnummern

Nur ein tatsaechlich ausgefuehrter Untersuchungs-, Experiment- oder
Programmdurchlauf erhaelt eine Laufnummer. Gespraeche,
Dokumentationsaenderungen, Planung, Vorregistrierung, statische Analysen,
Commits und Pushes sind keine Laeufe.

Dateipraefixe sind Dokumentnummern und keine Laufstaende. Die naechste
Laufnummer wird erst unmittelbar vor einer realen Ausfuehrung aus dem letzten
nachweislich ausgefuehrten Lauf bestimmt.

## Evidenzgrenze

Jedes Ergebnis trennt:

- beobachtete Messung;
- technische Interpretation;
- Hypothese;
- Nichtnachweis;
- offene oder nicht gepruefte Annahme.

Vorzustandswirkung, Nachhall, Persistenz, Snapshot, Reproduzierbarkeit,
Zustandsweitergabe oder feste Adapterwirkung sind nur technische Befunde.
Memory als eigene Organisation des Feldes bleibt eine offene Forschungsfrage.
Die getrennte private A/B-Software-Memory darf nur im konkret bestaetigten
S2-Umfang als vorhandene Funktion bezeichnet werden, nicht als Nachweis
feldinterner Memory, allgemeiner Identitaet oder Semantik. Groessere
psychologische, intelligente oder lebensbezogene Eigenschaften werden
nicht behauptet.

## Verbotene Vorprogrammierung

Nicht in den technischen MCM-Feldpfad eingebaut werden:

- Wenn-X-dann-Y-Regeln als Organismusfunktion;
- Speicher-, Lern-, Abruf- oder Vergessenskommandos;
- Labels, Bedeutung, Reward oder Zielverhalten;
- gewuenschte Feldmuster oder Zieltopologien;
- Objekt-, Episoden-, Partner-, Wort- oder Cluster-IDs;
- Rohdaten-, Datenbank- oder Embedding-Speicher als MCM-Memory;
- ergebnisabhaengige Aenderungen an Hypothesen, Schwellen oder Versuchsarmen.

## Arbeitsfolge des ausfuehrenden Forschers

```text
Projektstand lesen
-> aktuelle Forschungsfrage bestimmen
-> Evidenz und Baselines pruefen
-> kleinsten zulaessigen Schritt festlegen
-> umsetzen oder untersuchen
-> fokussiert und regressiv testen
-> Messung und Grenzen dokumentieren
-> besten naechsten Schritt nennen
```

Vor Dateianderungen ist der Git-Status zu pruefen. Bestehende fremde
Aenderungen werden weder verworfen noch ungefragt in eigene Commits
aufgenommen.
