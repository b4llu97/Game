# Jarvis AI - Vollständige Test-Anleitung

Diese Anleitung führt dich durch das komplette Setup und Testing aller Jarvis-Services.

## 📋 Inhaltsverzeichnis

1. [System-Voraussetzungen](#system-voraussetzungen)
2. [Installation & Setup](#installation--setup)
3. [Service-Tests](#service-tests)
4. [End-to-End Tests](#end-to-end-tests)
5. [Fehlerbehebung](#fehlerbehebung)

---

## System-Voraussetzungen

### Hardware
- **CPU**: 4+ Cores empfohlen
- **RAM**: Mindestens 8GB, 16GB empfohlen
- **Disk**: 20GB freier Speicher

### Software
- Docker (Version 20.10+)
- Docker Compose (Version 2.0+)
- curl (für API-Tests)

### Installations-Check
```bash
docker --version
docker-compose --version
curl --version
```

---

## Installation & Setup

### 1. Repository klonen
```bash
git clone https://github.com/b4llu97/Jarvis.git
cd Jarvis
```

### 2. Umgebungsvariablen konfigurieren

**Basis-Konfiguration (bereits vorhanden):**
```bash
cat config/.env
```

**Optional: Telegram-Bot konfigurieren**
```bash
# Falls du Telegram-Benachrichtigungen nutzen möchtest:
nano config/.env

# Füge hinzu oder ersetze:
TELEGRAM_BOT_TOKEN=dein_bot_token
TELEGRAM_CHAT_ID=deine_chat_id
```

**Telegram-Bot erstellen:**
1. Öffne [@BotFather](https://t.me/botfather) in Telegram
2. Sende `/newbot` und folge den Anweisungen
3. Kopiere den Bot Token
4. Sende eine Nachricht an deinen Bot
5. Hole deine Chat ID: `https://api.telegram.org/bot<TOKEN>/getUpdates`

### 3. Services starten
```bash
# Alle Services im Hintergrund starten
docker-compose up -d

# Warte ~30 Sekunden, damit alle Services hochfahren
sleep 30

# Status prüfen
docker-compose ps
```

**Erwartete Ausgabe:**
```
NAME                   STATUS          PORTS
jarvis-asr            Up              0.0.0.0:8004->8004/tcp
jarvis-chroma         Up              0.0.0.0:8001->8000/tcp
jarvis-ingestion      Up              
jarvis-llama          Up              0.0.0.0:11434->11434/tcp
jarvis-orchestrator   Up              0.0.0.0:8003->8003/tcp
jarvis-proactivity    Up              0.0.0.0:8006->8006/tcp
jarvis-toolserver     Up              0.0.0.0:8002->8002/tcp
jarvis-tts            Up              0.0.0.0:8005->8005/tcp
```

### 4. LLM-Modell herunterladen
```bash
# llama3.1 (8B Parameter, ~4.9GB) herunterladen
docker exec jarvis-llama ollama pull llama3.1

# Fortschritt wird angezeigt
# Dauer: ~5-10 Minuten je nach Internetverbindung
```

---

## Service-Tests

### Test 1: Health-Checks aller Services

```bash
echo "=== Testing Health Endpoints ==="

# 1. Toolserver
echo "1. Toolserver:"
curl -s http://localhost:8002/health | jq
# Erwartete Ausgabe: {"status":"healthy"}

# 2. Chroma
echo "2. ChromaDB:"
curl -s http://localhost:8001/api/v1/heartbeat | jq
# Erwartete Ausgabe: {"nanosecond heartbeat": <timestamp>}

# 3. Ollama/LLM
echo "3. Ollama:"
curl -s http://localhost:11434/api/tags | jq '.models[].name'
# Erwartete Ausgabe: "llama3.1:latest"

# 4. ASR (Speech Recognition)
echo "4. ASR Service:"
curl -s http://localhost:8004/health | jq
# Erwartete Ausgabe: {"status":"healthy","model":"Systran/faster-whisper-large-v3"}

# 5. TTS (Text-to-Speech)
echo "5. TTS Service:"
curl -s http://localhost:8005/health | jq
# Erwartete Ausgabe: {"status":"healthy","model":"thorsten-medium"}

# 6. Orchestrator
echo "6. Orchestrator:"
curl -s http://localhost:8003/health | jq
# Erwartete Ausgabe: {"status":"healthy","llm_url":"http://llama:11434"}

# 7. Proactivity
echo "7. Proactivity:"
curl -s http://localhost:8006/health | jq
# Erwartete Ausgabe: {"status":"healthy","scheduler":"running"}
```

**✅ Erfolg wenn:** Alle Services antworten mit Status "healthy"

---

### Test 2: Toolserver - Facts Database

```bash
echo "=== Testing Facts Database ==="

# Fakt speichern
curl -X PUT http://localhost:8002/v1/facts/test.name \
  -H "Content-Type: application/json" \
  -d '{"value":"Mario Hunziker"}'

# Fakt abrufen
curl -s http://localhost:8002/v1/facts/test.name | jq

# Erwartete Ausgabe:
# {
#   "key": "test.name",
#   "value": "Mario Hunziker",
#   "created_at": "2025-10-05T...",
#   "updated_at": "2025-10-05T..."
# }

# Versicherungsdaten als Beispiel
curl -X PUT http://localhost:8002/v1/facts/versicherung.gebaeude.summe \
  -H "Content-Type: application/json" \
  -d '{"value":"980000 CHF"}'

curl -X PUT http://localhost:8002/v1/facts/versicherung.hausrat.summe \
  -H "Content-Type: application/json" \
  -d '{"value":"150000 CHF"}'

# Alle Facts anzeigen
curl -s http://localhost:8002/v1/facts | jq
```

**✅ Erfolg wenn:** Facts werden korrekt gespeichert und abgerufen

---

### Test 3: Toolserver - Semantische Suche

```bash
echo "=== Testing Semantic Search ==="

# Dokument hinzufügen
curl -X POST http://localhost:8002/v1/documents \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Die Gebäudeversicherung deckt Schäden am Haus ab. Die Versicherungssumme beträgt 980000 CHF.",
    "metadata": {
      "source": "test",
      "type": "versicherung"
    }
  }'

# Semantische Suche
curl -X POST http://localhost:8002/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Gebäudeversicherung Summe","n_results":3}' | jq

# Erwartete Ausgabe: Dokument mit Distanz < 1.0
```

**✅ Erfolg wenn:** Dokument wird gefunden und relevante Inhalte zurückgegeben

---

### Test 4: TTS - Sprachausgabe

```bash
echo "=== Testing Text-to-Speech ==="

# Text in Sprache konvertieren
curl -X POST http://localhost:8005/v1/speak \
  -H "Content-Type: application/json" \
  -d '{"text":"Hallo, ich bin Jarvis, dein persönlicher Assistent."}' \
  --output /tmp/jarvis_test.wav

# Datei prüfen
file /tmp/jarvis_test.wav
# Erwartete Ausgabe: RIFF (little-endian) data, WAVE audio

# Optional: Abspielen (Linux mit aplay)
# aplay /tmp/jarvis_test.wav

# Oder: Browser öffnen und Datei abspielen
ls -lh /tmp/jarvis_test.wav
```

**✅ Erfolg wenn:** WAV-Datei wird erstellt und ist > 0 Bytes

---

### Test 5: ASR - Spracherkennung

```bash
echo "=== Testing Speech Recognition ==="

# Erst eine Test-Audio-Datei mit TTS erstellen
curl -X POST http://localhost:8005/v1/speak \
  -H "Content-Type: application/json" \
  -d '{"text":"Wie hoch ist meine Gebäudeversicherung?"}' \
  --output /tmp/test_frage.wav

# Jetzt mit ASR transkribieren
curl -X POST http://localhost:8004/v1/transcribe \
  -F "file=@/tmp/test_frage.wav" | jq

# Erwartete Ausgabe:
# {
#   "text": "Wie hoch ist meine Gebäudeversicherung?",
#   "language": "de",
#   "duration": <seconds>
# }
```

**✅ Erfolg wenn:** Text wird korrekt transkribiert (evtl. mit kleinen Abweichungen)

---

### Test 6: Orchestrator - LLM Integration

```bash
echo "=== Testing Orchestrator ==="

# Test 1: Einfache Konversation (ohne Tool-Call)
curl -X POST http://localhost:8003/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Hallo, wer bist du?"}' | jq

# Erwartete Ausgabe: Freundliche Begrüßung von Jarvis

# Test 2: Anfrage mit Tool-Call (Fakt abrufen)
curl -X POST http://localhost:8003/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Wie hoch ist meine Gebäudeversicherung?"}' | jq

# Erwartete Ausgabe:
# {
#   "response": "Ihre Gebäudeversicherung beträgt 980.000 CHF.",
#   "tool_calls": [...],
#   "tool_results": [...]
# }

# Test 3: Dokumentensuche
curl -X POST http://localhost:8003/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Suche nach Informationen über Versicherungen"}' | jq
```

**✅ Erfolg wenn:** Orchestrator ruft LLM auf, führt Tool-Calls aus und liefert korrekte Antworten

---

### Test 7: Ingestion - Dokumenten-Verarbeitung

```bash
echo "=== Testing Document Ingestion ==="

# Test-Dokument erstellen
cat > data/test_versicherung.txt << 'EOF'
Versicherungspolice Nr. 12345

Gebäudeversicherung:
- Versicherungssumme: 980.000 CHF
- Selbstbehalt: 1.000 CHF
- Gültig bis: 31.12.2025

Hausratversicherung:
- Versicherungssumme: 150.000 CHF
- Selbstbehalt: 500 CHF
- Gültig bis: 31.12.2025
EOF

# Warte auf File-Watcher (5 Sekunden)
echo "Warte auf Ingestion Service..."
sleep 5

# Logs prüfen
docker-compose logs ingestion | tail -20

# Nach indexiertem Dokument suchen
curl -X POST http://localhost:8002/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Versicherungspolice Selbstbehalt","n_results":3}' | jq
```

**✅ Erfolg wenn:** Dokument wird automatisch indexiert und ist via Suche auffindbar

---

### Test 8: Proactivity - Erinnerungen

```bash
echo "=== Testing Proactivity Service ==="

# Status prüfen
curl -s http://localhost:8006/v1/status | jq

# Steuer-Frist setzen (in 5 Tagen)
FUTURE_DATE=$(date -d "+5 days" +%Y-%m-%dT00:00:00)
curl -X PUT http://localhost:8002/v1/facts/naechste_steuer_frist \
  -H "Content-Type: application/json" \
  -d "{\"value\":\"$FUTURE_DATE\"}"

# Termin setzen (morgen um 14:30)
TOMORROW=$(date -d "+1 day" +%Y-%m-%dT14:30:00)
curl -X PUT http://localhost:8002/v1/facts/naechster_termin \
  -H "Content-Type: application/json" \
  -d "{\"value\":\"${TOMORROW}|Zahnarzttermin\"}"

# Facts prüfen
curl -s http://localhost:8002/v1/facts/naechste_steuer_frist | jq
curl -s http://localhost:8002/v1/facts/naechster_termin | jq

# Logs überwachen (Benachrichtigungen erfolgen nur in Zeitfenstern)
docker-compose logs -f proactivity
```

**✅ Erfolg wenn:** 
- Status-Endpoint zeigt Zeitfenster korrekt an
- Facts werden gespeichert
- In den Zeitfenstern (07:30-08:30, 18:30-20:00) werden Erinnerungen versendet

---

## End-to-End Tests

### Vollständiger Workflow: Sprache → LLM → Sprache

```bash
echo "=== End-to-End Test: ASR → Orchestrator → TTS ==="

# 1. Test-Audio erstellen
curl -X POST http://localhost:8005/v1/speak \
  -H "Content-Type: application/json" \
  -d '{"text":"Wie hoch ist meine Hausratversicherung?"}' \
  --output /tmp/frage.wav

# 2. Mit ASR transkribieren
TRANSCRIPT=$(curl -s -X POST http://localhost:8004/v1/transcribe \
  -F "file=@/tmp/frage.wav" | jq -r '.text')

echo "Transkribiert: $TRANSCRIPT"

# 3. An Orchestrator senden
RESPONSE=$(curl -s -X POST http://localhost:8003/v1/query \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"$TRANSCRIPT\"}" | jq -r '.response')

echo "Antwort: $RESPONSE"

# 4. Antwort in Sprache umwandeln
curl -X POST http://localhost:8005/v1/speak \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"$RESPONSE\"}" \
  --output /tmp/antwort.wav

# 5. Prüfen
ls -lh /tmp/frage.wav /tmp/antwort.wav
echo "✅ End-to-End Test abgeschlossen!"
```

---

## Fehlerbehebung

### Services starten nicht

```bash
# Container-Status prüfen
docker-compose ps

# Logs einzelner Services anzeigen
docker-compose logs toolserver
docker-compose logs orchestrator
docker-compose logs proactivity

# Services neu starten
docker-compose restart
```

### Ollama Modell fehlt

```bash
# Installierte Modelle prüfen
docker exec jarvis-llama ollama list

# Modell herunterladen
docker exec jarvis-llama ollama pull llama3.1
```

### Speicherprobleme

```bash
# Docker-Speicher freigeben
docker system prune -a --volumes

# Services neu bauen und starten
docker-compose up -d --build
```

### Port-Konflikte

```bash
# Belegte Ports prüfen
ss -tlnp | grep -E ':(8001|8002|8003|8004|8005|8006|11434)'

# Falls Ports belegt: Port-Mappings in docker-compose.yml anpassen
```

### Proactivity-Service erhält keine Benachrichtigungen

**Prüfpunkte:**
1. Sind Zeitfenster aktiv? `curl http://localhost:8006/v1/status`
2. Sind Facts gesetzt? `curl http://localhost:8002/v1/facts`
3. Telegram-Credentials korrekt? (Logs prüfen)
4. Zeit stimmt? Benachrichtigungen nur 07:30-08:30 und 18:30-20:00

---

## Erfolgreiche Test-Zusammenfassung

Nach Abschluss aller Tests solltest du:

✅ **Alle 8 Services laufen** (docker-compose ps)  
✅ **Health-Checks bestanden** (alle Endpoints antworten)  
✅ **Facts speichern & abrufen** funktioniert  
✅ **Semantische Suche** findet Dokumente  
✅ **TTS** generiert Audio-Dateien  
✅ **ASR** transkribiert korrekt  
✅ **Orchestrator** führt Tool-Calls aus  
✅ **Ingestion** indexiert Dokumente automatisch  
✅ **Proactivity** zeigt Status korrekt an  
✅ **End-to-End Workflow** funktioniert  

---

## Nächste Schritte

1. **Produktiv-Konfiguration:**
   - Telegram-Bot einrichten und Token in `.env` eintragen
   - E-Mail-Zugangsdaten für Ingestion konfigurieren
   - NAS-Mount einrichten (Synology DS224+)

2. **Weitere Tests:**
   - Eigene Audio-Dateien mit ASR testen
   - Eigene Dokumente indexieren
   - Konversationen mit dem Orchestrator führen

3. **Monitoring:**
   ```bash
   # Alle Logs live verfolgen
   docker-compose logs -f
   
   # Ressourcen-Nutzung
   docker stats
   ```

---

**Bei Fragen oder Problemen:**
- GitHub Issues: https://github.com/b4llu97/Jarvis/issues
- Repository: https://github.com/b4llu97/Jarvis
