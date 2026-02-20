from speechmarkdown.speechmarkdown import SpeechMarkdown


def test_google_basic():
    sm = SpeechMarkdown(platform="google-assistant")
    text = sm.to_ssml("Hello (world) [whisper]")
    assert (
        text
        == '<speak>\nHello <prosody volume="x-soft" rate="slow">world</prosody>\n</speak>'
    )
