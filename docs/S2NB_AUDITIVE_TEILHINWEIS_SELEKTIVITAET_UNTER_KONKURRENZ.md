# S2-NB: Auditive Teilhinweis-Selektivitaet unter Konkurrenz

## Frage und Aussagegrenze

Wie stark veraendert das Weglassen der oberen 24 Spektralbaender die
auditive Treffermenge unter den tatsaechlich verbliebenen A-Konkurrenten?
Bleibt die Konkurrenz auch im vollstaendigen Rezeptorprofil bestehen?

Dieser enge read-only Vergleich bindet seine Messregeln vor der neuen
Auswertung. Er verwendet bereits bekannte, eingefrorene Quellen und ist
deshalb eine Diagnose, kein unabhaengiger Transfer- oder Lerntest.
S2-MT Lauf 05 bleibt `S2MT_FUNCTION_FALSIFIED`; Lauf 04 bleibt
`NOT_EVALUABLE`. Es wird kein neuer Memorylauf vorbereitet.

## Eingefrorene Eingaben

Verwendet werden ausschliesslich die vorhandenen Dateien:

- `reports/s2mt/s2mt-presealed-transfer-runtime-20260906-05/result.json`,
  SHA-256 `2de06dfc17728fd1c9aa7793e616e5a530cbf716306431117ce9dce4325d886f`;
- `reports/s2mw/s2mw-audio-receptor-compatibility-20260906-02/result.json`,
  SHA-256 `b1ca1ad9d11e29c6d5b547d166741f1afbf40fb3e8f240ea6eb07d3f4e7d87ef`.

Die 13 `scaled_outputs` enthalten die tatsaechlich erzeugten 48-Werte-
Rezeptorausgaben. Vor jeder arithmetischen Auswertung sind kanonische
Recorddigests, Vektor-Bytedigests und PCM-Bindungen zum skalierten Plan zu
pruefen. Die historisch falsche interne Audit-ID wird weder korrigiert
noch als alleiniger Identitaetsbeleg verwendet.

Es gibt keine neue PCM-Erzeugung, Rezeptoranalyse, Skalierung oder
Rekonstruktion eines Vektors aus seinem Digest.

Die vier Hinweise sind in der Reihenfolge e21/n00, e23/n01, e25/n02,
e27/n12 gebunden. Fachliche Rollen A/B/C/unbekannt stehen ausschliesslich
in der getrennten nachgelagerten Bewertung.

## Vollstaendige Konkurrenzbindung

Jeder Hinweis wird gegen alle neun finalen B4-Eintraege und alle drei
finalen Fast-Slots betrachtet, ohne vorzeitigen Abbruch:

- B4: Formationen 12 bis 20, zugehoerige Eingaben n03 bis n11;
- Fast 000: n10, Formation 19;
- Fast 001: n11, Formation 20;
- Fast 002: n09, Formation 18.

Die B4-Zuordnung ist ueber Formationsbeleg und Fast-Geschwisterbindung
nachzuweisen. Fast-Werte werden gegen ihre gespeicherten Slot-Vektordigests
geprueft. Doppelte Werte in verschiedenen Slots bleiben verschiedene
Treffer; sie duerfen die vorhandene Bankmehrdeutigkeit nicht verdecken.

Zusaetzlich wird jeder Hinweis gegen n00/n01/n02 als urspruengliche
Lernrezeptorwerte verglichen. Diese drei Referenzen sind ausdruecklich
keine finalen Slow-Prototypen. Deren Werte sind nicht gespeichert; ihre
Digests erlauben keine Wiederherstellung. Es wird daher keine genaue
finale Slow-Treffermenge und keine neue A/B-Zulassungsentscheidung behauptet.

## Zwei fest gebundene Messarme

1. `OBSERVED_24`: Baender 0 bis 23, identisch zur S2-KZ-Sicht.
2. `FULL_48_DIAGNOSTIC`: Baender 0 bis 47 derselben gespeicherten
   Rezeptorausgabe als Vollinformationskontrolle.

Der zweite Arm besitzt mehr Eingabeinformation. Er ist keine nachtraegliche
Erweiterung des Teilhinweises und kein ausfuehrbarer Ersatzscanner.
Verdeckte Werte werden im Teilhinweisarm weder benutzt noch ergaenzt.
Weitere Masken, Bandgewichtungen oder normalisierte Spektralformen sind
nicht Teil des Vergleichs.

Fuer jeden Arm gilt die ungewichtete mittlere L1-Distanz in aufsteigender
Bandreihenfolge mit Binary64-Operationen:

```text
d_I(q, x) = sum(abs(float(x[i]) - float(q[i])) for i in I) / len(I)
```

Der bestehende A-Wert `0.2` und der Slow-Referenzwert `0.02` bleiben fest.
Match bedeutet `distance <= threshold`; keine Floatgleichheit, Rundung,
Toleranz oder neue globale Schwelle. Die Grenzwerte sind gegen die
gebundene Konfiguration zu pruefen, ohne Projektfunktionen aufzurufen.
Der Vollprofilarm nutzt dieselben Zahlen nur diagnostisch; damit wird
keine neue Abrufregel qualifiziert.

## Messumfang und Bericht

Pro Arm entstehen 48 A-Beziehungen (vier Hinweise mal zwoelf Slots) und
zwoelf Lernreferenzbeziehungen. Beide Arme umfassen zusammen 120
Distanzwerte und exakt `60 * (24 + 48) = 4320` absolute Wertdifferenzen.
Die neun B4- und drei Fast-Rollen bleiben in der Ausgabe getrennt.

Zu berichten sind je Hinweis, Arm und Slot:

- Quellen-/Vektorbindung, Bank, Slot und Formationsbezug;
- Distanz, geltender Vergleichswert und vorzeichenbehaftete Reserve
  `threshold - distance`;
- Trefferstatus, vollstaendige indexgeordnete Treffermenge je Bank;
- Anzahl 0/1/mehrere Treffer und Veraenderung zwischen beiden Armen.

Die zwoelf Lernreferenzbeziehungen erhalten denselben Distanzbericht,
aber keine Slot-, Stabilitaets- oder B_STABLE-Behauptung.
Die direkte arithmetische Vergleichsbasis bleibt labelblind. Die
Auswertungsrollen duerfen nur die fertigen Tabellen interpretieren.
Es wird weder ein Gewinner gewaehlt noch die A-Konkurrenz uebergangen.

## Vorab gebundene Interpretation

- Weniger A-Treffer im Vollprofil: Weggelassene Baender tragen auf diesen
  Quellen zur Trennung bei. Das allein qualifiziert keine neue Maske.
- Weiterhin mehrere A-Treffer im Vollprofil: Zusaetzliche Baender allein
  loesen die Konkurrenz bei der bestehenden A-Regel nicht.
- Unterschiedliche Wirkungen je Hinweis: regulaerer gemischter Befund.
- Eine entstehende Eindeutigkeit beweist ohne Kandidatenidentitaet und
  verfuegbare Slow-Werte weder korrekte Erinnerung noch Kontextzulassung.

Kein geometrisches Ergebnis ist technischer Ausschlussgrund. Nur Quellen-,
Digest-, Form- oder Rechenfehler machen den Vergleich `NOT_EVALUABLE`.
Es gibt keine Variantenauswahl, keinen Mindestgewinn als Startgate und
keine nachtraegliche Anpassung anhand der Distanzen.

## Durchfuehrungsgrenze

Dieser Stand ist ausschliesslich ein statischer Vergleichsplan.
Die neue Tabellenberechnung wurde noch nicht ausgefuehrt. Fuer die spaetere
einmalige Auswertung genuegen vorhandene JSON-Belege und reine Arithmetik;
eine neue Runner-/Recorderarchitektur ist nicht erforderlich.
Rezeptor, Memory, Runtime, Kontext und Feld bleiben unaufgerufen.

Vor einer spaeteren unabhaengigen Bestaetigung muesste ein neues Korpus
vor jeder Rezeptoranalyse versiegelt werden. Dieser Diagnosevergleich
ersetzt eine solche Vorversiegelung nicht und autorisiert keine neue
Memorymechanik, B_STABLE-Praeferenz oder Schwellenanpassung.
