#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

JOGADOR1 = {"arquivo": "csv/everton-ribeiro.csv"}
JOGADOR2 = {"arquivo": "csv/cristian-casseres.csv"}
PNG = "png/EvertonxCasseres2.png"

METRICAS = [
    #"Goals",
    #"Expected goals (xG)",
    "xG on target (xGOT)",
    #"Penalty goals",
    "Non-penalty xG",
    "Shots",
    "Shots on target",
    "Headed shots",
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
    "Aerial duels won %",
    "Touches",
    "Touches in opposition box",
    "Dispossessed",
    "Fouls won",
    #"Defensive contributions",
    "Tackles",
    "Interceptions",
    "Blocked shots",
    "Fouls committed",
    "Recoveries",
    "Possession won final 3rd",
    "Dribbled past",
    "Clearances",
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


def carregar(arquivo):
    bruto = pd.read_csv(arquivo)
    info = {
        "nome": bruto["atleta"].dropna().iloc[0],
        "competicao": bruto["competicao"].dropna().iloc[0],
    }
    df = (
        bruto.dropna(subset=["percentil"])
        .drop_duplicates("stat")
        .set_index("stat")
    )
    return df, info

def metricas(df1, df2):
    comuns = [m for m in METRICAS if m in df1.index and m in df2.index]
    faltando = [m for m in METRICAS if m not in comuns]
    if faltando:
        print("Métricas ausentes em um dos jogadores:", faltando)
    return pd.DataFrame({
        "player1": df1.loc[comuns, "percentil"],
        "player2": df2.loc[comuns, "percentil"],
    })

p1, info1 = carregar(JOGADOR1["arquivo"])
p2, info2 = carregar(JOGADOR2["arquivo"])
df = metricas(p1, p2)
df.index = [TRADUCAO.get(m, m) for m in df.index]

sim = 100 - np.sqrt(((df["player1"] - df["player2"]) ** 2).mean())

BRANCO, PRETO, DOURADO, CINZA_LINHA, CINZA_GRADE = "#FFFFFF", "#000000", "#C9A227", "#9e9e9e", "#e6e6e6"

fig, ax = plt.subplots(figsize=(9, 13), facecolor=BRANCO)
ax.set_facecolor(BRANCO)

y = np.arange(len(df))[::-1]

for yi, (_, row) in zip(y, df.iterrows()):
    ax.plot([row["player2"], row["player1"]], [yi, yi], color=CINZA_LINHA, lw=2, zorder=1)

TAM_BOLA = 500
ax.scatter(df["player2"], y, color=PRETO, s=TAM_BOLA, zorder=2)
ax.scatter(df["player1"], y, color=DOURADO, s=TAM_BOLA, zorder=3)

for yi, (_, row) in zip(y, df.iterrows()):
    ax.text(row["player2"], yi, f"{row['player2']:.0f}", ha="center", va="center",
            color=BRANCO, fontsize=12.5, fontweight="bold", zorder=4)
    ax.text(row["player1"], yi, f"{row['player1']:.0f}", ha="center", va="center",
            color=PRETO, fontsize=12.5, fontweight="bold", zorder=5)

ax.set_yticks(y)
ax.set_yticklabels(df.index, color=PRETO, fontsize=12, fontweight="bold")
ax.tick_params(axis="y", length=0, pad=8)

ax.set_xlim(0, 100)
ax.set_xlabel("Percentil", color=PRETO, fontsize=11, fontweight="bold")
ax.tick_params(axis="x", colors=PRETO, labelsize=10)
ax.grid(axis="x", color=CINZA_GRADE)
ax.set_axisbelow(True)
for s in ax.spines.values():
    s.set_visible(False)

handles = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor=DOURADO, markeredgecolor=DOURADO,
           markersize=12, label=f"{info1['nome']} ({info1['competicao']})"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor=PRETO, markeredgecolor=PRETO,
           markersize=12, label=f"{info2['nome']} ({info2['competicao']})"),
]
fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.955), ncol=2,
           frameon=False, fontsize=11, labelcolor=PRETO, handletextpad=0.6, columnspacing=2.5)

ax.set_title(f"Similaridade: {sim:.1f}%", color=PRETO, loc="left", fontsize=15, fontweight="bold", pad=12)

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(PNG, dpi=200, facecolor=BRANCO)
plt.show()
# %%
