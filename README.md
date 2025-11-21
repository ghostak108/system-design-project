# System Design Project – EV3 Mehrzweck-Roboter

Dieses Projekt ist ein fortgeschrittener LEGO Mindstorms EV3 Roboter, der eine Vielzahl autonomer Aufgaben ausführt. Er kombiniert Linienverfolgung, Objekterkennung, dynamische Geschwindigkeitsanpassung, Ballaufnahme/-abwurf und Umgebungsanalyse (Licht + Steigung) mit durchgehender visueller und akustischer Rückmeldung auf dem EV3 Brick.

## Hauptfunktionen
- Linienverfolgung mit drei Farbsensoren (Links, Mitte, Rechts) und adaptivem Schwellenwert (gleitende Kalibrierung aus gemittelten Reflektionswerten)
- Suchmodus bei Linienverlust (alternierende Dreh-/Kurvenbewegungen bis Wiederfinden)
- Hinderniserkennung mit Ultraschallsensor (Rückzug, U-Turn, Reset der Suchhistorie)
- Ball-Erkennung über Farbe (Rot) oder Reflexionssignatur, Aufnahme mit Greifmechanik (Klaue + Arm), kontrollierter Abwurf auf hellen Markern
- Dynamische Geschwindigkeitsreglung nach Steigung (uphill/downhill), Lichtverhältnissen (dunkel/hell/normal) und Nutzlast (Ball transportiert)
- Kontinuierliche Anzeige des Zustands auf dem Display (Aktion, Sensorlinienstatus, Steigung, Licht, Ballzustand, Modus, Geschwindigkeit)
- Akustische Signale für Ereignisse (pickup, release, obstacle, lost, regain, line, init, search, track)
- Automatisches Re-Kalibrieren des Basis-Schwellenwerts bei langanhaltendem Linienverlust

## Hardware-Zuordnung (Ports)
- Motor Links: Port D
- Motor Rechts: Port A
- Arm-Motor: Port B
- Klaue-Motor: Port C
- Farbsensor Links: Port S1
- Farbsensor Rechts: Port S2
- Farbsensor Mitte: Port S4
- Ultraschallsensor: Port S3

## Zentrale States und Profile
- `line_state`: boolescher Status pro Sensor (links/mitte/rechts)
- `line_history`: zählt gefundene/verlorene Frames zur Suchlogik und Re-Kalibrierung
- `environment_state`: `incline` (flat/uphill/downhill), `light` (dark/normal/bright)
- `speed_profile`: gleitender Übergang zwischen aktueller und Zielgeschwindigkeit
- `search_mode`: kennzeichnet aktiven Suchzustand bei Linienverlust
- `ball_locked`: zeigt ob Ball sicher gehalten wird

## Steuerlogik (Ablauf pro Zyklus)
1. Reflektionswerte erfassen und Schwellenwert glätten
2. Linienstatus evaluieren und Historie fortschreiben
3. Lichtprofil aktualisieren und Klassifikation vornehmen
4. Steigung anhand Motor-Speed-Ratio abschätzen
5. Geschwindigkeitsschichtung anwenden (Steigung → Licht → Nutzlast)
6. Ballstatus prüfen und ggf. Aufnahme/Freigabe auslösen
7. Hindernis prüfen → bei Treffer Hindernisroutine (Halt, Rückzug, U-Turn)
8. Falls Linie erfasst: Normalsteuerung / Regain-Sequenz
9. Falls Linie verloren: Suchmuster fahren

## Akustik & Anzeige
Jede relevante Aktion ruft `announce(action)` auf, aktualisiert den Bildschirm und spielt einen spezifischen Signalton (Fallback auf Standardton falls nicht definiert). Dadurch lassen sich Zustandswechsel (z.B. Übergang von track zu search oder Aufnahme eines Balls) unmittelbar nachvollziehen.

## Erweiterungsmöglichkeiten
- Persistente Log-Ausgabe (z.B. auf SD-Karte oder seriell)
- Mehrstufiges Suchmuster (Spiralen, adaptive Drehgeschwindigkeit)
- Farbliche Marker für Ball-Abwurf (gezielte Positionierung statt Helligkeitsschwelle)
- Energiemanagement (Monitoring der Batteriespannung zur Anpassung der Dynamik)
- Multi-Ball Handling (State-Maschine mit Inventar-Zähler)

## Nutzung
1. Hardware gemäß Port-Zuordnung verbinden.
2. Programm (`finaler_code_abgabe.py` oder `rainbow_tank.py`) auf den Brick übertragen.
3. Starten: Hauptschleife beginnt automatisch mit Initialkalibrierung und Arm/Greifer-Initialisierung.
4. Beobachten: Display liefert Live-Telemetrie; Töne signalisieren Ereignisse.

## Team
Projekt von Noah, Lukas, Kai und Alex.

## Lizenz / Nutzung
Interne Projektarbeit; keine externe Lizenz angegeben. Bei Weiterverwendung bitte Quellen nennen.

## Hinweis
Kein Kommentar-Code im Implementierungsfile, um die geforderte Klarheit ohne Inline-Erklärungen zu wahren. Funktionale Semantik ergibt sich aus klaren Funktionsnamen und State-Struktur.



