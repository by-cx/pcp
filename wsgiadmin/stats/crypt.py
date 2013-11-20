# -*- coding: utf-8 -*-
import base64
from Crypto.Cipher import AES

from django.conf import settings

__all__ = ['encode', 'decode']

# the block size for the cipher object; must be 16, 24, or 32 for AES
_BLOCK_SIZE = 32

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
_PADDING = '{'

# one-liner to sufficiently pad the text to be encrypted
_pad = lambda s: s + (_BLOCK_SIZE - len(s) % _BLOCK_SIZE) * _PADDING

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
_EncodeAES = lambda c, s: base64.b64encode(c.encrypt(_pad(s)))
_DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(_PADDING)

_secret = _pad(settings.SECRET_KEY[1:_BLOCK_SIZE])

# create a cipher object using the random secret
_cipher = AES.new(_secret)


def encode(data):
    """
    Zakoduje data a vrati retezec

    :param data: Data ktera chceme zakodovat
    :type data: string
    :return: Zakodovana data v retezci base64
    :rtype: string
    """
    return _EncodeAES(_cipher, data)


def decode(data):
    """
    Dekoduje data

    :param data: Retezec s datay
    :type data: string
    :return: Zakodovana data
    :rtype: string
    """
    return _DecodeAES(_cipher, data)

