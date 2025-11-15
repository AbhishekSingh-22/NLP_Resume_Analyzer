from src.text_extraction import clean_text
def test_clean_text_basic():
    raw = " Hello\n\nWorld \n"
    assert clean_text(raw) == "Hello\nWorld"
