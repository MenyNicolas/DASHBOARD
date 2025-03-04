import numpy as np
import pandas as pd

##########################################################
### CHARGE LES DONNEES RELATIVES AUX COUTS
##########################################################

# on définis les fonctions de transformations assurant un format adéquat
def transform_1(df):
    df = df.iloc[:, 1:]
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)
    
    return df

def transform(df_std, df):
    df_std = transform_1(df_std)
    df = transform_1(df)

    df_std.columns = df_std.columns.str.upper()
    df.columns = df.columns.str.upper()

    return df.fillna(df_std)

def load_couts():
    # on récupère les couts des différents clients
    df_std = pd.read_csv('FICHIERS CSV/couts standards.csv')
    df_aliive = pd.read_csv('FICHIERS CSV/aliive.csv')
    df_comme_j_aime = pd.read_csv('FICHIERS CSV/comme j_aime.csv')
    df_eol_eldorado = pd.read_csv('FICHIERS CSV/eol eldorado.csv')
    df_greenweez = pd.read_csv('FICHIERS CSV/greenweez.csv')
    df_hellofresh_c13 = pd.read_csv('FICHIERS CSV/hellofresh c13.csv')
    df_hellofresh_c18 = pd.read_csv('FICHIERS CSV/hellofresh c18.csv')
    df_la_fourche = pd.read_csv('FICHIERS CSV/la fourche.csv')
    df_picard = pd.read_csv('FICHIERS CSV/picard.csv')
    df_quitoque = pd.read_csv('FICHIERS CSV/quitoque.csv')
    df_regime_de_vero = pd.read_csv('FICHIERS CSV/regime de vero.csv')
    df_valrhona = pd.read_csv('FICHIERS CSV/valrhona.csv')
    df_vitagermine = pd.read_csv('FICHIERS CSV/vitagermine.csv')
    df_yooji = pd.read_csv('FICHIERS CSV/yooji.csv')

    # on applqiue les transformations afin d'obtenir les couts des clients
    df_aliive = transform(df_std, df_aliive)
    df_comme_j_aime = transform(df_std, df_comme_j_aime)
    df_eol_eldorado = transform(df_std, df_eol_eldorado)
    df_greenweez = transform(df_std, df_greenweez)
    df_hellofresh_c13 = transform(df_std, df_hellofresh_c13)
    df_hellofresh_c18 = transform(df_std, df_hellofresh_c18)
    df_la_fourche = transform(df_std, df_la_fourche)
    df_picard = transform(df_std, df_picard)
    df_quitoque = transform(df_std, df_quitoque)
    df_regime_de_vero = transform(df_std, df_regime_de_vero)
    df_valrhona = transform(df_std, df_valrhona)
    df_vitagermine = transform(df_std, df_vitagermine)
    df_yooji = transform(df_std, df_yooji)

    # on définis un dictionnaire associant les noms des clients à leurs couts respectifs
    dict_couts = {
        "ALIIVE": df_aliive,
        'COMME J"AIME': df_comme_j_aime,
        "EOL GROUP-ELDORADO": df_eol_eldorado,
        "GREENWEEZ": df_greenweez,
        "HELLOFRESH FRANCE SAS 13": df_hellofresh_c13,
        "HELLOFRESH FRANCE SAS 18": df_hellofresh_c18,
        "LA FOURCHE": df_la_fourche,
        "PICARD SURGELES": df_picard,
        "QUITOQUE": df_quitoque,
        "LE REGIME DE VERO": df_regime_de_vero,
        "VALRHONA": df_valrhona,
        "VITAGERMINE": df_vitagermine,
        "YOOJI": df_yooji
    }

    return dict_couts

##########################################################
### CHARGE LES DONNEES RELATIVES AUX CLIENTS
##########################################################

def transform_2(df):
    df = df.iloc[2:].reset_index(drop=True)
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)
    df = df.dropna(axis=1, how='all')

    return df

def load_data():
    # on récupère les data extraites de bo
    df_hellofresh = transform_2(pd.read_excel('EXTRACT/BO_HELLOFRESH.xlsx'))
    df_other = transform_2(pd.read_excel('EXTRACT/BO_OTHER.xlsx'))

    # on les combine en une seule dataframe
    df_combined = pd.concat([df_hellofresh, df_other], ignore_index=True)
    df_combined["temperature"] = df_combined["temp hello"].fillna(df_combined["température"])
    df_combined.drop(columns=["temp hello", "température"], inplace=True, errors="ignore")
    df_combined = df_combined.rename(columns={'CLI - Raison sociale': 'CLI', 'Montant total': 'Montant', 'Nb XP': 'XP', 'Nb objet': 'Colis', 'Code secteur tarifaire': 'flux'})

    return df_combined