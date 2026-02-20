from speechmarkdown.speechmarkdown import SpeechMarkdown

def test_azure_basic():
    sm = SpeechMarkdown(platform="microsoft-azure")
    text = sm.to_ssml("Hello (world) [cheerful]")
    assert text == "<speak xmlns:mstts=\"https://www.w3.org/2001/mstts\">\nHello <mstts:express-as style=\"cheerful\">world</mstts:express-as>\n</speak>"
