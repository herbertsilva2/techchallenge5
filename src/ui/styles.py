"""
Estilos CSS e Design System da Guardiã AI
Interface moderna, elegante e profissional para ambientes de saúde e assistência.
"""

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Header e Banner Principal */
    .guardia-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F766E 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .guardia-title {
        color: #F8FAFC;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .guardia-subtitle {
        color: #94A3B8;
        font-size: 14px;
        font-weight: 400;
        margin-top: 6px;
        margin-bottom: 0;
    }

    /* Banner Ético CDSS & Human-in-the-Loop (Caixa Arredondada Alto Contraste) */
    .ethical-banner {
        background-color: #F0FDFA !important;
        border: 1px solid #A7F3D0 !important;
        border-left: 6px solid #0D9488 !important;
        border-radius: 14px !important;
        padding: 14px 20px !important;
        margin-bottom: 22px !important;
        color: #0F172A !important;
        box-shadow: 0 2px 8px rgba(13, 148, 136, 0.08) !important;
    }
    .ethical-banner strong {
        color: #0F766E !important;
    }

    /* Estilização para Blockquotes de Aviso Ético do Streamlit */
    blockquote {
        background: #0B192C !important;
        border: 1px solid #334155 !important;
        border-left: 5px solid #F59E0B !important;
        border-radius: 8px !important;
        padding: 14px 18px !important;
        color: #F8FAFC !important;
        margin: 18px 0 !important;
    }
    blockquote p, blockquote strong, blockquote span {
        color: #F8FAFC !important;
    }


    /* Cards de Risco */
    .risk-card {
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 20px;
        color: #FFFFFF;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .risk-card-high {
        background: linear-gradient(135deg, #991B1B 0%, #DC2626 100%);
        border: 1px solid #EF4444;
    }
    .risk-card-moderate {
        background: linear-gradient(135deg, #9A3412 0%, #EA580C 100%);
        border: 1px solid #F97316;
    }
    .risk-card-low {
        background: linear-gradient(135deg, #065F46 0%, #059669 100%);
        border: 1px solid #10B981;
    }

    /* Cards de Métricas Rápidas */
    .metric-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #0D9488;
    }
    .metric-value {
        font-size: 22px;
        font-weight: 700;
        color: #F8FAFC;
    }
    .metric-label {
        font-size: 12px;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }

    /* Badge de Citação RAG */
    .citation-badge {
        display: inline-block;
        background: #0284C7;
        color: #FFFFFF;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
        margin-right: 6px;
    }

    /* Badge de Integridade Hash */
    .hash-badge {
        font-family: monospace;
        background: #0F172A;
        color: #38BDF8;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
        border: 1px solid #1E293B;
    }

    /* Tag de Alerta de Segurança */
    .security-alert-box {
        background: rgba(225, 29, 72, 0.15);
        border: 1px solid #E11D48;
        border-radius: 10px;
        padding: 16px;
        margin-top: 14px;
        color: #FFE4E6;
    }
</style>
"""
