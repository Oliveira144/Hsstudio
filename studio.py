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
            "4-6": "Ficar atento à quebra; Camada 4–5, ficar atento à quebra; Camada 6–9, esperar confirmação antes de apostar",
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
            "4-6": "Ficar atento à quebra; Mesma lógica do padrão 1",
            "7-9": "Esperar confirmação antes de apostar"
        }
    },
    3: {
        "name": "Alternância Simples",
        "description": "Vermelho e azul alternando",
        "formation": "🔴 🔵 🔴 🔵",
        "normal_bet": "Apostar na sequência da alternância",
        "manipulation_bet": {
            "1-3": "Seguir alternância; Camada 1–3, seguir alternância",
            "4-6": "Cuidado com empates; Camada 4–5, cuidado com empates",
            "7-9": "Apostar só quando padrão completo aparecer duas vezes; Camada 6–9, apostar só quando padrão completo aparecer duas vezes"
        }
    },
    4: {
        "name": "Empate como âncora",
        "description": "Empate aparece entre duas cores",
        "formation": "🔴 🟡 🔵",
        "normal_bet": "Ignorar o empate, apostar na cor que rompe o padrão",
        "manipulation_bet": {
            "1-3": "Padrão simples; Camadas 1–3, padrão simples",
            "4-6": "Apostar na cor que veio antes do empate; 4–6, apostar na cor que veio antes do empate",
            "7-9": "Aguardar confirmação da cor dominante após empate; 7–9, aguardar confirmação da cor dominante após empate"
        }
    },
    5: {
        "name": "Repetição + Alternância",
        "description": "Dupla repetida seguida de alternância",
        "formation": "🔴 🔴 🔵 🔵",
        "normal_bet": "Apostar na próxima cor seguindo a alternância",
        "manipulation_bet": {
            "1-3": "Padrão previsível; Camada 1–3, padrão previsível",
            "4-6": "Apostar após confirmar dois ciclos; Camada 4–6, apostar após confirmar dois ciclos",
            "7-9": "Só apostar se ciclo completo se repetir; Camada 7–9, só apostar se ciclo completo se repetir"
        }
    },
    6: {
        "name": "Tripla Alternada",
        "description": "Alternância de três blocos",
        "formation": "🔴 🔵 🔴 🔵 🔴",
        "normal_bet": "Apostar na próxima cor seguindo o ciclo",
        "manipulation_bet": {
            "1-3": "Apostar conforme padrão; Camadas 1–3, apostar conforme padrão",
            "4-6": "Confirmar inversão antes de apostar; 4–6, confirmar inversão antes de apostar",
            "7-9": "Aguardar padrão duplo para segurança; 7–9, aguardar padrão duplo para segurança"
        }
    },
    7: {
        "name": "Empate no meio",
        "description": "Empate ocorre no meio de sequência",
        "formation": "🔴 🔵 🟡 🔴",
        "normal_bet": "Apostar na cor que veio antes do empate",
        "manipulation_bet": {
            "1-3": "Seguir tendência simples; Camada 1–3, seguir tendência simples",
            "4-6": "Esperar ver se a cor dominante retorna; 4–6, esperar ver se a cor dominante retorna",
            "7-9": "Só apostar após padrão se repetir; 7–9, só apostar após padrão se repetir"
        }
    },
    8: {
        "name": "Padrão Zig-Zag",
        "description": "Alternância irregular",
        "formation": "🔴 🔵 🔵 🔴 🔵",
        "normal_bet": "Apostar seguindo zig-zag",
        "manipulation_bet": {
            "1-3": "Aposta direta; Camadas 1–3, aposta direta",
            "4-6": "Aguardar confirmação de duas sequências; 4–6, aguardar confirmação de duas sequências",
            "7-9": "Só apostar se ciclo longo se repetir; 7–9, só apostar se ciclo longo se repetir"
        }
    },
    9: {
        "name": "Quebra de repetição",
        "description": "Cor diferente quebra repetição",
        "formation": "🔴 🔴 🔵",
        "normal_bet": "Apostar na cor que rompeu a repetição",
        "manipulation_bet": {
            "1-3": "Apostar na cor nova; Camada 1–3, apostar na cor nova",
            "4-6": "Esperar nova confirmação; 4–6, esperar nova confirmação",
            "7-9": "Aguardar dois ciclos da cor nova; 7–9, aguardar dois ciclos da cor nova"
        }
    },
    10: {
        "name": "Quebra dupla",
        "description": "Duas cores repetidas e depois troca",
        "formation": "🔴 🔵 🔵 🔴 🔴 🔵",
        "normal_bet": "Apostar na cor que rompeu sequência dupla",
        "manipulation_bet": {
            "1-3": "Seguir sequência; Camada 1–3, seguir sequência",
            "4-6": "Confirmar ciclo; 4–6, confirmar ciclo",
            "7-9": "Esperar padrão completo antes de apostar; 7–9, esperar padrão completo antes de apostar"
        }
    },
    11: {
        "name": "Empate repetido",
        "description": "Dois empates seguidos",
        "formation": "🟡 🟡 🔴",
        "normal_bet": "Apostar na cor que vem após os empates",
        "manipulation_bet": {
            "1-3": "Apostar imediatamente na cor que rompeu; Camadas 1–3, apostar imediatamente na cor que rompeu",
            "4-6": "Esperar padrão se repetir; 4–6, esperar padrão se repetir",
            "7-9": "Aguardar confirmação de dois ciclos; 7–9, aguardar confirmação de dois ciclos"
        }
    },
    12: {
        "name": "Tripla alternada invertida",
        "description": "Alternância de 6 resultados invertida",
        "formation": "🔵 🔴 🔵 🔴 🔵 🔴",
        "normal_bet": "Apostar seguindo alternância",
        "manipulation_bet": {
            "1-3": "Apostar na sequência; Camadas 1–3, apostar na sequência",
            "4-6": "Esperar inversão se confirmar; 4–6, esperar inversão se confirmar",
            "7-9": "Só apostar após padrão completo se repetir; 7–9, só apostar após padrão completo se repetir"
        }
    },
    13: {
        "name": "Sequência crescente",
        "description": "Pares de cores repetidos e alternados",
        "formation": "🔴 🔴 🔵 🔵 🔴 🔴 🔵",
        "normal_bet": "Apostar seguindo próximo par",
        "manipulation_bet": {
            "1-3": "Seguir o próximo par; Camadas 1–3, seguir o próximo par",
            "4-6": "Confirmar ciclo; 4–6, confirmar ciclo",
            "7-9": "Só apostar se ciclo duplo se repetir; 7–9, só apostar se ciclo duplo se repetir"
        }
    },
    14: {
        "name": "Sequência decrescente",
        "description": "Sequência alternada terminando em cor repetida",
        "formation": "🔵 🔴 🔵 🔴 🔵 🔴 🔴",
        "normal_bet": "Apostar na cor que rompe a repetição",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Esperar confirmação; 4–6, esperar confirmação",
            "7-9": "Aguardar dois ciclos completos; 7–9, aguardar dois ciclos completos"
        }
    },
    15: {
        "name": "Alternância com empate",
        "description": "Empates entre alternâncias",
        "formation": "🔴 🟡 🔵 🟡 🔴",
        "normal_bet": "Apostar na cor anterior ao empate",
        "manipulation_bet": {
            "1-3": "Seguir cor anterior; Camadas 1–3, seguir cor anterior",
            "4-6": "Esperar padrão se repetir; 4–6, esperar padrão se repetir",
            "7-9": "Apostar somente após confirmação de ciclo; 7–9, apostar somente após confirmação de ciclo"
        }
    },
    16: {
        "name": "Ciclo triplo",
        "description": "Ciclos de três cores repetidos",
        "formation": "🔴 🔵 🔵 🔴 🔵 🔵",
        "normal_bet": "Apostar na cor que completa o ciclo",
        "manipulation_bet": {
            "1-3": "Apostar conforme ciclo; Camadas 1–3, apostar conforme ciclo",
            "4-6": "Esperar repetição dupla; 4–6, esperar repetição dupla",
            "7-9": "Só apostar após dois ciclos completos; 7–9, só apostar após dois ciclos completos"
        }
    },
    17: {
        "name": "Sequência complexa",
        "description": "Alternância irregular com dominância de cor",
        "formation": "🔴 🔵 🔴 🔵 🔵 🔴 🔵",
        "normal_bet": "Apostar na cor dominante",
        "manipulation_bet": {
            "1-3": "Seguir dominância; Camadas 1–3, seguir dominância",
            "4-6": "Aguardar confirmação; 4–6, aguardar confirmação",
            "7-9": "Esperar padrão se repetir duas vezes; 7–9, esperar padrão se repetir duas vezes"
        }
    },
    18: {
        "name": "Empate entre cores",
        "description": "Empate separando duas cores",
        "formation": "🔵 🟡 🔴",
        "normal_bet": "Apostar na cor que rompe o empate",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Esperar confirmação; 4–6, esperar confirmação",
            "7-9": "Só apostar após dois ciclos completos; 7–9, só apostar após dois ciclos completos"
        }
    },
    19: {
        "name": "Padrão 'goleada'",
        "description": "Três repetições de uma cor seguidas por duas da outra",
        "formation": "🔴 🔴 🔴 🔵 🔵",
        "normal_bet": "Apostar na cor da sequência dupla",
        "manipulation_bet": {
            "1-3": "Seguir a dupla; Camadas 1–3, seguir a dupla",
            "4-6": "Confirmar ciclo; 4–6, confirmar ciclo",
            "7-9": "Esperar repetição do padrão completo; 7–9, esperar repetição do padrão completo"
        }
    },
    20: {
        "name": "Alternância com repetição dupla",
        "description": "Duas alternâncias consecutivas",
        "formation": "🔴 🔵 🔵 🔴 🔵 🔵",
        "normal_bet": "Apostar seguindo o ciclo da segunda dupla",
        "manipulation_bet": {
            "1-3": "Apostar diretamente; Camadas 1–3, apostar diretamente",
            "4-6": "Aguardar confirmação da segunda dupla; 4–6, aguardar confirmação da segunda dupla",
            "7-9": "Só apostar após padrão duplo; 7–9, só apostar após padrão duplo"
        }
    },
    21: {
        "name": "Tripla repetida com alternância",
        "description": "Três da mesma cor seguidas por alternância",
        "formation": "🔴 🔴 🔴 🔵 🔵 🔴",
        "normal_bet": "Apostar seguindo a alternância",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Confirmar ciclo; 4–6, confirmar ciclo",
            "7-9": "Esperar repetição; 7–9, esperar repetição"
        }
    },
    22: {
        "name": "Dupla invertida",
        "description": "Dupla de cores invertidas no meio da sequência",
        "formation": "🔵 🔵 🔴 🔴 🔵",
        "normal_bet": "Apostar na cor que fecha a inversão",
        "manipulation_bet": {
            "1-3": "Apostar diretamente; Camadas 1–3, apostar diretamente",
            "4-6": "Aguardar confirmação; 4–6, aguardar confirmação",
            "7-9": "Só após repetição; 7–9, só após repetição"
        }
    },
    23: {
        "name": "Empate entre duplas",
        "description": "Empate separando duplas de cores",
        "formation": "🔴 🔴 🟡 🔵 🔵",
        "normal_bet": "Apostar na cor que segue após empate",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Esperar confirmação; 4–6, esperar confirmação",
            "7-9": "Esperar dois ciclos completos; 7–9, esperar dois ciclos completos"
        }
    },
    24: {
        "name": "Sequência zig-zag longa",
        "description": "Alternância de várias cores sem repetição direta",
        "formation": "🔴 🔵 🔴 🔵 🔴 🔵 🔴",
        "normal_bet": "Apostar seguindo zig-zag",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Aguardar repetição parcial; 4–6, aguardar repetição parcial",
            "7-9": "Só apostar após ciclo completo; 7–9, só apostar após ciclo completo"
        }
    },
    25: {
        "name": "Padrão 'correr e parar'",
        "description": "Repetições curtas seguidas por mudança",
        "formation": "🔵 🔵 🔴 🔴 🔴",
        "normal_bet": "Apostar na cor que interrompe a repetição longa",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Esperar confirmação; 4–6, esperar confirmação",
            "7-9": "Aguardar repetição do padrão; 7–9, aguardar repetição do padrão"
        }
    },
    26: {
        "name": "Alternância tripla com empate",
        "description": "Alternância de três cores com empate no meio",
        "formation": "🔴 🔵 🔵 🟡 🔴 🔵",
        "normal_bet": "Apostar na cor dominante antes do empate",
        "manipulation_bet": {
            "1-3": "Seguir direto; Camadas 1–3, seguir direto",
            "4-6": "Aguardar confirmação; 4–6, aguardar confirmação",
            "7-9": "Só apostar após ciclo completo; 7–9, só apostar após ciclo completo"
        }
    },
    27: {
        "name": "Repetição quádrupla",
        "description": "Quatro da mesma cor seguidos por outra cor",
        "formation": "🔴 🔴 🔴 🔴 🔵",
        "normal_bet": "Apostar na nova cor",
        "manipulation_bet": {
            "1-3": "Apostar na cor que rompe; Camadas 1–3, apostar na cor que rompe",
            "4-6": "Confirmar padrão; 4–6, confirmar padrão",
            "7-9": "Esperar repetição do padrão; 7–9, esperar repetição do padrão"
        }
    },
    28: {
        "name": "Quebra dupla com empate",
        "description": "Duas cores repetidas e empate",
        "formation": "🔴 🔴 🟡 🔵 🔵",
        "normal_bet": "Apostar na cor que rompe a dupla",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Confirmar padrão; 4–6, confirmar padrão",
            "7-9": "Esperar ciclo duplo; 7–9, esperar ciclo duplo"
        }
    },
    29: {
        "name": "Empate seguido de cor dominante",
        "description": "Empate seguido por sequência de mesma cor",
        "formation": "🟡 🔵 🔵 🔵",
        "normal_bet": "Apostar na cor dominante",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Esperar confirmação; 4–6, esperar confirmação",
            "7-9": "Aguardar dois ciclos; 7–9, aguardar dois ciclos"
        }
    },
    30: {
        "name": "Sequência inversa",
        "description": "Padrão invertido de alternância",
        "formation": "🔴 🔵 🔵 🔴 🔴 🔵 🔴",
        "normal_bet": "Apostar na cor dominante",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Confirmar ciclo; 4–6, confirmar ciclo",
            "7-9": "Aguardar repetição do padrão; 7–9, aguardar repetição do padrão"
        }
    },
    31: {
        "name": "Padrão contínuo de 5",
        "description": "Cinco resultados consecutivos com cores alternadas ou repetidas",
        "formation": "🔵 🔵 🔴 🔴 🔵",
        "normal_bet": "Apostar na cor que completa a sequência de 5",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Esperar confirmação da última cor; 4–6, esperar confirmação da última cor",
            "7-9": "Só apostar após repetição do ciclo completo; 7–9, só apostar após repetição do ciclo completo"
        }
    },
    32: {
        "name": "Tripla alternada com inversão",
        "description": "Alternância de três blocos repetidos invertidos",
        "formation": "🔴 🔵 🔴 🔵 🔴 🔵 🔴",
        "normal_bet": "Apostar na cor que mantém a alternância",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Confirmar padrão antes de apostar; 4–6, confirmar padrão antes de apostar",
            "7-9": "Aguardar repetição completa do ciclo; 7–9, aguardar repetição completa do ciclo"
        }
    },
    33: {
        "name": "Empate interrompendo ciclo",
        "description": "Empate aparece no meio de uma sequência",
        "formation": "🔵 🔵 🟡 🔴 🔴",
        "normal_bet": "Apostar na cor que retoma o ciclo",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Aguardar confirmação da retomada; 4–6, aguardar confirmação da retomada",
            "7-9": "Só apostar após dois ciclos completos; 7–9, só apostar após dois ciclos completos"
        }
    },
    34: {
        "name": "Padrão 'ancorado' no empate",
        "description": "Empate usado como reset de padrão",
        "formation": "🟡 🔴 🔵 🔴 🔵",
        "normal_bet": "Apostar na cor dominante antes do empate",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Confirmar sequência; 4–6, confirmar sequência",
            "7-9": "Esperar ciclo duplo para segurança; 7–9, esperar ciclo duplo para segurança"
        }
    },
    35: {
        "name": "Ciclo longo de alternância dupla",
        "description": "Alternância de pares de cores por 8 resultados",
        "formation": "🔴 🔵 🔵 🔴 🔵 🔵 🔴 🔵",
        "normal_bet": "Apostar seguindo o próximo par do ciclo",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Esperar confirmação parcial; 4–6, esperar confirmação parcial",
            "7-9": "Só apostar após ciclo completo; 7–9, só apostar após ciclo completo"
        }
    },
    36: {
        "name": "Sequência dupla + tripla alternada",
        "description": "Combinação de duas repetições e alternância tripla",
        "formation": "🔵 🔵 🔴 🔵 🔴 🔵",
        "normal_bet": "Apostar na cor que completa a alternância tripla",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Esperar confirmação do ciclo; 4–6, esperar confirmação do ciclo",
            "7-9": "Aguardar repetição do padrão completo; 7–9, aguardar repetição do padrão completo"
        }
    },
    37: {
        "name": "Repetição parcial com inversão",
        "description": "Repetição de duas cores seguida por inversão",
        "formation": "🔴 🔴 🔵 🔴 🔵",
        "normal_bet": "Apostar na cor que completa a inversão",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Confirmar padrão antes de apostar; 4–6, confirmar padrão antes de apostar",
            "7-9": "Esperar repetição do ciclo completo; 7–9, esperar repetição do ciclo completo"
        }
    },
    38: {
        "name": "Empate em sequência complexa",
        "description": "Empate aparece em meio a padrão irregular",
        "formation": "🔴 🔵 🟡 🔵 🔴",
        "normal_bet": "Apostar na cor que domina após empate",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Confirmar sequência; 4–6, confirmar sequência",
            "7-9": "Só apostar após ciclo completo; 7–9, só apostar após ciclo completo"
        }
    },
    39: {
        "name": "Dupla repetida + inversão",
        "description": "Duas cores repetidas seguidas de inversão",
        "formation": "🔴 🔴 🔵 🔵 🔴",
        "normal_bet": "Apostar na cor que fecha a inversão",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Aguardar confirmação; 4–6, aguardar confirmação",
            "7-9": "Só apostar após repetição do padrão; 7–9, só apostar após repetição do padrão"
        }
    },
    40: {
        "name": "Sequência final de quebra",
        "description": "Três ou mais repetições seguidas por cor diferente",
        "formation": "🔵 🔵 🔵 🔴 🔵",
        "normal_bet": "Apostar na cor que rompe a sequência longa",
        "manipulation_bet": {
            "1-3": "Apostar direto; Camadas 1–3, apostar direto",
            "4-6": "Confirmar padrão; 4–6, confirmar padrão",
            "7-9": "Esperar repetição do padrão completo; 7–9, esperar repetição do padrão completo"
        }
    }
}

# Funções auxiliares
def add_result(result):
    st.session_state.history.insert(0, result)
    st.session_state.manipulation_alerts = [] # Limpa os alertas a cada nova rodada
    update_stats()
    determine_layer()
    analyze_patterns()

def undo_last():
    if st.session_state.history:
        st.session_state.history.pop(0)
        st.session_state.manipulation_alerts = []
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

def get_bet_suggestion(pattern_id, history):
    if pattern_id == 1:
        return 'casa'
    elif pattern_id == 2:
        return 'visitante'
    elif pattern_id == 3:
        return 'visitante' if history[0] == 'casa' else 'casa'
    elif pattern_id == 4:
        return history[0] if history[0] != 'empate' else history[2]
    elif pattern_id == 5:
        return 'visitante' if history[0] == 'casa' else 'casa'
    elif pattern_id == 6:
        return history[1] if history[0] == history[2] else history[0]
    elif pattern_id == 7:
        return history[0]
    elif pattern_id == 8:
        return 'visitante' if history[0] == 'casa' else 'casa'
    elif pattern_id == 9:
        return history[0] if history[0] != history[1] else history[2]
    elif pattern_id == 10:
        return history[0] if history[0] != history[1] else history[2]
    elif pattern_id == 11:
        return history[0]
    elif pattern_id == 12:
        return history[0] if history[0] != history[1] else history[2]
    elif pattern_id == 13:
        return history[0] if history[0] != history[1] else history[2]
    elif pattern_id == 14:
        return history[0] if history[0] != history[1] else history[2]
    elif pattern_id == 15:
        return history[0] if history[0] != history[2] else history[1]
    elif pattern_id == 16:
        return history[0] if history[0] != history[1] else history[2]
    elif pattern_id == 17:
        return history[1] if history[0] == 'casa' and history[1] == 'visitante' else history[0]
    elif pattern_id == 18:
        return history[0] if history[0] != 'empate' else history[2]
    elif pattern_id == 19:
        return history[2] if history[0] == history[1] == history[2] else history[0]
    elif pattern_id == 20:
        return history[0] if history[0] == history[1] and history[2] == history[3] else history[2]
    elif pattern_id == 21:
        return history[0] if history[0] == history[1] and history[2] == history[3] and history[3] != history[4] else history[1]
    elif pattern_id == 22:
        return history[0] if history[0] == history[1] and history[2] == history[3] and history[3] != history[4] else history[1]
    elif pattern_id == 23:
        return history[0] if history[0] == history[1] and history[2] == 'empate' and history[3] == history[4] else history[2]
    elif pattern_id == 24:
        return history[0] if history[0] != history[1] and history[1] != history[2] else history[2]
    elif pattern_id == 25:
        return history[0] if history[0] == history[1] and history[2] == history[3] and history[3] == history[4] else history[2]
    elif pattern_id == 26:
        return history[0] if history[0] != 'empate' else history[1]
    elif pattern_id == 27:
        return history[0] if history[0] == history[1] and history[1] == history[2] and history[2] == history[3] else history[4]
    elif pattern_id == 28:
        return history[0] if history[0] == history[1] and history[2] == 'empate' else history[3]
    elif pattern_id == 29:
        return history[1] if history[0] == 'empate' else history[0]
    elif pattern_id == 30:
        return history[0] if history[0] == history[1] and history[2] == history[3] and history[3] != history[4] else history[2]
    elif pattern_id == 31:
        return history[0] if history[0] == history[1] and history[2] == history[3] and history[4] == history[5] else history[1]
    elif pattern_id == 32:
        return history[0] if history[0] != history[1] and history[1] != history[2] and history[2] != history[3] and history[3] != history[4] else history[1]
    elif pattern_id == 33:
        return history[0] if history[0] == history[1] and history[2] == 'empate' else history[3]
    elif pattern_id == 34:
        return history[1] if history[0] == 'empate' else history[0]
    elif pattern_id == 35:
        return history[0] if history[0] == history[1] and history[2] == history[3] and history[4] == history[5] and history[6] == history[7] else history[2]
    elif pattern_id == 36:
        return history[0] if history[0] == history[1] and history[2] == 'empate' else history[3]
    elif pattern_id == 37:
        return history[0] if history[0] == history[1] and history[2] != history[3] else history[2]
    elif pattern_id == 38:
        return history[0] if history[0] != history[1] and history[1] == 'empate' else history[2]
    elif pattern_id == 39:
        return history[0] if history[0] == history[1] and history[2] == history[3] and history[3] != history[4] else history[2]
    elif pattern_id == 40:
        return history[0] if history[0] == history[1] and history[1] == history[2] and history[2] != history[3] else history[3]
    
    return 'Aguarde' # Palpite padrão se não houver lógica específica

def detect_pattern(history):
    history_tuple = tuple(history)
    
    # Lógica de detecção para os 40 padrões
    if len(history) >= 3 and history[0] == 'casa' and history[1] == 'casa' and history[2] == 'casa': return 1
    if len(history) >= 3 and history[0] == 'visitante' and history[1] == 'visitante' and history[2] == 'visitante': return 2
    if len(history) >= 4 and history[0] != history[1] and history[1] != history[2] and history[2] != history[3] and history[0] != history[2]: return 3
    if len(history) >= 3 and history[1] == 'empate' and history[0] != 'empate' and history[2] != 'empate' and history[0] != history[2]: return 4
    if len(history) >= 4 and history[0] == history[1] and history[2] == history[3] and history[0] != history[2]: return 5
    if len(history) >= 5 and history[0] != history[1] and history[1] != history[2] and history[2] != history[3] and history[3] != history[4] and history[0] == history[2] and history[2] == history[4]: return 6
    if len(history) >= 4 and history[1] != history[2] and history[2] == 'empate': return 7
    if len(history) >= 5 and history[0] != history[1] and history[1] == history[2] and history[2] != history[3] and history[3] != history[4]: return 8
    if len(history) >= 3 and history[0] == history[1] and history[1] != history[2]: return 9
    if len(history) >= 6 and history[0] == history[1] and history[1] != history[2] and history[2] == history[3] and history[3] != history[4] and history[4] == history[5]: return 10
    if len(history) >= 3 and history[0] == 'empate' and history[1] == 'empate' and history[2] != 'empate': return 11
    if len(history) >= 6 and history[0] != history[1] and history[1] != history[2] and history[2] != history[3] and history[3] != history[4] and history[4] != history[5]: return 12
    if len(history) >= 7 and history[0] == history[1] and history[2] == history[3] and history[4] == history[5]: return 13
    if len(history) >= 7 and history[0] != history[1] and history[1] != history[2] and history[2] != history[3] and history[3] != history[4] and history[4] != history[5] and history[5] == history[6]: return 14
    if len(history) >= 5 and history[0] == history[2] and history[2] == history[4] and history[1] == 'empate' and history[3] == 'empate': return 15
    if len(history) >= 6 and history[0] != history[1] and history[1] == history[2] and history[2] != history[3] and history[3] == history[4] and history[4] != history[5]: return 16
    if len(history) >= 7 and history[0] != history[1] and history[1] != history[2] and history[2] != history[3] and history[3] == history[4] and history[4] != history[5] and history[5] == history[6]: return 17
    if len(history) >= 3 and history[1] == 'empate': return 18
    if len(history) >= 5 and history[0] == history[1] == history[2] and history[3] == history[4] and history[2] != history[3]: return 19
    if len(history) >= 6 and history[0] != history[1] and history[1] == history[2] and history[2] != history[3] and history[3] == history[4] and history[4] != history[5]: return 20
    if len(history) >= 6 and history[0] == history[1] == history[2] and history[3] != history[4] and history[4] != history[5]: return 21
    if len(history) >= 5 and history[0] == history[1] and history[1] != history[2] and history[2] == history[3] and history[3] != history[4]: return 22
    if len(history) >= 5 and history[0] == history[1] and history[2] == 'empate' and history[3] == history[4]: return 23
    if len(history) >= 7 and history[0] != history[1] and history[1] != history[2] and history[2] != history[3] and history[3] != history[4] and history[4] != history[5] and history[5] != history[6]: return 24
    if len(history) >= 5 and history[0] == history[1] and history[1] != history[2] and history[2] == history[3] == history[4]: return 25
    if len(history) >= 6 and history[0] != history[1] and history[1] == history[2] and history[2] != history[3] and history[3] == 'empate': return 26
    if len(history) >= 5 and history[0] == history[1] == history[2] == history[3] and history[3] != history[4]: return 27
    if len(history) >= 5 and history[0] == history[1] and history[2] == 'empate' and history[3] == history[4] and history[0] != history[3]: return 28
    if len(history) >= 4 and history[0] == 'empate' and history[1] == history[2] == history[3]: return 29
    if len(history) >= 7 and history[0] != history[1] and history[1] == history[2] and history[2] != history[3] and history[3] == history[4] and history[4] != history[5] and history[5] == history[6]: return 30
    if len(history) >= 5:
        sub_history = history[:5]
        is_alternating = sub_history[0] != sub_history[1] and sub_history[1] != sub_history[2] and sub_history[2] != sub_history[3] and sub_history[3] != sub_history[4]
        is_repeating = sub_history[0] == sub_history[1] and sub_history[2] == sub_history[3] and sub_history[3] != sub_history[4]
        if is_alternating or is_repeating: return 31
    if len(history) >= 7 and history[0] != history[1] and history[1] == history[2] and history[2] != history[3] and history[3] == history[4] and history[4] != history[5] and history[5] == history[6]: return 32
    if len(history) >= 5 and history[0] == history[1] and history[2] == 'empate' and history[3] == history[4] and history[0] != history[3]: return 33
    if len(history) >= 5 and history[0] == 'empate' and history[1] != history[2] and history[2] != history[3] and history[3] != history[4]: return 34
    if len(history) >= 8 and history[0] == history[1] and history[2] == history[3] and history[4] == history[5] and history[6] == history[7]: return 35
    if len(history) >= 6 and history[0] == history[1] and history[1] != history[2] and history[2] == history[3] and history[3] != history[4] and history[4] == history[5]: return 36
    if len(history) >= 5 and history[0] == history[1] and history[1] != history[2] and history[2] == history[3] and history[3] != history[4]: return 37
    if len(history) >= 5 and history[1] == 'empate' and history[0] != history[2] and history[2] != history[3] and history[3] != history[4]: return 38
    if len(history) >= 5 and history[0] == history[1] and history[2] == history[3] and history[3] != history[4]: return 39
    if len(history) >= 4 and history[0] == history[1] == history[2] and history[2] != history[3]: return 40
    
    return None

def calculate_pattern_confidence(pattern_id, history_len):
    base_confidence = 0
    
    # Ponderação de confiança baseada na complexidade/raridade do padrão
    if pattern_id in [1, 2, 3, 9, 11, 18, 29]: # Padrões mais simples/comuns
        base_confidence = 60
    elif pattern_id in [4, 5, 8, 10, 15, 19, 23, 27, 28, 30, 31, 33, 34, 37, 39, 40]: # Padrões de complexidade média
        base_confidence = 75
    elif pattern_id in [6, 7, 12, 13, 14, 16, 17, 20, 21, 22, 24, 25, 26, 32, 35, 36, 38]: # Padrões mais longos/raros
        base_confidence = 90
    
    # Reduz a confiança com base na camada de manipulação
    layer = st.session_state.current_layer
    if layer >= 7:
        base_confidence *= 0.7  # Reduz 30%
    elif layer >= 4:
        base_confidence *= 0.85 # Reduz 15%
        
    return int(base_confidence)

def analyze_patterns():
    history = st.session_state.history
    
    st.session_state.manipulation_alerts = [] # Reseta os alertas
    
    if len(history) < 3:
        st.session_state.analysis = {'pattern': 'Dados insuficientes', 'confidence': 0, 'description': 'Aguarde mais resultados', 'formation': 'N/A'}
        st.session_state.suggestion = {'bet': 'Aguarde', 'reason': 'Aguarde mais resultados para análise', 'confidence': 'baixa'}
        st.session_state.current_pattern = None
        return
    
    # Adiciona alertas de quebra de padrão em camadas de manipulação
    if st.session_state.current_layer >= 7:
        if len(history) >= 5 and history[0] == history[1] == history[2] == history[3] and history[4] != history[3]:
            st.session_state.manipulation_alerts.append("Alerta: Quebra de repetição longa! Possível alteração de tendência.")
        if len(history) >= 4 and history[0] != history[1] and history[1] == 'empate':
             st.session_state.manipulation_alerts.append("Alerta: Empate inesperado! Fique atento a uma possível quebra de ciclo.")
    
    pattern_id = detect_pattern(history)
    
    if pattern_id:
        pattern = PATTERNS.get(pattern_id)
        if pattern:
            st.session_state.current_pattern = pattern_id
            
            layer = st.session_state.current_layer
            
            if layer <= 3:
                manipulation_key = "1-3"
            elif layer <= 6:
                manipulation_key = "4-6"
            else:
                manipulation_key = "7-9"
                
            manipulation_advice = pattern["manipulation_bet"].get(manipulation_key, "")
            
            confidence = calculate_pattern_confidence(pattern_id, len(history))
            
            st.session_state.analysis = {
                'pattern': pattern["name"],
                'confidence': confidence,
                'description': pattern["description"],
                'formation': pattern["formation"]
            }
            
            bet = get_bet_suggestion(pattern_id, history)
            
            st.session_state.suggestion = {
                'bet': bet,
                'reason': f"{pattern['name']}. {manipulation_advice}",
                'confidence': 'alta' if layer <= 3 else 'média' if layer <= 6 else 'baixa'
            }
        else:
            st.session_state.analysis = {'pattern': 'Padrão não encontrado', 'confidence': 0, 'description': 'Padrão detectado, mas não definido no dicionário', 'formation': 'N/A'}
            st.session_state.suggestion = {'bet': 'Aguarde', 'reason': 'Erro na definição do padrão', 'confidence': 'baixa'}
    else:
        # Lógica de análise estatística quando nenhum padrão é detectado
        recent_history = st.session_state.history[:20]
        stats = {'casa': 0, 'visitante': 0, 'empate': 0}
        for result in recent_history:
            stats[result] += 1
        
        total = len(recent_history)
        if total > 0:
            probabilities = {
                'casa': (stats['casa'] / total),
                'visitante': (stats['visitante'] / total),
                'empate': (stats['empate'] / total),
            }
            dominant_color = max(probabilities, key=probabilities.get)
            confidence = int(probabilities[dominant_color] * 100)
            
            st.session_state.analysis = {
                'pattern': 'Análise Estatística',
                'confidence': confidence,
                'description': f'Nenhum padrão, mas {dominant_color.upper()} está dominante nos últimos resultados.',
                'formation': 'Tendência'
            }
            
            st.session_state.suggestion = {
                'bet': dominant_color,
                'reason': 'Estatísticas recentes sugerem esta tendência.',
                'confidence': 'baixa'
            }
        else:
            st.session_state.analysis = {
                'pattern': 'Padrão Aleatório',
                'confidence': 40,
                'description': 'Nenhum padrão claro detectado',
                'formation': 'N/A'
            }
            st.session_state.suggestion = {
                'bet': 'Aguarde',
                'reason': 'Aguarde mais resultados para análise',
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
        st.warning(alert)

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
    
    history_html = ""
    for result in st.session_state.history:
        if result == 'casa':
            history_html += '<span class="result-badge casa-badge">C</span>'
        elif result == 'visitante':
            history_html += '<span class="result-badge visitante-badge">V</span>'
        else:
            history_html += '<span class="result-badge empate-badge">E</span>'
    
    st.markdown(history_html, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

# Seção de Padrões (apenas para referência)
with st.expander("📚 Referência de Padrões (1-40)"):
    for i in range(1, 41): 
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
