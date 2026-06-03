from korean_llm_aes.features import mattr, simple_korean_tokenize, keyword_density


def test_simple_tokenizer():
    assert simple_korean_tokenize("우리말을 바르게 사용해야 한다.")[:2] == ["우리말을", "바르게"]


def test_mattr_short_text():
    assert mattr(["a", "b", "a"], window=50) == 2 / 3


def test_keyword_density():
    val = keyword_density("구성원 존중 의사소통", "구성원, 존중, 오해, 의사소통")
    assert val > 0
