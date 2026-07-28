"""Forecast 201: como o protocolo de validação altera a conclusão.

Objetivo
--------
Comparar protocolos temporais mantendo dados, modelos, horizonte e métricas
constantes. O laboratório mede o efeito de janela, gap, sobreposição e cadência
de refit, executa seleção temporal aninhada e consulta um teste final bloqueado.

Entradas
--------
Não há arquivos externos. A série diária sintética contém tendência,
sazonalidade semanal e anual, dois regimes e eventos não fornecidos aos modelos.

Processamento
-------------
1. Reserva os 168 dias finais antes de qualquer comparação.
2. Executa backtests no desenvolvimento com horizonte de 28 dias.
3. Compara seasonal naive, média sazonal e regressão de calendário.
4. Varia uma dimensão do protocolo por vez.
5. Seleciona a janela da regressão em folds internos e avalia folds externos.
6. Reajusta a especificação escolhida e consulta uma única vez o teste final.

Saídas
------
Tabelas no terminal e `assets/images/forecast-201-validation.svg`.

Interpretação
-------------
Os resultados descrevem sensibilidade ao desenho de avaliação em uma simulação.
Não estimam desempenho para uma empresa real nem tornam folds sobrepostos
independentes.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from statistics import mean, median


SEED = 201
N_OBSERVATIONS = 1460
HORIZON = 28
FINAL_TEST_DAYS = 168
SEASONAL_LAG = 7
OUTPUT = Path(__file__).resolve().parents[2] / "assets/images/forecast-201-validation.svg"


@dataclass(frozen=True)
class Protocol:
    name: str
    window: int | None
    gap: int
    step: int
    refit_every: int = 1


@dataclass(frozen=True)
class Fold:
    protocol: str
    model: str
    origin: int
    mae: float
    wape: float
    bias: float


def make_series() -> tuple[list[date], list[float]]:
    """Gera demanda com mudanças que tornam a escolha de janela substantiva."""
    rng = random.Random(SEED)
    start = date(2022, 1, 3)
    dates = [start + timedelta(days=i) for i in range(N_OBSERVATIONS)]
    weekday = [8, 14, 10, 2, -5, -18, -11]
    events = {220: 42, 411: -38, 705: 55, 990: -46, 1215: 61, 1392: 45}
    values: list[float] = []

    for i, current in enumerate(dates):
        if i < 760:
            level, slope, weekly_scale = 210.0, 0.055, 1.0
        elif i < 1190:
            level, slope, weekly_scale = 278.0, -0.018, 1.35
        else:
            level, slope, weekly_scale = 238.0, 0.082, 0.82
        local_i = i if i < 760 else i - (760 if i < 1190 else 1190)
        annual = 17 * math.sin(2 * math.pi * i / 365.25)
        noise = rng.gauss(0, 11.5)
        value = (
            level
            + slope * local_i
            + weekly_scale * weekday[current.weekday()]
            + annual
            + events.get(i, 0)
            + noise
        )
        values.append(max(value, 1.0))
    return dates, values


def calendar_features(current: date, reference: date) -> list[float]:
    """Cria atributos conhecidos na origem: tendência, calendário e harmônicos."""
    elapsed = (current - reference).days / 365.25
    weekday = [1.0 if current.weekday() == day else 0.0 for day in range(1, 7)]
    angle = 2 * math.pi * elapsed
    return [1.0, elapsed, *weekday, math.sin(angle), math.cos(angle)]


def solve_linear(rows: list[list[float]], target: list[float]) -> list[float]:
    """Resolve mínimos quadrados com regularização diagonal numérica."""
    width = len(rows[0])
    matrix = [
        [sum(row[i] * row[j] for row in rows) for j in range(width)]
        for i in range(width)
    ]
    vector = [sum(row[i] * value for row, value in zip(rows, target)) for i in range(width)]
    scale = max(matrix[i][i] for i in range(width))
    for i in range(width):
        matrix[i][i] += scale * 1e-9

    for pivot in range(width):
        best = max(range(pivot, width), key=lambda row: abs(matrix[row][pivot]))
        matrix[pivot], matrix[best] = matrix[best], matrix[pivot]
        vector[pivot], vector[best] = vector[best], vector[pivot]
        divisor = matrix[pivot][pivot]
        if abs(divisor) < 1e-12:
            raise ValueError("Matriz singular.")
        for column in range(pivot, width):
            matrix[pivot][column] /= divisor
        vector[pivot] /= divisor
        for row in range(width):
            if row == pivot:
                continue
            factor = matrix[row][pivot]
            for column in range(pivot, width):
                matrix[row][column] -= factor * matrix[pivot][column]
            vector[row] -= factor * vector[pivot]
    return vector


def fit_calendar(
    dates: list[date], values: list[float], start: int, end: int
) -> tuple[list[float], date]:
    """Ajusta a regressão exclusivamente em [start, end)."""
    reference = dates[start]
    rows = [calendar_features(dates[i], reference) for i in range(start, end)]
    return solve_linear(rows, values[start:end]), reference


def predict_calendar(
    coefficients: list[float], reference: date, future: list[date]
) -> list[float]:
    return [
        max(0.0, sum(x * beta for x, beta in zip(calendar_features(day, reference), coefficients)))
        for day in future
    ]


def seasonal_naive(values: list[float], train_end: int, horizon: int) -> list[float]:
    season = values[train_end - SEASONAL_LAG : train_end]
    return [season[h % SEASONAL_LAG] for h in range(horizon)]


def seasonal_mean(
    dates: list[date], values: list[float], train_start: int, train_end: int, future: list[date]
) -> list[float]:
    buckets = {
        weekday: [
            values[i]
            for i in range(train_start, train_end)
            if dates[i].weekday() == weekday
        ]
        for weekday in range(7)
    }
    return [mean(buckets[day.weekday()]) for day in future]


def metrics(actual: list[float], predicted: list[float]) -> tuple[float, float, float]:
    errors = [p - y for p, y in zip(predicted, actual)]
    absolute = [abs(error) for error in errors]
    volume = sum(abs(value) for value in actual)
    return mean(absolute), 100 * sum(absolute) / volume, 100 * sum(errors) / volume


def origins_for(protocol: Protocol, development_end: int, folds: int = 10) -> list[int]:
    """Retorna origens cujos testes terminam dentro do desenvolvimento."""
    latest = development_end - protocol.gap - HORIZON
    origins = [latest - protocol.step * offset for offset in reversed(range(folds))]
    minimum = 420 if protocol.window is None else protocol.window
    return [origin for origin in origins if origin >= minimum]


def run_protocol(
    dates: list[date],
    values: list[float],
    development_end: int,
    protocol: Protocol,
    folds: int = 10,
) -> list[Fold]:
    """Executa um protocolo sem permitir acesso ao teste final."""
    results: list[Fold] = []
    cached_fit: tuple[list[float], date] | None = None

    for fold_number, origin in enumerate(origins_for(protocol, development_end, folds)):
        train_start = 0 if protocol.window is None else origin - protocol.window
        test_start = origin + protocol.gap
        test_end = test_start + HORIZON
        future_dates = dates[test_start:test_end]
        actual = values[test_start:test_end]

        predictions = {
            "Seasonal naive": seasonal_naive(values, origin, HORIZON),
            "Média sazonal": seasonal_mean(
                dates, values, train_start, origin, future_dates
            ),
        }
        if cached_fit is None or fold_number % protocol.refit_every == 0:
            cached_fit = fit_calendar(dates, values, train_start, origin)
        predictions["Regressão de calendário"] = predict_calendar(
            cached_fit[0], cached_fit[1], future_dates
        )

        for model, forecast in predictions.items():
            mae, wape, bias = metrics(actual, forecast)
            results.append(Fold(protocol.name, model, origin, mae, wape, bias))
    return results


def summarize(results: list[Fold]) -> dict[tuple[str, str], dict[str, float]]:
    grouped: dict[tuple[str, str], list[Fold]] = {}
    for row in results:
        grouped.setdefault((row.protocol, row.model), []).append(row)
    return {
        key: {
            "MAE": mean(row.mae for row in rows),
            "WAPE": mean(row.wape for row in rows),
            "MEDIAN_WAPE": median(row.wape for row in rows),
            "BIAS": mean(row.bias for row in rows),
            "FOLDS": float(len(rows)),
        }
        for key, rows in grouped.items()
    }


def protocol_grid() -> list[Protocol]:
    """Varia uma dimensão por vez em torno do protocolo de referência."""
    return [
        Protocol("Expansiva", None, 0, 28),
        Protocol("Deslizante 365d", 365, 0, 28),
        Protocol("Deslizante 180d", 180, 0, 28),
        Protocol("Gap 7d", 365, 7, 28),
        Protocol("Gap 14d", 365, 14, 28),
        Protocol("Sobreposição 50%", 365, 0, 14),
        Protocol("Sobreposição 75%", 365, 0, 7),
        Protocol("Refit a cada 2 origens", 365, 0, 28, 2),
        Protocol("Refit a cada 4 origens", 365, 0, 28, 4),
    ]


def winner_by_protocol(summary: dict[tuple[str, str], dict[str, float]]) -> dict[str, str]:
    protocols = sorted({key[0] for key in summary})
    return {
        protocol: min(
            (key for key in summary if key[0] == protocol),
            key=lambda key: summary[key]["WAPE"],
        )[1]
        for protocol in protocols
    }


def nested_validation(
    dates: list[date], values: list[float], development_end: int
) -> tuple[list[dict[str, float | int]], dict[int, int]]:
    """Seleciona a janela em folds internos e avalia origens externas."""
    windows = [180, 365, 730]
    outer_origins = list(range(development_end - 4 * 56, development_end, 56))
    records: list[dict[str, float | int]] = []
    selected: dict[int, int] = {}

    for outer_origin in outer_origins:
        inner_scores: dict[int, float] = {}
        for window in windows:
            protocol = Protocol(f"inner-{window}", window, 0, 28)
            inner = run_protocol(dates, values, outer_origin, protocol, folds=4)
            candidate = [row.wape for row in inner if row.model == "Regressão de calendário"]
            inner_scores[window] = mean(candidate)
        best_window = min(inner_scores, key=inner_scores.get)
        selected[outer_origin] = best_window

        train_start = outer_origin - best_window
        coefficients, reference = fit_calendar(dates, values, train_start, outer_origin)
        future = dates[outer_origin : outer_origin + HORIZON]
        forecast = predict_calendar(coefficients, reference, future)
        mae, wape, bias = metrics(values[outer_origin : outer_origin + HORIZON], forecast)
        records.append(
            {
                "origin": outer_origin,
                "window": best_window,
                "mae": mae,
                "wape": wape,
                "bias": bias,
            }
        )
    return records, selected


def locked_final_test(
    dates: list[date],
    values: list[float],
    development_end: int,
    window: int,
) -> dict[str, dict[str, float]]:
    """Avalia origens não sobrepostas no teste final, após congelar a janela."""
    rows: dict[str, list[tuple[float, float, float]]] = {
        "Seasonal naive": [],
        "Média sazonal": [],
        "Regressão de calendário": [],
    }
    for origin in range(development_end, len(values) - HORIZON + 1, HORIZON):
        train_start = max(0, origin - window)
        future = dates[origin : origin + HORIZON]
        actual = values[origin : origin + HORIZON]
        coefficients, reference = fit_calendar(dates, values, train_start, origin)
        forecasts = {
            "Seasonal naive": seasonal_naive(values, origin, HORIZON),
            "Média sazonal": seasonal_mean(dates, values, train_start, origin, future),
            "Regressão de calendário": predict_calendar(coefficients, reference, future),
        }
        for model, forecast in forecasts.items():
            rows[model].append(metrics(actual, forecast))
    return {
        model: {
            "MAE": mean(item[0] for item in scores),
            "WAPE": mean(item[1] for item in scores),
            "BIAS": mean(item[2] for item in scores),
            "FOLDS": float(len(scores)),
        }
        for model, scores in rows.items()
    }


def svg_chart(summary: dict[tuple[str, str], dict[str, float]]) -> None:
    """Cria gráfico vetorial da sensibilidade do WAPE ao protocolo."""
    protocols = [protocol.name for protocol in protocol_grid()]
    models = ["Seasonal naive", "Média sazonal", "Regressão de calendário"]
    colors = {"Seasonal naive": "#22201d", "Média sazonal": "#b4492c", "Regressão de calendário": "#c59622"}
    width, height = 1180, 620
    left, top, plot_width, plot_height = 90, 70, 1010, 410
    max_value = max(summary[(p, m)]["WAPE"] for p in protocols for m in models) * 1.12

    def x(index: int) -> float:
        return left + index * plot_width / (len(protocols) - 1)

    def y(value: float) -> float:
        return top + plot_height * (1 - value / max_value)

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f3eedf"/>',
        '<text x="90" y="35" font-family="Georgia,serif" font-size="24" fill="#22201d">WAPE estimado por protocolo de validação</text>',
    ]
    for tick in range(0, math.ceil(max_value) + 1, 2):
        yy = y(tick)
        elements.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{left+plot_width}" y2="{yy:.1f}" stroke="#d7cfbb"/>')
        elements.append(f'<text x="{left-12}" y="{yy+5:.1f}" text-anchor="end" font-family="Arial" font-size="13" fill="#625d54">{tick}%</text>')
    for model in models:
        points = " ".join(f"{x(i):.1f},{y(summary[(p, model)]['WAPE']):.1f}" for i, p in enumerate(protocols))
        elements.append(f'<polyline points="{points}" fill="none" stroke="{colors[model]}" stroke-width="3"/>')
        for i, protocol in enumerate(protocols):
            elements.append(f'<circle cx="{x(i):.1f}" cy="{y(summary[(protocol, model)]["WAPE"]):.1f}" r="4" fill="{colors[model]}"/>')
    for i, protocol in enumerate(protocols):
        label = protocol.replace("Deslizante ", "Janela ").replace("Sobreposição ", "Sobrep. ")
        elements.append(f'<text x="{x(i):.1f}" y="505" transform="rotate(35 {x(i):.1f} 505)" font-family="Arial" font-size="12" fill="#403c36">{label}</text>')
    for i, model in enumerate(models):
        xx = 90 + i * 270
        elements.append(f'<line x1="{xx}" y1="590" x2="{xx+28}" y2="590" stroke="{colors[model]}" stroke-width="4"/>')
        elements.append(f'<text x="{xx+36}" y="595" font-family="Arial" font-size="14" fill="#22201d">{model}</text>')
    elements.append("</svg>")
    OUTPUT.write_text("\n".join(elements), encoding="utf-8")


def main() -> None:
    dates, values = make_series()
    development_end = len(values) - FINAL_TEST_DAYS
    all_results = [
        row
        for protocol in protocol_grid()
        for row in run_protocol(dates, values, development_end, protocol)
    ]
    summary = summarize(all_results)
    winners = winner_by_protocol(summary)
    nested, selected = nested_validation(dates, values, development_end)
    final_window = int(median(selected.values()))
    final = locked_final_test(dates, values, development_end, final_window)
    svg_chart(summary)

    print(f"Forecast 201 | desenvolvimento={development_end} dias | teste final={FINAL_TEST_DAYS} dias")
    print(f"Horizonte={HORIZON} | série sintética | seed={SEED}\n")
    print("WAPE médio por protocolo")
    print(f"{'Protocolo':28} {'SNaive':>9} {'Média':>9} {'Regressão':>10}  Vencedor")
    for protocol in protocol_grid():
        print(
            f"{protocol.name:28} "
            f"{summary[(protocol.name, 'Seasonal naive')]['WAPE']:8.2f}% "
            f"{summary[(protocol.name, 'Média sazonal')]['WAPE']:8.2f}% "
            f"{summary[(protocol.name, 'Regressão de calendário')]['WAPE']:9.2f}%  "
            f"{winners[protocol.name]}"
        )
    print("\nValidação aninhada da janela da regressão")
    for row in nested:
        print(
            f"origem={int(row['origin']):4d} janela={int(row['window']):3d} "
            f"WAPE externo={row['wape']:.2f}%"
        )
    print(f"Janela congelada para o teste final: {final_window} dias\n")
    print("Teste final bloqueado")
    for model, values_ in final.items():
        print(
            f"{model:26} MAE={values_['MAE']:.2f} "
            f"WAPE={values_['WAPE']:.2f}% viés={values_['BIAS']:.2f}%"
        )


if __name__ == "__main__":
    main()
