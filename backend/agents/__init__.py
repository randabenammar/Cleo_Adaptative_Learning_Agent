# Package agents
from .subject_agent import SubjectAgent
from .content_agent import ContentAgent
from .quiz_agent import QuizAgent
from .evaluation_agent import EvaluationAgent
from .bloom_agent import BloomAgent
from .analytics_agent import AnalyticsAgent
from .support_agent import SupportAgent
from .admin_agent import AdminAgent  # ⭐ NOUVEAU

__all__ = [
    'SubjectAgent',
    'ContentAgent',
    'QuizAgent',
    'EvaluationAgent',
    'BloomAgent',
    'AnalyticsAgent',
    'SupportAgent',
    'AdminAgent'  # ⭐ NOUVEAU
]