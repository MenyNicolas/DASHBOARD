import numpy as np
import pandas as pd
import streamlit as st
import utils
import matplotlib.pyplot as plt
import seaborn as sns

def compute_data():
    dict_couts = utils.load_couts()
    df_combined = utils.load_data()

    # 📌 Liste pour stocker les données avant l'export
    data_list = []

    # 📌 Parcourir chaque client
    for client in dict_couts.keys():

        if(client == "HELLOFRESH FRANCE SAS 13"):
            df_client_data = df_combined[(df_combined["CLI"] == "HELLOFRESH FRANCE SAS") & (df_combined["temperature"] == "FRESH 13")]
        elif(client == "HELLOFRESH FRANCE SAS 18"):
            df_client_data = df_combined[(df_combined["CLI"] == "HELLOFRESH FRANCE SAS") & (df_combined["temperature"] == "FRESH 18")]
        else :
            df_client_data = df_combined[df_combined["CLI"] == client]

        # Vérifier si le client a des données
        if df_client_data.empty:
            continue

        # 📌 Parcourir les températures uniques pour ce client
        for temperature in df_client_data["temperature"].unique():
            df_temp_data = df_client_data[df_client_data["temperature"] == temperature]

            # 📌 Parcourir les flux uniques pour cette température
            for flux in df_temp_data["flux"].unique():
                df_flux_data = df_temp_data[df_temp_data["flux"] == flux]

                # Sommes des quantités
                total_poids = df_flux_data["Poids"].sum()
                total_colis = df_flux_data["Colis"].sum()
                total_xp = df_flux_data["XP"].sum()
                total_ca = df_flux_data["Montant"].sum()

                # Récupérer les coûts unitaires
                df_couts_client = dict_couts[client]

                # Vérifier si la température existe dans le fichier de coûts
                if temperature not in df_couts_client.columns:
                    temperature = "FRESH" # CAS SPECIAL POUR HELLOFRESH

                # 📌 Calcul des coûts effectifs
                couts_collecte = float(df_couts_client.loc[0, temperature]) * total_colis
                couts_tri = float(df_couts_client.loc[1, temperature]) * total_colis
                couts_manut = float(df_couts_client.loc[2, temperature]) * total_colis
                couts_acheminement = float(df_couts_client.loc[3, temperature]) * total_poids
                couts_distribution = float(df_couts_client.loc[4, temperature]) * total_xp
                couts_pickup_colis = float(df_couts_client.loc[5, temperature]) * total_colis
                couts_pickup_kg = float(df_couts_client.loc[6, temperature]) * total_poids
                couts_support = float(df_couts_client.loc[7, temperature]) * total_colis
                couts_branding = float(df_couts_client.loc[8, temperature]) * total_colis
                couts_carboglace = float(df_couts_client.loc[9, temperature]) * total_colis

                # 📌 Ajustement des coûts en fonction du flux
                if flux == "NR":
                    couts_acheminement *= 0.75
                elif flux == "ND":
                    couts_acheminement = 0

                # 📌 Calcul du coût total
                cout_total = (
                    couts_collecte + couts_tri + couts_manut + couts_acheminement + 
                    couts_distribution + couts_pickup_colis + couts_pickup_kg + 
                    couts_support + couts_branding + couts_carboglace
                )

                # 📌 Ajouter les données à la liste
                data_list.append([
                    client, temperature, flux, total_poids, total_colis, total_xp, total_ca,
                    couts_collecte, couts_tri, couts_manut, couts_acheminement, couts_distribution,
                    couts_pickup_colis, couts_pickup_kg, couts_support, couts_branding, couts_carboglace,
                    cout_total
                ])

    # 📌 Création du DataFrame final
    df_result = pd.DataFrame(data_list, columns=[
        "Client", "Température", "Flux", "Total Poids", "Total Colis", "Total XP", "CA Total",
        "Coût Collecte", "Coût Tri", "Coût Manutention", "Coût Acheminement", "Coût Distribution",
        "Coût Pickup Colis", "Coût Pickup KG", "Coût Support", "Coût Branding", "Coût Carboglace",
        "Coût Total"
    ])

    return df_result

def main():
    df = compute_data()

    # 📌 Interface utilisateur - Sélection du niveau de détail
    st.title("🔍 Analyse des Coûts et Rentabilité")

    niveau_detail = st.radio(
        "📊 Sélectionnez la vue souhaitée :", 
        ["Globale", "Par Client", "Par température et flux"]
    )

    # 📌 Fonction pour générer le graphique Marge + MCV
    def plot_marge_mcv(df_data, x_col, title):
        fig, ax1 = plt.subplots(figsize=(10, 5))

        # 📌 Graphique à barres pour la Marge (€)
        ax1 = sns.barplot(x=x_col, y="Marge", data=df_data, color="royalblue", ax=ax1, label="Marge (€)")

        # 📌 Ajouter une deuxième échelle Y pour MCV (%)
        ax2 = ax1.twinx()
        ax2 = sns.lineplot(x=x_col, y="MCV (%)", data=df_data, color="red", marker="o", linewidth=2, ax=ax2, label="MCV (%)")

        # 📌 Titres et labels
        ax1.set_ylabel("Marge (€)", color="royalblue")
        ax2.set_ylabel("MCV (%)", color="red")
        ax1.set_xlabel(x_col)
        plt.title(title)

        # 📌 Rotation des labels X pour meilleure lisibilité
        ax1.set_xticklabels(df_data[x_col], rotation=45, ha="right")

        # 📌 Ajouter les légendes
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")

        return fig

    # 📌 Vue Globale (par Client)
    if niveau_detail == "Globale":
        df_global = df.groupby("Client").sum().reset_index()
        df_global["Marge"] = df_global["CA Total"] - df_global["Coût Total"]
        df_global["MCV (%)"] = (df_global["Marge"] / df_global["CA Total"]) * 100

        st.write("### 📈 Vue Globale des Coûts et Marges par Client")
        st.dataframe(df_global[["Client", "CA Total", "Coût Total", "Marge", "MCV (%)"]])

        # 📌 Affichage du graphique Marge & MCV
        st.pyplot(plot_marge_mcv(df_global, "Client", "Marge et MCV par Client"))

    # 📌 Vue par Température
    elif niveau_detail == "Par Client":
        client_selectionne = st.selectbox("Sélectionnez un client :", df["Client"].unique())
        df_client = df[df["Client"] == client_selectionne]

        df_temp = df_client.groupby("Température").sum().reset_index()
        df_temp["Marge"] = df_temp["CA Total"] - df_temp["Coût Total"]
        df_temp["MCV (%)"] = (df_temp["Marge"] / df_temp["CA Total"]) * 100

        st.write(f"### 📊 Vue par Température - {client_selectionne}")
        st.dataframe(df_temp[["Température", "CA Total", "Coût Total", "Marge", "MCV (%)"]])

        # 📌 Affichage du graphique Marge & MCV
        st.pyplot(plot_marge_mcv(df_temp, "Température", f"Marge et MCV par Température ({client_selectionne})"))

    # 📌 Vue par Flux
    elif niveau_detail == "Par température et flux":
        client_selectionne = st.selectbox("Sélectionnez un client :", df["Client"].unique())
        df_client = df[df["Client"] == client_selectionne]

        temperature_selectionnee = st.selectbox("Sélectionnez une température :", df_client["Température"].unique())
        df_temp = df_client[df_client["Température"] == temperature_selectionnee]

        flux_selectionne = st.selectbox("Sélectionnez un flux :", df_temp["Flux"].unique())
        df_filtre = df_temp[df_temp["Flux"] == flux_selectionne]

        if df_filtre.empty:
            st.error("⚠️ Aucune donnée disponible pour cette combinaison.")
        else:
            total_ca = df_filtre["CA Total"].values[0]
            total_cout = df_filtre["Coût Total"].values[0]

            # 📌 Calcul des indicateurs financiers
            marge_brute = total_ca - total_cout
            mcv = (marge_brute / total_ca) * 100 if total_ca > 0 else 0

            st.subheader(f"📊 Détails pour {client_selectionne} - {temperature_selectionnee} - {flux_selectionne}")
            st.metric(label="Chiffre d'Affaires (CA)", value=f"{total_ca:,.2f} €")
            st.metric(label="Coût Total", value=f"{total_cout:,.2f} €")
            st.metric(label="Marge Brute", value=f"{marge_brute:,.2f} €")
            st.metric(label="MCV (%)", value=f"{mcv:.2f} %")

            # 📌 Affichage des coûts détaillés
            colonnes_couts = [
                "Coût Collecte", "Coût Tri", "Coût Manutention", "Coût Acheminement", "Coût Distribution",
                "Coût Pickup Colis", "Coût Pickup KG", "Coût Support", "Coût Branding", "Coût Carboglace"
            ]

            df_couts = df_filtre[["Client", "Température", "Flux"] + colonnes_couts].T
            df_couts.columns = ["Valeur (€)"]
            df_couts = df_couts.iloc[3:]  # Retirer les premières lignes d'infos
            st.write("### 📝 Détail des coûts")
            st.dataframe(df_couts)

            # 📌 Graphique des coûts détaillés
            st.write("### 📊 Répartition des coûts")
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(x=df_couts.index, y=df_couts["Valeur (€)"], palette="coolwarm", ax=ax)
            ax.set_title(f"Répartition des coûts pour {client_selectionne} ({temperature_selectionnee}, {flux_selectionne})")
            ax.set_ylabel("Coût (€)")
            ax.set_xlabel("Type de coût")
            plt.xticks(rotation=45, ha="right")
            
            st.pyplot(fig)

if __name__ == "__main__":
    main()