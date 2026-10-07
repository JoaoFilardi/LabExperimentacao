"""Camada de cache local e retomada transparente de execução.

Permite armazenar em disco as respostas da API do GitHub para evitar
requisições redundantes, respeitar a cota de rate limit e garantir que o
pipeline possa ser interrompido e continuado sem perda de progresso.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def sanitize_filename(name: str) -> str:
    """Substitui caracteres inválidos para sistemas de arquivos em Windows/Linux."""
    return re.sub(r'[\\/*?:"<>| ]', "_", name)


class CacheManager:
    """Gerencia leitura e escrita de respostas da API em arquivos JSON locais."""

    def __init__(self, cache_dir: Path | str, enabled: bool = True) -> None:
        self.cache_dir = Path(cache_dir)
        self.enabled = enabled
        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, category: str, key: str) -> Path:
        """Gera o caminho físico para o arquivo de cache."""
        category_dir = self.cache_dir / sanitize_filename(category)
        category_dir.mkdir(parents=True, exist_ok=True)

        # Para chaves longas ou com parâmetros complexos, usa um nome legível + hash curto
        sanitized_key = sanitize_filename(key)
        if len(sanitized_key) > 60:
            key_hash = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
            sanitized_key = f"{sanitized_key[:48]}_{key_hash}"

        return category_dir / f"{sanitized_key}.json"

    def has(self, category: str, key: str) -> bool:
        """Verifica se existe entrada válida no cache."""
        if not self.enabled:
            return False
        return self._get_path(category, key).is_file()

    def get(self, category: str, key: str) -> Optional[Any]:
        """Recupera dado serializado do cache, retornando None se não encontrado."""
        if not self.enabled:
            return None

        file_path = self._get_path(category, key)
        if not file_path.is_file():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def set(self, category: str, key: str, data: Any) -> None:
        """Persiste dado no cache em formato JSON UTF-8."""
        if not self.enabled:
            return

        file_path = self._get_path(category, key)
        temp_path = file_path.with_suffix(".tmp")

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            temp_path.replace(file_path)
        except Exception:
            if temp_path.exists():
                temp_path.unlink()
            raise

    def list_keys(self, category: str) -> List[str]:
        """Lista as chaves (nomes de arquivo sem extensão) já persistidas em uma categoria."""
        if not self.enabled:
            return []
        category_dir = self.cache_dir / sanitize_filename(category)
        if not category_dir.is_dir():
            return []
        return sorted(path.stem for path in category_dir.glob("*.json"))

    def mark_processed(
        self,
        task: str,
        identifier: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Registra que um repositório/período de uma tarefa já foi processado (retomada)."""
        payload: Dict[str, Any] = {"processed": True}
        if metadata:
            payload["metadata"] = metadata
        self.set(f"progress_{task}", identifier, payload)

    def is_processed(self, task: str, identifier: str) -> bool:
        """Indica se o identificador já foi marcado como processado para a tarefa."""
        data = self.get(f"progress_{task}", identifier)
        return bool(isinstance(data, dict) and data.get("processed"))

    def get_progress(self, task: str, identifier: str) -> Optional[Dict[str, Any]]:
        """Recupera o registro de progresso de um repositório/período, se existir."""
        data = self.get(f"progress_{task}", identifier)
        return data if isinstance(data, dict) else None
