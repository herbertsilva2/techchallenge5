"""
Agente de Testes e Garantia de Qualidade (Tester Agent) — Guardiã AI
Responsável por verificar cobertura de testes, suítes de regressão e integridade das asserções.
"""

from typing import Dict, Any, List
from pathlib import Path
import subprocess
import sys
from src.config import PROJECT_ROOT


class TesterAgent:
    """
    Agente especialista em execução e validação da suíte de testes unitários.
    """

    def __init__(self, root_dir: Path = PROJECT_ROOT):
        self.root_dir = root_dir

    def verify(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executa a suíte de testes pytest no ambiente Python disponível e sintetiza os resultados.
        """
        tests_dir = self.root_dir / "tests"
        test_files = [p.name for p in tests_dir.glob("test_*.py")]

        # Localizar o interpretador do .venv preferencialmente
        venv_python = self.root_dir / ".venv" / "Scripts" / "python.exe"
        python_exec = str(venv_python) if venv_python.exists() else sys.executable

        try:
            res = subprocess.run(
                [python_exec, "-m", "pytest", "-v", str(tests_dir)],
                capture_output=True,
                text=True,
                cwd=str(self.root_dir),
                timeout=60,
            )
            success = (res.returncode == 0)
            output_lines = res.stdout.splitlines()
            summary_line = output_lines[-1] if output_lines else "No output"

            return {
                "agent": "TesterAgent",
                "python_used": python_exec,
                "test_files_found": test_files,
                "success": success,
                "return_code": res.returncode,
                "summary": summary_line,
                "status": "APROVADO" if success else "FALHA_NOS_TESTES",
                "raw_output_tail": output_lines[-5:] if len(output_lines) >= 5 else output_lines,
            }
        except Exception as e:
            return {
                "agent": "TesterAgent",
                "test_files_found": test_files,
                "success": False,
                "status": "ERRO_DE_EXECUÇÃO",
                "error": str(e),
            }
