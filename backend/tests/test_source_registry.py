import json
import tempfile
import unittest
from pathlib import Path
from pydantic import ValidationError

from app.models.source import (
    GovernmentClassification,
    OfficialSource,
    SourceType,
    TrustLevel,
    is_authorized_government_domain,
)
from app.services.source_registry import SourceRegistry, get_source_registry


class TestSourceRegistry(unittest.TestCase):
    """Unit tests for the Official Source Registry and domain validation rules."""

    def setUp(self):
        self.registry = get_source_registry()

    def test_default_sources_loaded(self):
        """Verify the bundled official government sources load successfully."""
        sources = self.registry.list_sources(enabled_only=False)
        self.assertGreaterEqual(len(sources), 10)

        # Check key national aggregators and portals
        myscheme = self.registry.get_source("myscheme")
        self.assertIsNotNone(myscheme)
        self.assertEqual(myscheme.classification, GovernmentClassification.NATIONAL_PORTAL)
        self.assertIn("myscheme.gov.in", myscheme.allowed_domains)

        pm_kisan = self.registry.get_source("pm_kisan")
        self.assertIsNotNone(pm_kisan)
        self.assertEqual(pm_kisan.classification, GovernmentClassification.CENTRAL)

        nsp = self.registry.get_source("nsp")
        self.assertIsNotNone(nsp)

        data_gov = self.registry.get_source("data_gov")
        self.assertIsNotNone(data_gov)

    def test_domain_validation_official_suffixes(self):
        """Verify authorized government domain suffixes."""
        self.assertTrue(is_authorized_government_domain("pmkisan.gov.in"))
        self.assertTrue(is_authorized_government_domain("www.myscheme.gov.in"))
        self.assertTrue(is_authorized_government_domain("nrega.nic.in"))
        self.assertTrue(is_authorized_government_domain("sevasindhu.karnataka.gov.in"))
        self.assertTrue(is_authorized_government_domain("tnesevai.tn.gov.in"))
        self.assertTrue(is_authorized_government_domain("scholarships.gov.in"))
        self.assertTrue(is_authorized_government_domain("iisc.ac.in"))

    def test_domain_validation_special_statutory_domains(self):
        """Verify whitelisted statutory platforms with non-standard TLDs."""
        self.assertTrue(is_authorized_government_domain("mudra.org.in"))
        self.assertTrue(is_authorized_government_domain("www.mudra.org.in"))
        self.assertTrue(is_authorized_government_domain("jansamarth.in"))
        self.assertTrue(is_authorized_government_domain("www.jansamarth.in"))

    def test_domain_validation_rejection_of_unauthorized_domains(self):
        """Verify commercial, blog, and unofficial domains are rejected."""
        self.assertFalse(is_authorized_government_domain("government-schemes.com"))
        self.assertFalse(is_authorized_government_domain("pmkisanyojana.org"))
        self.assertFalse(is_authorized_government_domain("sarkariyojana.in"))
        self.assertFalse(is_authorized_government_domain("randomblog.net"))
        self.assertFalse(is_authorized_government_domain("blogspot.com"))
        self.assertFalse(is_authorized_government_domain(""))
        self.assertFalse(is_authorized_government_domain(None))

    def test_official_source_schema_validation_success(self):
        """Verify valid OfficialSource creation."""
        source = OfficialSource(
            source_id="bihar_epass",
            name="Bihar Post Matric Scholarship Portal",
            base_url="https://pmsonline.bih.nic.in/",
            allowed_domains=["pmsonline.bih.nic.in", "bih.nic.in"],
            classification=GovernmentClassification.STATE_UT,
            source_type=SourceType.STATE_PORTAL,
            state_or_ut="Bihar",
        )
        self.assertEqual(source.source_id, "bihar_epass")
        self.assertIn("bih.nic.in", source.allowed_domains)

    def test_official_source_schema_validation_rejection(self):
        """Verify invalid OfficialSource definitions trigger ValidationError."""
        # Non-governmental base_url
        with self.assertRaises(ValidationError):
            OfficialSource(
                source_id="fake_scheme",
                name="Fake Scheme Blog",
                base_url="https://unofficial-schemes.com/",
                classification=GovernmentClassification.CENTRAL,
                source_type=SourceType.SCHEME_PORTAL,
            )

        # Invalid source_id with uppercase and spaces
        with self.assertRaises(ValidationError):
            OfficialSource(
                source_id="INVALID ID WITH SPACES",
                name="Valid Portal",
                base_url="https://pmkisan.gov.in/",
                classification=GovernmentClassification.CENTRAL,
                source_type=SourceType.SCHEME_PORTAL,
            )

        # Non-government allowed_domains
        with self.assertRaises(ValidationError):
            OfficialSource(
                source_id="test_portal",
                name="Test Portal",
                base_url="https://pmkisan.gov.in/",
                allowed_domains=["pmkisan.gov.in", "thirdparty-scraper.com"],
                classification=GovernmentClassification.CENTRAL,
                source_type=SourceType.SCHEME_PORTAL,
            )

    def test_url_lookup_and_allowed_domain_matching(self):
        """Verify source matching and URL authorization."""
        # Valid PM-KISAN URL
        kisan_url = "https://pmkisan.gov.in/RegistrationFormNew.aspx"
        source = self.registry.get_source_for_url(kisan_url)
        self.assertIsNotNone(source)
        self.assertEqual(source.source_id, "pm_kisan")
        self.assertTrue(self.registry.validate_source_url(kisan_url))
        self.assertTrue(self.registry.is_allowed_domain("pmkisan.gov.in"))

        # Valid myScheme URL
        myscheme_url = "https://www.myscheme.gov.in/schemes/pm-kisan"
        source_ms = self.registry.get_source_for_url(myscheme_url)
        self.assertIsNotNone(source_ms)
        self.assertEqual(source_ms.source_id, "myscheme")
        self.assertTrue(self.registry.validate_source_url(myscheme_url))

        # Unofficial / fake URL
        fake_url = "https://pmkisan-fake-scam.com/apply"
        self.assertIsNone(self.registry.get_source_for_url(fake_url))
        self.assertFalse(self.registry.validate_source_url(fake_url))
        self.assertFalse(self.registry.is_allowed_domain("pmkisan-fake-scam.com"))

    def test_filtering_sources(self):
        """Verify filtering by classification, source_type, and state."""
        central_sources = self.registry.list_sources(
            classification=GovernmentClassification.CENTRAL
        )
        self.assertTrue(all(s.classification == GovernmentClassification.CENTRAL for s in central_sources))
        self.assertGreaterEqual(len(central_sources), 3)

        state_sources = self.registry.list_sources(
            classification=GovernmentClassification.STATE_UT
        )
        self.assertTrue(all(s.classification == GovernmentClassification.STATE_UT for s in state_sources))
        self.assertGreaterEqual(len(state_sources), 2)

        karnataka_sources = self.registry.list_sources(state_or_ut="karnataka")
        self.assertEqual(len(karnataka_sources), 1)
        self.assertEqual(karnataka_sources[0].source_id, "karnataka_sevasindhu")

    def test_custom_registry_file_loading(self):
        """Verify SourceRegistry loading from an arbitrary configuration file."""
        custom_data = [
            {
                "source_id": "test_delhi",
                "name": "Delhi e-District Portal",
                "base_url": "https://edistrict.delhigovt.nic.in",
                "allowed_domains": ["edistrict.delhigovt.nic.in", "delhigovt.nic.in"],
                "classification": "state_ut",
                "source_type": "state_portal",
                "state_or_ut": "Delhi",
                "enabled": True,
            }
        ]

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as tf:
            json.dump(custom_data, tf)
            temp_path = tf.name

        try:
            custom_registry = SourceRegistry(config_path=temp_path)
            self.assertEqual(len(custom_registry.list_sources()), 1)
            delhi_source = custom_registry.get_source("test_delhi")
            self.assertIsNotNone(delhi_source)
            self.assertEqual(delhi_source.name, "Delhi e-District Portal")
            self.assertTrue(custom_registry.is_allowed_domain("edistrict.delhigovt.nic.in"))
        finally:
            Path(temp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
