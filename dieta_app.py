# -*- coding: utf-8 -*-
"""
Created on Tue Jun  3 17:37:04 2025

@author: Isadora
"""

import streamlit as st
import pulp

# ---------- Dados base ----------
alimentos = [
    "Frango", "Mandioca", "Macarrão", "Batata doce", "Ovo", "Milho canjica",
    "Leite em pó", "Cenoura", "Batata inglesa", "Farinha de cuscuz",
    "Laranja pêra", "Mamão papaia"
]

dados = {
    "Frango":          {"proteina": 25, "carbo": 0, "lipidio": 7.1, "energia": 170.4, "preco": 2.33},
    "Mandioca":        {"proteina": 0.6, "carbo": 30.1, "lipidio": 0.3, "energia": 125.4, "preco": 1.07},
    "Macarrão":        {"proteina": 9.36, "carbo": 72, "lipidio": 1.32, "energia": 338.4, "preco": 0.80},
    "Batata doce":     {"proteina": 0.6, "carbo": 18.4, "lipidio": 0.1, "energia": 76.8, "preco": 0.30},
    "Ovo":             {"proteina": 15.6, "carbo": 1.2, "lipidio": 18.6, "energia": 240.2, "preco": 1.59},
    "Milho canjica":   {"proteina": 7.2, "carbo": 78.1, "lipidio": 1.0, "energia": 357.6, "preco": 1.66},
    "Leite em pó":     {"proteina": 6.8, "carbo": 9.9, "lipidio": 0.0, "energia": 130, "preco": 5.52},
    "Cenoura":         {"proteina": 0.9, "carbo": 6.7, "lipidio": 0.2, "energia": 29.9, "preco": 0.76},
    "Batata inglesa":  {"proteina": 1.2, "carbo": 11.9, "lipidio": 0.0, "energia": 51.6, "preco": 1.51},
    "Farinha de cuscuz": {"proteina": 2.2, "carbo": 25.3, "lipidio": 0.7, "energia": 113.5, "preco": 0.82},
    "Laranja pêra":    {"proteina": 1.0, "carbo": 9.0, "lipidio": 0.1, "energia": 36.8, "preco": 0.41},
    "Mamão papaia":    {"proteina": 0.5, "carbo": 10.4, "lipidio": 0.1, "energia": 40.2, "preco": 1.44},
}

requisitos = {
    "proteina": 15,
    "carbo": 60,
    "lipidio": 11,
    "energia": 400
}

# ---------- Interface ----------
st.title("Simulador do Problema da Dieta Escolar")
st.markdown("Defina as preferências e restrições, e o sistema calculará a dieta de menor custo.")

# Excluir alimentos
excluir = st.multiselect("Alimentos que devem ser excluídos da dieta:", alimentos)

# Limites máximos por alimento
limites = {}
st.markdown("### Limite máximo (porções de 100g):")
for a in alimentos:
    limite = st.slider(f"{a}", 0.0, 3.0, value=3.0 if a not in excluir else 0.0, step=0.1)
    limites[a] = limite

# Botão para calcular
if st.button("Calcular dieta ótima"):

    # ----------- Modelo LP -----------
    modelo = pulp.LpProblem("Dieta_Escolar", pulp.LpMinimize)
    q = pulp.LpVariable.dicts("Qtd", alimentos, lowBound=0)

    # Objetivo: minimizar custo
    modelo += pulp.lpSum(q[a] * dados[a]["preco"] for a in alimentos), "Custo_Total"

    # Restrições nutricionais
    modelo += pulp.lpSum(q[a] * dados[a]["proteina"] for a in alimentos) >= requisitos["proteina"]
    modelo += pulp.lpSum(q[a] * dados[a]["carbo"] for a in alimentos) >= requisitos["carbo"]
    modelo += pulp.lpSum(q[a] * dados[a]["lipidio"] for a in alimentos) >= requisitos["lipidio"]
    modelo += pulp.lpSum(q[a] * dados[a]["energia"] for a in alimentos) >= requisitos["energia"]

    # Limites por alimento
    for a in alimentos:
        modelo += q[a] <= limites[a]

    # Resolver
    modelo.solve()

    # Resultado
    if pulp.LpStatus[modelo.status] == "Optimal":
        st.success("✅ Solução encontrada!")
        custo_total = pulp.value(modelo.objective)
        st.write(f"**Custo total**: R$ {custo_total:.2f}")

        # Mostrar quantidades
        st.markdown("### Quantidades sugeridas:")
        result_data = []
        total_nutrientes = {"proteina": 0, "carbo": 0, "lipidio": 0, "energia": 0}

        for a in alimentos:
            q_val = q[a].varValue
            if q_val and q_val > 0:
                preco = q_val * dados[a]["preco"]
                prot = q_val * dados[a]["proteina"]
                carb = q_val * dados[a]["carbo"]
                lip = q_val * dados[a]["lipidio"]
                ener = q_val * dados[a]["energia"]
                total_nutrientes["proteina"] += prot
                total_nutrientes["carbo"] += carb
                total_nutrientes["lipidio"] += lip
                total_nutrientes["energia"] += ener
                result_data.append((a, f"{q_val:.2f} porções", f"R$ {preco:.2f}"))

        st.table(result_data)

        st.markdown("### Composição nutricional total:")
        st.markdown(f"- **Proteína**: {total_nutrientes['proteina']:.1f} g")
        st.markdown(f"- **Carboidratos**: {total_nutrientes['carbo']:.1f} g")
        st.markdown(f"- **Lipídios**: {total_nutrientes['lipidio']:.1f} g")
        st.markdown(f"- **Energia**: {total_nutrientes['energia']:.1f} kcal")

    else:
        st.error("⚠️ Não foi possível encontrar uma solução viável com as restrições definidas.")
