# 🚀 Deploy Rápido no Railway

## 1️⃣ Criar Repositório no GitHub

```bash
# Criar repo no GitHub: multistream-cron-service
# Depois:
git remote add origin https://github.com/SEU-USUARIO/multistream-cron-service.git
git push -u origin main
```

## 2️⃣ Deploy no Railway

1. Acesse [railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub repo**
3. Selecione `multistream-cron-service`

## 3️⃣ Adicionar PostgreSQL

1. No projeto → **+ New** → **Database** → **PostgreSQL**
2. Railway cria automaticamente!

## 4️⃣ Configurar Variável

1. Clique no serviço Python
2. **Variables** → **+ New Variable**:

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

3. Railway conecta automaticamente!

## 5️⃣ Deploy Automático! 🎉

Railway vai:
- ✅ Instalar Python 3.12
- ✅ Instalar dependências
- ✅ Rodar migrations
- ✅ Iniciar servidor
- ✅ Iniciar cron jobs

## 6️⃣ Testar

```bash
# Copie a URL do Railway (ex: multistream-cron-service-production.up.railway.app)
curl https://SEU-APP.up.railway.app/health

# Ver eventos
curl https://SEU-APP.up.railway.app/api/events

# Ver evento específico
curl https://SEU-APP.up.railway.app/api/events/starladder-budapest-major-2025/overlay
```

## ⏰ Cron Jobs Automáticos

Assim que subir, os jobs rodam sozinhos:

- **sync_events**: 00:00 UTC (diário)
- **sync_event_data**: A cada 10 minutos

## 📊 Monitorar

- **Logs**: Railway → Deployments → View Logs  
- **Database**: Railway → PostgreSQL → Data
- **Metrics**: Railway → Observability

## ✅ Pronto!

Seu backend FastAPI está no ar! 🎉
