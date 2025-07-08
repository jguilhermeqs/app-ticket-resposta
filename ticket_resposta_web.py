   import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("Análise de Respostas por Executante")

st.markdown("""
Este aplicativo analisa tickets com base nas seguintes regras:
- Se o **Executante = Responsável** e o **Status = Respondidos** → ✅
- Se o **Executante = Responsável** e o **Status = Não respondido** → ❌
- Se o **Executante ≠ Responsável** → vazio
""")

# Upload da planilha
arquivo = st.file_uploader("Envie a planilha de tickets (.xlsx)", type="xlsx")

if arquivo:
    df = pd.read_excel(arquivo)

    # Selecionar parâmetros
    col1, col2 = st.columns(2)
    executante = col1.selectbox("Executante", sorted(df["Executante"].dropna().unique()))
    loja = col2.selectbox("Empresa", sorted(df["Empresa"].dropna().unique()))
    gerente = st.selectbox("Gerente", sorted(df["Gerente"].dropna().unique()))
    dias_analise = st.slider("Quantos dias para analisar?", 1, 30, 7)

    # Gerar datas
    hoje = datetime.today().date()
    datas = [hoje - timedelta(days=i) for i in range(dias_analise)]

    # Função de análise por linha
    def avaliar_ticket(row, data_alvo):
        if row["Executante"] != executante:
            return ""
        if pd.to_datetime(row["Data da Última Execução"]).date() != data_alvo:
            return ""
        if row["Empresa"] != loja or row["Gerente"] != gerente:
            return ""
        if row["Responsável"] == executante:
            if row["Preenchido?"] == "Respondidos":
                return "✅"
            elif row["Preenchido?"] == "Não respondido":
                return "❌"
        return ""

    # Construir resultado
    resultados = []
    for dia in datas:
        resultado_dia = df.apply(lambda row: avaliar_ticket(row, dia), axis=1)
        if "✅" in resultado_dia.values:
            resultados.append("✅")
        elif "❌" in resultado_dia.values:
            resultados.append("❌")
        else:
            resultados.append("")

    df_resultado = pd.DataFrame({"Data": datas, "Resultado": resultados})
    st.dataframe(df_resultado)

    # Download da planilha final
    csv = df_resultado.to_csv(index=False).encode('utf-8')
    st.download_button("🔹 Baixar resultado (.csv)", data=csv, file_name="resultado_tickets.csv", mime="text/csv")
