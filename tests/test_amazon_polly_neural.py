from speechmarkdown.speechmarkdown import SpeechMarkdown

def test_amazon_polly_neural_basic():
    sm = SpeechMarkdown(platform="amazon-polly-neural")
    text = sm.to_ssml("#[newscaster]\nHello world")
    assert text == "<speak>\n\n<amazon:domain name=\"news\">Hello world</amazon:domain>\n\n</speak>"

