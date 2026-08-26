# S1-WP: Statischer PPB-1-Frische-/Einmaligkeits-/Verbrauchsvertrag

## Auftrag und Grenze

S1-WP bindet ausschliesslich statisch die Voraussetzungen fuer eine spaetere
Frischepruefung und einen einmaligen Autorisierungsverbrauch vor H1. Es wurde
keine Runtime, kein Adapter und keine Dateioperation implementiert oder
ausgefuehrt.

Nicht freigegeben und nicht erfolgt sind:

- Receipt-, Adapter- oder Koordinatorausfuehrung;
- Produktionsautorisierungsinstanziierung;
- Lock- oder Terminalschreibvorgang;
- PPB-1-Produktion;
- realer Feld-, Rezeptor- oder Medienlauf;
- Baselineausfuehrung oder Vergleichsurteil.

## Kausale Frische

Frische wird nicht aus Systemzeit, Dateialter oder einem Zeitfenster
abgeleitet. Sie besteht nur, wenn Autorisierung und unmittelbarer H0C-
Ressourcengatedigest derselben lueckenlosen H0A-bis-H0E-Digestkette
angehoeren und die Ausfuehrungs-ID in keiner Lock-, Erfolgs-, Fehler- oder
Temporaerrolle vorhanden ist.

Eine zwischen H0C und H1 neu entstandene Ressourcenbeobachtung, Digestdrift,
ein belegter Artefaktpfad oder eine bereits bekannte Ausfuehrungs-ID machen
die Bindung stale und sperren H1.

## Einmaligkeit und Commitpunkt

Der Vertrag erlaubt genau zwei positive Zustandsuebergaenge:

```text
F0_UNSEEN
  -> F1_FRESH_H0D_VALIDATED_UNCONSUMED
  -> F2_H1_LOCK_COMMITTED_AUTHORIZATION_CONSUMED
```

Der einzige Verbrauchs-Commitpunkt ist ein vollstaendiger, kanonischer,
dauerhaft sichtbarer und exklusiv ohne Ersetzen erzeugter H1-Lock. Es gibt
keinen getrennten Verbrauchsmarker. Der Lock bindet Ausfuehrungs-ID,
Autorisierungs- und Ressourcengatedigest, Vertrags-, Kalibrierungs-, Plan-
und Quelldigests sowie Budgets, `authorization_consumed = true` und
`retry_permitted = false`.

Lockumschreiben, Lockloeschen, H2 vor Commit sowie Wiederverwendung von Text,
Digest oder Ausfuehrungs-ID sind verboten. Aufraeumen gibt eine ID nicht
wieder frei.

## Fail-Closed-Regeln

Sechs Regeln trennen:

- wiederverwendete Ausfuehrungs-ID;
- stale Autorisierungs- oder Ressourcenbindung;
- belegte oder widerspruechliche Artefaktrolle;
- partiellen, fehlerhaften oder nicht beweisbar atomaren H1-Zustand;
- Widerspruch zwischen Verbrauch und Lock-Sichtbarkeit;
- Fehler nach vollstaendig committed H1.

Jeder Fall bindet ausdruecklich `NO_RETRY`. Unklare oder partielle
H1-Zustaende quarantinieren die Ausfuehrungs-ID und erlauben weder Reparatur
noch H2. Nach vollstaendig committed H1 bleibt der Lock bestehen; ein
spaeterer Fehler darf nur einen terminalen Fehler erzeugen.

## Produktions- und Vergleichsgrenze

Alle sechs bisherigen Produktionsblocker bleiben unveraendert offen. Die
spaetere Vergleichsrichtung bleibt bei gleichen Eingabe-, Kapazitaets- und
Probebudgets gebunden an:

- No-Memory;
- Replay oder Rohdatenzugriff;
- einfache statische Prototypbank oder Vektorquantisierung;
- gleitende Statistik oder Nachhall;
- Attraktor- oder Hopfield-artige Variante;
- begrenzten dynamischen Reservoirzustand.

Vor dieser Produktionsgrundlage gibt es weder einen PPB-1-Vergleichsbefund
noch einen MCM-spezifischen Memory-Befund.

## Kanonische Bindung

Vertragsdatei:

```text
S1WP_PPB1_FRISCHE_EINMALIGKEITS_UND_VERBRAUCHSVERTRAG_V1.json
```

Vertragsdigest:

```text
905d7cb4da886a2e7d819938ebcae4108863f027dee6bbbf2c4823eb5c167850
```

Die zehn neuen Tests pruefen kanonischen Digest, Parentbindungen, kausale
Frische, Zustandsmaschine, Nichtwiederverwendung, atomaren H1-Commit,
Fail-Closed-Regeln, sechs Produktionsblocker, Vergleichsrichtung und
vollstaendige Verbote. Zusammen bestehen `318 von 318` aktuelle fokussierte
PPB-1-Tests.

## Genau ein naechster Schritt

S1-WQ darf ausschliesslich die private reine In-Memory-Zustandsmaschine aus
S1-WP und synthetische Vertragstests implementieren. Keine Dateioperation,
kein Lockwriter, keine reale Frischepruefung, keine Autorisierung, kein
Receipt-/Koordinatorlauf und keine PPB-1-, Feld- oder Baselineausfuehrung.

## Grundlagen

- [Kanonischer S1-WP-Vertrag](S1WP_PPB1_FRISCHE_EINMALIGKEITS_UND_VERBRAUCHSVERTRAG_V1.json)
- [S1-WO statischer Receipt-/Kompositionspreflight](S1WO_PPB1_STATISCHER_RECEIPT_KOMPOSITIONSPREFLIGHT.md)
- [S1-WG statischer Integrationsdelta-Vertrag](S1WG_PPB1_STATISCHER_PRODUKTIONSINTEGRATIONSDELTA_VERTRAG.md)
