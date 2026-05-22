import streamlit as st
import base64


def render_report_image():

    # carregar logo
    with open("logob.png", "rb") as img:
        logo = base64.b64encode(img.read()).decode()

    # CSS
    st.markdown(
        f"""
        <style>

        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        .painel_imagem {{
            border-radius: 28px;

            padding: 22px;

            background: linear-gradient(180deg, #0066FF, #0047B3);

            display: flex;
            flex-direction: column;

            gap: 14px;

            width: 320px;
            min-height: 500px;

            margin: auto;

            box-shadow:
                0 12px 35px rgba(0,0,0,0.18);

            overflow: hidden;
        }}

        .cliques,
        .impressoes,
        .ctr,
        .valor,
        .nome {{

            font-family: 'Inter', sans-serif;

            font-size: 16px;
            font-weight: 700;

            color: #111827;

            background: rgba(255,255,255,0.96);

            display: flex;
            align-items: center;

            min-height: 60px;

            padding: 0 18px;

            width: 100%;

            border-radius: 18px;

            box-sizing: border-box;

            box-shadow:
                0 4px 12px rgba(0,0,0,0.08);
        }}

        .logo {{
            background-image: url("data:image/png;base64,{logo}");

            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;

            width: 140px;
            height: 70px;

            margin: auto;
            margin-top: 18px;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

    # HTML
    st.markdown(
        """
        <div class="painel_imagem">

            <div class="nome">
                Campanha: MOTO PEÇAS AUTO
            </div>

            <div class="valor">
                Total investido: R$ 20.000
            </div>

            <div class="cliques">
                Cliques: 100
            </div>

            <div class="impressoes">
                Impressões: 1000
            </div>

            <div class="ctr">
                CTR: 10%
            </div>

            <div class="logo"></div>

        </div>
        """,
        unsafe_allow_html=True
    )


# renderizar painel
render_report_image()