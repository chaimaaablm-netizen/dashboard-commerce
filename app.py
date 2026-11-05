
"""Dashboard decisionnel Atlas Commerce."""

from dash import Dash, dcc, html, Input, Output, ctx
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from donnees import df, filtrer, calculer_kpis, mad


# =====================================================
# 1. CREATION DE L'APPLICATION
# =====================================================

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY]
)

app.title = "Atlas Commerce | Dashboard decisionnel"

# Pour le deploiement
server = app.server

DATE_MIN = df["Date"].min().date().isoformat()
DATE_MAX = df["Date"].max().date().isoformat()


# =====================================================
# 2. FONCTIONS REUTILISABLES
# =====================================================

def carte_kpi(titre, identifiant):
    return dbc.Card(
        dbc.CardBody([
            html.Div(titre, className="kpi-label"),
            html.Div("--", id=identifiant, className="kpi-valeur")
        ]),
        className="kpi-card h-100"
    )


def carte_graphique(identifiant):
    return dbc.Card(
        dbc.CardBody(
            dcc.Loading(
                dcc.Graph(
                    id=identifiant,
                    config={"displayModeBar": True},
                    style={"width": "100%"}
                )
            )
        ),
        className="graph-card h-100"
    )


def figure_vide(titre):
    fig = go.Figure()

    fig.add_annotation(
        text="Aucune vente pour ces filtres",
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=16)
    )

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    fig.update_layout(
        title=titre,
        template="plotly_white",
        height=360
    )

    return fig


def harmoniser(fig):
    fig.update_layout(
        template="plotly_white",
        height=360,
        margin=dict(l=35, r=25, t=65, b=45),
        title_font=dict(size=18),
        hoverlabel=dict(bgcolor="white")
    )

    return fig


# =====================================================
# 3. LAYOUT : STRUCTURE DU DASHBOARD
# =====================================================

app.layout = dbc.Container([

    # EN-TETE
    html.Div([
        html.H1("ATLAS COMMERCE"),
        html.P("Pilotage des ventes | jeu de donnees fictif")
    ], className="bandeau"),

    # FILTRES
    dbc.Card(
        dbc.CardBody(
            dbc.Row([

                dbc.Col([
                    html.Label("Periode", className="etiquette"),
                    dcc.DatePickerRange(
                        id="dates",
                        start_date=DATE_MIN,
                        end_date=DATE_MAX,
                        min_date_allowed=DATE_MIN,
                        max_date_allowed=DATE_MAX,
                        display_format="DD/MM/YYYY",
                        start_date_placeholder_text="Date debut",
                        end_date_placeholder_text="Date fin"
                    )
                ], xs=12, lg=5),

                dbc.Col([
                    html.Label("Categorie", className="etiquette"),
                    dcc.Dropdown(
                        id="categorie",
                        value="Toutes",
                        options=[
                            {"label": "Toutes", "value": "Toutes"}
                        ] + [
                            {"label": c, "value": c}
                            for c in sorted(df["Categorie"].dropna().unique())
                        ],
                        clearable=False
                    )
                ], xs=12, lg=4),

                dbc.Col([
                    html.Label(
                        "Regroupement temporel",
                        className="etiquette"
                    ),
                    dcc.RadioItems(
                        id="freq",
                        value="M",
                        inline=True,
                        options=[
                            {"label": "Jour", "value": "J"},
                            {"label": "Mois", "value": "M"}
                        ],
                        labelStyle={"marginRight": "15px"}
                    )
                ], xs=12, lg=3),

            ], className="g-3")
        ),
        className="filter-card mb-3"
    ),

    # KPI
    dbc.Row([
        dbc.Col(
            carte_kpi("Chiffre d'affaires", "ca"),
            xs=12, sm=6, lg=3
        ),
        dbc.Col(
            carte_kpi("Commandes distinctes", "commandes"),
            xs=12, sm=6, lg=3
        ),
        dbc.Col(
            carte_kpi("Panier moyen", "panier"),
            xs=12, sm=6, lg=3
        ),
        dbc.Col(
            carte_kpi("Marge commerciale", "marge"),
            xs=12, sm=6, lg=3
        ),
    ], className="g-3 mb-2"),

    html.P(id="etat", className="text-muted mt-2"),

    # GRAPHIQUE 1 : EVOLUTION DU CA
    dbc.Row([
        dbc.Col(carte_graphique("evolution"), xs=12)
    ], className="g-3 mb-4"),

    # GRAPHIQUE 2 : CA PAR CATEGORIE
    dbc.Row([
        dbc.Col(carte_graphique("categories"), xs=12)
    ], className="g-3 mb-4"),

    # GRAPHIQUE 3 : REPARTITION PAR REGION
    dbc.Row([
        dbc.Col(carte_graphique("regions"), xs=12)
    ], className="g-3 mb-4"),

    # GRAPHIQUE 4 : MARGE PAR CATEGORIE
    dbc.Row([
        dbc.Col(carte_graphique("marges"), xs=12)
    ], className="g-3 mb-4"),

    # BOUTON RESET REGION
    dbc.Row([
        dbc.Col(
            dbc.Button(
                "Effacer le filtre region",
                id="reset-region",
                color="secondary",
                outline=True,
                className="mb-3"
            ),
            xs=12
        )
    ]),

    # GRAPHIQUE 5 : TOP 10 PRODUITS
    dbc.Row([
        dbc.Col([
            html.H5(id="titre-top"),
            carte_graphique("top-produits")
        ], xs=12)
    ], className="g-3 mb-4"),

    # MEMORISATION DE LA REGION
    dcc.Store(id="region-active", data=None),

    # MESSAGE METIER
    dbc.Alert(
        id="lecture-metier",
        color="info",
        className="mt-3"
    )

], fluid=True, className="px-3 px-xl-5 py-4")


# =====================================================
# 4. CALLBACK KPI
# =====================================================

@app.callback(
    Output("ca", "children"),
    Output("commandes", "children"),
    Output("panier", "children"),
    Output("marge", "children"),
    Output("etat", "children"),
    Input("dates", "start_date"),
    Input("dates", "end_date"),
    Input("categorie", "value")
)
def actualiser_kpis(debut, fin, categorie):

    ventes = filtrer(debut, fin, categorie)
    k = calculer_kpis(ventes)

    message = (
        f"{len(ventes)} lignes | "
        f"{k['commandes']} commandes"
    )

    return (
        mad(k["ca"]),
        str(k["commandes"]),
        mad(k["panier"]),
        mad(k["marge"]),
        message
    )


# =====================================================
# 5. CALLBACK EVOLUTION DU CA
# =====================================================

@app.callback(
    Output("evolution", "figure"),
    Input("dates", "start_date"),
    Input("dates", "end_date"),
    Input("categorie", "value"),
    Input("freq", "value")
)
def tracer_evolution(debut, fin, categorie, freq):

    ventes = filtrer(debut, fin, categorie).copy()

    if ventes.empty:
        return figure_vide("Evolution du chiffre d'affaires")

    ventes["Date"] = pd.to_datetime(
        ventes["Date"], errors="coerce"
    )

    ventes["Chiffre_Affaires"] = pd.to_numeric(
        ventes["Chiffre_Affaires"], errors="coerce"
    )

    ventes = ventes.dropna(
        subset=["Date", "Chiffre_Affaires"]
    )

    if ventes.empty:
        return figure_vide("Evolution du chiffre d'affaires")

    if freq == "M":
        ventes["Periode"] = (
            ventes["Date"].dt.to_period("M").dt.to_timestamp()
        )
    else:
        ventes["Periode"] = ventes["Date"].dt.floor("D")

    evolution = (
        ventes.groupby("Periode", as_index=False)
        .agg(Chiffre_Affaires=("Chiffre_Affaires", "sum"))
        .sort_values("Periode")
    )

    fig = px.line(
        evolution,
        x="Periode",
        y="Chiffre_Affaires",
        markers=True,
        title="Evolution du chiffre d'affaires",
        labels={
            "Periode": "Date",
            "Chiffre_Affaires": "CA (MAD)"
        }
    )

    fig.update_traces(
        line=dict(color="#2866aa", width=3),
        marker=dict(size=7)
    )

    return harmoniser(fig)


# =====================================================
# 6. CALLBACK CA PAR CATEGORIE
# =====================================================

@app.callback(
    Output("categories", "figure"),
    Input("dates", "start_date"),
    Input("dates", "end_date"),
    Input("categorie", "value")
)
def tracer_categories(debut, fin, categorie):

    ventes = filtrer(debut, fin, categorie).copy()

    if ventes.empty:
        return figure_vide("CA par categorie")

    ventes["Chiffre_Affaires"] = pd.to_numeric(
        ventes["Chiffre_Affaires"], errors="coerce"
    )

    ventes = ventes.dropna(
        subset=["Categorie", "Chiffre_Affaires"]
    )

    resume = (
        ventes.groupby("Categorie", as_index=False)
        .agg(Chiffre_Affaires=("Chiffre_Affaires", "sum"))
        .sort_values("Chiffre_Affaires", ascending=False)
    )

    if resume.empty:
        return figure_vide("CA par categorie")

    fig = px.bar(
        resume,
        x="Categorie",
        y="Chiffre_Affaires",
        color="Categorie",
        title="CA par categorie",
        labels={
            "Categorie": "Categorie",
            "Chiffre_Affaires": "CA (MAD)"
        },
        text_auto=".2s"
    )

    fig.update_layout(showlegend=False)

    return harmoniser(fig)


# =====================================================
# 7. CALLBACK REPARTITION PAR REGION
# =====================================================

@app.callback(
    Output("regions", "figure"),
    Input("dates", "start_date"),
    Input("dates", "end_date"),
    Input("categorie", "value")
)
def tracer_regions(debut, fin, categorie):

    ventes = filtrer(debut, fin, categorie).copy()

    if ventes.empty:
        return figure_vide("Part de chaque region")

    ventes = ventes.dropna(
        subset=["Region", "Chiffre_Affaires"]
    )

    resume = (
        ventes.groupby("Region", as_index=False)
        .agg(Chiffre_Affaires=("Chiffre_Affaires", "sum"))
    )

    if resume.empty:
        return figure_vide("Part de chaque region")

    fig = px.pie(
        resume,
        names="Region",
        values="Chiffre_Affaires",
        title="Part de chaque region dans le CA",
        hole=0.40
    )

    fig.update_traces(
        textinfo="percent+label",
        hovertemplate="%{label}<br>CA : %{value:,.0f} MAD<br>Part : %{percent}<extra></extra>"
    )

    return harmoniser(fig)


# =====================================================
# 8. CALLBACK MARGE PAR CATEGORIE
# =====================================================

@app.callback(
    Output("marges", "figure"),
    Input("dates", "start_date"),
    Input("dates", "end_date"),
    Input("categorie", "value")
)
def tracer_marges(debut, fin, categorie):

    ventes = filtrer(debut, fin, categorie).copy()

    if ventes.empty:
        return figure_vide("Marge par categorie")

    ventes["Marge"] = pd.to_numeric(
        ventes["Marge"], errors="coerce"
    )

    ventes = ventes.dropna(
        subset=["Categorie", "Marge"]
    )

    resume = (
        ventes.groupby("Categorie", as_index=False)
        .agg(Marge=("Marge", "sum"))
        .sort_values("Marge", ascending=False)
    )

    if resume.empty:
        return figure_vide("Marge par categorie")

    fig = px.bar(
        resume,
        x="Categorie",
        y="Marge",
        color="Categorie",
        title="Marge commerciale par categorie",
        labels={
            "Categorie": "Categorie",
            "Marge": "Marge (MAD)"
        },
        text_auto=".2s"
    )

    fig.update_layout(showlegend=False)

    return harmoniser(fig)


# =====================================================
# 9. CALLBACK TOP 10 PRODUITS
# =====================================================

@app.callback(
    Output("top-produits", "figure"),
    Output("titre-top", "children"),
    Input("dates", "start_date"),
    Input("dates", "end_date"),
    Input("categorie", "value"),
    Input("region-active", "data")
)
def tracer_top(debut, fin, categorie, region):

    ventes = filtrer(debut, fin, categorie).copy()

    if region:
        ventes = ventes[ventes["Region"] == region]

    titre = (
        "Top 10 produits"
        + (f" | {region}" if region else " | Toutes regions")
    )

    if ventes.empty:
        return figure_vide(titre), titre

    resume = (
        ventes.groupby("Produit", as_index=False)
        .agg(Chiffre_Affaires=("Chiffre_Affaires", "sum"))
        .nlargest(10, "Chiffre_Affaires")
        .sort_values("Chiffre_Affaires", ascending=True)
    )

    if resume.empty:
        return figure_vide(titre), titre

    fig = px.bar(
        resume,
        x="Chiffre_Affaires",
        y="Produit",
        orientation="h",
        color="Chiffre_Affaires",
        color_continuous_scale="Blues",
        title=titre,
        labels={
            "Chiffre_Affaires": "CA (MAD)",
            "Produit": "Produit"
        },
        text_auto=".2s"
    )

    fig.update_layout(coloraxis_showscale=False)

    return harmoniser(fig), titre


# =====================================================
# 10. CALLBACK FILTRE CROISE ET RESET REGION
# =====================================================

@app.callback(
    Output("region-active", "data"),
    Input("regions", "clickData"),
    Input("reset-region", "n_clicks"),
    Input("dates", "start_date"),
    Input("dates", "end_date"),
    Input("categorie", "value"),
    prevent_initial_call=True
)
def selectionner_region(clic, _reset, _debut, _fin, _categorie):

    if ctx.triggered_id == "regions" and clic and clic.get("points"):
        return clic["points"][0].get("label")

    return None


# =====================================================
# 11. CALLBACK MESSAGE METIER
# =====================================================

@app.callback(
    Output("lecture-metier", "children"),
    Input("dates", "start_date"),
    Input("dates", "end_date"),
    Input("categorie", "value")
)
def recommandation_metier(debut, fin, categorie):

    ventes = filtrer(debut, fin, categorie)

    if ventes.empty:
        return (
            "Aucune vente : elargissez la plage "
            "ou changez la categorie."
        )

    par_region = (
        ventes.groupby("Region")["Chiffre_Affaires"].sum()
    )

    par_categorie = ventes.groupby("Categorie")["Marge"].sum()

    region = par_region.idxmax()
    cat = par_categorie.idxmax()

    return (
        f"Region au CA le plus eleve : {region}. "
        f"Categorie a la marge totale la plus forte : {cat}. "
        "Analyse sur les filtres courants."
    )


# =====================================================
# 12. LANCEMENT
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)
