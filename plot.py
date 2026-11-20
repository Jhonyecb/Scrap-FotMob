#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import textwrap

# ---------- Configuração ----------
ATLETA_POSICAO = "Volante"
ATLETA_TIME = "Athletic-MG"
NOME_ARQUIVO = "csv/João-Miguel.csv"
PNG = "png/João-Miguel.png"

METRICAS = [
    #"Goals",
    #"Expected goals (xG)",
    "xG on target (xGOT)",
    #"Penalty goals",
    "Non-penalty xG",
    "Shots",
    "Shots on target",
    #"Headed shots",
    "Assists",
    "Expected assists (xA)",
    "Successful passes",
    "Successful passes %",
    "Accurate long balls",
    "Accurate long balls %",
    "Line-breaking passes",
    "Chances created",
    "Big chances created",
    "Successful crosses",
    "Successful crosses %",
    "Successful dribbles",
    "Successful dribbles %",
    "Duels won",
    "Duels won %",
    "Aerial duels won",
    #"Aerial duels won %",
    "Touches",
    "Touches in opposition box",
    "Dispossessed",
    "Fouls won",
    "Defensive contributions",
    #"Tackles",
    #"Interceptions",
    #"Blocked shots",
    #"Fouls committed",
    #"Recoveries",
    "Possession won final 3rd",
    #"Dribbled past",
    #"Clearances",
    #"Clean sheets",
    #"Goals conceded while on pitch",
    #"xG against while on pitch",
    #"Yellow cards",
    #"Red cards",
]

TRADUCAO = {
    "Goals": "Gols",
    "Expected goals (xG)": "xG",
    "xG on target (xGOT)": "xGOT",
    "Penalty goals": "Gols de pênalti",
    "Non-penalty xG": "npxG",
    "Shots": "Finalizações",
    "Shots on target": "Finalizações no alvo",
    "Headed shots": "Finalizações de cabeça",
    "Assists": "Assistências",
    "Expected assists (xA)": "xA",
    "Successful passes": "Passes certos",
    "Successful passes %": "Passes certos (%)",
    "Accurate long balls": "Bolas longas certas",
    "Accurate long balls %": "Bolas longas certos (%)",
    "Line-breaking passes": "Passes que quebram linhas",
    "Chances created": "Chances criadas",
    "Big chances created": "Grandes chances criadas",
    "Successful crosses": "Cruzamentos certos",
    "Successful crosses %": "Cruzamentos certos (%)",
    "Successful dribbles": "Dribles certos",
    "Successful dribbles %": "Dribles certos (%)",
    "Duels won": "Duelos ganhos",
    "Duels won %": "Duelos ganhos (%)",
    "Aerial duels won": "Duelos aéreos ganhos",
    "Aerial duels won %": "Duelos aéreos ganhos (%)",
    "Touches": "Toques na bola",
    "Touches in opposition box": "Toques na área adversária",
    "Dispossessed": "Perdas de posse",
    "Fouls won": "Faltas sofridas",
    "Defensive contributions": "Contribuições defensivas",
    "Tackles": "Desarmes",
    "Interceptions": "Interceptações",
    "Blocked shots": "Chutes bloqueados",
    "Fouls committed": "Faltas cometidas",
    "Recoveries": "Recuperações",
    "Possession won final 3rd": "Recuperações no terço final",
    "Dribbled past": "Driblado por adversários",
    "Clearances": "Cortes",
    "Clean sheets": "Jogos sem sofrer gols",
    "Goals conceded while on pitch": "Gols sofridos em campo",
    "xG against while on pitch": "xG contra em campo",
    "Yellow cards": "Cartões amarelos",
    "Red cards": "Cartões vermelhos",
}

GRUPO_MAP = {
    "Shooting Rank": "Finalização",
    "Passing": "Passe",
    "Possession": "Posse",
    "Defending": "Defesa",
}

CORES = {
    "Finalização": "#F0C36B",
    "Passe": "#E0A030",
    "Posse": "#8A5A14",
    "Defesa": "#3B2A08",
}

FUNDO = "#FFFFFF"
TEXTO = "#111111"
TEXTO_SECUNDARIO = "#444444"

RAIO_INTERNO = 8     # furo central
RAIO_MAX = 116        # borda do gráfico; menor = gráfico maior
RAIO_ROTULO = 109     # distância dos rótulos; deve ficar acima de 100


# ---------- Dados ----------
def carregar_csv(caminho=NOME_ARQUIVO):
    """Lê o CSV e descarta linhas sem percentil."""
    return pd.read_csv(caminho).dropna(subset=["percentil"])

def buscar_metricas(df, metricas):
    """Filtra pelas métricas escolhidas, mantendo a ordem da lista."""
    ordem = {m: i for i, m in enumerate(metricas)}
    filtrado = df[df["stat"].isin(metricas)].copy()
    faltando = set(metricas) - set(filtrado["stat"])
    if faltando:
        print("Métricas não encontradas no CSV:", faltando)
    filtrado["ordem"] = filtrado["stat"].map(ordem)
    return filtrado.sort_values("ordem").reset_index(drop=True)

def traduzir(df, traducao):
    """Troca o nome da métrica pelo nome traduzido."""
    df = df.copy()
    df["stat"] = df["stat"].map(lambda s: traducao.get(s, s))
    return df

# ---------- Desenho ----------
def tom_claro(cor, mistura=0.8):
    rgb = np.array([int(cor[i:i + 2], 16) for i in (1, 3, 5)]) / 255
    return tuple(rgb + (1 - rgb) * mistura)

def desenhar(df, atleta, competicao, minutos):
    N = len(df)
    theta = np.linspace(0, 2 * np.pi, N, endpoint=False)
    largura = (2 * np.pi / N) * 0.82

    fig = plt.figure(figsize=(12, 12), facecolor=FUNDO)
    ax = fig.add_axes([0.12, 0.14, 0.76, 0.72], projection="polar")
    ax.set_facecolor(FUNDO)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_rorigin(-RAIO_INTERNO)
    ax.set_rlim(0, RAIO_MAX)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    ax.spines["polar"].set_visible(False)

    ax.bar(theta, np.full(N, 100), width=largura,
           color=[tom_claro(c) for c in df["cor"]],
           edgecolor=FUNDO, linewidth=1.5, zorder=1)

    ax.bar(theta, df["percentil"], width=largura,
           color=df["cor"], edgecolor=FUNDO, linewidth=1.5, zorder=2)

    for t, p in zip(theta, df["percentil"]):
        y = p - 7 if p >= 14 else p + 6
        ax.text(t, y, f"{p:.0f}", ha="center", va="center", fontsize=10,
                fontweight="bold", color=TEXTO, zorder=4,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=TEXTO, lw=0.6))

    for t, stat, valor in zip(theta, df["stat"], df["valor"]):
        nome_quebrado = textwrap.fill(str(stat), width=14)
        tela = (90 - np.degrees(t)) % 360
        rot = tela - 90
        if rot > 90:
            rot -= 180
        if rot < -90:
            rot += 180
        ax.text(t, RAIO_ROTULO, f"{nome_quebrado}\n{valor}",
                rotation=rot, rotation_mode="anchor",
                ha="center", va="center",
                fontsize=9, color=TEXTO, clip_on=False,
                linespacing=1.1)

    # Títulos
    fig.text(0.5, 0.955, atleta, ha="center", va="center",
             fontsize=26, fontweight="bold", color=TEXTO)
    fig.text(0.5, 0.925,
             f"{ATLETA_POSICAO} · {ATLETA_TIME} · {competicao} · {minutos} min",
             ha="center", va="center", fontsize=12, color=TEXTO_SECUNDARIO)

    # Legenda: só grupos presentes
    grupos = [g for g in GRUPO_MAP.values() if g in set(df["grupo_pt"])]
    legenda = [Patch(facecolor=CORES[g], label=g) for g in grupos]
    fig.legend(handles=legenda, loc="upper center", bbox_to_anchor=(0.5, 0.895),
               ncol=len(legenda), frameon=False, fontsize=11)

    # Rodapé
    fig.text(0.5, 0.09,
             "Fatia = percentil (100 = melhor). Rótulos = valor por 90 min, exceto %.\n"
             "Dados: FotMob | Gráfico: @FalandodeBahia",
             ha="center", va="center", fontsize=9, color=TEXTO_SECUNDARIO)

    plt.savefig(PNG, dpi=200, facecolor=FUNDO, bbox_inches="tight")
    plt.show()

# ---------- Execução ----------
if __name__ == "__main__":
    raw = carregar_csv()
    atleta = raw["atleta"].iloc[0]
    competicao = raw["competicao"].iloc[0]
    minutos = raw["minutos"].iloc[0]

    df = buscar_metricas(raw, METRICAS)
    df = traduzir(df, TRADUCAO)
    df["grupo_pt"] = df["grupo"].map(GRUPO_MAP)
    df = df.dropna(subset=["grupo_pt"])
    df["cor"] = df["grupo_pt"].map(CORES)

    desenhar(df, atleta, competicao, minutos)
# %%
