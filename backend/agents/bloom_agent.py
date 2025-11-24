import logging
from typing import Dict, Any, List

logger = logging.getLogger("cleo.bloom_agent")


class BloomAgent:
    """
    Agent spécialisé dans la gestion de la taxonomie de Bloom
    et l'adaptation pédagogique selon le niveau cognitif.
    """
    
    BLOOM_TAXONOMY = {
        1: {
            "level": "Remember",
            "description": "Recall facts and basic concepts",
            "verbs": ["define", "list", "recall", "name", "identify", "state"],
            "difficulty_range": (1, 2),
            "question_types": ["mcq", "true_false"]
        },
        2: {
            "level": "Understand",
            "description": "Explain ideas or concepts",
            "verbs": ["explain", "describe", "summarize", "interpret", "classify"],
            "difficulty_range": (2, 3),
            "question_types": ["mcq", "open_ended"]
        },
        3: {
            "level": "Apply",
            "description": "Use information in new situations",
            "verbs": ["apply", "implement", "solve", "use", "demonstrate"],
            "difficulty_range": (3, 4),
            "question_types": ["open_ended", "matching"]
        },
        4: {
            "level": "Analyze",
            "description": "Draw connections among ideas",
            "verbs": ["analyze", "compare", "contrast", "examine", "categorize"],
            "difficulty_range": (3, 5),
            "question_types": ["open_ended", "matching"]
        },
        5: {
            "level": "Evaluate",
            "description": "Justify a decision or course of action",
            "verbs": ["evaluate", "critique", "judge", "defend", "assess"],
            "difficulty_range": (4, 5),
            "question_types": ["open_ended"]
        },
        6: {
            "level": "Create",
            "description": "Produce new or original work",
            "verbs": ["create", "design", "construct", "develop", "formulate"],
            "difficulty_range": (4, 5),
            "question_types": ["open_ended"]
        }
    }
    
    def __init__(self):
        logger.info("BloomAgent initialized")
    
    def get_level_info(self, level: int) -> Dict[str, Any]:
        """Récupère les informations d'un niveau Bloom."""
        return self.BLOOM_TAXONOMY.get(level, self.BLOOM_TAXONOMY[2])
    
    def get_recommended_question_type(self, bloom_level: int) -> str:
        """Recommande un type de question selon le niveau Bloom."""
        level_info = self.get_level_info(bloom_level)
        question_types = level_info.get("question_types", ["mcq"])
        # Retourner le premier type (le plus adapté)
        return question_types[0]
    
    def get_difficulty_range(self, bloom_level: int) -> tuple:
        """Retourne la plage de difficulté recommandée."""
        level_info = self.get_level_info(bloom_level)
        return level_info.get("difficulty_range", (2, 3))
    
    def suggest_learning_activities(self, bloom_level: int) -> List[str]:
        """Suggère des activités d'apprentissage selon le niveau."""
        level_info = self.get_level_info(bloom_level)
        verbs = level_info.get("verbs", [])
        
        activities = [
            f"{verb.capitalize()} key concepts in the subject"
            for verb in verbs[:3]
        ]
        
        return activities
    
    def get_progression_path(self, current_level: int) -> Dict[str, Any]:
        """Génère le chemin de progression depuis le niveau actuel."""
        path = []
        for level in range(current_level, 7):
            info = self.get_level_info(level)
            path.append({
                "level": level,
                "label": info["level"],
                "description": info["description"],
                "is_current": level == current_level,
                "is_completed": level < current_level
            })
        
        return {
            "current_level": current_level,
            "next_level": min(current_level + 1, 6),
            "path": path,
            "completion_percentage": ((current_level - 1) / 5) * 100
        }