# Sensorspezifischer MCM-Schnittstellenvertrag

> **Historischer Architekturstand:** Dieser Vertrag gehört zur verworfenen
> Mehrfeld-Baseline. Für die aktuelle Runtime gilt
> [Gemeinsames MCM-Feld](024_GEMEINSAMES_MCM_FELD_ARCHITEKTUR.md).

## 1. Zweck

Dieser Vertrag legt fest, was ein visuelles, auditives oder taktiles MCM an den
gemeinsamen MCM-Strang übergeben darf. Er definiert keine MCM-Gleichung und
keine konkrete Datenklasse.

```text
Sensor -> Rezeptoren -> sensorspezifisches MCM
       -> MCM-Schnittstellenzustand -> gemeinsamer MCM-Strang
```

Die Grenze verhindert, dass Rohsensorik, Entwicklerlabels oder fertige Muster
unbemerkt in die gemeinsame innere Lage gelangen.

## 2. Verbindliche Zustandsrollen

Ein Übergabezustand muss mindestens folgende Rollen tragen:

| Rolle | Bedeutung |
|---|---|
| `modality_id` | Technische Herkunft, etwa visuell, auditiv oder taktil |
| `channel_id` | Stabile technische Identität dieses Sensorastes |
| `snapshot_id` | Eindeutige Identität des gelesenen Zustandszeitpunkts |
| `timestamp` | Gemeinsame kausale Systemzeit |
| `geometry_id` | Version der offen dokumentierten Trägergeometrie |
| `carrier_ids` | Stabile technische Identitäten der lokalen MCM-Träger |
| `activation` | Gegenwärtige lokale Aktivierungsstruktur |
| `afterimage` | Gegenwärtige lokale Nachhallstruktur |
| `local_resources` | Aktuell verfügbare lokale Kapazitäten, sofern definiert |
| `presence` | Zustand des Sensorastes und seines Kontakts |
| `validity` | Technische Gültigkeit und bekannte Ausfälle |

Diese Namen beschreiben Rollen. Die spätere Implementierung darf eine andere
technische Form wählen, muss aber dieselben Unterscheidungen erhalten.

## 3. Kontakt- und Präsenzzustände

Mindestens getrennt bleiben:

- **Kanal fehlt:** Sensor oder Adapter ist nicht vorhanden.
- **Kanal nicht verfügbar:** Technischer Ausfall oder ungültiger Frame.
- **Kein aktueller Kontakt:** Kanal ist gültig, empfängt aber keine aktuelle
  Weltenergie oberhalb seiner technischen Auflösung.
- **Aktiver Nullzustand:** Ein gültiger Kontakt erzeugt nach der
  Rezeptortransformation einen numerischen Nullzustand.
- **Aktiver Feldzustand:** Das sensorische MCM trägt gegenwärtige Aktivität oder
  Nachhall.

Ein Nullvektor darf diese Fälle nicht zusammenfassen.

## 4. Atomarer Schnappschuss

Alle Werte eines Übergabezustands stammen aus demselben abgeschlossenen
MCM-Zeitschritt. Der gemeinsame Strang darf keinen teilweise aktualisierten
Zustand sehen.

Bei demselben vorherigen Gesamtzustand und denselben aktuellen
Rezeptorkontakten muss jede technische Ausführungsreihenfolge denselben
Übergabezustand erzeugen.

## 5. Erlaubte Inhalte

Erlaubt sind ausschließlich technische und intern erzeugte Feldzustände:

- lokale Aktivität und Polarität
- lokale Nachhalllage
- technische Träger- und Geometrieidentität
- lokale Ressourcenlage
- Zeit- und Gültigkeitsinformation
- dokumentierte numerische Grenzfälle

## 6. Verbotene Inhalte

Nicht übergeben werden:

- Rohbilder, Audioframes oder Berührungsepisoden
- Objekt-, Personen-, Sprecher- oder Kontaktklassen
- Pattern- oder Episoden-IDs
- Wörter, Bedeutungen oder Emotionen
- Wichtigkeit, Aufmerksamkeit, Reward oder Zielwerte
- globale Ähnlichkeit und externe Memorytreffer
- Observerdiagnosen
- vorgefertigte multimodale Merkmale

## 7. Erweiterung um neue Sensoren

Ein neuer Sensor wird als neuer Ast ergänzt:

```text
neuer Sensor
-> eigener Rezeptorvertrag
-> eigenes sensorspezifisches MCM
-> derselbe Schnittstellenvertrag
-> neuer lokaler Anschluss am gemeinsamen Strang
```

Bestehende Sensoräste dürfen dafür nicht semantisch neu definiert werden. Eine
Erweiterung muss nur technische Geometrie und lokale Anschlussmöglichkeiten
ergänzen.

## 8. Pflichtinvarianten

1. Keine Zukunftsinformation.
2. Keine Abhängigkeit von Iterationsreihenfolge.
3. Keine Rohsensorik hinter der Schnittstelle.
4. Keine semantische oder observerseitige Kennung.
5. Modalitäts- und Kanalherkunft bleiben erhalten.
6. Fehlender Kanal und aktiver Nullzustand bleiben unterscheidbar.
7. Aktivierung und Nachhall stammen aus demselben Zeitschritt.
8. Träger- und Geometrieidentitäten sind stabil und reproduzierbar.
9. Numerische Grenzen sind offen dokumentiert.
10. Der Observer kann entfernt werden, ohne den Zustand zu verändern.

## 9. Nullprüfungen

- Sensorast vollständig entfernen.
- Gültigen Kanal ohne Kontakt einspeisen.
- Aktiven Nullkontakt einspeisen.
- Nur Nachhall ohne aktuellen Kontakt prüfen.
- Modalitäten in anderer technischer Reihenfolge berechnen.
- Einen Zustand verzögert oder doppelt anbieten; beides muss erkannt werden.
- Observer vollständig deaktivieren.
- Trägerkennungen bei gleicher Geometrie permutieren und die erwartete lokale
  Abbildung separat prüfen.

## 10. Freigabegrenze

Dieser Vertrag gibt nur eine passive Schnittstellenprüfung frei. Er gibt keine
Sensorhardware, Rezeptorformel, Feldgleichung, multimodale Kopplung,
langfristige Beziehung oder Lernregel frei.

## 11. Bester nächster Schritt

Die Rollen werden gemäß
[Methodik 001](../methodik/001_PASSIVE_SENSORSCHNITTSTELLEN_PRUEFUNG.md) in
einem mechanikfreien Testobjekt mit synthetischen Zuständen geprüft. Erst wenn
alle Invarianten tragen, darf eine konkrete sensorspezifische MCM-Dynamik
vorgeschlagen werden.
