import json
import tempfile
import unittest
from pathlib import Path

from app.models.document import ProcessedChunk, SchemeDocument
from app.services.chunking import chunk_document, split_text
from app.services.ingestion import DocumentIngestionService


class TestChunking(unittest.TestCase):
    """Focused tests for text splitting and chunking logic."""

    def test_empty_or_whitespace_text(self):
        self.assertEqual(split_text(""), [])
        self.assertEqual(split_text("   \n\t  "), [])

    def test_text_shorter_than_chunk_size(self):
        text = "PM Kisan Samman Nidhi provides financial assistance."
        chunks = split_text(text, chunk_size=200, chunk_overlap=50)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)

    def test_chunk_size_and_overlap_behavior(self):
        # Create text with several sentences
        sentence = "Government welfare schemes provide essential financial assistance to citizens. "
        long_text = sentence * 10  # ~800 characters
        chunk_size = 250
        chunk_overlap = 50

        chunks = split_text(long_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.assertGreater(len(chunks), 1)

        for chunk in chunks:
            # Chunk should not vastly exceed target chunk_size (may be slightly shorter due to word boundaries)
            self.assertLessEqual(len(chunk), chunk_size)
            self.assertGreater(len(chunk), 0)

        # Check that consecutive chunks have overlapping content
        for i in range(len(chunks) - 1):
            curr_words = set(chunks[i].split()[-3:])
            next_words = set(chunks[i + 1].split()[:6])
            # There should be common words due to overlap
            self.assertTrue(
                bool(curr_words.intersection(next_words)),
                f"Expected overlap between chunk {i} and {i+1}",
            )

    def test_invalid_parameters_raise_value_error(self):
        with self.assertRaises(ValueError):
            split_text("Sample text", chunk_size=0)

        with self.assertRaises(ValueError):
            split_text("Sample text", chunk_size=100, chunk_overlap=-1)

        with self.assertRaises(ValueError):
            split_text("Sample text", chunk_size=100, chunk_overlap=100)

        with self.assertRaises(ValueError):
            split_text("Sample text", chunk_size=100, chunk_overlap=150)

    def test_chunk_document_metadata_preservation(self):
        doc = SchemeDocument(
            id="pm_kisan_01",
            title="PM-KISAN",
            url="https://pmkisan.gov.in/",
            source_name="Ministry of Agriculture",
            language="en",
            content="Sentence one. " * 30,
            metadata={"category": "Agriculture", "beneficiaries": "Farmers"},
        )

        chunks = chunk_document(doc, chunk_size=150, chunk_overlap=30)
        self.assertGreater(len(chunks), 1)

        for idx, chunk in enumerate(chunks):
            self.assertEqual(chunk.scheme_id, "pm_kisan_01")
            self.assertEqual(chunk.chunk_id, f"pm_kisan_01#{idx}")
            self.assertEqual(chunk.title, "PM-KISAN")
            self.assertEqual(chunk.url, "https://pmkisan.gov.in/")
            self.assertEqual(chunk.source_name, "Ministry of Agriculture")
            self.assertEqual(chunk.language, "en")
            self.assertEqual(chunk.chunk_index, idx)
            self.assertEqual(chunk.total_chunks, len(chunks))
            self.assertEqual(chunk.metadata["category"], "Agriculture")
            self.assertEqual(chunk.metadata["beneficiaries"], "Farmers")
            self.assertEqual(chunk.char_length, len(chunk.text))


class TestDocumentIngestion(unittest.TestCase):
    """Focused tests for document loading, normalization, and pipeline execution."""

    def setUp(self):
        self.service = DocumentIngestionService(chunk_size=300, chunk_overlap=50)

    def test_normalize_scheme_sections(self):
        raw_dict = {
            "title": "Pradhan Mantri Awas Yojana",
            "url": "https://pmaymis.gov.in/",
            "ministry": "MoHUA",
            "description": "Housing for all mission.",
            "eligibility": "EWS and LIG families.",
            "benefits": "Subsidies up to Rs 2.67 Lakh.",
            "application_process": "Apply via CSC portal.",
            "category": "Housing",
        }

        doc = self.service.normalize_scheme_dict(raw_dict, fallback_id="fallback_01")
        self.assertEqual(doc.title, "Pradhan Mantri Awas Yojana")
        self.assertEqual(doc.url, "https://pmaymis.gov.in/")
        self.assertEqual(doc.source_name, "MoHUA")
        self.assertIn("Housing for all mission.", doc.content)
        self.assertIn("Eligibility:\nEWS and LIG families.", doc.content)
        self.assertIn("Benefits:\nSubsidies up to Rs 2.67 Lakh.", doc.content)
        self.assertIn("Application Process:\nApply via CSC portal.", doc.content)
        self.assertEqual(doc.metadata.get("category"), "Housing")

    def test_normalize_contributor_scheme_schema(self):
        raw_dict = {
            "scheme_name": "PM-KISAN",
            "category": "Agriculture",
            "description": "Income support to landholding farmers.",
            "eligibility": "All landholding farmer families.",
            "benefits": [
                "Financial benefit of Rs 6,000 per year.",
                "Payable in three equal installments of Rs 2,000.",
            ],
            "application_process": "Self-register on PM-KISAN portal.",
            "documents_required": ["Aadhaar Card", "Land records"],
            "important_conditions": ["e-KYC is mandatory."],
            "provider": "Ministry of Agriculture",
            "official_source": "PM-KISAN Portal",
            "official_source_url": "https://pmkisan.gov.in/",
        }

        doc = self.service.normalize_scheme_dict(raw_dict, fallback_id="pm_kisan_01")
        self.assertEqual(doc.title, "PM-KISAN")
        self.assertEqual(doc.url, "https://pmkisan.gov.in/")
        self.assertEqual(doc.source_name, "Ministry of Agriculture")
        self.assertIn("Income support to landholding farmers.", doc.content)
        self.assertIn("Benefits:\n- Financial benefit of Rs 6,000 per year.\n- Payable in three equal installments of Rs 2,000.", doc.content)
        self.assertIn("Documents Required:\n- Aadhaar Card\n- Land records", doc.content)
        self.assertIn("Important Conditions:\n- e-KYC is mandatory.", doc.content)
        self.assertEqual(doc.metadata.get("category"), "Agriculture")

    def test_load_json_list_and_metadata_preservation(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(
                [
                    {
                        "id": "scheme_a",
                        "title": "Scheme A",
                        "url": "https://example.gov.in/a",
                        "content": "Scheme A full content details.",
                        "ministry": "Ministry of Finance",
                        "target_group": "Youth",
                    },
                    {
                        "id": "scheme_b",
                        "title": "Scheme B",
                        "content": "Scheme B description.",
                    },
                ],
                f,
            )
            temp_path = Path(f.name)

        try:
            docs = self.service.load_file(temp_path)
            self.assertEqual(len(docs), 2)
            self.assertEqual(docs[0].id, "scheme_a")
            self.assertEqual(docs[0].title, "Scheme A")
            self.assertEqual(docs[0].source_name, "Ministry of Finance")
            self.assertEqual(docs[0].metadata["target_group"], "Youth")
            self.assertEqual(docs[1].title, "Scheme B")
            self.assertEqual(docs[1].source_name, "Government of India")  # Default fallback
        finally:
            temp_path.unlink()

    def test_load_jsonl(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
            f.write(json.dumps({"title": "Line 1 Scheme", "content": "Line 1 text"}) + "\n")
            f.write("\n")  # Empty line handling
            f.write(json.dumps({"title": "Line 2 Scheme", "content": "Line 2 text"}) + "\n")
            temp_path = Path(f.name)

        try:
            docs = self.service.load_file(temp_path)
            self.assertEqual(len(docs), 2)
            self.assertEqual(docs[0].title, "Line 1 Scheme")
            self.assertEqual(docs[1].title, "Line 2 Scheme")
        finally:
            temp_path.unlink()

    def test_load_markdown_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write("# National Scholarship Portal\n\nNSP is a one-stop solution for scholarship services.")
            temp_path = Path(f.name)

        try:
            docs = self.service.load_file(temp_path)
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0].title, "National Scholarship Portal")
            self.assertIn("NSP is a one-stop solution", docs[0].content)
        finally:
            temp_path.unlink()

    def test_empty_file_handling(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("   \n  ")
            temp_path = Path(f.name)

        try:
            docs = self.service.load_file(temp_path)
            self.assertEqual(docs, [])
        finally:
            temp_path.unlink()

    def test_nonexistent_file_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            self.service.load_file(Path("non_existent_file_path.json"))

    def test_full_pipeline_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_raw = Path(temp_dir) / "raw"
            temp_processed = Path(temp_dir) / "processed"
            temp_raw.mkdir()

            # Create test raw scheme file
            scheme_file = temp_raw / "test_scheme.json"
            scheme_file.write_text(
                json.dumps([
                    {
                        "id": "pmjay_test",
                        "title": "Ayushman Bharat PMJAY",
                        "url": "https://pmjay.gov.in/",
                        "description": "Healthcare cover of up to 5 lakh per family per year for secondary care. " * 8,
                        "category": "Health",
                    }
                ]),
                encoding="utf-8",
            )

            out_jsonl = temp_processed / "chunks.jsonl"

            res = self.service.run(raw_dir=temp_raw, output_file=out_jsonl)

            self.assertEqual(res["status"], "success")
            self.assertEqual(res["documents_loaded"], 1)
            self.assertGreater(res["chunks_created"], 1)
            self.assertEqual(res["chunks_saved"], res["chunks_created"])
            self.assertTrue(out_jsonl.exists())

            # Read back generated JSONL and validate schema
            with open(out_jsonl, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]

            self.assertEqual(len(lines), res["chunks_saved"])
            for line in lines:
                parsed = json.loads(line)
                # Verify ProcessedChunk Pydantic validation passes
                chunk_obj = ProcessedChunk.model_validate(parsed)
                self.assertEqual(chunk_obj.scheme_id, "pmjay_test")
                self.assertEqual(chunk_obj.url, "https://pmjay.gov.in/")
                self.assertIsNotNone(chunk_obj.text)
                self.assertEqual(chunk_obj.metadata["category"], "Health")


if __name__ == "__main__":
    unittest.main()
