import json
from pathlib import Path
from datetime import datetime
from typing import Any


class JSONStorage:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, category: str, subcategory: str, data: list[dict[str, Any]]) -> Path:
        dir_path = self.base_dir / category
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = dir_path / f"{subcategory}.json"

        payload = {
            "meta": {
                "category": category,
                "subcategory": subcategory,
                "count": len(data),
                "updated": datetime.utcnow().isoformat(),
            },
            "items": data,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        return file_path

    def load(self, category: str, subcategory: str) -> dict | None:
        file_path = self.base_dir / category / f"{subcategory}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_categories(self) -> list[str]:
        return [p.name for p in self.base_dir.iterdir() if p.is_dir()]

    def list_subcategories(self, category: str) -> list[str]:
        dir_path = self.base_dir / category
        if not dir_path.exists():
            return []
        return [p.stem for p in dir_path.glob("*.json")]
