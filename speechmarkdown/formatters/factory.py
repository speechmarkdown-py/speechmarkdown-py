from speechmarkdown.formatters.base import FormatterBase
from speechmarkdown.formatters.text import TextFormatter
from speechmarkdown.options import SpeechOptions

# We will import other formatters here as they are implemented


class FormatterFactory:
    """
    Factory for producing specific formatters given the SpeechOptions definition.
    """

    @staticmethod
    def create_formatter(options: SpeechOptions) -> FormatterBase:
        """
        Construct a format engine relying upon the defined target platform.

        Args:
            options (SpeechOptions): Formatter configuration parameters.

        Returns:
            FormatterBase: Appropriate concrete formatter instantiation.
        """
        platform = (options.platform or "").lower()
        if not platform or platform == "text":
            return TextFormatter(options)
        elif platform == "amazon-alexa":
            from speechmarkdown.formatters.amazon_alexa import AmazonAlexaSsmlFormatter

            return AmazonAlexaSsmlFormatter(options)
        elif platform == "google-assistant":
            from speechmarkdown.formatters.google_assistant import (
                GoogleAssistantSsmlFormatter,
            )

            return GoogleAssistantSsmlFormatter(options)
        elif platform == "ibm-watson":
            from speechmarkdown.formatters.ibm_watson import IbmWatsonSsmlFormatter

            return IbmWatsonSsmlFormatter(options)
        elif platform == "microsoft-azure":
            from speechmarkdown.formatters.microsoft_azure import (
                MicrosoftAzureSsmlFormatter,
            )

            return MicrosoftAzureSsmlFormatter(options)
        elif platform == "amazon-polly":
            from speechmarkdown.formatters.amazon_polly import AmazonPollySsmlFormatter

            return AmazonPollySsmlFormatter(options)
        elif platform == "amazon-polly-neural":
            from speechmarkdown.formatters.amazon_polly_neural import (
                AmazonPollyNeuralSsmlFormatter,
            )

            return AmazonPollyNeuralSsmlFormatter(options)
        elif platform == "samsung-bixby":
            from speechmarkdown.formatters.samsung_bixby import (
                SamsungBixbySsmlFormatter,
            )

            return SamsungBixbySsmlFormatter(options)

        # fallback to text if unknown
        return TextFormatter(options)

    @staticmethod
    def create_text_formatter(options: SpeechOptions) -> TextFormatter:
        """
        Specifically return the base text parsing formatter engine.

        Args:
            options (SpeechOptions): Formatting controls.

        Returns:
            TextFormatter: Configured instance generating just text chunks.
        """
        return TextFormatter(options)
