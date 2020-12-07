from common import crypto
from unittest import TestCase

TEST_PASSWORD = 'UnitTest123'

class TestCommonCrypto(TestCase):
    def test_pbkdf2(self):
        self.assertTrue(crypto.check_hash(TEST_PASSWORD, crypto.make_hash(TEST_PASSWORD)))

    def test_sha256(self):
        self.assertTrue(crypto.check_hash(TEST_PASSWORD, crypto.make_hash(TEST_PASSWORD, pbkdf2=False), pbkdf2=False))
