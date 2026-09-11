"""
Orquestrador Central da Equipe Virtual de Sustentação (Guardiã AI)
Coordena a atuação dos agentes especializados para diagnóstico, testes, auditoria e evolução.
"""

from typing import Dict, Any, List
from datetime import datetime


class SustentationOrchestrator:
    """
    Orquestrador que avalia a intenção da solicitação e aciona os agentes
    especializados correspondentes.
    """

    def __init__(self):
        # Importação sob demanda para manter inicialização leve
        from agents.architect_agent import ArchitectAgent
        from agents.code_analyst_agent import CodeAnalystAgent
        from agents.debugger_agent import DebuggerAgent
        from agents.tester_agent import TesterAgent
        from agents.ai_rag_agent import AIRAGAgent

        self.architect = ArchitectAgent()
        self.code_analyst = CodeAnalystAgent()
        self.debugger = DebuggerAgent()
        self.tester = TesterAgent()
        self.ai_rag = AIRAGAgent()

    def route_demand(self, demand_type: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Roteia a demanda técnica para o agente especializado responsável.
        """
        payload = payload or {}
        timestamp = datetime.now().isoformat()
        demand_type_lower = demand_type.lower().strip()

        if "arch" in demand_type_lower or "depend" in demand_type_lower:
            result = self.architect.analyze(payload)
            agent_name = "ArchitectAgent"

        elif "code" in demand_type_lower or "smell" in demand_type_lower or "refactor" in demand_type_lower:
            result = self.code_analyst.review(payload)
            agent_name = "CodeAnalystAgent"

        elif "debug" in demand_type_lower or "incident" in demand_type_lower or "error" in demand_type_lower:
            result = self.debugger.investigate(payload)
            agent_name = "DebuggerAgent"

        elif "test" in demand_type_lower or "qa" in demand_type_lower:
            result = self.tester.verify(payload)
            agent_name = "TesterAgent"

        elif "ai" in demand_type_lower or "rag" in demand_type_lower or "ml" in demand_type_lower or "shap" in demand_type_lower:
            result = self.ai_rag.audit(payload)
            agent_name = "AIRAGAgent"

        else:
            # Diagnóstico unificado 360º
            result = {
                "architecture": self.architect.analyze(payload),
                "code_quality": self.code_analyst.review(payload),
                "ai_rag_status": self.ai_rag.audit(payload),
            }
            agent_name = "FullTeamConsensus"

        return {
            "orchestrator": "SustentationOrchestrator",
            "routed_to": agent_name,
            "demand": demand_type,
            "timestamp": timestamp,
            "result": result,
        }
