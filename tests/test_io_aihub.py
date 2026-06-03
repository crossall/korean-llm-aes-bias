from korean_llm_aes.io_aihub import normalize_format, score_pair_to_columns


def test_score_pair_to_columns():
    assert score_pair_to_columns([3, 4]) == (3.0, 4.0, 3.5)


def test_normalize_format():
    assert normalize_format("서술형 글쓰기", None) == "descriptive"
    assert normalize_format("논술형 글쓰기", None) == "essay"
