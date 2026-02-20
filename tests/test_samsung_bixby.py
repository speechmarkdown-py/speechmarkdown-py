from speechmarkdown.speechmarkdown import SpeechMarkdown


def test_samsung_bixby_basic():
    sm = SpeechMarkdown(platform="samsung-bixby")
    text = sm.to_ssml("Wait a [1s]")
    assert text == '<speak>\nWait a <break time="1s"/>\n</speak>'


def test_samsung_bixby_whisper():
    sm = SpeechMarkdown(platform="samsung-bixby")
    text = sm.to_ssml("Hello (world) [whisper]")
    # Samsung Bixby uses prosody for whisper
    assert (
        text
        == '<speak>\nHello <prosody volume="x-soft" rate="slow">world</prosody>\n</speak>'
    )
