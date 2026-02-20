from speechmarkdown.speechmarkdown import SpeechMarkdown


def test_amazon_polly_basic():
    sm = SpeechMarkdown(platform="amazon-polly")
    text = sm.to_ssml("Hello (world) [whisper]")
    assert (
        text
        == '<speak>\nHello <amazon:effect name="whispered">world</amazon:effect>\n</speak>'
    )
