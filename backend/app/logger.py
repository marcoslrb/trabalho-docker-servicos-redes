"""
Cliente HTTP para envio de logs ao Grafana Loki.
Envia logs estruturados via Loki Push API (POST /loki/api/v1/push).

Eventos obrigatórios:
  - Inicialização da aplicação
  - Cada requisição recebida (método HTTP, rota, código de resposta)
  - Erros de conexão com o PostgreSQL
"""
import os
import time
import httpx


# URL do Loki — configurável via variável de ambiente.
# No cluster K8s, o Service se chama "loki" no namespace "catalogo".
LOKI_URL = os.environ.get("LOKI_URL", "http://loki:3100")

PUSH_ENDPOINT = f"{LOKI_URL}/loki/api/v1/push"

# Timeout curto para não bloquear a aplicação caso o Loki esteja indisponível.
TIMEOUT = 2.0


def _now_ns() -> str:
    """Retorna o timestamp atual em nanossegundos como string."""
    return str(int(time.time() * 1_000_000_000))


def send_log(
    message: str,
    level: str = "info",
    extra_labels: dict | None = None,
) -> None:
    """
    Envia uma entrada de log ao Loki.

    Args:
        message: Texto da mensagem de log.
        level: Nível do log (info, warning, error).
        extra_labels: Labels adicionais além dos padrão.
    """
    labels = {
        "service": "fastapi",
        "level": level,
    }
    if extra_labels:
        labels.update(extra_labels)

    # Formato esperado pela Loki Push API.
    payload = {
        "streams": [
            {
                "stream": labels,
                "values": [
                    [_now_ns(), message],
                ],
            }
        ]
    }

    try:
        response = httpx.post(
            PUSH_ENDPOINT,
            json=payload,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
    except Exception:
        # Silenciar erros — logs não podem derrubar a aplicação.
        pass


def log_startup() -> None:
    """Loga a inicialização da aplicação."""
    send_log(
        "Aplicação FastAPI inicializada com sucesso.",
        level="info",
        extra_labels={"event": "startup"},
    )


def log_request(method: str, path: str, status_code: int) -> None:
    """Loga uma requisição HTTP recebida."""
    send_log(
        f"{method} {path} → {status_code}",
        level="info",
        extra_labels={"event": "request", "method": method, "path": path},
    )


def log_db_error(error: str) -> None:
    """Loga um erro de conexão com o PostgreSQL."""
    send_log(
        f"Erro de conexão com PostgreSQL: {error}",
        level="error",
        extra_labels={"event": "db_error"},
    )
