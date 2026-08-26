# W6-F: Fake-Capture und Organismuszeit-Handoff fuer H_A, H_B und P

Stand: 2026-08-09

Entscheidung: `W6F_FAKE_CAPTURE_TIME_HANDOFF_TECHNICALLY_ACCEPTED`

Arbeitsart: technische Implementierung und deterministische Fake-Abnahme

Runtimeaenderung: ja, additive S1-B-Referenzoberflaeche

Browserprozess gestartet: nein

Formaler Forschungslauf: nein

## Entwicklungsfrage

Koennen die drei in W6-E statisch gebundenen Browserweltteile H_A, H_B und P
ueber die echte Browser-Rezeptorbruecke reduziert, digestgebunden und auf
einen fortlaufenden Organismuszeitplan uebergeben werden, ohne einen Browser
zu starten oder Rohpayloads in den Feldpfad zu tragen?

## Implementierter Zeitplan

`s1b_causal_capture_schedule()` bindet eine gemeinsame Uhr:

```text
clock_id:          organism.w6f.browser.ns
ticks_per_second:  1_000_000_000
H_A:               [0, 900_000_000]
H_B:               [0, 900_000_000]
P:                 [900_000_000, 1_800_000_000]
```

H_A und H_B sind alternative Formationen und besitzen deshalb exakt dieselbe
Zeitstuetze. P liegt fuer beide disjunkt und unmittelbar danach. Die
Zeitstempel werden bereits durch getrennte `BrowserReceptorBridgeConfig`-
Objekte erzeugt; es gibt keine nachtraegliche Umschreibung fertiger
Rezeptorframes.

## Implementierter Capture-Handoff

`mcm_field_organism/s1b_causal_capture_handoff.py` stellt bereit:

- `S1BCausalCaptureSchedule`;
- `S1BCausalCaptureHandoff`;
- `prepare_s1b_causal_capture_handoff(...)`;
- `run_s1b_causal_capture_handoff(...)`.

Die Vorbereitung akzeptiert ausschliesslich drei vollstaendige Paare aus
`BrowserReceptorSequenceBatch` und `BrowserPayloadCaptureReceipt`. Geprueft
werden:

1. Weltvertrags-ID und Weltvertragsdigest;
2. Quellen-ID und Quellendigest;
3. Batchdigest und Receiptbindung;
4. identisches lokales Assetinventar aller drei Captures;
5. freigegebener Audio-Rohpuffer und keine Rohpayloadhaltung;
6. gemeinsame Organismusuhr;
7. identische reduzierte H_A/H_B-Zeitstuetzen;
8. vollstaendige Formations- und Probezeitfenster;
9. unveraenderte Referenz auf das immutable P-Sequenzobjekt.

Erst ein gueltiger Handoff darf das gemeinsame Anfangsfeld aus den bereits
reduzierten ersten Rezeptorframes aufbauen und den W6-E-Vierarmadapter
aufrufen.

## Deterministische Fake-Capture

Die Tests verwenden ein lokales `FakePage`-Objekt, das genau die von
`capture_browser_payload_page()` verlangte Seitenoberflaeche implementiert:

- lokale Assetrequests;
- deterministische PNG-Frames;
- deterministische Offline-Sinus-Audiobloecke;
- explizite Audiofreigabe.

Es werden die produktive `capture_browser_payload_page()`-Funktion, echte
`LocalChannelGridReceptor`- und `BroadbandHearingPath`-Instanzen sowie der
produktive `BrowserReceptorBridge` verwendet. Nur Seiten- und
Browserprozessverhalten sind gefakt.

Beobachtete deterministische Fake-Batchdigests:

```text
H_A: 6d9b9b0fbbeb0bbc32593bd2d8607767a13a2d50c0d8f5f294f033ba3c389a4f
H_B: 730f18610b7287dc24492c9100eec61d4df604967b968bed8b45e14bea3d25fd
P:   c2b5971090048495f0b157e1cdf08a74af6fe26c9623ead3314cdae5a5bf346d
```

Diese Digests beschreiben nur die Test-Fakes. Sie sind keine erwarteten
Digests eines spaeteren Browserlaufs.

## Technische Abnahme

Geprueft wurden:

- exakt ausgerichtete alternative Formationen und disjunkte Probe;
- vollstaendige echte Rezeptorreduktion aller drei Fake-Payloads;
- Freigabe aller Audio-Rohpuffer;
- Objektidentitaet der gemeinsamen P-Sequenzen im Handoff;
- vollstaendiger R/N/X/Z-Weg aus Fake-Captures;
- exakter Nullarm gegen neutrale Runtime;
- technisch aufgeloeste konstruierte L-nach-S-Rueckwirkung;
- Abweisung eines falsch zugeordneten Receipts;
- identische Batchdigests und Ergebniscontainer in zwei unabhaengigen
  Fake-Capture-Wiederholungen.

Zusammen mit allen angrenzenden S1-B-, API-, neutralen Runtime- und AV-Tests
bestehen 65 Tests. Die neuen Module kompilieren fehlerfrei.

## Technisches Ergebnis

Der Fake-Capture-Pfad erreicht
`LOCAL_L_STATE_CAUSALLY_ALTERS_LATER_S_TRAJECTORY_IN_S1B_REFERENCE`. Dieses
Urteil bestaetigt nur, dass Browserquellenvertrag, echte Rezeptorreduktion,
Zeituebergabe, L-Interventionen und Metriken technisch miteinander verbunden
sind. Da die Seite gefakt ist und die Rueckwirkung konstruiert wurde, ist dies
kein Forschungsbefund.

## Aussagegrenze

W6-F belegt keine Praegung, Wiedererkennung, Rekonstruktion, Loesung,
Wiederverwendung, Feldzeit, Organisation, Topologie, Semantik,
Selbstregulation, Memory oder KI. Es wurde kein Browserprozess gestartet und
kein formaler Lauf erzeugt. Lauf 197 bleibt reserviert und unberuehrt.

## Bester naechster Schritt

W6-G registriert und prueft statisch den einmaligen kontrollierten
Browser-Ausfuehrungsvertrag. Vor jeder Ausfuehrung muessen lokales
Assetinventar, Browserbinary und Runtimeversion digestgebunden, genau drei
isolierte Seitenkontexte festgelegt und ein eindeutiger neuer Reportpfad
reserviert werden. W6-G selbst startet noch keinen Browser.
