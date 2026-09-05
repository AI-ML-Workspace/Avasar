import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.chat import ChatRequest, ChatResponse, SourceItem
from app.services.conversation_store import (
    ChatTurn,
    ConversationSession,
    ConversationStore,
    QueryContextualizer,
    get_conversation_store,
)
from app.services.language_pipeline import LanguagePipeline
from app.services.llm import LLMService
from app.services.rag import RAGService


class TestConversationalIntelligence(unittest.TestCase):
    """Automated unit and integration tests for Conversational Intelligence (Phase 11)."""

    def setUp(self):
        self.client = TestClient(app)
        self.store = ConversationStore(max_turns=10)
        # Clear store before each test
        self.store.clear()

        # Sample mock source
        self.pm_kisan_source = SourceItem(
            title="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
            url="https://pmkisan.gov.in/",
            snippet="Provides ₹6,000 per year to eligible landholder farmer families in three installments.",
            score=0.89,
            source_id="pm_kisan",
            is_official=True,
            trust_level="primary_authoritative",
            classification="central",
            official_domain="pmkisan.gov.in",
        )
        self.nsp_source = SourceItem(
            title="National Scholarship Portal (NSP)",
            url="https://scholarships.gov.in/",
            snippet="Central portal for pre-matric, post-matric, and higher education scholarships.",
            score=0.85,
            source_id="nsp",
            is_official=True,
            trust_level="primary_authoritative",
            classification="central",
            official_domain="scholarships.gov.in",
        )

    # 1. New Conversation Initialization
    def test_new_conversation(self):
        """Request without conversation_id initializes a new session and returns generated ID."""
        mock_rag = MagicMock()
        mock_rag.retrieve = AsyncMock(return_value=[self.pm_kisan_source])
        mock_llm = MagicMock()
        mock_llm.generate_answer = AsyncMock(return_value="PM-KISAN offers financial support to farmers.")

        from app.api.chat import get_conversation_store_dep, get_llm_service, get_rag_service
        app.dependency_overrides[get_rag_service] = lambda: mock_rag
        app.dependency_overrides[get_llm_service] = lambda: mock_llm
        app.dependency_overrides[get_conversation_store_dep] = lambda: self.store

        try:
            resp = self.client.post("/api/chat", json={"message": "What is PM-KISAN?"})
            self.assertEqual(resp.status_code, 200)
            data = resp.json()

            self.assertIn("conversation_id", data)
            cid = data["conversation_id"]
            self.assertTrue(cid.startswith("conv_"))

            # Session should be recorded in store
            session = self.store.get_session(cid)
            self.assertIsNotNone(session)
            self.assertEqual(len(session.turns), 1)
            self.assertEqual(session.turns[0].user_message, "What is PM-KISAN?")
            self.assertIn("PM-KISAN", session.active_scheme)
        finally:
            app.dependency_overrides.clear()

    # 2. Conversation ID Reuse
    def test_conversation_id_reuse(self):
        """Subsequent turns reusing the same conversation_id maintain history in that session."""
        mock_rag = MagicMock()
        mock_rag.retrieve = AsyncMock(return_value=[self.pm_kisan_source])
        mock_llm = MagicMock()
        mock_llm.generate_answer = AsyncMock(return_value="Answer for turn.")

        from app.api.chat import get_conversation_store_dep, get_llm_service, get_rag_service
        app.dependency_overrides[get_rag_service] = lambda: mock_rag
        app.dependency_overrides[get_llm_service] = lambda: mock_llm
        app.dependency_overrides[get_conversation_store_dep] = lambda: self.store

        try:
            cid = "conv_test_reuse_101"
            # Turn 1
            r1 = self.client.post("/api/chat", json={"message": "What is PM-KISAN?", "conversation_id": cid})
            self.assertEqual(r1.status_code, 200)
            self.assertEqual(r1.json()["conversation_id"], cid)

            # Turn 2
            r2 = self.client.post("/api/chat", json={"message": "Who is eligible?", "conversation_id": cid})
            self.assertEqual(r2.status_code, 200)
            self.assertEqual(r2.json()["conversation_id"], cid)

            session = self.store.get_session(cid)
            self.assertEqual(len(session.turns), 2)
            self.assertEqual(session.turns[0].user_message, "What is PM-KISAN?")
            self.assertEqual(session.turns[1].user_message, "Who is eligible?")
        finally:
            app.dependency_overrides.clear()

    # 3. Follow-up Contextualization
    def test_follow_up_contextualization(self):
        """Follow-up questions are contextualized with the active scheme before RAG retrieval."""
        mock_rag = MagicMock()
        mock_rag.retrieve = AsyncMock(return_value=[self.pm_kisan_source])
        mock_llm = MagicMock()
        mock_llm.generate_answer = AsyncMock(return_value="Eligible farmers are small and marginal landholders.")

        from app.api.chat import get_conversation_store_dep, get_llm_service, get_rag_service
        app.dependency_overrides[get_rag_service] = lambda: mock_rag
        app.dependency_overrides[get_llm_service] = lambda: mock_llm
        app.dependency_overrides[get_conversation_store_dep] = lambda: self.store

        try:
            cid = "conv_followup_202"
            # Turn 1: Discuss PM-KISAN
            self.client.post("/api/chat", json={"message": "Tell me about PM-KISAN", "conversation_id": cid})

            # Turn 2: Follow-up "Who is eligible?"
            self.client.post("/api/chat", json={"message": "Who is eligible?", "conversation_id": cid})

            # Check that RAG retrieve received contextualized query mentioning PM-KISAN
            last_rag_call = mock_rag.retrieve.call_args[1]["query"]
            self.assertIn("PM-KISAN", last_rag_call)
        finally:
            app.dependency_overrides.clear()

    # 4. Pronoun and Reference Resolution
    def test_pronoun_and_reference_resolution(self):
        """Pronoun references ('it', 'this scheme') resolve to the active scheme."""
        active_scheme = "Pradhan Mantri Awas Yojana (Urban)"

        # 'it' replacement
        q1, mod1 = QueryContextualizer.contextualize_query("How do I apply for it?", active_scheme)
        self.assertTrue(mod1)
        self.assertIn(active_scheme, q1)

        # 'this scheme' replacement
        q2, mod2 = QueryContextualizer.contextualize_query("Is this scheme active?", active_scheme)
        self.assertTrue(mod2)
        self.assertIn(active_scheme, q2)

        # Elliptical document requirement
        q3, mod3 = QueryContextualizer.contextualize_query("What documents are needed?", active_scheme)
        self.assertTrue(mod3)
        self.assertIn(active_scheme, q3)

    # 5. Bounded Memory Limit
    def test_bounded_history(self):
        """ConversationStore enforces max turns boundary and evicts older turns."""
        store = ConversationStore(max_turns=5)
        cid = "conv_bounded_303"

        for i in range(1, 10):
            store.add_turn(
                conversation_id=cid,
                user_message=f"Question {i}",
                assistant_answer=f"Answer {i}",
            )

        session = store.get_session(cid)
        self.assertEqual(len(session.turns), 5)
        # Should retain Question 5 to Question 9
        self.assertEqual(session.turns[0].user_message, "Question 5")
        self.assertEqual(session.turns[-1].user_message, "Question 9")

    # 6. Missing Context Clarification
    def test_missing_context_clarification(self):
        """Ambiguous query with no active scheme triggers clarification without hallucinating."""
        from app.api.chat import get_conversation_store_dep
        app.dependency_overrides[get_conversation_store_dep] = lambda: self.store

        try:
            resp = self.client.post("/api/chat", json={"message": "Am I eligible?"})
            self.assertEqual(resp.status_code, 200)
            data = resp.json()

            # Must ask clarification question
            self.assertIn("Which government scheme are you asking about?", data["answer"])
            self.assertEqual(len(data["sources"]), 0)
        finally:
            app.dependency_overrides.clear()

    # 7. Eligibility With Sufficient Context
    def test_eligibility_with_sufficient_context(self):
        """Specific farmer profile with scheme context passes through to grounded LLM evaluation."""
        mock_rag = MagicMock()
        mock_rag.retrieve = AsyncMock(return_value=[self.pm_kisan_source])
        mock_llm = MagicMock()
        mock_llm.generate_answer = AsyncMock(
            return_value="Based on your small landholding of 1 hectare, you are eligible for PM-KISAN benefits."
        )

        from app.api.chat import get_conversation_store_dep, get_llm_service, get_rag_service
        app.dependency_overrides[get_rag_service] = lambda: mock_rag
        app.dependency_overrides[get_llm_service] = lambda: mock_llm
        app.dependency_overrides[get_conversation_store_dep] = lambda: self.store

        try:
            resp = self.client.post(
                "/api/chat",
                json={"message": "I am a small farmer owning 1 hectare land, am I eligible for PM-KISAN?"}
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn("eligible", data["answer"].lower())
            self.assertGreaterEqual(len(data["sources"]), 1)
        finally:
            app.dependency_overrides.clear()

    # 8. Eligibility With Insufficient Context
    def test_eligibility_with_insufficient_context(self):
        """User asks if eligible for PM-KISAN without profile details -> LLM lists criteria and conditions."""
        mock_rag = MagicMock()
        mock_rag.retrieve = AsyncMock(return_value=[self.pm_kisan_source])
        mock_llm = MagicMock()
        mock_llm.generate_answer = AsyncMock(
            return_value="Under PM-KISAN, eligibility requires owning cultivable agricultural land. Please verify whether you own agricultural land."
        )

        from app.api.chat import get_conversation_store_dep, get_llm_service, get_rag_service
        app.dependency_overrides[get_rag_service] = lambda: mock_rag
        app.dependency_overrides[get_llm_service] = lambda: mock_llm
        app.dependency_overrides[get_conversation_store_dep] = lambda: self.store

        try:
            resp = self.client.post("/api/chat", json={"message": "Am I eligible for PM-KISAN?"})
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn("agricultural land", data["answer"].lower())
        finally:
            app.dependency_overrides.clear()

    # 9. Scheme Discovery by Persona
    def test_scheme_discovery(self):
        """Citizen asks for student schemes -> RAG retrieves student programs and presents them."""
        mock_rag = MagicMock()
        mock_rag.retrieve = AsyncMock(return_value=[self.nsp_source])
        mock_llm = MagicMock()
        mock_llm.generate_answer = AsyncMock(
            return_value="For students, available options include the National Scholarship Portal (NSP)."
        )

        from app.api.chat import get_conversation_store_dep, get_llm_service, get_rag_service
        app.dependency_overrides[get_rag_service] = lambda: mock_rag
        app.dependency_overrides[get_llm_service] = lambda: mock_llm
        app.dependency_overrides[get_conversation_store_dep] = lambda: self.store

        try:
            resp = self.client.post("/api/chat", json={"message": "I am a student, what schemes are available?"})
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn("scholarship", data["answer"].lower())
            self.assertEqual(data["sources"][0]["source_id"], "nsp")
        finally:
            app.dependency_overrides.clear()

    # 10. Language Continuity Across Turns
    def test_language_continuity(self):
        """Multi-turn conversation preserves Hindi continuity when follow-up has no explicit language."""
        cid = "conv_lang_404"
        session = self.store.get_or_create_session(conversation_id=cid, preferred_language="hi")
        session.active_scheme = "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)"
        self.store.add_turn(
            conversation_id=cid,
            user_message="पीएम किसान योजना क्या है?",
            assistant_answer="पीएम किसान एक सरकारी योजना है।",
            detected_language="hi",
            active_scheme="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        )

        mock_rag = MagicMock()
        mock_rag.retrieve = AsyncMock(return_value=[self.pm_kisan_source])
        mock_llm = MagicMock()
        mock_llm.generate_answer = AsyncMock(return_value="Aadhaar and land records are required.")

        mock_pipeline = MagicMock()
        from app.services.language_pipeline import ProcessedQuery
        mock_pipeline.process_query = AsyncMock(
            return_value=ProcessedQuery(
                original_text="dastavez kya lagenge?",
                detected_language="hi",
                normalized_query="What documents are required?",
            )
        )
        mock_pipeline.translate_response = AsyncMock(return_value="आधार कार्ड और खतौनी की आवश्यकता है।")

        from app.api.chat import (
            get_conversation_store_dep,
            get_language_pipeline,
            get_llm_service,
            get_rag_service,
        )
        app.dependency_overrides[get_rag_service] = lambda: mock_rag
        app.dependency_overrides[get_llm_service] = lambda: mock_llm
        app.dependency_overrides[get_language_pipeline] = lambda: mock_pipeline
        app.dependency_overrides[get_conversation_store_dep] = lambda: self.store

        try:
            resp = self.client.post(
                "/api/chat",
                json={"message": "dastavez kya lagenge?", "conversation_id": cid}
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data["language"], "hi")
            self.assertIn("आधार", data["answer"])
        finally:
            app.dependency_overrides.clear()

    # 11. Grounded Refusal for Out of Scope Queries
    def test_grounded_refusal(self):
        """Out of scope questions with empty or low-scoring sources yield grounded refusal."""
        mock_rag = MagicMock()
        mock_rag.retrieve = AsyncMock(return_value=[])

        from app.api.chat import get_conversation_store_dep, get_rag_service
        app.dependency_overrides[get_rag_service] = lambda: mock_rag
        app.dependency_overrides[get_conversation_store_dep] = lambda: self.store

        try:
            resp = self.client.post("/api/chat", json={"message": "How to make mango pickle?"})
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn("no matching scheme details were found", data["answer"].lower())
        finally:
            app.dependency_overrides.clear()

    # 12. Concurrent Conversation Isolation
    def test_concurrent_conversation_isolation(self):
        """Two concurrent sessions discuss different schemes without cross-talk or leakage."""
        cid_a = "conv_session_alpha"
        cid_b = "conv_session_beta"

        # Session A discusses PM-KISAN
        self.store.add_turn(
            conversation_id=cid_a,
            user_message="What is PM-KISAN?",
            assistant_answer="PM-KISAN explanation.",
            active_scheme="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        )

        # Session B discusses National Scholarship Portal
        self.store.add_turn(
            conversation_id=cid_b,
            user_message="Tell me about NSP scholarships.",
            assistant_answer="NSP explanation.",
            active_scheme="National Scholarship Portal (NSP)",
        )

        session_a = self.store.get_session(cid_a)
        session_b = self.store.get_session(cid_b)

        # Verify active scheme isolation
        self.assertEqual(session_a.active_scheme, "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)")
        self.assertEqual(session_b.active_scheme, "National Scholarship Portal (NSP)")

        # Verify follow-up contextualization isolation
        q_a, _ = QueryContextualizer.contextualize_query("Who is eligible?", session_a.active_scheme)
        q_b, _ = QueryContextualizer.contextualize_query("Who is eligible?", session_b.active_scheme)

        self.assertIn("PM-KISAN", q_a)
        self.assertNotIn("NSP", q_a)

        self.assertIn("NSP", q_b)
        self.assertNotIn("PM-KISAN", q_b)


if __name__ == "__main__":
    unittest.main()
