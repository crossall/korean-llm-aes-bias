from korean_llm_aes.metrics import quadratic_weighted_kappa


def test_qwk_perfect_agreement():
    y = [1, 2, 3, 4, 4]
    assert quadratic_weighted_kappa(y, y, 1, 4) == 1.0


def test_qwk_runs_on_disagreement():
    val = quadratic_weighted_kappa([1, 2, 3, 4], [4, 3, 2, 1], 1, 4)
    assert val < 1.0
