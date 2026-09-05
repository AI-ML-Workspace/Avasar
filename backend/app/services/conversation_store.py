import logging
import re
import threading
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from app.models.chat import SourceItem

logger = logging.getLogger(__name__)


class ChatTurn(BaseModel):
    """A single turn in a multi-turn scheme consultation."""
    turn_id: str = Field(default_factory=lambda: f"turn_{uuid.uuid4().hex[:8]}")
    user_message: str
    assistant_answer: str
    detected_language: str = "en"
    contextualized_query: Optional[str] = None
    active_scheme: Optional[str] = None
    sources: List[SourceItem] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)


class ConversationSession(BaseModel):
    """Bounded in-process conversation session."""
    conversation_id: str
    created_at: float = Field(default_factory=time.time)
    last_activity: float = Field(default_factory=time.time)
    turns: List[ChatTurn] = Field(default_factory=list)
    active_scheme: Optional[str] = None
    preferred_language: str = "en"

    def get_history_dicts(self, max_turns: int = 6) -> List[Dict[str, str]]:
        """Return history as standard user/assistant messages for LLM context."""
        recent_turns = self.turns[-max_turns:]
        history: List[Dict[str, str]] = []
        for t in recent_turns:
            history.append({"role": "user", "content": t.user_message})
            history.append({"role": "assistant", "content": t.assistant_answer})
        return history


# Known scheme keyword patterns for active scheme detection
_SCHEME_KEYWORDS: Dict[str, str] = {
    "pm-kisan": "PM-KISAN",
    "pm kisan": "PM-KISAN",
    "pmkisan": "PM-KISAN",
    "pradhan mantri kisan": "PM-KISAN",
    "kisan credit": "Kisan Credit Card (KCC)",
    "kcc": "Kisan Credit Card (KCC)",
    "nsp": "National Scholarship Portal (NSP)",
    "national scholarship": "National Scholarship Portal (NSP)",
    "scholarship": "National Scholarship Portal (NSP)",
    "pmay": "PMAY-U",
    "pmay-u": "PMAY-U",
    "pmay urban": "PMAY-U",
    "awas yojana": "PMAY-U",
    "pradhan mantri awas": "PMAY-U",
    "mudra": "PMMY (MUDRA Yojana)",
    "pmmy": "PMMY (MUDRA Yojana)",
    "mudra yojana": "PMMY (MUDRA Yojana)",
    "shishu": "PMMY (MUDRA Yojana)",
    "kishore": "PMMY (MUDRA Yojana)",
    "tarun": "PMMY (MUDRA Yojana)",
    "atal pension": "Atal Pension Yojana (APY)",
    "apy": "Atal Pension Yojana (APY)",
    "ujjwala": "PMUY (Pradhan Mantri Ujjwala Yojana)",
    "pmuy": "PMUY (Pradhan Mantri Ujjwala Yojana)",
    "ayushman": "Ayushman Bharat (PM-JAY)",
    "ayushman bharat": "Ayushman Bharat (PM-JAY)",
    "pmjay": "Ayushman Bharat (PM-JAY)",
    "pm-jay": "Ayushman Bharat (PM-JAY)",
    "jan arogya": "Ayushman Bharat (PM-JAY)",
    "sukanya": "Sukanya Samriddhi Yojana (SSAS)",
    "ssy": "Sukanya Samriddhi Yojana (SSAS)",
    "ssas": "Sukanya Samriddhi Yojana (SSAS)",
    "jan dhan": "PMJDY (Jan Dhan Yojana)",
    "pmjdy": "PMJDY (Jan Dhan Yojana)",
    "pmjjby": "PMJJBY",
    "pmsby": "PMSBY",
    "stand up india": "Stand Up India",
    "svanidhi": "PM SVANidhi",
    "pm svanidhi": "PM SVANidhi",
    "vishwakarma": "PM Vishwakarma",
    "pm vishwakarma": "PM Vishwakarma",
    "mgnrega": "MGNREGA",
    "nrega": "MGNREGA",
    "fasal bima": "PM Fasal Bima Yojana (PMFBY)",
    "pmfby": "PM Fasal Bima Yojana (PMFBY)",
    "pm fasal bima": "PM Fasal Bima Yojana (PMFBY)",
    "krishi sinchayee": "PM Krishi Sinchayee Yojana (PMKSY)",
    "pmksy": "PM Krishi Sinchayee Yojana (PMKSY)",
    "soil health card": "Soil Health Card Scheme",
    "enam": "e-NAM",
    "e-nam": "e-NAM",
    "matru vandana": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
    "pmmvy": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
    "jan aushadhi": "Jan Aushadhi Scheme",
    "pmbjp": "Jan Aushadhi Scheme",
    "indradhanush": "Mission Indradhanush",
    "pm poshan": "PM POSHAN",
    "mid day meal": "PM POSHAN",
    "pmkvy": "PM Kaushal Vikas Yojana (PMKVY)",
    "kaushal vikas": "PM Kaushal Vikas Yojana (PMKVY)",
    "pmegp": "PMEGP",
    "startup india": "Startup India",
    "cgtmse": "CGTMSE",
    "pmay-g": "PMAY-Gramin",
    "pmay gramin": "PMAY-Gramin",
    "awaas gramin": "PMAY-Gramin",
    "saubhagya": "Saubhagya Scheme",
    "nsap": "National Social Assistance Programme (NSAP)",
    "old age pension": "National Social Assistance Programme (NSAP)",
    "one stop centre": "One Stop Centre (Sakhi)",
    "sakhi": "One Stop Centre (Sakhi)",
    "mission shakti": "Mission Shakti",
    "shram yogi": "PM-SYM",
    "pm-sym": "PM-SYM",
    "eshram": "e-Shram",
    "e-shram": "e-Shram",
    "inspire": "INSPIRE Scholarship",
    "ddu-gky": "DDU-GKY",
}

# Retrieval expansion: canonical scheme name → extra search terms to boost embedding similarity
# These mirror the actual chunk titles stored in FAISS, so cosine similarity improves.
_SCHEME_RETRIEVAL_EXPANSION: Dict[str, str] = {
    "PM-KISAN": "Pradhan Mantri Kisan Samman Nidhi farmer income support",
    "Ayushman Bharat (PM-JAY)": "Pradhan Mantri Jan Arogya Yojana health insurance cashless hospitalization",
    "PMAY-U": "Pradhan Mantri Awas Yojana Urban housing affordable",
    "PMMY (MUDRA Yojana)": "Pradhan Mantri MUDRA Yojana micro enterprise loan",
    "National Scholarship Portal (NSP)": "national scholarship portal student scholarship education",
    "Atal Pension Yojana (APY)": "Atal Pension Yojana retirement pension unorganised sector",
    "PMUY (Pradhan Mantri Ujjwala Yojana)": "Pradhan Mantri Ujjwala Yojana LPG gas cylinder BPL women",
    "Sukanya Samriddhi Yojana (SSAS)": "Sukanya Samriddhi Account girl child savings scheme",
    "PMJDY (Jan Dhan Yojana)": "Pradhan Mantri Jan Dhan Yojana bank account financial inclusion",
    "Stand Up India": "Stand Up India SC ST women entrepreneur loan",
    "PM SVANidhi": "PM SVANidhi street vendor working capital loan",
    "PM Vishwakarma": "PM Vishwakarma artisan craftsperson tool kit training",
    "MGNREGA": "MGNREGA rural employment guarantee job card wages",
    "PMSBY": "Pradhan Mantri Suraksha Bima Yojana accident insurance",
    "PMJJBY": "Pradhan Mantri Jeevan Jyoti Bima Yojana life insurance",
    "Kisan Credit Card (KCC)": "Kisan Credit Card agricultural short term loan farmer",
    "PM Fasal Bima Yojana (PMFBY)": "Pradhan Mantri Fasal Bima Yojana PMFBY crop insurance agriculture loss farmer",
    "PM Krishi Sinchayee Yojana (PMKSY)": "PM Krishi Sinchayee Yojana PMKSY irrigation Har Khet Ko Pani",
    "Soil Health Card Scheme": "Soil Health Card soil testing nutrient management farmer",
    "e-NAM": "e-NAM Electronic National Agriculture Market online trading mandi farmer",
    "Pradhan Mantri Matru Vandana Yojana (PMMVY)": "Pradhan Mantri Matru Vandana Yojana PMMVY maternity cash benefit pregnancy",
    "Jan Aushadhi Scheme": "Pradhan Mantri Jan Aushadhi Pariyojana PMBJP generic medicine affordable",
    "Mission Indradhanush": "Mission Indradhanush universal immunization vaccination children pregnant women",
    "PM POSHAN": "PM POSHAN Pradhan Mantri Poshan Shakti Nirman Mid-Day Meal school children nutrition",
    "PM Kaushal Vikas Yojana (PMKVY)": "Pradhan Mantri Kaushal Vikas Yojana PMKVY skill training certification youth",
    "PMEGP": "Prime Minister Employment Generation Programme PMEGP loan subsidy micro enterprise",
    "Startup India": "Startup India DPIIT tax exemption seed fund innovation entrepreneur",
    "CGTMSE": "Credit Guarantee Fund Trust Micro Small Enterprises CGTMSE collateral free loan MSME",
    "PMAY-Gramin": "Pradhan Mantri Awaas Yojana Gramin PMAY-G rural pucca house financial assistance",
    "Saubhagya Scheme": "Pradhan Mantri Sahaj Bijli Har Ghar Yojana Saubhagya free electricity connection rural",
    "National Social Assistance Programme (NSAP)": "National Social Assistance Programme NSAP old age widow disability pension BPL",
    "One Stop Centre (Sakhi)": "One Stop Centre Sakhi women violence emergency medical legal shelter",
    "Mission Shakti": "Mission Shakti women empowerment safety Sambal Samarthya",
    "PM-SYM": "Pradhan Mantri Shram Yogi Maan-dhan PM-SYM pension unorganised workers monthly 3000",
    "e-Shram": "e-Shram portal unorganised worker Universal Account Number UAN registration",
    "INSPIRE Scholarship": "INSPIRE Scholarship DST Innovation in Science Pursuit for Inspired Research higher education",
    "DDU-GKY": "Deen Dayal Upadhyaya Grameen Kaushalya Yojana DDU-GKY rural placement skill training",
}

# Ambiguous query patterns when asked without any active scheme context
_AMBIGUOUS_PATTERNS = [
    r"^(am\s+i|can\s+i|do\s+i)\s+(eligible|qualify|apply|get\s+it)\b",
    r"^(who\s+is\s+eligible|who\s+can\s+apply|eligibility\s+criteria)\??$",
    r"^(what\s+documents|documents\s+required|documents\s+needed|which\s+documents)\??$",
    r"^(how\s+to\s+apply|how\s+do\s+i\s+apply|where\s+to\s+apply|application\s+process)\??$",
    r"^(what\s+are\s+the\s+benefits|how\s+much\s+money|how\s+much\s+amount|benefit\s+amount)\??$",
    r"^(is\s+it\s+free|what\s+is\s+the\s+age\s+limit|what\s+is\s+the\s+deadline|last\s+date)\??$",
    # Hindi patterns
    r"^(kya\s+main\s+patra\s+hoon|patrata\s+kya\s+hai|kaun\s+apply\s+kar\s+sakta\s+hai)\??$",
    r"^(documents\s+kya\s+chahiye|dastavez\s+kya\s+chahiye|kagaz\s+kya\s+lagenge)\??$",
    r"^(kaise\s+apply\s+karein|kaise\s+aavedan\s+karein|kahan\s+apply\s+karein)\??$",
    r"^(kitna\s+paisa\s+milega|kya\s+labh\s+hai|labh\s+kya\s+hai)\??$",
]

# Follow-up intent patterns that should attach to active scheme
_FOLLOW_UP_PATTERNS = [
    (r"\b(who\s+is\s+eligible|who\s+can\s+apply|eligibility)\b", "eligibility"),
    (r"\b(what\s+documents|documents\s+required|documents\s+needed|which\s+documents|papers)\b", "documents"),
    (r"\b(how\s+to\s+apply|how\s+do\s+i\s+apply|where\s+to\s+apply|application\s+process)\b", "application process"),
    (r"\b(what\s+are\s+the\s+benefits|benefit\s+amount|how\s+much)\b", "benefits"),
    (r"\b(deadline|last\s+date|age\s+limit|validity)\b", "details"),
    # Hindi follow-up patterns
    (r"\b(patrata|kaun\s+apply|kaun\s+patra)\b", "eligibility"),
    (r"\b(documents|dastavez|kagaz)\b", "documents"),
    (r"\b(kaise\s+apply|aavedan)\b", "application process"),
    (r"\b(kitna\s+paisa|labh)\b", "benefits"),
]


class QueryContextualizer:
    """Detects scheme entities, ambiguity, and resolves follow-up queries."""

    @staticmethod
    def detect_scheme_in_text(text: str) -> Optional[str]:
        """Detect if text explicitly references a known government scheme."""
        if not text:
            return None
        t_lower = text.lower()
        for kw, canonical in _SCHEME_KEYWORDS.items():
            if re.search(rf"\b{re.escape(kw)}\b", t_lower):
                return canonical
        return None

    @staticmethod
    def expand_query_for_retrieval(query: str) -> str:
        """Expand a short scheme query with domain-specific terms to improve FAISS similarity.

        When a citizen asks "What is Ayushman Bharat?" the short query may not match
        the chunk title "Ayushman Bharat – Pradhan Mantri Jan Arogya Yojana" well enough.
        This method appends the expansion string from _SCHEME_RETRIEVAL_EXPANSION only
        when the query is short (≤8 words) and an explicit scheme is detected.

        Returns the original query unchanged if no expansion is warranted.
        """
        if len(query.split()) > 8:
            return query  # Long queries already provide enough context
        canonical = QueryContextualizer.detect_scheme_in_text(query)
        if not canonical:
            return query
        expansion = _SCHEME_RETRIEVAL_EXPANSION.get(canonical)
        if not expansion:
            return query
        return f"{query.strip()} {expansion}"

    @staticmethod
    def is_ambiguous_standalone(query: str, active_scheme: Optional[str]) -> bool:
        """Return True if the query is asking for scheme specifics but has no scheme context."""
        if active_scheme:
            return False

        # If an explicit scheme is mentioned in the query itself, not ambiguous
        if QueryContextualizer.detect_scheme_in_text(query):
            return False

        clean = query.strip()
        clean_no_punct = re.sub(r"[?!.,]+$", "", clean).strip().lower()

        # Check against predefined ambiguous regexes
        for pat in _AMBIGUOUS_PATTERNS:
            if re.search(pat, clean_no_punct):
                return True

        # Extremely short queries without scheme
        if len(clean_no_punct.split()) <= 3 and any(
            w in clean_no_punct for w in ["eligible", "documents", "apply", "benefits", "process", "patrata", "dastavez"]
        ):
            return True

        return False

    @staticmethod
    def get_clarification_message(language: str = "en") -> str:
        """Return concise clarification question in user's language."""
        if language == "hi":
            return (
                "आप किस सरकारी योजना के बारे में पूछ रहे हैं? कृपया योजना का नाम बताएं "
                "(जैसे कि पीएम-किसान, पीएम आवास योजना, राष्ट्रीय छात्रवृत्ति पोर्टल, या मुद्रा योजना) "
                "ताकि मैं आपको सही पात्रता, आवश्यक दस्तावेज और आवेदन प्रक्रिया बता सकूँ।"
            )
        return (
            "Which government scheme are you asking about? Please specify the scheme name "
            "(for example, PM-KISAN, PMAY-U, National Scholarship Portal, or MUDRA Loan) "
            "so I can provide accurate eligibility criteria and application requirements."
        )

    @staticmethod
    def contextualize_query(query: str, active_scheme: Optional[str]) -> Tuple[str, bool]:
        """Convert a conversational follow-up into a standalone retrieval-ready query.

        Args:
            query: The current normalized query.
            active_scheme: The currently active scheme in context, if any.

        Returns:
            Tuple of (contextualized_query, was_modified).
        """
        if not active_scheme:
            return query, False

        # If user explicitly mentioned a scheme in this query, don't force previous scheme
        explicit_scheme = QueryContextualizer.detect_scheme_in_text(query)
        if explicit_scheme:
            return query, False

        clean = query.strip()
        clean_lower = clean.lower()

        # Pronoun and reference replacements
        pronoun_replaced = re.sub(r"\b(this|that)\s+scheme\b", active_scheme, clean, flags=re.IGNORECASE)
        pronoun_replaced = re.sub(r"\b(it|they)\b", active_scheme, pronoun_replaced, flags=re.IGNORECASE)

        if pronoun_replaced != clean:
            return pronoun_replaced, True

        # Strip trailing punctuation before appending context
        clean_base = re.sub(r"[?!.,]+$", "", clean).strip()

        # Follow-up intent attachments (e.g. "Who is eligible?" -> "Who is eligible for PM-KISAN?")
        for pattern, phrase in _FOLLOW_UP_PATTERNS:
            if re.search(pattern, clean_lower):
                return f"{clean_base} for {active_scheme}?", True

        # Generic short follow-up fallback
        if len(clean.split()) <= 6:
            return f"{clean_base} for {active_scheme}?", True

        return query, False


class ConversationStore:
    """Thread-safe, bounded in-process session repository.

    Stores conversation history, tracks active scheme context, and enforces turn limits.
    """

    def __init__(self, max_turns: int = 10, max_sessions: int = 1000):
        self.max_turns = max_turns
        self.max_sessions = max_sessions
        self._sessions: Dict[str, ConversationSession] = {}
        self._lock = threading.Lock()

    def get_session(self, conversation_id: str) -> Optional[ConversationSession]:
        """Retrieve an existing session by ID."""
        with self._lock:
            return self._sessions.get(conversation_id)

    def get_or_create_session(
        self,
        conversation_id: Optional[str] = None,
        preferred_language: str = "en",
    ) -> ConversationSession:
        """Retrieve existing session or create a new one with a deterministic or random ID."""
        with self._lock:
            cid = conversation_id.strip() if conversation_id and conversation_id.strip() else f"conv_{uuid.uuid4().hex[:12]}"
            if cid in self._sessions:
                session = self._sessions[cid]
                session.last_activity = time.time()
                return session

            # Evict oldest session if capacity reached
            if len(self._sessions) >= self.max_sessions:
                oldest_cid = min(self._sessions.keys(), key=lambda k: self._sessions[k].last_activity)
                del self._sessions[oldest_cid]

            session = ConversationSession(
                conversation_id=cid,
                preferred_language=preferred_language,
            )
            self._sessions[cid] = session
            return session

    def add_turn(
        self,
        conversation_id: str,
        user_message: str,
        assistant_answer: str,
        detected_language: str = "en",
        contextualized_query: Optional[str] = None,
        sources: Optional[List[SourceItem]] = None,
        active_scheme: Optional[str] = None,
    ) -> ChatTurn:
        """Record a completed conversation turn and update session context."""
        with self._lock:
            session = self._sessions.get(conversation_id)
            if not session:
                session = ConversationSession(
                    conversation_id=conversation_id,
                    preferred_language=detected_language,
                )
                self._sessions[conversation_id] = session

            turn = ChatTurn(
                user_message=user_message,
                assistant_answer=assistant_answer,
                detected_language=detected_language,
                contextualized_query=contextualized_query,
                active_scheme=active_scheme or session.active_scheme,
                sources=sources or [],
            )

            session.turns.append(turn)
            # Enforce bounded memory
            if len(session.turns) > self.max_turns:
                session.turns = session.turns[-self.max_turns:]

            if active_scheme:
                session.active_scheme = active_scheme
            session.preferred_language = detected_language
            session.last_activity = time.time()

            return turn

    def clear(self) -> None:
        """Clear all active sessions (useful for tests)."""
        with self._lock:
            self._sessions.clear()


# Global in-process store instance
_global_conversation_store: Optional[ConversationStore] = None


def get_conversation_store() -> ConversationStore:
    """Access singleton ConversationStore instance."""
    global _global_conversation_store
    if _global_conversation_store is None:
        _global_conversation_store = ConversationStore()
    return _global_conversation_store
