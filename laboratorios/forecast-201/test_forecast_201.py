"""Testes de segurança metodológica do Forecast 201."""

import unittest

import forecast_201 as study


class Forecast201Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dates, cls.values = study.make_series()
        cls.development_end = len(cls.values) - study.FINAL_TEST_DAYS

    def test_development_never_reaches_locked_test(self) -> None:
        for protocol in study.protocol_grid():
            for origin in study.origins_for(protocol, self.development_end):
                self.assertLessEqual(
                    origin + protocol.gap + study.HORIZON,
                    self.development_end,
                )

    def test_gap_changes_test_start_not_training_end(self) -> None:
        origin = 1000
        window = 365
        no_gap = study.Protocol("sem gap", window, 0, 28)
        gap = study.Protocol("gap", window, 14, 28)
        self.assertEqual(origin - no_gap.window, origin - gap.window)
        self.assertEqual(origin + gap.gap, origin + no_gap.gap + 14)
        self.assertEqual(
            origin + gap.gap + study.HORIZON,
            origin + no_gap.gap + study.HORIZON + 14,
        )

    def test_overlapping_protocol_has_more_dependent_folds(self) -> None:
        non_overlap = study.Protocol("não sobreposto", 365, 0, 28)
        overlap = study.Protocol("sobreposto", 365, 0, 7)
        non_origins = study.origins_for(non_overlap, self.development_end)
        overlap_origins = study.origins_for(overlap, self.development_end)
        self.assertEqual(non_origins[1] - non_origins[0], study.HORIZON)
        self.assertLess(overlap_origins[1] - overlap_origins[0], study.HORIZON)

    def test_nested_selection_uses_only_pre_outer_data(self) -> None:
        records, selected = study.nested_validation(
            self.dates, self.values, self.development_end
        )
        self.assertEqual(len(records), len(selected))
        self.assertTrue(all(origin < self.development_end for origin in selected))
        self.assertTrue(all(window in {180, 365, 730} for window in selected.values()))

    def test_final_test_has_six_non_overlapping_folds(self) -> None:
        final = study.locked_final_test(
            self.dates, self.values, self.development_end, 365
        )
        self.assertEqual(final["Regressão de calendário"]["FOLDS"], 6.0)
        self.assertEqual(set(final), {"Seasonal naive", "Média sazonal", "Regressão de calendário"})


if __name__ == "__main__":
    unittest.main()
