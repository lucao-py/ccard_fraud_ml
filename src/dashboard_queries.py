from __future__ import annotations

from pathlib import Path

from src.persistence import (
    DEFAULT_DB_PATH,
    conectar_banco
)


# ==========================================================
# RUNS
# ==========================================================

def listar_runs(
    caminho_banco: Path = DEFAULT_DB_PATH
) -> list[dict]:

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linhas = conexao.execute(
            """
            SELECT
                run_id,
                status,
                total_transacoes,
                processadas,
                intervalo_segundos,
                started_at,
                completed_at,
                model_version,
                policy_version

            FROM replay_runs

            ORDER BY started_at DESC
            """
        ).fetchall()

    return [
        dict(linha)
        for linha in linhas
    ]


# ==========================================================
# STATUS DO REPLAY
# ==========================================================

def buscar_status_replay(
    run_id: str,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> dict | None:

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linha = conexao.execute(
            """
            SELECT
                run_id,
                status,
                total_transacoes,
                processadas,
                last_index,
                intervalo_segundos,
                started_at,
                updated_at,
                completed_at,
                model_version,
                policy_version

            FROM replay_runs

            WHERE run_id = ?
            """,
            (run_id,)
        ).fetchone()

    if linha is None:
        return None

    resultado = dict(linha)

    total = (
        resultado.get(
            "total_transacoes"
        )
        or 0
    )

    processadas = (
        resultado.get(
            "processadas"
        )
        or 0
    )

    resultado["progresso"] = (
        processadas / total
        if total > 0
        else 0.0
    )

    return resultado


# ==========================================================
# KPIs PRINCIPAIS
# ==========================================================

def buscar_resumo_execucao(
    run_id: str,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> dict:

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linha = conexao.execute(
            """
            SELECT

                COUNT(*) AS total_processadas,

                SUM(
                    CASE
                        WHEN decisao = 'APROVAR'
                        THEN 1
                        ELSE 0
                    END
                ) AS aprovadas,

                SUM(
                    CASE
                        WHEN decisao = 'REVISAR'
                        THEN 1
                        ELSE 0
                    END
                ) AS revisar,

                SUM(
                    CASE
                        WHEN decisao = 'ALERTA_CRITICO'
                        THEN 1
                        ELSE 0
                    END
                ) AS alertas_criticos

            FROM transacoes_processadas

            WHERE run_id = ?
            """,
            (run_id,)
        ).fetchone()

    resultado = dict(linha)

    for chave in [
        "total_processadas",
        "aprovadas",
        "revisar",
        "alertas_criticos"
    ]:
        resultado[chave] = (
            resultado[chave]
            or 0
        )

    total = resultado[
        "total_processadas"
    ]

    if total > 0:

        resultado[
            "percentual_aprovadas"
        ] = (
            resultado["aprovadas"]
            / total
        )

        resultado[
            "percentual_revisar"
        ] = (
            resultado["revisar"]
            / total
        )

        resultado[
            "percentual_criticos"
        ] = (
            resultado[
                "alertas_criticos"
            ]
            / total
        )

        resultado[
            "percentual_encaminhado"
        ] = (
            (
                resultado["revisar"]
                +
                resultado[
                    "alertas_criticos"
                ]
            )
            / total
        )

    else:

        resultado[
            "percentual_aprovadas"
        ] = 0.0

        resultado[
            "percentual_revisar"
        ] = 0.0

        resultado[
            "percentual_criticos"
        ] = 0.0

        resultado[
            "percentual_encaminhado"
        ] = 0.0

    return resultado


# ==========================================================
# MÉTRICAS DE FRAUDE
# ==========================================================

def buscar_metricas_fraude(
    run_id: str,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> dict:

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linha = conexao.execute(
            """
            SELECT

                SUM(
                    CASE
                        WHEN is_fraud = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS fraudes_reais,

                SUM(
                    CASE
                        WHEN is_fraud = 1
                        AND decisao != 'APROVAR'
                        THEN 1
                        ELSE 0
                    END
                ) AS fraudes_detectadas,

                SUM(
                    CASE
                        WHEN is_fraud = 1
                        AND decisao = 'APROVAR'
                        THEN 1
                        ELSE 0
                    END
                ) AS fraudes_perdidas,

                SUM(
                    CASE
                        WHEN is_fraud = 0
                        AND decisao != 'APROVAR'
                        THEN 1
                        ELSE 0
                    END
                ) AS legitimas_encaminhadas,

                SUM(
                    CASE
                        WHEN decisao != 'APROVAR'
                        THEN 1
                        ELSE 0
                    END
                ) AS total_encaminhadas,

                SUM(
                    CASE
                        WHEN decisao = 'ALERTA_CRITICO'
                        THEN 1
                        ELSE 0
                    END
                ) AS total_criticas,

                SUM(
                    CASE
                        WHEN decisao = 'ALERTA_CRITICO'
                        AND is_fraud = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS fraudes_criticas

            FROM transacoes_processadas

            WHERE run_id = ?
            """,
            (run_id,)
        ).fetchone()

    resultado = dict(linha)

    for chave in [
        "fraudes_reais",
        "fraudes_detectadas",
        "fraudes_perdidas",
        "legitimas_encaminhadas",
        "total_encaminhadas",
        "total_criticas",
        "fraudes_criticas"
    ]:

        resultado[chave] = (
            resultado[chave]
            or 0
        )


    fraudes_reais = resultado[
        "fraudes_reais"
    ]

    fraudes_detectadas = resultado[
        "fraudes_detectadas"
    ]

    total_encaminhadas = resultado[
        "total_encaminhadas"
    ]

    total_criticas = resultado[
        "total_criticas"
    ]

    fraudes_criticas = resultado[
        "fraudes_criticas"
    ]


    resultado["recall_politica"] = (
        fraudes_detectadas
        / fraudes_reais

        if fraudes_reais > 0
        else None
    )


    resultado[
        "precision_encaminhamento"
    ] = (
        fraudes_detectadas
        / total_encaminhadas

        if total_encaminhadas > 0
        else None
    )


    resultado[
        "taxa_fraude_critica"
    ] = (
        fraudes_criticas
        / total_criticas

        if total_criticas > 0
        else None
    )

    return resultado


# ==========================================================
# TRANSAÇÕES RECENTES
# ==========================================================

def buscar_transacoes_recentes(
    run_id: str,
    limite: int = 20,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> list[dict]:

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linhas = conexao.execute(
            """
            SELECT

                trans_num,
                trans_date_trans_time,

                first,
                last,
                merchant,
                category,
                amt,
                city,
                state,
                cc_last4,

                score_fraude,
                decisao,

                is_fraud,
                latency_ms,
                processed_at

            FROM transacoes_processadas

            WHERE run_id = ?

            ORDER BY id DESC

            LIMIT ?
            """,
            (
                run_id,
                int(limite)
            )
        ).fetchall()

    return [
        dict(linha)
        for linha in linhas
    ]


# ==========================================================
# ALERTAS CRÍTICOS
# ==========================================================

def buscar_alertas_criticos(
    run_id: str,
    limite: int = 20,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> list[dict]:

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linhas = conexao.execute(
            """
            SELECT

                trans_num,
                trans_date_trans_time,

                first,
                last,

                merchant,
                category,
                amt,

                city,
                state,
                cc_last4,

                score_fraude,
                decisao,

                is_fraud,
                processed_at

            FROM transacoes_processadas

            WHERE
                run_id = ?
                AND decisao = 'ALERTA_CRITICO'

            ORDER BY id DESC

            LIMIT ?
            """,
            (
                run_id,
                int(limite)
            )
        ).fetchall()

    return [
        dict(linha)
        for linha in linhas
    ]

# ==========================================================
# SCORE ACTIVITY
# ==========================================================

def buscar_atividade_risco(
    run_id: str,
    limite: int = 100,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> list[dict]:

    """
    Retorna os últimos scores para o gráfico
    compacto de atividade de risco.
    """

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linhas = conexao.execute(
            """
            SELECT

                id,
                trans_num,
                trans_date_trans_time,
                score_fraude,
                decisao

            FROM transacoes_processadas

            WHERE run_id = ?

            ORDER BY id DESC

            LIMIT ?
            """,
            (
                run_id,
                int(limite)
            )
        ).fetchall()

    # Retorna em ordem cronológica,
    # não na ordem DESC utilizada para buscar
    # os registros mais recentes.
    return [
        dict(linha)
        for linha in reversed(
            linhas
        )
    ]


# ==========================================================
# TOP CATEGORIAS DE RISCO
# ==========================================================

def buscar_top_categorias_risco(
    run_id: str,
    limite: int = 6,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> list[dict]:

    """
    Ranking das categorias com maior quantidade
    de transações encaminhadas para REVISAR ou
    ALERTA_CRITICO.
    """

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linhas = conexao.execute(
            """
            SELECT

                category,

                COUNT(*) AS total_encaminhadas,

                SUM(
                    CASE
                        WHEN decisao = 'REVISAR'
                        THEN 1
                        ELSE 0
                    END
                ) AS revisar,

                SUM(
                    CASE
                        WHEN decisao = 'ALERTA_CRITICO'
                        THEN 1
                        ELSE 0
                    END
                ) AS criticas,

                AVG(
                    score_fraude
                ) AS score_medio

            FROM transacoes_processadas

            WHERE
                run_id = ?
                AND decisao != 'APROVAR'
                AND category IS NOT NULL

            GROUP BY category

            ORDER BY
                total_encaminhadas DESC,
                score_medio DESC

            LIMIT ?
            """,
            (
                run_id,
                int(limite)
            )
        ).fetchall()

    return [
        dict(linha)
        for linha in linhas
    ]


# ==========================================================
# CATEGORIAS CRÍTICAS
# ==========================================================

def buscar_top_categorias_criticas(
    run_id: str,
    limite: int = 6,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> list[dict]:

    """
    Ranking específico das categorias com maior
    quantidade de ALERTA_CRITICO.
    """

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linhas = conexao.execute(
            """
            SELECT

                category,

                COUNT(*) AS alertas_criticos,

                AVG(
                    score_fraude
                ) AS score_medio,

                AVG(
                    amt
                ) AS valor_medio,

                SUM(
                    CASE
                        WHEN is_fraud = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS fraudes_reais

            FROM transacoes_processadas

            WHERE
                run_id = ?
                AND decisao = 'ALERTA_CRITICO'
                AND category IS NOT NULL

            GROUP BY category

            ORDER BY
                alertas_criticos DESC,
                score_medio DESC

            LIMIT ?
            """,
            (
                run_id,
                int(limite)
            )
        ).fetchall()

    return [
        dict(linha)
        for linha in linhas
    ]


# ==========================================================
# VALORES TRANSACIONADOS
# ==========================================================

def buscar_resumo_valores(
    run_id: str,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> dict:

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linha = conexao.execute(
            """
            SELECT

                SUM(
                    amt
                ) AS valor_total,

                AVG(
                    amt
                ) AS ticket_medio,

                SUM(
                    CASE
                        WHEN decisao = 'REVISAR'
                        THEN amt
                        ELSE 0
                    END
                ) AS valor_revisao,

                SUM(
                    CASE
                        WHEN decisao = 'ALERTA_CRITICO'
                        THEN amt
                        ELSE 0
                    END
                ) AS valor_critico

            FROM transacoes_processadas

            WHERE run_id = ?
            """,
            (run_id,)
        ).fetchone()

    resultado = dict(linha)

    for chave in [
        "valor_total",
        "ticket_medio",
        "valor_revisao",
        "valor_critico"
    ]:

        resultado[chave] = (
            float(
                resultado[chave]
            )

            if resultado[chave]
            is not None

            else 0.0
        )

    return resultado


# ==========================================================
# LATÊNCIA
# ==========================================================

def buscar_metricas_latencia(
    run_id: str,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> dict:

    """
    Retorna estatísticas básicas de latency_ms.

    O P95 não é calculado diretamente pelo SQLite
    para manter compatibilidade e simplicidade.
    """

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linha = conexao.execute(
            """
            SELECT

                AVG(
                    latency_ms
                ) AS media_ms,

                MIN(
                    latency_ms
                ) AS minima_ms,

                MAX(
                    latency_ms
                ) AS maxima_ms

            FROM transacoes_processadas

            WHERE
                run_id = ?
                AND latency_ms IS NOT NULL
            """,
            (run_id,)
        ).fetchone()

    resultado = dict(linha)

    for chave in [
        "media_ms",
        "minima_ms",
        "maxima_ms"
    ]:

        resultado[chave] = (
            float(
                resultado[chave]
            )

            if resultado[chave]
            is not None

            else None
        )

    return resultado


# ==========================================================
# SNAPSHOT COMPLETO DO DASHBOARD
# ==========================================================

def carregar_snapshot_dashboard(
    run_id: str,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> dict:

    return {

        "replay":
            buscar_status_replay(
                run_id=run_id,
                caminho_banco=caminho_banco
            ),

        "resumo":
            buscar_resumo_execucao(
                run_id=run_id,
                caminho_banco=caminho_banco
            ),

        "fraudes":
            buscar_metricas_fraude(
                run_id=run_id,
                caminho_banco=caminho_banco
            ),

        "valores":
            buscar_resumo_valores(
                run_id=run_id,
                caminho_banco=caminho_banco
            ),

        "latencia":
            buscar_metricas_latencia(
                run_id=run_id,
                caminho_banco=caminho_banco
            ),

        "transacoes_recentes":
            buscar_transacoes_recentes(
                run_id=run_id,
                limite=20,
                caminho_banco=caminho_banco
            ),

        "alertas_criticos":
            buscar_alertas_criticos(
                run_id=run_id,
                limite=8,
                caminho_banco=caminho_banco
            ),

        "atividade_risco":
            buscar_atividade_risco(
                run_id=run_id,
                limite=100,
                caminho_banco=caminho_banco
            ),

        "top_categorias_risco":
            buscar_top_categorias_risco(
                run_id=run_id,
                limite=6,
                caminho_banco=caminho_banco
            ),

        "top_categorias_criticas":
            buscar_top_categorias_criticas(
                run_id=run_id,
                limite=6,
                caminho_banco=caminho_banco
            ),
         "sinalizacoes":
        buscar_resumo_sinalizacoes(
        run_id=run_id,
        caminho_banco=caminho_banco
    ),

            "transacoes_sinalizadas":
            buscar_transacoes_sinalizadas(
            run_id=run_id,
            limite=20,
            caminho_banco=caminho_banco
        )
    }

# ==========================================================
# TRANSAÇÕES SINALIZADAS
# ==========================================================

def buscar_transacoes_sinalizadas(
    run_id: str,
    limite: int = 20,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> list[dict]:

    """
    Retorna as transações mais recentes que exigiram
    algum tipo de tratamento adicional:

    - REVISAR
    - ALERTA_CRITICO
    """

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linhas = conexao.execute(
            """
            SELECT

                trans_num,
                trans_date_trans_time,

                first,
                last,
                merchant,
                category,
                amt,
                city,
                state,
                cc_last4,

                score_fraude,
                decisao,

                is_fraud,
                latency_ms,
                processed_at

            FROM transacoes_processadas

            WHERE
                run_id = ?
                AND decisao IN (
                    'REVISAR',
                    'ALERTA_CRITICO'
                )

            ORDER BY id DESC

            LIMIT ?
            """,
            (
                run_id,
                int(limite)
            )
        ).fetchall()

    return [
        dict(linha)
        for linha in linhas
    ]

# ==========================================================
# RESUMO DAS SINALIZAÇÕES
# ==========================================================

def buscar_resumo_sinalizacoes(
    run_id: str,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> dict:

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linha = conexao.execute(
            """
            SELECT

                COUNT(*) AS total_sinalizadas,

                SUM(
                    CASE
                        WHEN decisao = 'REVISAR'
                        THEN 1
                        ELSE 0
                    END
                ) AS total_revisao,

                SUM(
                    CASE
                        WHEN decisao = 'ALERTA_CRITICO'
                        THEN 1
                        ELSE 0
                    END
                ) AS total_criticas,

                MAX(
                    score_fraude
                ) AS maior_score,

                AVG(
                    score_fraude
                ) AS score_medio

            FROM transacoes_processadas

            WHERE
                run_id = ?
                AND decisao IN (
                    'REVISAR',
                    'ALERTA_CRITICO'
                )
            """,
            (run_id,)
        ).fetchone()

    resultado = dict(
        linha
    )

    for chave in [
        "total_sinalizadas",
        "total_revisao",
        "total_criticas"
    ]:

        resultado[chave] = (
            resultado[chave]
            or 0
        )

    resultado["maior_score"] = (
        float(
            resultado["maior_score"]
        )
        if resultado[
            "maior_score"
        ] is not None
        else None
    )

    resultado["score_medio"] = (
        float(
            resultado["score_medio"]
        )
        if resultado[
            "score_medio"
        ] is not None
        else None
    )

    return resultado