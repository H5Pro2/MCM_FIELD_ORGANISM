# Visuelle Rezeptor-zu-Feld-Grenze

> **Historischer Architekturstand:** Die Rezeptorbefunde bleiben gültige
> Baselines; das getrennte visuelle MCM-Feld ist ersetzt durch das
> [gemeinsame MCM-Feld](024_GEMEINSAMES_MCM_FELD_ARCHITEKTUR.md).

## 1. Pfad

```text
endliche Videoquelle
-> lokale visuelle Rezeptorfläche
-> visuelle Rezeptorlage
-> visuelle MCM-Schnittstelle
-> technische visuelle MCM-Feldhülle
-> vollständiges Feldfenster
```

## 2. Erlaubte Rezeptorrollen

- technische Quell- und Rastergeometrie,
- Frameindex und technische Bildrate,
- stabile lokale Trägeridentitäten,
- aktuelle lokale Werte der drei Quellkanäle,
- exakter Kontaktstatus.

## 3. Gesperrte Rollen

Die lokale Kanalfläche und die technische Feldhülle dürfen nicht automatisch
umbenannt werden in:

- entwickelte visuelle Feldwirkung,
- Bewegung oder Richtung,
- visuellen Nachhall,
- Aufmerksamkeit oder Wichtigkeit,
- Form, Objekt, Person oder Szene,
- innere Bezeichnung oder Bedeutung.

## 4. Rohdatengrenze

Rohframes existieren nur während der technischen Rezeptortransformation. Hinter
der Grenze bleiben ausschließlich lokale skalierte Kanalwerte. Es werden keine
Bilder, Videofolgen oder Frameausschnitte gespeichert.

## 5. Freigabestatus

Die technische Rezeptorfläche trägt nach Methodik 014 **E1**. Der explizite
reale Kamerapfad trägt nach Methodik 016 bis zu dieser Rezeptorgrenze **E2**.
Die verlustfreie technische Rezeptorprojektion in eine visuelle MCM-Feldhülle
trägt nach Methodik 019 **E2**. Eine lokale visuelle Feldfunktion jenseits
dieser expliziten Baseline bleibt bei **E0**.

## 6. Bester nächster Schritt

Als Nächstes wird die saubere Schnittstelle in einer kontrollierten visuellen
Zeitfolge verwendet. Dabei werden nur Veränderungen der lokalen Feldlage
beobachtet; Bewegung, Form oder Objekt dürfen nicht vorab programmiert werden.
