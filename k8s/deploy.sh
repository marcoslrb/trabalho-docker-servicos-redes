#!/bin/bash
# ============================================================
# Script de Deploy — Catálogo de Produtos (Grupo 2) em K3s
# ============================================================
# Este script deve ser executado na VM2 (control plane / server)
# após o K3s estar instalado e ambas as VMs no cluster.
#
# Uso: bash k8s/deploy.sh
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo " Deploy — Catálogo de Produtos (K3s)"
echo "=========================================="

# 1. Criar o namespace
echo ""
echo "[1/8] Criando namespace..."
kubectl apply -f "$SCRIPT_DIR/namespace.yaml"

# 2. Criar o Secret
echo "[2/8] Criando Secret do PostgreSQL..."
kubectl apply -f "$SCRIPT_DIR/secret-postgres.yaml"

# 3. Criar ConfigMaps
echo "[3/8] Criando ConfigMaps..."
kubectl apply -f "$SCRIPT_DIR/configmap-loki.yaml"
kubectl apply -f "$SCRIPT_DIR/configmap-nginx.yaml"

# Criar ConfigMap dos arquivos HTML do frontend a partir dos arquivos locais
echo "         Criando ConfigMap do frontend (HTML/CSS/JS)..."
kubectl create configmap nginx-html \
  --from-file="$PROJECT_DIR/nginx/html/index.html" \
  --from-file="$PROJECT_DIR/nginx/html/style.css" \
  --from-file="$PROJECT_DIR/nginx/html/script.js" \
  --namespace=catalogo \
  --dry-run=client -o yaml | kubectl apply -f -

# 4. Criar PVCs
echo "[4/8] Criando volumes persistentes..."
kubectl apply -f "$SCRIPT_DIR/pvc-postgres.yaml"
kubectl apply -f "$SCRIPT_DIR/pvc-loki.yaml"

# 5. Deploy da camada de dados (VM1)
echo "[5/8] Implantando camada de dados (PostgreSQL + Loki)..."
kubectl apply -f "$SCRIPT_DIR/statefulset-postgres.yaml"
kubectl apply -f "$SCRIPT_DIR/service-postgres.yaml"
kubectl apply -f "$SCRIPT_DIR/deployment-loki.yaml"
kubectl apply -f "$SCRIPT_DIR/service-loki.yaml"

# 6. Aguardar PostgreSQL ficar pronto
echo "[6/8] Aguardando PostgreSQL ficar pronto..."
kubectl wait --for=condition=ready pod -l app=postgres -n catalogo --timeout=120s || {
  echo "AVISO: PostgreSQL não ficou pronto em 120s. Verifique com: kubectl get pods -n catalogo"
}

# 7. Deploy da camada de aplicação (VM2)
echo "[7/8] Implantando camada de aplicação (FastAPI + NGINX)..."
kubectl apply -f "$SCRIPT_DIR/deployment-fastapi.yaml"
kubectl apply -f "$SCRIPT_DIR/service-fastapi.yaml"
kubectl apply -f "$SCRIPT_DIR/deployment-nginx.yaml"
kubectl apply -f "$SCRIPT_DIR/service-nginx.yaml"

# 8. Verificar estado
echo "[8/8] Verificando estado dos pods..."
echo ""
sleep 5
kubectl get pods -n catalogo -o wide
echo ""
kubectl get services -n catalogo
echo ""
echo "=========================================="
echo " Deploy concluído!"
echo ""
echo " Acesse a aplicação em:"
echo "   HTTP:  http://<IP-VM2>:30080"
echo "   HTTPS: https://<IP-VM2>:30443"
echo ""
echo " Consultar logs do Loki:"
echo "   kubectl port-forward svc/loki 3100:3100 -n catalogo"
echo "   curl http://localhost:3100/loki/api/v1/labels"
echo "=========================================="
