import os
import json
import time
import urllib.request
import urllib.error

# Token do GitHub armazenado em variavel de ambiente
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

TRANSIENT_HTTP_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 4

# Se nao encontrar, tenta ler de um arquivo .env local
if not GITHUB_TOKEN:
    for caminho in [".env", "lab01/.env", "../.env"]:
        if os.path.exists(caminho):
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    for linha in f:
                        linha = linha.strip()
                        if linha and not linha.startswith("#") and "=" in linha:
                            chave, valor = linha.split("=", 1)
                            if chave.strip() == "GITHUB_TOKEN":
                                GITHUB_TOKEN = valor.strip()
                                break
            except Exception:
                pass
        if GITHUB_TOKEN:
            break

def execute_query(query: str, variables: dict = None, max_retries: int = MAX_RETRIES) -> dict:
    """Envia uma consulta GraphQL para o GitHub com retry para erros temporários."""
    if not GITHUB_TOKEN:
        raise ValueError("ERRO: GITHUB_TOKEN nao configurado nas variaveis de ambiente nem no arquivo .env.")

    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Python-urllib"
    }

    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    req_data = json.dumps(payload).encode("utf-8")

    for tentativa in range(max_retries + 1):
        req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                res_data = response.read().decode("utf-8")
                res_json = json.loads(res_data)

                if "errors" in res_json:
                    print("Erros no GraphQL:")
                    for error in res_json["errors"]:
                        print("-", error.get("message"))
                    raise RuntimeError("Falha na consulta GraphQL")

                return res_json

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            print(f"Erro HTTP {e.code}: {error_body}")

            if e.code in TRANSIENT_HTTP_STATUS_CODES and tentativa < max_retries:
                wait_time = 2 ** tentativa
                print(f"Tentativa {tentativa + 1}/{max_retries + 1} falhou por erro temporário. Repetindo em {wait_time}s...")
                time.sleep(wait_time)
                continue
            raise

        except urllib.error.URLError as e:
            print(f"Erro de rede: {e.reason}")
            if tentativa < max_retries:
                wait_time = 2 ** tentativa
                print(f"Tentativa {tentativa + 1}/{max_retries + 1} falhou por rede. Repetindo em {wait_time}s...")
                time.sleep(wait_time)
                continue
            raise

    raise RuntimeError("Consulta GraphQL falhou após todas as tentativas.")
