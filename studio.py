import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Configuração inicial da página
st.set_page_config(
    page_title="HS Studio App - Padrões Avançados",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inicialização do estado da sessão
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
if 'current_pattern' not in st.session_state:
    st.session_state.current_pattern = None
if 'current_layer' not in st.session_state:
    st.session_state.current_layer = 1

# Dicionário de padrões (1-40)
PATTERNS = {
    1: {
        "name": "Repetição Simples Vermelha",
        "description": "Três ou mais vermelhos consecutivos",
        "formation": "🔴 🔴 🔴",
        "normal_bet": "Apostar vermelho na próxima rodada",
        "manipulation_bet": {
            "1-3": "Seguir vermelho",
            "4-6": "Ficar atento à quebra",
            "7-9": "Esperar confirmação antes de apostar"
        }
    },
    2: {
        "name": "Repetição Simples Azul",
        "description": "Três ou mais azuis consecutivos",
        "formation": "🔵 🔵 🔵",
        "normal_bet": "Apostar azul",
        "manipulation_bet": {
            "1-3": "Seguir azul",
            "4-6": "Ficar atento à quebra",
            "7-9": "Esperar confirmação antes de apostar"
        }
    },
    3: {
        "name": "Alternância Simples",
        "description": "Vermelho e azul alternando",
        "formation": "🔴 🔵 🔴 🔵",
        "normal_bet": "Apostar na sequência da alternância",
        "manipulation_bet": {
            "1-3": "Seguir alternância",
            "4-6": "Cuidado com empates",
            "7-9": "Apostar só quando padrão completo aparecer duas vezes"
        }
    },
    4: {
        "name": "Empate como âncora",
        "description": "Empate aparece entre duas cores",
        "formation": "🔴 🟡 🔵",
        "normal_bet": "Ignorar o empate, apostar na cor que rompe o padrão",
        "manipulation_bet": {
            "1-3": "Padrão simples",
            "4-6": "Apostar na cor que veio antes do empate",
            "7-9": "Aguardar confirmação da cor dominante após empate"
        }
    },
    5: {
        "name": "Repetição + Alternância",
        "description": "Dupla repetida seguida de alternância",
        "formation": "🔴 🔴 🔵 🔵",
        "normal_bet": "Apostar na próxima cor seguindo la alternância",
        "manipulation_bet": {
            "1-3": "Padrão previsível",
            "4-6": "Apostar após confirmar dois ciclos",
            "7-9": "Só apostar se ciclo completo se repetir"
        }
    },
    # Adicione os outros padrões seguindo a mesma estrutura
}

# Funções auxiliares
def add_result(result):
    st.session_state.history.insert(0, result)
    update_stats()
    determine_layer()
    analyze_patterns()

def undo_last():
    if st.session_state.history:
        st.session_state.history.pop(0)
        update_stats()
        determine_layer()
        analyze_patterns()

def clear_history():
    st.session_state.history = []
    st.session_state.stats = {'casa': 0, 'visitante': 0, 'empate': 0}
    st.session_state.analysis = None
    st.session_state.suggestion = None
    st.session_state.manipulation_alerts = []
    st.session_state.current_pattern = None
    st.session_state.current_layer = 1

def update_stats():
    stats = {'casa': 0, 'visitante': 0, 'empate': 0}
    for result in st.session_state.history:
        stats[result] += 1
    st.session_state.stats = stats

def determine_layer():
    history_len = len(st.session_state.history)
    if history_len < 15:
        st.session_state.current_layer = 1
    elif history_len < 30:
        st.session_state.current_layer = 4
    else:
        st.session_state.current_layer = 7

def detect_pattern(history):
    if len(history) < 3:
        return None
    
    # Verifica padrão 1: Repetição Simples Vermelha
    if len(history) >= 3 and history[0] == 'casa' and history[1] == 'casa' and history[2] == 'casa':
        return 1
    
    # Verifica padrão 2: Repetição Simples Azul
    if len(history) >= 3 and history[0] == 'visitante' and history[1] == 'visitante' and history[2] == 'visitante':
        return 2
    
    # Verifica padrão 3: Alternância Simples
    if len(history) >= 4 and history[0] != history[1] and history[1] != history[2] and history[2] != history[3] and history[0] != history[2]:
        return 3
    
    # Verifica padrão 4: Empate como âncora
    if len(history) >= 3 and history[1] == 'empate' and history[0] != 'empate' and history[2] != 'empate' and history[0] != history[2]:
        return 4
    
    # Verifica padrão 5: Repetição + Alternância
    if len(history) >= 4 and history[0] == history[1] and history[2] == history[3] and history[0] != history[2]:
        return 5
    
    return None

def analyze_patterns():
    history = st.session_state.history
    if len(history) < 3:
        st.session_state.analysis = {'pattern': 'Dados insuficientes', 'confidence': 0, 'description': 'Aguarde mais resultados', 'formation': 'N/A'}
        st.session_state.suggestion = {'bet': 'Aguarde', 'reason': 'Aguarde mais resultados para análise', 'confidence': 'baixa'}
        st.session_state.manipulation_alerts = []
        st.session_state.current_pattern = None
        return
    
    pattern_id = detect_pattern(history)
    
    if pattern_id:
        pattern = PATTERNS[pattern_id]
        st.session_state.current_pattern = pattern_id
        
        layer = st.session_state.current_layer
        
        if layer <= 3:
            manipulation_key = "1-3"
        elif layer <= 6:
            manipulation_key = "4-6"
        else:
            manipulation_key = "7-9"
            
        manipulation_advice = pattern["manipulation_bet"].get(manipulation_key, "")
        
        st.session_state.analysis = {
            'pattern': pattern["name"],
            'confidence': 75,
            'description': pattern["description"],
            'formation': pattern["formation"]
        }
        
        bet = 'Aguarde'
        if pattern_id == 1:
            bet = 'casa'
        elif pattern_id == 2:
            bet = 'visitante'
        elif pattern_id == 3:
            bet = 'visitante' if history[0] == 'casa' else 'casa'
        elif pattern_id == 4:
            bet = history[0] if history[0] != 'empate' else history[2]
        elif pattern_id == 5:
            bet = 'visitante' if history[0] == 'casa' else 'casa'
        
        st.session_state.suggestion = {
            'bet': bet,
            'reason': f"{pattern['name']}. {manipulation_advice}",
            'confidence': 'alta' if layer <= 3 else 'média' if layer <= 6 else 'baixa'
        }
    else:
        st.session_state.analysis = {
            'pattern': 'Padrão Aleatório',
            'confidence': 40,
            'description': 'Nenhum padrão claro detectado',
            'formation': 'N/A'
        }
        
        if st.session_state.stats['casa'] > st.session_state.stats['visitante']:
            bet_suggestion = 'visitante'
        elif st.session_state.stats['visitante'] > st.session_state.stats['casa']:
            bet_suggestion = 'casa'
        else:
            bet_suggestion = 'empate'
        
        st.session_state.suggestion = {
            'bet': bet_suggestion,
            'reason': 'Estatísticas sugerem equilíbrio',
            'confidence': 'baixa'
        }
        st.session_state.current_pattern = None

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
        border: none;
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
    .pattern-card {
        background-color: rgba(255, 255, 255, 0.15);
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #86efac;
    }
    .layer-indicator {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
        background-color: #3b82f6;
        color: white;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Layout principal do aplicativo
st.markdown('<div class="main">', unsafe_allow_html=True)

# Cabeçalho
st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <h1 style="font-size: 2.25rem; font-weight: bold; color: white; margin-bottom: 0.5rem;">⚽ HS-Studio</h1>
        <p style="color: #bbf7d0;">Analisador Inteligente de Padrões Avançados - Camada {st.session_state.current_layer}</p>
    </div>
""", unsafe_allow_html=True)

# Botões de aposta
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 CASA\nVermelho", help="Registrar vitória da casa", use_container_width=True):
        add_result('casa')

with col2:
    if st.button("⚖️ EMPATE\nAmarelo", help="Registrar empate", use_container_width=True):
        add_result('empate')

with col3:
    if st.button("👥 VISITANTE\nAzul", help="Registrar vitória do visitante", use_container_width=True):
        add_result('visitante')

# Botões de controle
col1, col2 = st.columns(2)

with col1:
    if st.button("↩️ Desfazer", disabled=len(st.session_state.history) == 0, 
                 help="Desfazer a última ação", use_container_width=True):
        undo_last()

with col2:
    if st.button("🗑️ Limpar Tudo", disabled=len(st.session_state.history) == 0,
                 help="Limpar todo o histórico", use_container_width=True):
        clear_history()

# Indicador de camada
layer = st.session_state.current_layer
layer_text = ""
if layer <= 3:
    layer_text = "Camada 1-3: Padrões simples, apostar direto"
elif layer <= 6:
    layer_text = "Camada 4-6: Manipulação intermediária, esperar confirmação"
else:
    layer_text = "Camada 7-9: Manipulação avançada, confirmar padrões"

st.markdown(f"""
    <div class="card">
        <div class="layer-indicator">Camada {layer}</div>
        <p style="color: white; margin: 0;">{layer_text}</p>
    </div>
""", unsafe_allow_html=True)

# Alertas de manipulação
if st.session_state.manipulation_alerts:
    for alert in st.session_state.manipulation_alerts:
        st.error(alert)

# Análise e sugestão
if st.session_state.analysis and st.session_state.suggestion:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="card">
            <h3 style="color: white; margin-bottom: 0.75rem;">🔍 Análise de Padrão</h3>
            <div style="margin-bottom: 0.5rem;">
                <span style="font-weight: bold;">Padrão:</span> 
                {st.session_state.analysis['pattern']}
            </div>
            <div style="margin-bottom: 0.5rem;">
                <span style="font-weight: bold;">Formação:</span> 
                {st.session_state.analysis.get('formation', 'N/A')}
            </div>
            <div style="margin-bottom: 0.5rem;">
                <span style="font-weight: bold;">Confiança:</span> 
                {st.session_state.analysis['confidence']}%
            </div>
            <div>
                <span style="font-weight: bold;">Descrição:</span> 
                {st.session_state.analysis['description']}
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

# SEÇÃO DE HISTÓRICO CORRIGIDA PARA EXIBIÇÃO HORIZONTAL
if st.session_state.history:
    st.markdown("""
    <div class="card">
        <h3 style="color: white; margin-bottom: 0.75rem;">📋 Histórico de Resultados</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 0.25rem;">
    """, unsafe_allow_html=True)
    
    for result in st.session_state.history:
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

# Seção de Padrões (apenas para referência)
with st.expander("📚 Referência de Padrões (1-10)"):
    for i in range(1, 11):
        if i in PATTERNS:
            pattern = PATTERNS[i]
            st.markdown(f"""
            <div class="pattern-card">
                <h4 style="color: white; margin-bottom: 0.5rem;">Padrão {i}: {pattern['name']}</h4>
                <p style="color: #d1d5db; margin-bottom: 0.5rem;"><strong>Formação:</strong> {pattern['formation']}</p>
                <p style="color: #d1d5db; margin-bottom: 0.5rem;"><strong>Descrição:</strong> {pattern['description']}</p>
                <p style="color: #d1d5db; margin-bottom: 0.5rem;"><strong>Aposta Normal:</strong> {pattern['normal_bet']}</p>
                <p style="color: #d1d5db;"><strong>Aposta com Manipulação:</strong></p>
                <ul style="color: #d1d5db;">
                    <li>Camada 1-3: {pattern['manipulation_bet']['1-3']}</li>
                    <li>Camada 4-6: {pattern['manipulation_bet']['4-6']}</li>
                    <li>Camada 7-9: {pattern['manipulation_bet']['7-9']}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
