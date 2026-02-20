from speechmarkdown.speechmarkdown import SpeechMarkdown

def test_text_formatting():
    sm = SpeechMarkdown()
    text = sm.to_text("Hello (world) [whisper]")
    assert text == "Hello world"

def test_plain_text():
    sm = SpeechMarkdown()
    assert sm.to_text("Simply some text.") == "Simply some text."

def test_multiline_text():
    sm = SpeechMarkdown()
    assert sm.to_text("First line\nSecond line\n\nThird paragraph") == "First line\nSecond line\n\nThird paragraph"
