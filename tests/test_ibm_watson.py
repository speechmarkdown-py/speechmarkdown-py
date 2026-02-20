from speechmarkdown.speechmarkdown import SpeechMarkdown


def test_ibm_basic():
    sm = SpeechMarkdown(platform="ibm-watson")
    text = sm.to_ssml("Hello (world) [whisper]")
    # whisper is disabled in IBM Watson, so it just returns the text
    # without whispering
    assert text == "<speak>\nHello world\n</speak>"
