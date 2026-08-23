# S1-WQ: Privater perzeptiver Zustandslebenszyklus

## Auftrag und Grenze

S1-WQ implementiert eine private, reine In-Memory-Zustandsmaschine fuer den
technischen Lebenszyklus begrenzter auditiver oder visueller
Wahrnehmungszustaende. Sie ist eine Engineeringgrundlage fuer die spaetere
Entwicklung einer MCM-kompatiblen perzeptiven Memory-Komponente. Aus S1-WQ
folgt kein Memory-Befund.

S1-WQ fuehrt keine zweite Prototyp- oder Speichermechanik ein. Der Baustein
verwendet den vorhandenen reinen PPB-1-Referenzkern genau einmal pro
akzeptiertem Schritt und ordnet dessen Ergebnis einer expliziten
Lebenszyklusrolle zu.

Nicht enthalten sind Datei- oder Produktionspersistenz, oeffentliche API,
Feldrueckwirkung, semantische Rollen, Woerter, innere Kontextuebergabe und
reale Feldlaeufe.

## Gebundene Uebergaenge

Die private Uebergangsakte unterscheidet genau diese Rollen:

- `PERCEPTUAL_STATE_FORMED`: Ein freier Platz wird erstmals belegt.
- `VALID_STATE_CONTINUATION_UPDATED`: Eine passende Exposition setzt einen
  noch nicht stabilisierten Zustand fort.
- `PERCEPTUAL_STATE_STABILIZED`: Der gebundene Stuetzschwellwert wird genau
  in diesem Schritt erreicht.
- `STABILIZED_STATE_UPDATED`: Ein bereits stabilisierter Zustand wird
  innerhalb seiner festen Grenze aktualisiert.
- `CAPACITY_STATE_DISCARDED_AND_REFORMED`: Bei voller Kapazitaet wird ein
  Zustand nach der bestehenden PPB-1-Regel verworfen und derselbe feste
  Platz neu belegt.

Zusaetzlich werden abgelaufene Zustaende in der Uebergangsakte ausdruecklich
als verworfen ausgewiesen. Abschwaechung bedeutet in S1-WQ daher keine neue
kontinuierliche Dynamik. Sie endet nach der vorhandenen schrittgebundenen
Ablaufregel oder durch begrenzten Kapazitaetsersatz im Verwerfen.

## Identitaet und Atomaritaet

Bank-ID, Konfigurationsdigest und die feste Menge der Platz-IDs bilden die
unveraenderliche Zustandsidentitaet. Inhalt, Stuetzung und Auswahlzeit eines
Platzes duerfen sich regelgebunden aendern; seine Identitaet darf es nicht.

Jede erfolgreiche Uebergangsakte bindet:

- Vorzustands-, Eingabe-, Nachzustands- und Referenzreadoutdigest;
- betroffenen Platz sowie Bildung, Aktualisierung, Stabilisierung und
  Verwerfen;
- genau einen akzeptierten Schritt und genau einen Referenzkernaufruf;
- null Teil-Commits, Retries, Dateisystemwirkungen und Feldrueckwirkungen.

Ungueltige Eingaben, widerspruechliche Rollen, Digestmanipulation und der
gesperrte Produktionseinstieg stoppen fail-closed. Nachzustand, Readout und
Uebergangsakte werden als ein unveraenderliches Ergebnis zurueckgegeben.

## Reproduzierbare Bindungen

- PPB-1-Referenzkerndigest:
  `9fad3b04661fb9b8da053afd5599e3bdfe73019681ae50115263c39f3052ca9d`
- S1-WQ-Quelldigest:
  `7b21391ee86ce597c9434d46fe3d76cf3d8dbe8a65f2da49555ad2b26a203954`
- Gebundener Digest der ersten Zustandsbildung:
  `b8fb740334314aa5ff2419accc24d2ab9fa73d60846a7298828a4e6e6b092371`

`14 von 14` neue S1-WQ-Vertragstests und `332 von 332` aktuelle fokussierte
PPB-1-Tests bestehen.

## Ergebnis und naechster Schritt

S1-WQ stellt den privaten technischen Zustandslebenszyklus reproduzierbar
dar. Es bestaetigt weder eine Feldrueckwirkung noch eine perzeptive
Memory-Funktion.

Der naechste Schritt ist S1-WR, ausschliesslich als statischer Audit des
S1-WQ-Quelltexts und seiner Bindung an den unveraenderten Referenzkern. Der
Audit darf keine S1-WQ- oder Referenzfunktion ausfuehren und keine Runtime-,
Feld- oder Produktionsintegration vornehmen.
