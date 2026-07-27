"""Forecast 101: um experimento didático de previsão de demanda diária.

Objetivo
--------
Comparar um baseline seasonal naive (lag 7) com uma regressão linear de
calendário em uma série sintética. O experimento mostra como um backtest com
origem móvel transforma uma previsão em evidência para uma decisão.

Entradas
--------
Não há arquivos de entrada. A demanda é gerada de forma determinística com
730 observações diárias, semente aleatória 42, e contém tendência, sazonalidade
semanal, ciclo anual e ruído.

Processamento
-------------
São avaliados três folds de 28 dias usando janela expansiva. O candidato usa
tendência, dia da semana, seno anual e cosseno anual. O intervalo empírico de
80% usa os resíduos do treino do modelo candidato.

Saídas
------
O programa imprime as métricas MAE, WAPE, viés e cobertura do intervalo e
salva `assets/images/forecast-101-backtest.svg`, com o último fold.

Interpretação
-------------
Os dados são sintéticos e o modelo não está pronto para produção. O exercício
mede associação preditiva fora da amostra; não estima efeitos causais.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


SEED = 42
N_OBSERVATIONS = 730
HORIZON = 28
FOLDS = 3
SEASONAL_LAG = 7
OUTPUT = Path(__file__).resolve().parents[2] / "assets/images/forecast-101-backtest.svg"


@dataclass
class FoldResult:
    name: str
    mae: float
    wape: float
    bias: float
    coverage: float | None = None


def make_series() -> tuple[list[date], list[float]]:
    """Create the didactic daily demand series without external data."""
    rng = random.Random(SEED)
    start = date(2024, 1, 1)
    dates = [start + timedelta(days=i) for i in range(N_OBSERVATIONS)]
    values = []
    weekly_effect = [12, 18, 9, -3, -12, -22, -6]
    for t, current in enumerate(dates):
        trend = 0.13 * t
        weekly = weekly_effect[current.weekday()]
        annual = 18 * math.sin(2 * math.pi * t / 365.25)
        noise = rng.gauss(0, 12.9)
        values.append(220 + trend + weekly + annual + noise)
    return dates, values


def features(current: date, origin: date) -> list[float]:
    """Calendar design row: intercept, trend, weekday dummies, annual cycle."""
    elapsed = (current - origin).days
    weekday = [1.0 if current.weekday() == day else 0.0 for day in range(1, 7)]
    angle = 2 * math.pi * elapsed / 365.25
    return [1.0, elapsed, *weekday, math.sin(angle), math.cos(angle)]


def solve_linear(rows: list[list[float]], target: list[float]) -> list[float]:
    """Solve ordinary least squares using Gaussian elimination."""
    width = len(rows[0])
    matrix = [[sum(row[i] * row[j] for row in rows) for j in range(width)] for i in range(width)]
    vector = [sum(row[i] * y for row, y in zip(rows, target)) for i in range(width)]
    for pivot in range(width):
        best = max(range(pivot, width), key=lambda row: abs(matrix[row][pivot]))
        matrix[pivot], matrix[best] = matrix[best], matrix[pivot]
        vector[pivot], vector[best] = vector[best], vector[pivot]
        divisor = matrix[pivot][pivot]
        for col in range(pivot, width):
            matrix[pivot][col] /= divisor
        vector[pivot] /= divisor
        for row in range(width):
            if row == pivot:
                continue
            factor = matrix[row][pivot]
            for col in range(pivot, width):
                matrix[row][col] -= factor * matrix[pivot][col]
            vector[row] -= factor * vector[pivot]
    return vector


def predict_calendar(train_dates: list[date], train_values: list[float], future_dates: list[date]) -> tuple[list[float], list[float]]:
    origin = train_dates[0]
    coefficients = solve_linear([features(d, origin) for d in train_dates], train_values)
    fitted = [sum(a * b for a, b in zip(features(d, origin), coefficients)) for d in train_dates]
    forecast = [sum(a * b for a, b in zip(features(d, origin), coefficients)) for d in future_dates]
    return forecast, [actual - fitted_value for actual, fitted_value in zip(train_values, fitted)]


def metrics(actual: list[float], forecast: list[float]) -> tuple[float, float, float]:
    errors = [prediction - observed for prediction, observed in zip(forecast, actual)]
    mae = sum(abs(error) for error in errors) / len(errors)
    wape = sum(abs(error) for error in errors) / sum(abs(value) for value in actual)
    bias = sum(errors) / len(errors)
    return mae, wape, bias


def backtest(dates: list[date], values: list[float]) -> tuple[dict[str, list[FoldResult]], dict[str, object]]:
    results: dict[str, list[FoldResult]] = {"Seasonal naive": [], "Regressão de calendário": []}
    last_fold: dict[str, object] = {}
    first_test_start = N_OBSERVATIONS - FOLDS * HORIZON
    for fold in range(FOLDS):
        train_end = first_test_start + fold * HORIZON
        test_end = train_end + HORIZON
        train_dates, train_values = dates[:train_end], values[:train_end]
        test_dates, test_values = dates[train_end:test_end], values[train_end:test_end]

        naive_forecast = values[train_end - SEASONAL_LAG:train_end - SEASONAL_LAG + HORIZON]
        naive_metrics = metrics(test_values, naive_forecast)
        results["Seasonal naive"].append(FoldResult("Seasonal naive", *naive_metrics))

        calendar_forecast, residuals = predict_calendar(train_dates, train_values, test_dates)
        calendar_metrics = metrics(test_values, calendar_forecast)
        quantile = sorted(abs(residual) for residual in residuals)[int(0.80 * len(residuals)) - 1]
        lower = [prediction - quantile for prediction in calendar_forecast]
        upper = [prediction + quantile for prediction in calendar_forecast]
        coverage = sum(low <= observed <= high for low, observed, high in zip(lower, test_values, upper)) / HORIZON
        results["Regressão de calendário"].append(FoldResult("Regressão de calendário", *calendar_metrics, coverage))
        if fold == FOLDS - 1:
            last_fold = {"dates": test_dates, "actual": test_values, "naive": naive_forecast,
                         "calendar": calendar_forecast, "lower": lower, "upper": upper}
    return results, last_fold


def write_svg(fold: dict[str, object]) -> None:
    dates = fold["dates"]
    series = [fold["actual"], fold["naive"], fold["calendar"], fold["lower"], fold["upper"]]
    minimum = min(min(values) for values in series) - 5
    maximum = max(max(values) for values in series) + 5
    width, height = 960, 460
    left, right, top, bottom = 72, 28, 58, 58
    plot_width, plot_height = width - left - right, height - top - bottom

    def point(index: int, value: float) -> str:
        x = left + index * plot_width / (HORIZON - 1)
        y = top + (maximum - value) * plot_height / (maximum - minimum)
        return f"{x:.1f},{y:.1f}"

    def polyline(values: list[float], color: str, dash: str = "") -> str:
        style = f' stroke-dasharray="{dash}"' if dash else ""
        return f'<polyline points="{" ".join(point(i, v) for i, v in enumerate(values))}" fill="none" stroke="{color}" stroke-width="3"{style}/>'

    band_points = " ".join(point(i, v) for i, v in enumerate(fold["lower"]))
    band_points += " " + " ".join(reversed([point(i, v) for i, v in enumerate(fold["upper"])]))
    ticks = range(0, HORIZON, 7)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
           '<title id="title">Backtest do último fold de 28 dias</title>',
           '<desc id="desc">Demanda observada, seasonal naive, regressão de calendário e intervalo empírico de 80 por cento.</desc>',
           '<rect width="100%" height="100%" fill="#f8f3e8"/>',
           '<text x="72" y="30" font-family="Georgia, serif" font-size="21" fill="#171612">Último fold · origem móvel · horizonte de 28 dias</text>']
    for tick in ticks:
        x = left + tick * plot_width / (HORIZON - 1)
        svg.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{height-bottom}" stroke="#171612" opacity=".12"/>')
        svg.append(f'<text x="{x:.1f}" y="{height-28}" text-anchor="middle" font-family="monospace" font-size="12" fill="#656057">{dates[tick].strftime("%d/%m")}</text>')
    svg += [f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#171612"/>',
            f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#171612"/>',
            f'<polygon points="{band_points}" fill="#e3cf79" opacity=".55"/>',
            polyline(fold["naive"], "#656057", "7 6"), polyline(fold["calendar"], "#a43a2b"), polyline(fold["actual"], "#171612"),
            '<g font-family="monospace" font-size="12" fill="#171612"><text x="690" y="30">observado</text><text x="770" y="30" fill="#a43a2b">modelo</text><text x="850" y="30" fill="#656057">naive</text></g>',
            '</svg>']
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    dates, values = make_series()
    results, last_fold = backtest(dates, values)
    write_svg(last_fold)
    print("Forecast 101 | série didática sintética | seed=42 | folds=3 | horizonte=28")
    for name, fold_results in results.items():
        mean_mae = sum(item.mae for item in fold_results) / FOLDS
        mean_wape = sum(item.wape for item in fold_results) / FOLDS
        mean_bias = sum(item.bias for item in fold_results) / FOLDS
        coverage = [item.coverage for item in fold_results if item.coverage is not None]
        coverage_text = f" | cobertura 80% média: {100 * sum(coverage) / len(coverage):.2f}%" if coverage else ""
        print(f"{name}: MAE médio={mean_mae:.2f} | WAPE médio={100 * mean_wape:.2f}% | viés médio={100 * mean_bias / (sum(values) / len(values)):.2f}%{coverage_text}")


if __name__ == "__main__":
    main()
