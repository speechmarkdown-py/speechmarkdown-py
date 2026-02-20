# Speech Markdown for Python

Welcome to the documentation for **Speech Markdown**, the Python library for parsing and formatting speech markup into SSML or plain text.

## Overview

```python
from speechmarkdown import SpeechMarkdown

smd = SpeechMarkdown()
ssml = smd.to_ssml("(Hello world)[whisper]")
print(ssml)
```

## Contents

```{toctree}
:maxdepth: 2

api
```
