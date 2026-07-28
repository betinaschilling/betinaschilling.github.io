"""Testes de segurança metodológica para o laboratório Forecast 101."""

import unittest

import forecast_101 as study


class Forecast101Tests(unittest.TestCase):
    def test_seasonal_naive_uses_only_known_season(self) -> None:
        train = [float(value) for value in range(30)]
        forecast = study.seasonal_naive_forecast(train, horizon=15, period=7)
        self.assertEqual(forecast[:7], train[-7:])
        self.assertEqual(forecast[7:14], train[-7:])
        self.assertEqual(forecast[14], train[-7])

    def test_backtest_produces_all_models_and_folds(self) -> None:
        dates, values = study.make_series()
        results, last_fold, diagnostics = study.run_backtest(dates, values)
        self.assertEqual(len(results), study.FOLDS * 3)
        self.assertEqual(len(last_fold["actual"]), study.HORIZON)
        self.assertEqual(
            len(diagnostics["Regressão de calendário"]),
            study.FOLDS * study.HORIZON,
        )

    def test_candidate_metrics_match_published_rounding(self) -> None:
        dates, values = study.make_series()
        results, _, _ = study.run_backtest(dates, values)
        summary = study.summarize(results)["Regressão de calendário"]
        self.assertEqual(round(summary["WAPE"], 2), 4.05)
        self.assertEqual(round(summary["Bias"], 2), -2.53)
        self.assertEqual(round(summary["Coverage"], 2), 82.14)

    def test_interval_bounds_are_ordered(self) -> None:
        dates, values = study.make_series()
        _, last_fold, _ = study.run_backtest(dates, values)
        self.assertTrue(
            all(
                low <= prediction <= high
                for low, prediction, high in zip(
                    last_fold["lower"],
                    last_fold["calendar"],
                    last_fold["upper"],
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
