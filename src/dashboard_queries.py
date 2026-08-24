from __future__ import annotations

from pathlib import Path
import sqlite3

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


def buscar_execucao_ativa(
    caminho_banco: Path = DEFAULT_DB_PATH
) -> dict | None:
    """Resolve o processamento que o dashboard deve acompanhar."""

    try:
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
                    started_at,
                    updated_at,
                    model_version,
                    policy_version

                FROM replay_runs

                WHERE status = 'RUNNING'

                ORDER BY started_at DESC

                LIMIT 1
                """
            ).fetchone()

            if linha is None:
                linha = conexao.execute(
                    """
                    SELECT
                        run_id,
                        status,
                        total_transacoes,
                        processadas,
                        started_at,
                        updated_at,
                        model_version,
                        policy_version

                    FROM replay_runs

                    ORDER BY started_at DESC

                    LIMIT 1
                    """
                ).fetchone()

    except sqlite3.OperationalError as exc:
        if "no such table" in str(exc).lower():
            return None
        raise

    if linha is None:
        return None

    return dict(linha)


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
    """Retorna o feed com o vetor necessário à explicação local sob demanda."""

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
                model_features_json,

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
                model_features_json,

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
# ANÁLISE COMERCIAL
# ==========================================================

def buscar_metricas_comerciais(
    run_id: str,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> dict:
    """Consolida volume, exposição e eficiência financeira da política."""

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linha = conexao.execute(
            """
            SELECT
                COALESCE(SUM(amt), 0) AS volume_processado,

                COALESCE(SUM(
                    CASE WHEN decisao = 'APROVAR' THEN amt ELSE 0 END
                ), 0) AS volume_liberado,

                COALESCE(SUM(
                    CASE WHEN decisao = 'REVISAR' THEN amt ELSE 0 END
                ), 0) AS valor_revisao,

                COALESCE(SUM(
                    CASE WHEN decisao = 'ALERTA_CRITICO' THEN amt ELSE 0 END
                ), 0) AS valor_critico,

                COALESCE(SUM(
                    CASE WHEN is_fraud = 1 THEN amt ELSE 0 END
                ), 0) AS valor_fraudulento_total,

                COALESCE(SUM(
                    CASE
                        WHEN is_fraud = 1
                         AND decisao IN ('REVISAR', 'ALERTA_CRITICO')
                        THEN amt ELSE 0
                    END
                ), 0) AS valor_fraudulento_identificado,

                COALESCE(SUM(
                    CASE
                        WHEN is_fraud = 1 AND decisao = 'APROVAR'
                        THEN amt ELSE 0
                    END
                ), 0) AS valor_fraudulento_nao_interceptado,

                COALESCE(SUM(
                    CASE WHEN is_fraud = 0 THEN amt ELSE 0 END
                ), 0) AS valor_legitimo_total,

                COALESCE(SUM(
                    CASE
                        WHEN is_fraud = 0
                         AND decisao IN ('REVISAR', 'ALERTA_CRITICO')
                        THEN amt ELSE 0
                    END
                ), 0) AS valor_legitimo_sinalizado,

                COALESCE(SUM(
                    CASE
                        WHEN is_fraud = 0 AND decisao = 'APROVAR'
                        THEN amt ELSE 0
                    END
                ), 0) AS valor_legitimo_liberado,

                AVG(amt) AS ticket_medio,

                AVG(
                    CASE
                        WHEN decisao IN ('REVISAR', 'ALERTA_CRITICO')
                        THEN amt
                    END
                ) AS ticket_medio_sinalizado,

                AVG(
                    CASE WHEN decisao = 'ALERTA_CRITICO' THEN amt END
                ) AS ticket_medio_critico

            FROM transacoes_processadas

            WHERE run_id = ?
            """,
            (run_id,)
        ).fetchone()

    resultado = dict(linha)

    for chave in resultado:
        resultado[chave] = (
            float(resultado[chave])
            if resultado[chave] is not None
            else 0.0
        )

    resultado["exposicao_sinalizada"] = (
        resultado["valor_revisao"]
        + resultado["valor_critico"]
    )

    volume_processado = resultado["volume_processado"]
    valor_fraudulento_total = resultado["valor_fraudulento_total"]
    valor_legitimo_total = resultado["valor_legitimo_total"]

    resultado["percentual_liberado"] = (
        resultado["volume_liberado"] / volume_processado
        if volume_processado > 0
        else None
    )
    resultado["taxa_retencao_financeira"] = (
        resultado["exposicao_sinalizada"] / volume_processado
        if volume_processado > 0
        else None
    )
    resultado["cobertura_financeira"] = (
        resultado["valor_fraudulento_identificado"]
        / valor_fraudulento_total
        if valor_fraudulento_total > 0
        else None
    )
    resultado["friccao_financeira"] = (
        resultado["valor_legitimo_sinalizado"]
        / valor_legitimo_total
        if valor_legitimo_total > 0
        else None
    )

    return resultado


def buscar_exposicao_por_categoria(
    run_id: str,
    limite: int = 5,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> list[dict]:
    """Ordena categorias pelo valor financeiro total sinalizado."""

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linhas = conexao.execute(
            """
            SELECT
                category,
                COUNT(*) AS operacoes_sinalizadas,
                COALESCE(SUM(amt), 0) AS exposicao_sinalizada,
                COALESCE(SUM(
                    CASE WHEN decisao = 'REVISAR' THEN amt ELSE 0 END
                ), 0) AS valor_revisao,
                COALESCE(SUM(
                    CASE WHEN decisao = 'ALERTA_CRITICO' THEN amt ELSE 0 END
                ), 0) AS valor_critico

            FROM transacoes_processadas

            WHERE
                run_id = ?
                AND decisao IN ('REVISAR', 'ALERTA_CRITICO')
                AND category IS NOT NULL

            GROUP BY category

            ORDER BY exposicao_sinalizada DESC

            LIMIT ?
            """,
            (
                run_id,
                int(limite),
            )
        ).fetchall()

    resultado = []
    for linha in linhas:
        item = dict(linha)
        for chave in (
            "exposicao_sinalizada",
            "valor_revisao",
            "valor_critico",
        ):
            item[chave] = float(item[chave] or 0)
        resultado.append(item)

    return resultado


def buscar_evolucao_financeira(
    run_id: str,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> list[dict]:
    """Retorna a exposição acumulada em intervalos de processamento."""

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linhas = conexao.execute(
            """
            SELECT
                substr(processed_at, 1, 16) || ':00' AS momento,
                COALESCE(SUM(
                    CASE WHEN decisao = 'REVISAR' THEN amt ELSE 0 END
                ), 0) AS valor_revisao,
                COALESCE(SUM(
                    CASE WHEN decisao = 'ALERTA_CRITICO' THEN amt ELSE 0 END
                ), 0) AS valor_critico

            FROM transacoes_processadas

            WHERE run_id = ?

            GROUP BY substr(processed_at, 1, 16)

            ORDER BY momento
            """,
            (run_id,)
        ).fetchall()

    revisao_acumulada = 0.0
    critico_acumulado = 0.0
    resultado = []

    for linha in linhas:
        revisao_acumulada += float(linha["valor_revisao"] or 0)
        critico_acumulado += float(linha["valor_critico"] or 0)
        resultado.append({
            "momento": linha["momento"],
            "valor_revisao_acumulado": revisao_acumulada,
            "valor_critico_acumulado": critico_acumulado,
            "exposicao_sinalizada_acumulada": (
                revisao_acumulada + critico_acumulado
            ),
        })

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

    metricas_comerciais = buscar_metricas_comerciais(
        run_id=run_id,
        caminho_banco=caminho_banco
    )

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

        "valores": {
            "valor_total": metricas_comerciais["volume_processado"],
            "ticket_medio": metricas_comerciais["ticket_medio"],
            "valor_revisao": metricas_comerciais["valor_revisao"],
            "valor_critico": metricas_comerciais["valor_critico"],
        },

        "metricas_comerciais": metricas_comerciais,

        "exposicao_por_categoria":
            buscar_exposicao_por_categoria(
                run_id=run_id,
                limite=5,
                caminho_banco=caminho_banco
            ),

        "evolucao_financeira":
            buscar_evolucao_financeira(
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
                model_features_json,

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

# ==========================================================
# TRANSAÇÕES & ALERTAS
# ==========================================================

DECISOES_VALIDAS = {
    "APROVAR",
    "REVISAR",
    "ALERTA_CRITICO",
}


def _montar_filtros_transacoes(
    run_id: str,
    decisoes: list[str] | tuple[str, ...] | None = None,
    categoria: str | None = None,
    estado: str | None = None,
    busca: str | None = None,
    score_min: float | None = None,
    score_max: float | None = None,
) -> tuple[str, list]:

    """
    Monta de forma segura a cláusula WHERE utilizada
    nas consultas da página Transações & Alertas.
    """

    condicoes = [
        "run_id = ?"
    ]

    parametros = [
        run_id
    ]

    # ------------------------------------------------------
    # DECISÃO
    # ------------------------------------------------------

    if decisoes:

        decisoes = list(
            decisoes
        )

        invalidas = (
            set(decisoes)
            - DECISOES_VALIDAS
        )

        if invalidas:
            raise ValueError(
                "Decisões inválidas: "
                + ", ".join(
                    sorted(invalidas)
                )
            )

        placeholders = ", ".join(
            "?"
            for _ in decisoes
        )

        condicoes.append(
            f"decisao IN ({placeholders})"
        )

        parametros.extend(
            decisoes
        )

    # ------------------------------------------------------
    # CATEGORIA
    # ------------------------------------------------------

    if categoria:

        condicoes.append(
            "category = ?"
        )

        parametros.append(
            categoria
        )

    # ------------------------------------------------------
    # ESTADO
    # ------------------------------------------------------

    if estado:

        condicoes.append(
            "state = ?"
        )

        parametros.append(
            estado
        )

    # ------------------------------------------------------
    # SCORE
    # ------------------------------------------------------

    if score_min is not None:

        condicoes.append(
            "score_fraude >= ?"
        )

        parametros.append(
            float(score_min)
        )

    if score_max is not None:

        condicoes.append(
            "score_fraude <= ?"
        )

        parametros.append(
            float(score_max)
        )

    # ------------------------------------------------------
    # BUSCA LIVRE
    # ------------------------------------------------------

    if busca:

        termo = (
            f"%{busca.strip()}%"
        )

        condicoes.append(
            """
            (
                first LIKE ?
                OR last LIKE ?
                OR (
                    COALESCE(first, '')
                    || ' '
                    || COALESCE(last, '')
                ) LIKE ?
                OR merchant LIKE ?
                OR trans_num LIKE ?
                OR cc_last4 LIKE ?
                OR city LIKE ?
            )
            """
        )

        parametros.extend(
            [
                termo,
                termo,
                termo,
                termo,
                termo,
                termo,
                termo,
            ]
        )

    where_sql = (
        " AND ".join(
            condicoes
        )
    )

    return (
        where_sql,
        parametros,
    )

def buscar_transacoes(
    run_id: str,
    decisoes: list[str] | tuple[str, ...] | None = None,
    categoria: str | None = None,
    estado: str | None = None,
    busca: str | None = None,
    score_min: float | None = None,
    score_max: float | None = None,
    limite: int = 100,
    offset: int = 0,
    caminho_banco: Path = DEFAULT_DB_PATH,
) -> list[dict]:

    """
    Consulta transações para a área de investigação.

    Permite filtrar por:
    - decisão;
    - categoria;
    - estado;
    - texto;
    - score mínimo;
    - score máximo.

    A consulta é paginável através de limite + offset.
    """

    where_sql, parametros = (
        _montar_filtros_transacoes(
            run_id=run_id,
            decisoes=decisoes,
            categoria=categoria,
            estado=estado,
            busca=busca,
            score_min=score_min,
            score_max=score_max,
        )
    )

    sql = f"""
        SELECT

            id,
            run_id,

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

            processed_at,
            latency_ms

        FROM transacoes_processadas

        WHERE
            {where_sql}

        ORDER BY
            id DESC

        LIMIT ?
        OFFSET ?
    """

    parametros.extend(
        [
            int(limite),
            int(offset),
        ]
    )

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linhas = conexao.execute(
            sql,
            parametros,
        ).fetchall()

    return [
        dict(linha)
        for linha in linhas
    ]

def contar_transacoes_filtradas(
    run_id: str,
    decisoes: list[str] | tuple[str, ...] | None = None,
    categoria: str | None = None,
    estado: str | None = None,
    busca: str | None = None,
    score_min: float | None = None,
    score_max: float | None = None,
    caminho_banco: Path = DEFAULT_DB_PATH,
) -> int:

    where_sql, parametros = (
        _montar_filtros_transacoes(
            run_id=run_id,
            decisoes=decisoes,
            categoria=categoria,
            estado=estado,
            busca=busca,
            score_min=score_min,
            score_max=score_max,
        )
    )

    sql = f"""
        SELECT
            COUNT(*) AS total

        FROM transacoes_processadas

        WHERE
            {where_sql}
    """

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linha = conexao.execute(
            sql,
            parametros,
        ).fetchone()

    return int(
        linha["total"]
        or 0
    )

def buscar_detalhe_transacao(
    run_id: str,
    trans_num: str,
    caminho_banco: Path = DEFAULT_DB_PATH,
) -> dict | None:

    """
    Retorna todos os dados operacionais disponíveis
    para uma transação específica.
    """

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linha = conexao.execute(
            """
            SELECT

                id,
                run_id,

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

                latency_ms,
                processed_at,

                model_version,
                policy_version

            FROM transacoes_processadas

            WHERE
                run_id = ?
                AND trans_num = ?

            LIMIT 1
            """,
            (
                run_id,
                trans_num,
            )
        ).fetchone()

    if linha is None:
        return None

    return dict(
        linha
    )

def buscar_opcoes_filtros_transacoes(
    run_id: str,
    caminho_banco: Path = DEFAULT_DB_PATH,
) -> dict:

    with conectar_banco(
        caminho_banco
    ) as conexao:

        categorias = conexao.execute(
            """
            SELECT DISTINCT
                category

            FROM transacoes_processadas

            WHERE
                run_id = ?
                AND category IS NOT NULL

            ORDER BY
                category
            """,
            (run_id,)
        ).fetchall()

        estados = conexao.execute(
            """
            SELECT DISTINCT
                state

            FROM transacoes_processadas

            WHERE
                run_id = ?
                AND state IS NOT NULL

            ORDER BY
                state
            """,
            (run_id,)
        ).fetchall()

    return {

        "categorias": [
            linha["category"]
            for linha in categorias
        ],

        "estados": [
            linha["state"]
            for linha in estados
        ],

        "decisoes": [
            "APROVAR",
            "REVISAR",
            "ALERTA_CRITICO",
        ],
    }
