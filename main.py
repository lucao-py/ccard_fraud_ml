"""Inicialização oficial do sistema de monitoramento antifraude."""

from __future__ import annotations

from datetime import datetime
import fcntl
import os
from pathlib import Path
import subprocess
import sys
from time import sleep
import uuid

from src.persistence import (
    inicializar_banco,
    limpar_estado_operacional,
)


PROJECT_ROOT = Path(__file__).resolve().parent
WORKER_PATH = PROJECT_ROOT / "scripts" / "run_live_replay.py"
DASHBOARD_PATH = PROJECT_ROOT / "dashboard" / "app.py"
LOCK_PATH = PROJECT_ROOT / "runtime" / ".main.lock"
SHUTDOWN_TIMEOUT_SECONDS = 5


def _gerar_run_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"runtime_{timestamp}_{uuid.uuid4().hex[:8]}"


def _resolver_python_projeto() -> str:
    candidatos = (
        PROJECT_ROOT / "venv" / "bin" / "python",
        PROJECT_ROOT / ".venv" / "bin" / "python",
        PROJECT_ROOT / "venv" / "Scripts" / "python.exe",
        PROJECT_ROOT / ".venv" / "Scripts" / "python.exe",
    )

    for candidato in candidatos:
        if candidato.is_file():
            return str(candidato)

    return sys.executable


def _adquirir_lock_sistema():
    LOCK_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    arquivo_lock = LOCK_PATH.open(
        "a+",
        encoding="utf-8",
    )

    try:
        fcntl.flock(
            arquivo_lock.fileno(),
            fcntl.LOCK_EX | fcntl.LOCK_NB,
        )
    except BlockingIOError:
        arquivo_lock.close()
        return None

    arquivo_lock.seek(0)
    arquivo_lock.truncate()
    arquivo_lock.write(str(os.getpid()))
    arquivo_lock.flush()

    return arquivo_lock


def _liberar_lock_sistema(arquivo_lock) -> None:
    if arquivo_lock is None:
        return

    fcntl.flock(
        arquivo_lock.fileno(),
        fcntl.LOCK_UN,
    )
    arquivo_lock.close()


def _encerrar_processo(processo: subprocess.Popen) -> None:
    if processo.poll() is not None:
        return

    processo.terminate()

    try:
        processo.wait(timeout=SHUTDOWN_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        processo.kill()
        processo.wait()


def main() -> int:
    print(
        "Iniciando sistema de monitoramento antifraude...",
        flush=True,
    )

    arquivo_lock = _adquirir_lock_sistema()

    if arquivo_lock is None:
        print(
            "O sistema já está em execução. "
            "Encerre a instância atual antes de iniciar outra.",
            flush=True,
        )
        return 1

    worker = None
    dashboard = None

    try:
        print("Limpando estado operacional anterior...", flush=True)
        inicializar_banco()
        limpar_estado_operacional()
        print("Banco preparado.", flush=True)

        ambiente = os.environ.copy()
        ambiente["FRAUD_RUN_ID"] = _gerar_run_id()
        porta_dashboard = ambiente.get("STREAMLIT_SERVER_PORT", "8501")
        python_projeto = _resolver_python_projeto()

        print("Iniciando processamento...", flush=True)
        worker = subprocess.Popen(
            [python_projeto, str(WORKER_PATH)],
            cwd=PROJECT_ROOT,
            env=ambiente,
        )

        print("Iniciando dashboard...", flush=True)
        dashboard = subprocess.Popen(
            [
                python_projeto,
                "-m",
                "streamlit",
                "run",
                str(DASHBOARD_PATH),
                "--server.port",
                porta_dashboard,
            ],
            cwd=PROJECT_ROOT,
            env=ambiente,
        )

        print("Processamento iniciado.", flush=True)
        print(
            f"Dashboard disponível em http://localhost:{porta_dashboard}",
            flush=True,
        )

        while True:
            codigo_dashboard = dashboard.poll()
            codigo_worker = worker.poll()

            if codigo_dashboard is not None:
                if codigo_dashboard != 0:
                    print(
                        "O dashboard foi encerrado inesperadamente.",
                        flush=True,
                    )
                return codigo_dashboard

            if codigo_worker is not None and codigo_worker != 0:
                print(
                    "O processamento foi interrompido inesperadamente.",
                    flush=True,
                )
                return codigo_worker

            sleep(0.5)

    except KeyboardInterrupt:
        print("\nEncerrando sistema...", flush=True)
        return 0

    except Exception as exc:
        print(
            f"Falha ao iniciar o sistema: {exc}",
            flush=True,
        )
        return 1

    finally:
        if dashboard is not None:
            _encerrar_processo(dashboard)

        if worker is not None:
            _encerrar_processo(worker)

        _liberar_lock_sistema(arquivo_lock)
        print("Sistema encerrado.", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
