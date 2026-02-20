from speechmarkdown.speechmarkdown import SpeechMarkdown


def test_alexa_basic():
    sm = SpeechMarkdown(platform="amazon-alexa")
    text = sm.to_ssml("Hello (world) [whisper]")
    assert (
        text
        == '<speak>\nHello <amazon:effect name="whispered">world</amazon:effect>\n</speak>'
    )


def test_alexa_escape_attributes():
    sm = SpeechMarkdown(platform="amazon-alexa")
    text = sm.to_ssml("Hello (world) {&<>\"'}")
    assert (
        text
        == '<speak>\nHello <sub alias="&amp;&lt;&gt;&quot;&apos;">world</sub>\n</speak>'
    )
