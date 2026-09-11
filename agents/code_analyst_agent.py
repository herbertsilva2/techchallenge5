"""
Agente Analista de Código (Code Analyst Agent) — Guardiã AI
Responsável por auditar qualidade de código, boas práticas Python, PEP 8 e detecção de code smells.
"""

from typing import Dict, Any, List
from pathlib import Path
import re
from src.config import PROJECT_ROOT


class CodeAnalystAgent:
    """
    Agente responsável por inspecionar arquivos Python em busca de code smells,
    caminhos absolutos hardcoded e conformidade de estilo.
    """

    def __init__(self, root_dir: Path = PROJECT_ROOT):
        self.root_dir = root_dir

    def review(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Varre os arquivos Python em busca de padrões problemáticos conhecidos.
        """
        src_dir = self.root_dir / "src"
        py_files = list(src_dir.rglob("*.py"))
        py_files.extend([self.root_dir / "app.py", self.root_dir / "main.py"])

        findings: List[Dict[str, Any]] = []

        hardcoded_user_pattern = re.compile(r'["\']/(?:Users|home)/[a-zA-Z0-9_-]+')
        broad_except_pattern = re.compile(r'except\s*:')

        for fpath in py_files:
            if not fpath.exists():
                continue
            try:
                content = fpath.read_text(encoding="utf-8")
                lines = content.splitlines()
                rel_path = fpath.relative_to(self.root_dir).as_posix()

                for idx, line in enumerate(lines, 1):
                    # Checagem de caminhos absolutos de usuário
                    if hardcoded_user_pattern.search(line):
                        findings.append({
                            "file": rel_path,
                            "line": idx,
                            "severity": "ALTA",
                            "type": "Hardcoded User Path",
                            "snippet": line.strip()[:80],
                        })
                    # Checagem de bare except
                    if broad_except_pattern.search(line):
                        findings.append({
                            "file": rel_path,
                            "line": idx,
                            "severity": "MEDIA",
                            "type": "Bare Except (Anti-Pattern)",
                            "snippet": line.strip()[:80],
                        })
            except Exception as e:
                findings.append({
                    "file": fpath.name,
                    "severity": "BAIXA",
                    "type": "Read Error",
                    "snippet": str(e),
                })

        return {
            "agent": "CodeAnalystAgent",
            "files_scanned": len(py_files),
            "findings_count": len(findings),
            "findings": findings,
            "status": "APROVADO" if not any(f["severity"] == "ALTA" for f in findings) else "REVISÃO_NECESSÁRIA",
        }
