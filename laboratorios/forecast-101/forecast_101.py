"""Forecast 101: avaliação temporal reproduzível e orientada à decisão.

Objetivo
--------
Comparar dois baselines honestos com uma regressão de calendário em demanda
diária sintética, sem permitir que qualquer previsão acesse o período de teste.

Entradas
--------
Não há arquivos externos. A série tem 730 dias, semente 42, tendência,
sazonalidade semanal, ciclo anual, eventos pontuais e uma mudança moderada de
nível. Os eventos e a mudança não entram no modelo candidato: eles existem para
produzir erros que precisem ser diagnosticados.

Processamento
-------------
1. Executa oito folds de origem móvel, com horizonte de 28 dias.
2. Compara naive, seasonal naive recursivo e regressão de calendário.
3. Mede MAE, RMSE, WAPE, viés, MASE e custo assimétrico.
4. Resume os erros por fold e por bloco de horizonte.
5. Constrói um intervalo de 80% com calibração temporal separada.
6. Diagnostica cobertura, largura, interval score e autocorrelação dos erros.

Saídas
------
Tabelas no terminal e uma figura SVG com o último fold.

Interpretação
-------------
O experimento demonstra avaliação preditiva, não causalidade nem prontidão para
produção. Um candidato só avança se superar baselines, permanecer estável por
horizonte e oferecer erro e incerteza compatíveis com a decisão.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from statistics import mean


SEED = 42
N_OBSERVATIONS = 730
HORIZON = 28
FOLDS = 8
SEASONAL_LAG = 7
CALIBRATION_DAYS = 56
INTERVAL_LEVEL = 0.80
SHORTAGE_COST = 3.0
EXCESS_COST = 1.0
OUTPUT = Path(__file__).resolve().parents[2] / "assets/images/forecast-101-backtest.svg"


@dataclass(frozen=True)
class Metrics:
    mae: float
    rmse: float
    wape_pct: float
    bias_pct: float
    mase: float
    cost_index: float


@dataclass(frozen=True)
class FoldResult:
    fold: int
    model: str
    metrics: Metrics
    coverage_pct: float | None = None
    mean_width: float | None = None
    interval_score: float | None = None


def make_series() -> tuple[list[date], list[float]]:
    """Cria uma série didática com estrutura e falhas de especificação."""
    rng = random.Random(SEED)
    start = date(2024, 1, 1)
    dates = [start + timedelta(days=index) for index in range(N_OBSERVATIONS)]
    weekly_effect = [12, 18, 9, -3, -12, -22, -6]
    event_offsets = {110: 48, 248: -35, 418: 62, 612: 45}
    values: list[float] = []

    for index, current in enumerate(dates):
        trend = 0.13 * index
        weekly = weekly_effect[current.weekday()]
        annual = 18 * math.sin(2 * math.pi * index / 365.25)
        level_shift = 16 if index >= 540 else 0
        event = event_offsets.get(index, 0)
        noise = rng.gauss(0, 12.9)
        values.append(max(0.0, 220 + trend + weekly + annual + level_shift + event + noise))
    return dates, values


def features(current: date, origin: date) -> list[float]:
    """Retorna apenas atributos conhecidos antes da origem da previsão."""
    elapsed_years = (current - origin).days / 365.25
    weekday = [1.0 if current.weekday() == day else 0.0 for day in range(1, 7)]
    angle = 2 * math.pi * elapsed_years
    return [1.0, elapsed_years, *weekday, math.sin(angle), math.cos(angle)]


def solve_linear(rows: list[list[float]], target: list[float]) -> list[float]:
    """Resolve mínimos quadrados com estabilização diagonal pequena."""
    width = len(rows[0])
    matrix = [
        [sum(row[i] * row[j] for row in rows) for j in range(width)]
        for i in range(width)
    ]
    vector = [sum(row[i] * value for row, value in zip(rows, target)) for i in range(width)]

    scale = max(matrix[index][index] for index in range(width))
    for index in range(width):
        matrix[index][index] += scale * 1e-10

    for pivot in range(width):
        best = max(range(pivot, width), key=lambda row: abs(matrix[row][pivot]))
        matrix[pivot], matrix[best] = matrix[best], matrix[pivot]
        vector[pivot], vector[best] = vector[best], vector[pivot]
        divisor = matrix[pivot][pivot]
        if abs(divisor) < 1e-12:
            raise ValueError("Matriz singular no ajuste da regressão.")
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
    train_dates: list[date],
    train_values: list[float],
) -> tuple[list[float], date]:
    """Ajusta a regressão de calendário e retorna coeficientes e origem."""
    origin = train_dates[0]
    coefficients = solve_linear(
        [features(current, origin) for current in train_dates],
        train_values,
    )
    return coefficients, origin


def predict_calendar(
    coefficients: list[float],
    origin: date,
    future_dates: list[date],
) -> list[float]:
    """Gera previsões sem consultar valores futuros do alvo."""
    return [
        max(
            0.0,
            sum(
                value * coefficient
                for value, coefficient in zip(features(current, origin), coefficients)
            ),
        )
        for current in future_dates
    ]


def naive_forecast(train_values: list[float], horizon: int) -> list[float]:
    """Repete o último valor conhecido em todos os passos."""
    return [train_values[-1]] * horizon


def seasonal_naive_forecast(
    train_values: list[float],
    horizon: int,
    period: int = SEASONAL_LAG,
) -> list[float]:
    """Repete recursivamente a última semana, sem acessar o teste."""
    last_season = train_values[-period:]
    return [last_season[step % period] for step in range(horizon)]


def seasonal_scale(train_values: list[float], period: int = SEASONAL_LAG) -> float:
    """Calcula a escala do MASE usando diferenças sazonais do treino."""
    differences = [
        abs(train_values[index] - train_values[index - period])
        for index in range(period, len(train_values))
    ]
    return mean(differences)


def calculate_metrics(
    actual: list[float],
    forecast: list[float],
    scale: float,
) -> Metrics:
    """Calcula magnitude, direção, escala relativa e custo de decisão."""
    errors = [prediction - observed for prediction, observed in zip(forecast, actual)]
    absolute_errors = [abs(error) for error in errors]
    squared_errors = [error**2 for error in errors]
    shortage = sum(max(observed - prediction, 0.0) for observed, prediction in zip(actual, forecast))
    excess = sum(max(prediction - observed, 0.0) for observed, prediction in zip(actual, forecast))
    volume = sum(abs(value) for value in actual)
    return Metrics(
        mae=mean(absolute_errors),
        rmse=math.sqrt(mean(squared_errors)),
        wape_pct=100 * sum(absolute_errors) / volume,
        bias_pct=100 * sum(errors) / volume,
        mase=mean(absolute_errors) / scale,
        cost_index=100 * (SHORTAGE_COST * shortage + EXCESS_COST * excess) / volume,
    )


def temporal_calibration(
    train_dates: list[date],
    train_values: list[float],
) -> float:
    """Estima o raio do intervalo em um bloco temporal fora do ajuste."""
    fit_dates = train_dates[:-CALIBRATION_DAYS]
    fit_values = train_values[:-CALIBRATION_DAYS]
    calibration_dates = train_dates[-CALIBRATION_DAYS:]
    calibration_values = train_values[-CALIBRATION_DAYS:]
    coefficients, origin = fit_calendar(fit_dates, fit_values)
    predictions = predict_calendar(coefficients, origin, calibration_dates)
    residuals = sorted(
        abs(actual - prediction)
        for actual, prediction in zip(calibration_values, predictions)
    )
    rank = min(
        len(residuals) - 1,
        math.ceil((len(residuals) + 1) * INTERVAL_LEVEL) - 1,
    )
    return residuals[rank]


def interval_diagnostics(
    actual: list[float],
    lower: list[float],
    upper: list[float],
) -> tuple[float, float, float]:
    """Avalia cobertura, largura e interval score de Winkler."""
    alpha = 1 - INTERVAL_LEVEL
    covered = 0
    widths: list[float] = []
    scores: list[float] = []
    for observed, low, high in zip(actual, lower, upper):
        width = high - low
        score = width
        if observed < low:
            score += (2 / alpha) * (low - observed)
        elif observed > high:
            score += (2 / alpha) * (observed - high)
        else:
            covered += 1
        widths.append(width)
        scores.append(score)
    return 100 * covered / len(actual), mean(widths), mean(scores)


def autocorrelation(values: list[float], lag: int) -> float:
    """Calcula autocorrelação amostral para um lag informado."""
    if len(values) <= lag:
        return float("nan")
    center = mean(values)
    denominator = sum((value - center) ** 2 for value in values)
    if denominator == 0:
        return 0.0
    numerator = sum(
        (values[index] - center) * (values[index - lag] - center)
        for index in range(lag, len(values))
    )
    return numerator / denominator


def run_backtest(
    dates: list[date],
    values: list[float],
) -> tuple[list[FoldResult], dict[str, object], dict[str, list[float]]]:
    """Executa oito origens móveis e preserva erros por modelo e horizonte."""
    results: list[FoldResult] = []
    errors_by_model: dict[str, list[float]] = {
        "Naive": [],
        "Seasonal naive": [],
        "Regressão de calendário": [],
    }
    horizon_errors: dict[str, list[float]] = {
        "h01-07": [],
        "h08-14": [],
        "h15-21": [],
        "h22-28": [],
    }
    last_fold: dict[str, object] = {}
    first_test_start = N_OBSERVATIONS - FOLDS * HORIZON

    for fold in range(FOLDS):
        train_end = first_test_start + fold * HORIZON
        test_end = train_end + HORIZON
        train_dates = dates[:train_end]
        train_values = values[:train_end]
        test_dates = dates[train_end:test_end]
        actual = values[train_end:test_end]
        scale = seasonal_scale(train_values)

        forecasts = {
            "Naive": naive_forecast(train_values, HORIZON),
            "Seasonal naive": seasonal_naive_forecast(train_values, HORIZON),
        }
        coefficients, origin = fit_calendar(train_dates, train_values)
        forecasts["Regressão de calendário"] = predict_calendar(
            coefficients,
            origin,
            test_dates,
        )

        interval_radius = temporal_calibration(train_dates, train_values)
        candidate = forecasts["Regressão de calendário"]
        lower = [max(0.0, prediction - interval_radius) for prediction in candidate]
        upper = [prediction + interval_radius for prediction in candidate]
        coverage, mean_width, interval_score = interval_diagnostics(actual, lower, upper)

        for model, forecast in forecasts.items():
            model_errors = [
                prediction - observed
                for prediction, observed in zip(forecast, actual)
            ]
            errors_by_model[model].extend(model_errors)
            model_metrics = calculate_metrics(actual, forecast, scale)
            results.append(
                FoldResult(
                    fold=fold + 1,
                    model=model,
                    metrics=model_metrics,
                    coverage_pct=coverage if model == "Regressão de calendário" else None,
                    mean_width=mean_width if model == "Regressão de calendário" else None,
                    interval_score=interval_score if model == "Regressão de calendário" else None,
                )
            )

        for block, start in zip(horizon_errors, range(0, HORIZON, 7)):
            horizon_errors[block].extend(
                candidate[index] - actual[index]
                for index in range(start, start + 7)
            )

        if fold == FOLDS - 1:
            last_fold = {
                "dates": test_dates,
                "actual": actual,
                "naive": forecasts["Naive"],
                "seasonal_naive": forecasts["Seasonal naive"],
                "calendar": candidate,
                "lower": lower,
                "upper": upper,
            }

    return results, last_fold, {**errors_by_model, **horizon_errors}


def summarize(results: list[FoldResult]) -> dict[str, dict[str, float]]:
    """Agrega métricas por modelo sem ocultar a dispersão entre folds."""
    summary: dict[str, dict[str, float]] = {}
    models = sorted({result.model for result in results})
    for model in models:
        selected = [result for result in results if result.model == model]
        wapes = [result.metrics.wape_pct for result in selected]
        summary[model] = {
            "MAE": mean(result.metrics.mae for result in selected),
            "RMSE": mean(result.metrics.rmse for result in selected),
            "WAPE": mean(wapes),
            "WAPE_min": min(wapes),
            "WAPE_max": max(wapes),
            "Bias": mean(result.metrics.bias_pct for result in selected),
            "MASE": mean(result.metrics.mase for result in selected),
            "Cost": mean(result.metrics.cost_index for result in selected),
        }
        coverages = [
            result.coverage_pct
            for result in selected
            if result.coverage_pct is not None
        ]
        if coverages:
            summary[model]["Coverage"] = mean(coverages)
            summary[model]["Width"] = mean(
                result.mean_width
                for result in selected
                if result.mean_width is not None
            )
            summary[model]["IntervalScore"] = mean(
                result.interval_score
                for result in selected
                if result.interval_score is not None
            )
    return summary


def print_report(
    results: list[FoldResult],
    diagnostics: dict[str, list[float]],
) -> None:
    """Imprime tabelas reproduzíveis para revisão do artigo."""
    summary = summarize(results)
    print(
        "Forecast 101 | série sintética | seed=42 | "
        f"folds={FOLDS} | horizonte={HORIZON}"
    )
    print(
        f"Função de custo: falta={SHORTAGE_COST:.0f}x | "
        f"excesso={EXCESS_COST:.0f}x\n"
    )
    print("Resumo por modelo")
    print(
        "Modelo                         MAE   RMSE   WAPE  faixa WAPE       "
        "Viés   MASE  Custo"
    )
    for model, values in summary.items():
        print(
            f"{model:<29} {values['MAE']:>5.2f} {values['RMSE']:>6.2f} "
            f"{values['WAPE']:>6.2f}% "
            f"[{values['WAPE_min']:.2f}, {values['WAPE_max']:.2f}]% "
            f"{values['Bias']:>6.2f}% {values['MASE']:>6.2f} "
            f"{values['Cost']:>6.2f}"
        )

    candidate = summary["Regressão de calendário"]
    print("\nDiagnóstico probabilístico do candidato")
    print(
        f"Cobertura 80%={candidate['Coverage']:.2f}% | "
        f"largura média={candidate['Width']:.2f} | "
        f"interval score={candidate['IntervalScore']:.2f}"
    )
    candidate_errors = diagnostics["Regressão de calendário"]
    print(
        f"ACF dos erros: lag 1={autocorrelation(candidate_errors, 1):.3f} | "
        f"lag 7={autocorrelation(candidate_errors, 7):.3f}"
    )

    print("\nErro do candidato por bloco de horizonte")
    print("Bloco      MAE    Viés")
    for block in ("h01-07", "h08-14", "h15-21", "h22-28"):
        errors = diagnostics[block]
        print(f"{block:<8} {mean(abs(error) for error in errors):>6.2f} {mean(errors):>7.2f}")


def write_svg(fold: dict[str, object]) -> None:
    """Salva o último fold em SVG acessível e coerente com o site."""
    dates = fold["dates"]
    series = [
        fold["actual"],
        fold["seasonal_naive"],
        fold["calendar"],
        fold["lower"],
        fold["upper"],
    ]
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
        points = " ".join(point(index, value) for index, value in enumerate(values))
        return (
            f'<polyline points="{points}" fill="none" stroke="{color}" '
            f'stroke-width="3"{style}/>'
        )

    band_points = " ".join(
        point(index, value) for index, value in enumerate(fold["lower"])
    )
    band_points += " " + " ".join(
        reversed(
            [
                point(index, value)
                for index, value in enumerate(fold["upper"])
            ]
        )
    )
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        'role="img" aria-labelledby="title desc">',
        '<title id="title">Backtest do último fold de 28 dias</title>',
        '<desc id="desc">Demanda observada, seasonal naive recursivo, regressão '
        'de calendário e intervalo de 80 por cento com calibração temporal.</desc>',
        '<rect width="100%" height="100%" fill="#f8f3e8"/>',
        '<text x="72" y="30" font-family="Georgia, serif" font-size="21" '
        'fill="#171612">Último fold · sem acesso ao futuro · horizonte de 28 dias</text>',
    ]
    for tick in range(0, HORIZON, 7):
        x = left + tick * plot_width / (HORIZON - 1)
        svg.append(
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" '
            f'y2="{height-bottom}" stroke="#171612" opacity=".12"/>'
        )
        svg.append(
            f'<text x="{x:.1f}" y="{height-28}" text-anchor="middle" '
            f'font-family="monospace" font-size="12" fill="#656057">'
            f'{dates[tick].strftime("%d/%m")}</text>'
        )
    svg += [
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" '
        'stroke="#171612"/>',
        f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" '
        f'y2="{height-bottom}" stroke="#171612"/>',
        f'<polygon points="{band_points}" fill="#e3cf79" opacity=".55"/>',
        polyline(fold["seasonal_naive"], "#656057", "7 6"),
        polyline(fold["calendar"], "#a43a2b"),
        polyline(fold["actual"], "#171612"),
        '<g font-family="monospace" font-size="12" fill="#171612">'
        '<text x="660" y="30">observado</text>'
        '<text x="750" y="30" fill="#a43a2b">modelo</text>'
        '<text x="830" y="30" fill="#656057">s-naive</text></g>',
        "</svg>",
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    """Executa o estudo completo e atualiza a evidência visual."""
    dates, values = make_series()
    results, last_fold, diagnostics = run_backtest(dates, values)
    print_report(results, diagnostics)
    write_svg(last_fold)


if __name__ == "__main__":
    main()
