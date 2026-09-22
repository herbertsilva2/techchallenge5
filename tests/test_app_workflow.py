"""
Testes automatizados de ciclo de vida e estado da aplicação Guardiã AI (Streamlit).
Verifica inicialização limpa, congelamento de inputs pós-análise e reset via 'Nova Análise'.
"""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


def test_initial_state_clean_and_no_reports():
    """Valida que a aplicação inicia com dados limpos e sem exibir gráficos ou relatórios."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception, f"Exceção encontrada: {at.exception}"

    # Validações de estado inicial da sessão
    assert at.session_state["is_analyzed"] is False
    assert at.session_state["current_pipeline_result"] is None
    assert at.session_state["selected_preset"] == "— Preenchimento Manual (Dados Limpos) —"

    # Validações de campos limpos
    # Encontrar text_area de relato clínico: deve estar vazio
    text_areas = at.text_area
    notes_widget = [ta for ta in text_areas if "Relato do Atendimento" in ta.label][0]
    assert notes_widget.value == ""
    assert notes_widget.disabled is False

    # Encontrar campo de identificação da paciente: deve estar vazio
    text_inputs = at.text_input
    patient_id_widget = [ti for ti in text_inputs if "Identificação" in ti.label][0]
    assert patient_id_widget.value == ""
    assert patient_id_widget.disabled is False

    # Nenhum botão de download de PDF de laudo deve existir antes da execução
    download_buttons = [btn for btn in at.download_button if "Laudo Clínico" in btn.label]
    assert len(download_buttons) == 0

    # Nenhum banner de bloqueio deve existir
    warnings = [w for w in at.warning if "Análise Executada e Bloqueada" in w.value]
    assert len(warnings) == 0


def test_apply_preset_loads_data():
    """Valida que selecionar e aplicar um caso clínico pré-configurado atualiza os campos."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()

    # Selecionar o Caso 1
    preset_select = at.selectbox[0]
    # Encontrar a opção do Caso 1
    caso_1_opt = [opt for opt in preset_select.options if "Caso 1" in opt][0]
    preset_select.select(caso_1_opt)

    # Clicar em "Aplicar Caso"
    apply_btn = [btn for btn in at.button if "Aplicar Caso" in btn.label][0]
    apply_btn.click().run()

    assert not at.exception
    assert at.session_state["selected_preset"] == caso_1_opt

    # O relato deve conter as observações do Caso 1
    notes_widget = [ta for ta in at.text_area if "Relato do Atendimento" in ta.label][0]
    assert "primigesta" in notes_widget.value.lower()


def test_execution_locks_inputs_and_shows_results_and_reset():
    """Valida o ciclo completo: execução trava campos e exibe laudo; 'Nova Análise' restaura o estado limpo."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()

    # Submeter a análise com os parâmetros atuais
    submit_btn = [btn for btn in at.button if "Executar Análise Completa" in btn.label][0]
    submit_btn.click().run()

    assert not at.exception
    # Deve estar com a flag de análise ativada
    assert at.session_state["is_analyzed"] is True
    assert at.session_state["current_pipeline_result"] is not None

    # Deve exibir o aviso de bloqueio de edição
    warnings = [w for w in at.warning if "Análise Executada e Bloqueada" in w.value]
    assert len(warnings) == 1

    # Campos de entrada devem estar travados (disabled=True)
    notes_widget = [ta for ta in at.text_area if "Relato do Atendimento" in ta.label][0]
    assert notes_widget.disabled is True

    patient_id_widget = [ti for ti in at.text_input if "Identificação" in ti.label][0]
    assert patient_id_widget.disabled is True

    # O botão de submissão do formulário agora deve estar desabilitado
    submit_btn_locked = [btn for btn in at.button if "Executar Análise Completa" in btn.label][0]
    assert submit_btn_locked.disabled is True

    # O botão de download do laudo PDF deve estar visível
    pdf_downloads = [btn for btn in at.download_button if "Laudo Clínico" in btn.label]
    assert len(pdf_downloads) == 1

    # Deve haver botões de "Nova Análise"
    new_analysis_buttons = [btn for btn in at.button if "Nova Análise" in btn.label]
    assert len(new_analysis_buttons) >= 1

    # Clicar no botão "Nova Análise"
    new_analysis_buttons[0].click().run()

    assert not at.exception
    # Estado pós-reset deve ser limpo novamente
    assert at.session_state["is_analyzed"] is False
    assert at.session_state["current_pipeline_result"] is None
    assert at.session_state["selected_preset"] == "— Preenchimento Manual (Dados Limpos) —"

    # Campos reabilitados e limpos
    notes_widget_clean = [ta for ta in at.text_area if "Relato do Atendimento" in ta.label][0]
    assert notes_widget_clean.value == ""
    assert notes_widget_clean.disabled is False

    # Download do PDF e avisos de bloqueio devem ter sumido
    assert len([btn for btn in at.download_button if "Laudo Clínico" in btn.label]) == 0
    assert len([w for w in at.warning if "Análise Executada e Bloqueada" in w.value]) == 0
