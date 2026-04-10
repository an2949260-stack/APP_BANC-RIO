# 📦 Guia de Deployment

## Pré-requisitos de Produção

### Servidor
- Ubuntu 22.04 LTS
- 4GB RAM mínimo
- 20GB SSD
- Docker e Docker Compose

### Domínio
- HTTPS/SSL configurado
- DNS apontando para o servidor

### Variáveis de Ambiente
```bash
SECRET_KEY=gere-com: python -c "import secrets; print(secrets.token_urlsafe(32))"
DATABASE_URL=postgresql://user:strong_password@postgres:5432/banco_app
ENCRYPTION_KEY=gere-com: from cryptography.fernet import Fernet; print(Fernet.generate_key())
ALLOWED_ORIGINS=https://seu-dominio.com,https://app.seu-dominio.com
DEBUG=False
ENV=production
```

## 1. Preparar o Servidor

### Atualizar sistema
```bash
sudo apt update && sudo apt upgrade -y
```

### Instalar Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### Instalar Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Instalar Nginx
```bash
sudo apt install -y nginx
```

### Instalar Certbot (Let's Encrypt)
```bash
sudo apt install -y certbot python3-certbot-nginx
```

## 2. Clonar e Configurar Projeto

```bash
cd /opt
sudo git clone <seu-repo> app
cd app
sudo chown -R $USER:$USER .
```

## 3. Configurar Variáveis de Ambiente

```bash
# Backend
cp backend/.env.example backend/.env
nano backend/.env
# Editar com valores de produção

# Verificar arquivo
cat backend/.env
```

## 4. Configurar Nginx como Reverse Proxy

```bash
# Criar configuração
sudo nano /etc/nginx/sites-available/banco-app
```

```nginx
upstream api {
    server backend:8000;
}

upstream frontend {
    server frontend:8501;
}

server {
    listen 80;
    server_name seu-dominio.com;

    # Redirecionar HTTP para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com;

    # SSL - gerado pelo Certbot
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;

    # Segurança SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Limite de taxa
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=web_limit:10m rate=30r/s;

    # Logs
    access_log /var/log/nginx/banco-access.log;
    error_log /var/log/nginx/banco-error.log;

    # API Backend
    location /api/ {
        limit_req zone=api_limit burst=20;
        
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Frontend Streamlit
    location / {
        limit_req zone=web_limit burst=50;
        
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket suporte
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check
    location /health {
        access_log off;
        proxy_pass http://api/api/health;
    }

    # Segurança headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
```

Ativar o site:
```bash
sudo ln -s /etc/nginx/sites-available/banco-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 5. Gerar Certificado SSL

```bash
sudo certbot certonly --nginx -d seu-dominio.com
# Renovação automática
sudo systemctl enable certbot.timer
```

## 6. Ajustar docker-compose.yml para Produção

```yaml
# Mudar para production
environment:
  - DEBUG=False
  - ENV=production

# Adicionar restart policies
restart_policy:
  condition: on-failure
  delay: 5s
  max_attempts: 5

# Adicionar volumes para persistência
volumes:
  - /data/postgres:/var/lib/postgresql/data
  - /data/prometheus:/prometheus
  - /data/grafana:/var/lib/grafana
```

## 7. Iniciar Aplicação

```bash
# Verificar .env está correto
cat backend/.env

# Iniciar serviços
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f backend

# Executar migrações (primeira vez)
docker-compose exec backend python -c "from app.database import init_db; init_db()"
```

## 8. Backup do Banco de Dados

### Script automático
```bash
# /usr/local/bin/backup-banco-app.sh
#!/bin/bash

BACKUP_DIR="/backups/banco-app"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="banco_app"

mkdir -p $BACKUP_DIR

docker-compose exec -T postgres pg_dump -U bancario $DB_NAME | gzip > $BACKUP_DIR/banco_$DATE.sql.gz

# Manter apenas últimos 7 dias
find $BACKUP_DIR -mtime +7 -delete

echo "Backup realizado: $BACKUP_DIR/banco_$DATE.sql.gz"
```

Agendar com cron:
```bash
sudo crontab -e
# Adicionar: 0 2 * * * /usr/local/bin/backup-banco-app.sh
```

## 9. Monitoramento

### Grafana
- Acesso: https://seu-dominio.com/grafana
- Usuario: admin
- Senha: admin (altere!)

### Prometheus
- Acesso: https://seu-dominio.com:9090
- Métricas da API

### Alertas
Configurar no Grafana:
1. Database connection to Prometheus
2. Criar alertas para:
   - Taxa de erro > 5%
   - Tempo de resposta > 1000ms
   - Disco cheio
   - CPU > 80%

## 10. Segurança em Produção

### Firewall
```bash
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw status
```

### Secrets Management
```bash
# Usar arquivo .env protegido
sudo chmod 600 backend/.env
sudo chown root:root backend/.env

# Ou usar secrets store
docker secret create db_password -
```

### Rate Limiting (já configurado no Nginx)

### CORS Restrito
```python
ALLOWED_ORIGINS="https://seu-dominio.com"
```

### SQL Injection Prevention
- ✅ Já implementado com SQLAlchemy ORM

### CSRF Protection
- ✅ Implementado com tokens JWT

## 11. Logs Centralizados

### ELK Stack (Elasticsearch, Logstash, Kibana)
```yaml
# docker-compose.yml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  # ...

logstash:
  image: docker.elastic.co/logstash/logstash:8.0.0
  # ...

kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
  # ...
```

## 12. CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Test
        run: docker-compose up --abort-on-container-exit
      
      - name: Build and Push
        run: |
          docker build -t myregistry/banco-api:latest backend/
          docker push myregistry/banco-api:latest
      
      - name: Deploy
        run: ssh user@server "cd /opt/app && docker-compose pull && docker-compose up -d"
```

## 13. Health Check

```bash
# Verificar saúde
curl -k https://seu-dominio.com/api/health

# Esperado:
# {"status":"healthy","app":"BancoApp","version":"1.0.0","environment":"production"}
```

## 14. Atualizar Aplicação

```bash
cd /opt/app

# Parar serviços
docker-compose down

# Atualizar código
git pull

# Iniciar novamente
docker-compose up -d

# Verificar logs
docker-compose logs -f backend
```

## 15. Disaster Recovery

### Restaurar Backup
```bash
# Listar backups
ls -lh /backups/banco-app/

# Restaurar
gunzip < /backups/banco-app/banco_20240101_020000.sql.gz | \
  docker-compose exec -T postgres psql -U bancario banco_app

# Verificar integridade
docker-compose exec backend python -c "from app.database import init_db; init_db()"
```

## Checklist Final

- [ ] Domínio apontando para servidor
- [ ] SSL/TLS ativo
- [ ] Backend respondendo em /api/health
- [ ] Frontend acessível
- [ ] Banco de dados conectado
- [ ] Backups funcionando
- [ ] Monitoramento configurado
- [ ] Logs centralizados
- [ ] Rate limiting ativo
- [ ] Firewall configurado
- [ ] SSH configurado com chave
- [ ] Senhas alteradas (admin Grafana)
- [ ] Email de alertas testado
- [ ] Documentação atualizada
- [ ] Plano de disaster recovery pronto

---

**Aplicação pronta para produção! 🚀**
