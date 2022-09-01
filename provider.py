# Provider class to wrap APIs for web operations
# TODO: Unit tests
import io
import logging
import warnings
import keyring

from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from constants import ProvidersConst, StabilityConst


# TODO: Unit tests for this
class Provider(object):
    """
    A superclass used to wrap APIs for web operations from pycasso.

    Attributes
    ----------

    Methods
    -------
    get_image_from_string(text)
        Retrieves image from API. Returns PIL Image object.

    add_secret(text):
        Adds a secret 'text' to the keyring for the appropriate provider
        
    get_secret(text):
        Retrieves appropriate secret from the keyring for the appropriate provider
    """

    def __init__(self):
        return

    def get_image_from_string(self, text):
        return

    @staticmethod
    def add_secret(text):
        pass

    @staticmethod
    def get_secret():
        pass


class StabilityProvider(Provider):
    stability_api = object

    # inherits from Provider
    def __init__(self, key=None, host=None):
        # Get the inputs if necessary
        super().__init__()
        if key is None:
            stability_key = self.get_secret()
            if stability_key is None:
                warnings.warn("Stability API key not in keychain, environment or provided")
                exit()
        else:
            stability_key = key

        if host is None:
            host = StabilityConst.DEFAULT_HOST.value
            logging.info(f"Using {host} as stability host")

        self.stability_api = client.StabilityInference(
            key=stability_key,
            host=host,
            verbose=True,
        )

        return

    def get_image_from_string(self, text, height=0, width=0):
        if height == 0 or width == 0:
            answers = self.stability_api.generate(
                prompt=text,
            )
        else:
            answers = self.stability_api.generate(
                prompt=text,
                height=height,
                width=width
            )

        # iterating over the generator produces the api response
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the APIs safety filters and could not be processed."
                        "Please modify the prompt and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
        return img  # TODO: fix logic in case there's no image

    @staticmethod
    def add_secret(text):
        keyring.set_password(ProvidersConst.KEYCHAIN.value, ProvidersConst.STABLE_KEYNAME.value, text)
        return

    @staticmethod
    def get_secret():
        return keyring.get_password(ProvidersConst.KEYCHAIN.value, ProvidersConst.STABLE_KEYNAME.value)