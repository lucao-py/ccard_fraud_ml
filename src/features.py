import numpy as np
import pandas as pd

FEATURES_MODELO = [
    "amt_log",
    "city_pop_log",
    "idade",
    "distancia_km",
    "hora_sin",
    "hora_cos",
    "dia_semana_sin",
    "dia_semana_cos",
    "fim_de_semana",
    "category",
    "gender",
    "state"
]

FEATURES_CATEGORICAS = [
    "category",
    "gender",
    "state"
]

def calcular_distancia_haversine(
    lat1,
    lon1,
    lat2,
    lon2
):
    raio_terra_km = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        np.sin(delta_lat / 2) ** 2
        +
        np.cos(lat1)
        * np.cos(lat2)
        * np.sin(delta_lon / 2) ** 2
    )

    c = 2 * np.arcsin(
        np.sqrt(a)
    )

    return raio_terra_km * c

def construir_features(
    df: pd.DataFrame
) -> pd.DataFrame:

    dados = df.copy()

    dados[
        "trans_date_trans_time"
    ] = pd.to_datetime(
        dados[
            "trans_date_trans_time"
        ]
    )

    dados["dob"] = pd.to_datetime(
        dados["dob"]
    )

    # Valor
    dados["amt_log"] = np.log1p(
        dados["amt"]
    )

    # População
    dados["city_pop_log"] = np.log1p(
        dados["city_pop"]
    )

    # Idade
    transacao = (
        dados[
            "trans_date_trans_time"
        ]
    )

    nascimento = dados["dob"]

    dados["idade"] = (
        transacao.dt.year
        -
        nascimento.dt.year
        -
        (
            (
                transacao.dt.month
                <
                nascimento.dt.month
            )
            |
            (
                (
                    transacao.dt.month
                    ==
                    nascimento.dt.month
                )
                &
                (
                    transacao.dt.day
                    <
                    nascimento.dt.day
                )
            )
        ).astype(int)
    )

    # Distância
    dados["distancia_km"] = (
        calcular_distancia_haversine(
            dados["lat"],
            dados["long"],
            dados["merch_lat"],
            dados["merch_long"]
        )
    )

    # Hora
    hora = (
        transacao.dt.hour
    )

    dados["hora_sin"] = np.sin(
        2 * np.pi * hora / 24
    )

    dados["hora_cos"] = np.cos(
        2 * np.pi * hora / 24
    )

    # Dia da semana
    dia_semana = (
        transacao.dt.dayofweek
    )

    dados["dia_semana_sin"] = (
        np.sin(
            2
            * np.pi
            * dia_semana
            / 7
        )
    )

    dados["dia_semana_cos"] = (
        np.cos(
            2
            * np.pi
            * dia_semana
            / 7
        )
    )

    dados["fim_de_semana"] = (
        dia_semana >= 5
    ).astype(int)

    # Categóricas
    for coluna in (
        FEATURES_CATEGORICAS
    ):
        dados[coluna] = (
            dados[coluna]
            .fillna("__MISSING__")
            .astype(str)
        )

    return dados[
        FEATURES_MODELO
    ]