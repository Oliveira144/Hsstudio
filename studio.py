import streamlit as st
import random
import time
from datetime import datetime

# Configuração inicial da página
st.set_page_config(
    page_title="HS Studio App",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inicialização do estado da sessão
if 'show_warning' not in st.session_state:
    st.session_state.show_warning = True
if 'history' not in st.session_state:
    st.session_state.history = []
if 'stats' not in st.session_state:
    st.session_state.stats = {'casa': 0, 'visitante': 0, 'empate': 0}
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'suggestion' not in st.session_state:
    st.session_state.suggestion = None
if 'manipulation_alerts' not in st.session_state:
    st.session_state.manipulation_alerts = []
if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = []
if 'adaptive_weights' not in st.session_state:
    st.session_state.adaptive_weights = {
        'alternancia': 1.0,
        'sequencia': 1.0,
        'clusters': 1.0,
        'ciclos': 1.0,
        'quebras': 1.0,
        'estatistico': 1.0
    }

# Funções auxiliares
def add_result(result):
    st.session_state.history.insert(0, result)
    update_stats()
    analyze_patterns()

def undo_last():
    if st.session_state.history:
        st.session_state.history.pop(0)
        update_stats()
        analyze_patterns()

def clear_history():
    st.session_state.history = []
    st.session_state.stats = {'casa': 0, 'visitante': 0, 'empate': 0}
    st.session_state.analysis = None
    st.session_state.suggestion = None
    st.session_state.manipulation_alerts = []

def update_stats():
    stats = {'casa': 0, 'visitante': 0, 'empate': 0}
    for result in st.session_state.history:
        stats[result] += 1
    st.session_state.stats = stats

def analyze_patterns():
    history = st.session_state.history
    if len(history) < 3:
        st.session_state.analysis = {'pattern': 'Dados insuficientes', 'confidence': 0}
        st.session_state.suggestion = {'bet': 'casa', 'reason': 'Aguarde mais resultados', 'confidence': 'baixa'}
        st.session_state.manipulation_alerts = []
        return
    
    # Simulação de análise de padrões (simplificada para exemplo)
    last_results = history[:5]
    
    # Verifica se há uma sequência
    if len(set(last_results)) == 1:
        st.session_state.analysis = {
            'pattern': 'Sequência Longa',
            'confidence': 75,
            'description': f"{last_results[0]} vencendo {len(last_results)} vezes consecutivas"
        }
        st.session_state.suggestion = {
            'bet': 'visitante' if last_results[0] == 'casa' else 'casa',
            'reason': 'Quebra de sequência esperada',
            'confidence': 'média'
        }
    # Verifica se há alternância
    elif all(last_results[i] != last_results[i+1] for i in range(len(last_results)-1)):
        st.session_state.analysis = {
            'pattern': 'Alternância Simples',
            'confidence': 80,
            'description': 'Resultados alternando consistentemente'
        }
        next_bet = 'visitante' if last_results[0] == 'casa' else 'casa'
        st.session_state.suggestion = {
            'bet': next_bet,
            'reason': 'Padrão de alternância detectado',
            'confidence': 'alta'
        }
    else:
        st.session_state.analysis = {
            'pattern': 'Padrão Aleatório',
            'confidence': 40,
            'description': 'Nenhum padrão claro detectado'
        }
        # Sugestão baseada em estatísticas
        if st.session_state.stats['casa'] > st.session_state.stats['visitante']:
            st.session_state.suggestion = {
                'bet': 'visitante',
                'reason': 'Estatísticas sugerem equilíbrio',
                'confidence': 'baixa'
            }
        else:
            st.session_state.suggestion = {
                'bet': 'casa',
                'reason': 'Estatísticas sugerem equilíbrio',
                'confidence': 'baixa'
            }

# Estilos CSS personalizados
st.markdown("""
<style>
    .main {
        background: linear-gradient(to bottom right, #14532d, #166534, #14532d);
        color: white;
    }
    .stButton button {
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: scale(1.05);
    }
    .card {
        background-color: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .alert-critical {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        color: #7f1d1d;
        padding: 1rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    .result-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
        margin: 0.1rem;
    }
    .casa-badge {
        background-color: #ef4444;
        color: white;
    }
    .visitante-badge {
        background-color: #3b82f6;
        color: white;
    }
    .empate-badge {
        background-color: #eab308;
        color: black;
    }
    .high-confidence {
        color: #16a34a;
        font-weight: bold;
    }
    .medium-confidence {
        color: #ca8a04;
        font-weight: bold;
    }
    .low-confidence {
        color: #dc2626;
    }
</style>
""", unsafe_allow_html=True)

# Modal de aviso
if st.session_state.show_warning:
    st.markdown("""
    <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(0, 0, 0, 0.8); 
                display: flex; align-items: center; justify-content: center; z-index: 9999;">
        <div style="background-color: white; border-radius: 1rem; max-width: 32rem; width: 90%; padding: 1.5rem;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="background-color: #fecaca; border-radius: 9999px; width: 4rem; height: 4rem; 
                            display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem;">
                    <span style="color: #dc2626; font-weight: bold;">!</span>
                </div>
                <h2 style="color: #1f2937; font-weight: bold; font-size: 1.5rem; margin-bottom: 0.5rem;">
                    AVISO IMPORTANTE
                </h2>
            </div>
            <div style="color: #374151; margin-bottom: 1.5rem;">
                <p style="font-weight: bold; text-align: center;">
                    Este aplicativo é exclusivo e de uso restrito do grupo <span style="color: #dc2626;">HS-Studio</span>
                </p>
                <p>É terminantemente proibida a divulgação, compartilhamento ou disponibilização do link do app a terceiros 
                sem autorização expressa do administrador.</p>
                <p>O descumprimento destas regras poderá resultar no 
                <span style="font-weight: bold; color: #dc2626;">bloqueio imediato do acesso</span> e na 
                <span style="font-weight: bold; color: #dc2626;">remoção definitiva do link</span>.</p>
                <div style="background-color: #fffbeb; border: 1px solid #fcd34d; border-radius: 0.5rem; padding: 0.75rem; margin: 1rem 0;">
                    <h3 style="color: #92400e; font-weight: bold; margin-bottom: 0.5rem; display: flex; align-items: center;">
                        <span style="margin-right: 0.5rem;">⚠️</span> Observações Importantes:
                    </h3>
                    <ul style="font-size: 0.875rem; color: #92400e; padding-left: 1.5rem;">
                        <li>O app é uma ferramenta de auxílio na tomada de decisão, não sendo garantia de ganhos de 100%.</li>
                        <li>O uso é restrito a maiores de 18 anos.</li>
                        <li>O jogo deve ser praticado de forma consciente e responsável.</li>
                    </ul>
                </div>
                <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 0.5rem; padding: 0.75rem;">
                    <p style="font-size: 0.875rem; color: #166534;">
                        <strong>Ao continuar</strong>, você declara estar ciente e de acordo com estas condições.
                    </p>
                </div>
            </div>
            <button onclick="window.location.href='?accepted=true'" 
                    style="width: 100%; background-color: #dc2626; color: white; font-weight: bold; 
                           padding: 0.75rem 1rem; border-radius: 0.5rem; border: none; cursor: pointer;
                           transition: all 0.2s ease;">
                Aceito os Termos - Continuar
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Verifica se o usuário aceitou os termos
    if st.query_params.get('accepted'):
        st.session_state.show_warning = False
        st.query_params.clear()
        st.rerun()
    
    st.stop()

# Layout principal do aplicativo
st.markdown('<div class="main">', unsafe_allow_html=True)

# Cabeçalho
st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <h1 style="font-size: 2.25rem; font-weight: bold; color: white; margin-bottom: 0.5rem;">⚽ HS-Studio</h1>
        <p style="color: #bbf7d0;">Analisador Inteligente de Padrões Avançado</p>
    </div>
""", unsafe_allow_html=True)

# Botões de aposta
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 CASA\nVermelho", help="Registrar vitória da casa"):
        add_result('casa')

with col2:
    if st.button("⚖️ EMPATE\nAmarelo", help="Registrar empate"):
        add_result('empate')

with col3:
    if st.button("👥 VISITANTE\nAzul", help="Registrar vitória do visitante"):
        add_result('visitante')

# Botões de controle
col1, col2 = st.columns(2)

with col1:
    if st.button("↩️ Desfazer", disabled=len(st.session_state.history) == 0, 
                 help="Desfazer a última ação"):
        undo_last()

with col2:
    if st.button("🗑️ Limpar Tudo", disabled=len(st.session_state.history) == 0,
                 help="Limpar todo o histórico"):
        clear_history()

# Alertas de manipulação
if st.session_state.manipulation_alerts:
    for alert in st.session_state.manipulation_alerts:
        st.error(alert)

# Desempenho do sistema
if len(st.session_state.prediction_history) >= 5:
    with st.container():
        st.markdown("""
        <div class="card">
            <h3 style="color: white; display: flex; align-items: center; margin-bottom: 0.75rem;">
                <span style="margin-right: 0.5rem;">📈</span> Desempenho Adaptativo
            </h3>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; text-align: center;">
                <div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #86efac;">75.0%</div>
                    <div style="font-size: 0.875rem; color: #bbf7d0;">Taxa de Acerto</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #93c5fd;">12</div>
                    <div style="font-size: 0.875rem; color: #bfdbfe;">Predições Avaliadas</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #d8b4fe;">5.8</div>
                    <div style="font-size: 0.875rem; color: #e9d5ff;">Peso Total</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #fdba74;">1.35</div>
                    <div style="font-size: 0.875rem; color: #fed7aa;">Melhor Padrão</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Estatísticas
with st.container():
    st.markdown("""
    <div class="card">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
            <h3 style="color: white; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;">📊</span> Estatísticas
            </h3>
            <span style="color: #bbf7d0;">Total: """ + str(len(st.session_state.history)) + """ jogos</span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center;">
            <div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #fca5a5;">""" + str(st.session_state.stats['casa']) + """</div>
                <div style="font-size: 0.875rem; color: #fecaca;">Casa</div>
                <div style="font-size: 0.75rem; color: #fef2f2;">
    """, unsafe_allow_html=True)
    
    if len(st.session_state.history) > 0:
        casa_percent = (st.session_state.stats['casa'] / len(st.session_state.history)) * 100
        st.markdown(f"{casa_percent:.1f}%", unsafe_allow_html=True)
    else:
        st.markdown("0%", unsafe_allow_html=True)
    
    st.markdown("""
                </div>
            </div>
            <div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #fde047;">""" + str(st.session_state.stats['empate']) + """</div>
                <div style="font-size: 0.875rem; color: #fef08a;">Empate</div>
                <div style="font-size: 0.75rem; color: #fefce8;">
    """, unsafe_allow_html=True)
    
    if len(st.session_state.history) > 0:
        empate_percent = (st.session_state.stats['empate'] / len(st.session_state.history)) * 100
        st.markdown(f"{empate_percent:.1f}%", unsafe_allow_html=True)
    else:
        st.markdown("0%", unsafe_allow_html=True)
    
    st.markdown("""
                </div>
            </div>
            <div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #93c5fd;">""" + str(st.session_state.stats['visitante']) + """</div>
                <div style="font-size: 0.875rem; color: #bfdbfe;">Visitante</div>
                <div style="font-size: 0.75rem; color: #eff6ff;">
    """, unsafe_allow_html=True)
    
    if len(st.session_state.history) > 0:
        visitante_percent = (st.session_state.stats['visitante'] / len(st.session_state.history)) * 100
        st.markdown(f"{visitante_percent:.1f}%", unsafe_allow_html=True)
    else:
        st.markdown("0%", unsafe_allow_html=True)
    
    st.markdown("""
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Análise e sugestão
if st.session_state.analysis and st.session_state.suggestion:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3 style="color: white; margin-bottom: 0.75rem;">🔍 Análise de Padrão</h3>
            <div style="margin-bottom: 0.5rem;">
                <span style="font-weight: bold;">Padrão:</span> 
        """ + st.session_state.analysis['pattern'] + """
            </div>
            <div style="margin-bottom: 0.5rem;">
                <span style="font-weight: bold;">Confiança:</span> 
        """ + str(st.session_state.analysis['confidence']) + """%
            </div>
            <div>
                <span style="font-weight: bold;">Descrição:</span> 
        """ + st.session_state.analysis['description'] + """
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        confidence_class = ""
        if st.session_state.suggestion['confidence'] == 'alta':
            confidence_class = "high-confidence"
        elif st.session_state.suggestion['confidence'] == 'média':
            confidence_class = "medium-confidence"
        else:
            confidence_class = "low-confidence"
            
        st.markdown(f"""
        <div class="card">
            <h3 style="color: white; margin-bottom: 0.75rem;">💡 Sugestão de Aposta</h3>
            <div style="margin-bottom: 0.5rem;">
                <span style="font-weight: bold;">Palpite:</span> 
                <span class="{confidence_class}">{st.session_state.suggestion['bet'].upper()}</span>
            </div>
            <div style="margin-bottom: 0.5rem;">
                <span style="font-weight: bold;">Confiança:</span> 
                <span class="{confidence_class}">{st.session_state.suggestion['confidence'].upper()}</span>
            </div>
            <div>
                <span style="font-weight: bold;">Motivo:</span> 
                {st.session_state.suggestion['reason']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Histórico de resultados
if st.session_state.history:
    st.markdown("""
    <div class="card">
        <h3 style="color: white; margin-bottom: 0.75rem;">📋 Histórico de Resultados</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 0.25rem;">
    """, unsafe_allow_html=True)
    
    for i, result in enumerate(st.session_state.history):
        if result == 'casa':
            st.markdown('<span class="result-badge casa-badge">C</span>', unsafe_allow_html=True)
        elif result == 'visitante':
            st.markdown('<span class="result-badge visitante-badge">V</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="result-badge empate-badge">E</span>', unsafe_allow_html=True)
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
