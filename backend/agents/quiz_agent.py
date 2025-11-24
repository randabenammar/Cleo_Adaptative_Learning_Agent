import logging
import json
from typing import Dict, Any, List, Optional

logger = logging.getLogger("cleo.quiz_agent")


class QuizAgent:
    """
    Agent spécialisé dans la génération de questions adaptatives
    selon le niveau Bloom, le sujet, et la performance de l'apprenant.
    """
    
    BLOOM_LEVELS = {
        1: "Remember",
        2: "Understand", 
        3: "Apply",
        4: "Analyze",
        5: "Evaluate",
        6: "Create"
    }
    
    QUESTION_TYPES = ["mcq", "open_ended", "matching", "true_false"]
    
    def __init__(self, groq_client):
        self.groq_client = groq_client
        logger.info("QuizAgent initialized")
    
    def generate_questions(
    self,
    subject: str,
    topic: str,
    bloom_level: int = 2,
    question_type: str = "mcq",
    num_questions: int = 5,
    difficulty: int = 3
) -> List[Dict[str, Any]]:
        """Génère des questions adaptatives."""
        bloom_label = self.BLOOM_LEVELS.get(bloom_level, "Understand")
        
        type_instructions = {
            "mcq": self._get_mcq_instructions(),
            "open_ended": self._get_open_instructions(),
            "matching": self._get_matching_instructions(),
            "true_false": self._get_true_false_instructions()
        }
        
        instruction = type_instructions.get(question_type, type_instructions["mcq"])
        
        # ⭐ Adapter max_tokens selon le type
        max_tokens_map = {
            "matching": 2500,      # Plus long à cause de la structure
            "open_ended": 1500,
            "mcq": 1200,
            "true_false": 800
        }
        max_tokens = max_tokens_map.get(question_type, 1500)
        
        prompt = f"""You are an expert educational assessment creator. Generate {num_questions} high-quality {question_type} questions.

    Subject: {subject}
    Topic: {topic}
    Bloom Taxonomy Level: {bloom_level} - {bloom_label}
    Difficulty: {difficulty}/5

    {instruction}

    Generate a JSON array of {num_questions} questions following this exact structure:
    {self._get_question_template(question_type)}

    CRITICAL RULES:
    - Output ONLY valid JSON, no markdown, no explanations, no comments
    - Start with [ and end with ]
    - Use double quotes for all strings
    - NO trailing commas after last item in arrays or objects
    - Questions must target Bloom level {bloom_level} ({bloom_label})

    Generate the JSON array now:"""

        try:
            response = self.groq_client.chat(prompt, max_tokens=max_tokens)
            
            # ⭐ Logger la réponse complète pour matching
            if question_type == "matching":
                logger.info("Full Groq response for matching:\n%s", response)
            else:
                logger.info("Raw Groq response (first 500 chars): %s", response[:500])
            
            # Parsing JSON
            questions = self._extract_json_from_response(response)
            
            if not questions:
                logger.warning("Failed to parse JSON, using fallback")
                return self._get_fallback_questions(subject, topic, question_type, num_questions)
        
            # ⭐ Valider les questions matching
            if question_type == "matching":
                valid_questions = []
                for q in questions:
                    if self._validate_matching_question(q):
                        valid_questions.append(q)
                    else:
                        logger.warning("Skipping invalid matching question")
                
                if not valid_questions:
                    logger.warning("No valid matching questions, using fallback")
                    return self._get_fallback_questions(subject, topic, question_type, num_questions)
                
                questions = valid_questions

            # Enrichir avec métadonnées
            for idx, q in enumerate(questions):
                q["question_id"] = f"{subject.lower().replace(' ', '_')}_{topic.lower().replace(' ', '_')}_{idx+1}"
                q["bloom_level"] = bloom_level
                q["bloom_label"] = bloom_label
                q["difficulty"] = difficulty
                q["subject"] = subject
                q["topic"] = topic
                q["question_type"] = question_type
            
            logger.info("✓ Generated %d %s questions for %s (Bloom=%d)", 
                    len(questions), question_type, topic, bloom_level)
            return questions
        
        except Exception as e:
            logger.exception("Failed to generate questions: %s", e)
            return self._get_fallback_questions(subject, topic, question_type, num_questions)
        

    def _extract_json_from_response(self, response: str) -> Optional[List[Dict[str, Any]]]:
        """
        Extrait et parse le JSON d'une réponse LLM, même avec du texte parasite.
        """
        import re
        
        # Méthode 1: Chercher un bloc JSON entre ```json et ```
        if "```json" in response:
            match = re.search(r'```json\s*(\[.*?\])\s*```', response, re.DOTALL)
            if match:
                json_str = self._clean_json_string(match.group(1))
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    logger.warning("Failed to parse JSON from ```json block: %s", e)
        
        # Méthode 2: Chercher un bloc entre ``` et ```
        if "```" in response:
            match = re.search(r'```\s*(\[.*?\])\s*```', response, re.DOTALL)
            if match:
                json_str = self._clean_json_string(match.group(1))
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    logger.warning("Failed to parse JSON from ``` block: %s", e)
        
        # Méthode 3: Chercher un array JSON [ ... ] dans la réponse
        match = re.search(r'\[\s*\{.*?\}\s*\]', response, re.DOTALL)
        if match:
            json_str = self._clean_json_string(match.group(0))
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse extracted JSON array: %s", e)
                # ⭐ Sauvegarder pour debug
                self._save_failed_response(response, f"JSON parse error: {e}")
        
        # Méthode 4: Nettoyer et essayer de parser la réponse entière
        cleaned = response.strip()
        if '[' in cleaned:
            cleaned = cleaned[cleaned.index('['):]
        if ']' in cleaned:
            cleaned = cleaned[:cleaned.rindex(']')+1]
        
        cleaned = self._clean_json_string(cleaned)
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error("All JSON parsing methods failed. Last error: %s", e)
            logger.error("Cleaned JSON attempt: %s", cleaned[:500])
            self._save_failed_response(response, f"All methods failed: {e}")
            return None
        
    def _clean_json_string(self, json_str: str) -> str:
        """
        Nettoie un JSON string pour retirer les erreurs communes.
        """
        import re
        
        # Retirer les trailing commas avant } ou ]
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # ⭐ Retirer les doublons de clés (comme "correct_matches" apparaissant 2 fois)
        # Pattern: trouve "correct_matches": [...], suivi de "correct_matches": [...]
        json_str = re.sub(
            r'("correct_matches"\s*:\s*\[.*?\]),\s*("correct_matches"\s*:\s*\[.*?\])',
            r'\2',  # Garde seulement le second
            json_str,
            flags=re.DOTALL
        )
        
        return json_str.strip()   
    

    def _validate_matching_question(self, question: Dict[str, Any]) -> bool:
        """Valide qu'une question matching a la structure correcte."""
        required_fields = ["question_text", "left_items", "right_items", "correct_matches"]
        
        for field in required_fields:
            if field not in question:
                logger.warning("Missing field '%s' in matching question", field)
                return False
        
        left_items = question.get("left_items", [])
        right_items = question.get("right_items", [])
        correct_matches = question.get("correct_matches", [])
        
        # Vérifier qu'il y a 5 items de chaque côté
        if len(left_items) != 5 or len(right_items) != 5:
            logger.warning("Matching question must have exactly 5 left and 5 right items")
            return False
        
        # Vérifier que correct_matches a 5 paires
        if len(correct_matches) != 5:
            logger.warning("Matching question must have exactly 5 correct_matches")
            return False
        
        # Vérifier que chaque match a "left" et "right"
        for match in correct_matches:
            if "left" not in match or "right" not in match:
                logger.warning("Invalid correct_match format: %s", match)
                return False
        
        return True

    def _get_mcq_instructions(self) -> str:
        return """For Multiple Choice Questions (MCQ):
- Provide 4 options (A, B, C, D)
- Only ONE correct answer
- Distractors should be plausible but clearly incorrect
- Avoid "all of the above" or "none of the above"
- Include brief explanation for the correct answer"""
    
    def _get_open_instructions(self) -> str:
        return """For Open-Ended Questions:
- Questions should require 2-3 sentence answers
- Clear evaluation criteria
- Sample answer provided
- Keywords that must be present in correct answers"""
    
    def _get_matching_instructions(self) -> str:
        return """For Matching Questions - STRICT FORMAT REQUIRED:

    STRUCTURE:
    - Provide EXACTLY 5 items to match (L1-L5 and R1-R5)
    - Left items: concepts, terms, or key words
    - Right items: definitions, descriptions, or explanations
    - Shuffle right items (different order than left)
    - One correct match per left item

    CRITICAL JSON REQUIREMENTS:
    - Use IDs: "L1", "L2", "L3", "L4", "L5" for left
    - Use IDs: "R1", "R2", "R3", "R4", "R5" for right
    - Text must be clear and distinct
    - correct_matches must have ALL 5 pairs
    - NO trailing commas
    - NO comments in JSON

    Example (you must follow this EXACT structure):
    [
    {
        "question_text": "Match the Big Data concepts:",
        "left_items": [
        {"id": "L1", "text": "HDFS"},
        {"id": "L2", "text": "MapReduce"}
        ],
        "right_items": [
        {"id": "R1", "text": "Processing framework"},
        {"id": "R2", "text": "Distributed storage"}
        ],
        "correct_matches": [
        {"left": "L1", "right": "R2"},
        {"left": "L2", "right": "R1"}
        ],
        "points": 20
    }
    ]"""
        
        
    def _get_true_false_instructions(self) -> str:
        return """For True/False Questions:
- Statement should be clearly true or false
- Avoid ambiguous statements
- Provide explanation for the correct answer"""
    
    def _get_question_template(self, question_type: str) -> str:
        if question_type == "mcq":
            return """[
  {
    "question_text": "What is...?",
    "options": [
      {"key": "A", "text": "Option A"},
      {"key": "B", "text": "Option B"},
      {"key": "C", "text": "Option C"},
      {"key": "D", "text": "Option D"}
    ],
    "correct_answer": "B",
    "explanation": "Explanation of why B is correct",
    "points": 10
  }
]"""
        elif question_type == "open_ended":
            return """[
  {
    "question_text": "Explain...",
    "sample_answer": "A model answer (2-3 sentences)",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "min_words": 30,
    "points": 15
  }
]"""
        elif question_type == "matching":
            return """[
    {
        "question_text": "Match concepts with definitions:",
        "left_items": [
        {"id": "L1", "text": "First concept"},
        {"id": "L2", "text": "Second concept"},
        {"id": "L3", "text": "Third concept"},
        {"id": "L4", "text": "Fourth concept"},
        {"id": "L5", "text": "Fifth concept"}
        ],
        "right_items": [
        {"id": "R1", "text": "Definition for first"},
        {"id": "R2", "text": "Definition for second"},
        {"id": "R3", "text": "Definition for third"},
        {"id": "R4", "text": "Definition for fourth"},
        {"id": "R5", "text": "Definition for fifth"}
        ],
        "correct_matches": [
        {"left": "L1", "right": "R1"},
        {"left": "L2", "right": "R2"},
        {"left": "L3", "right": "R3"},
        {"left": "L4", "right": "R4"},
        {"left": "L5", "right": "R5"}
        ],
        "points": 20
    }
    ]"""
        
        else:  # true_false
            return """[
  {
    "question_text": "Statement to evaluate",
    "correct_answer": true,
    "explanation": "Why this is true/false",
    "points": 5
  }
]"""
    
    def _save_failed_response(self, response: str, error: str):
        """Sauvegarde les réponses qui échouent pour debug."""
        import datetime
        import os
        
        debug_dir = "debug_responses"
        os.makedirs(debug_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(debug_dir, f"failed_response_{timestamp}.txt")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"ERROR: {error}\n")
            f.write("="*80 + "\n")
            f.write("RESPONSE:\n")
            f.write(response)
        
        logger.info("Saved failed response to %s", filename)

    def _get_fallback_questions(self, subject: str, topic: str, question_type: str, num: int) -> List[Dict[str, Any]]:
        """Questions de secours si génération IA échoue."""
        
        if question_type == "matching":
            # Fallback plus intelligent pour matching
            return [{
                "question_id": f"fallback_matching_{i}",
                "question_text": f"Match these {topic} concepts (Question {i+1}):",
                "left_items": [
                    {"id": "L1", "text": f"{topic} Component A"},
                    {"id": "L2", "text": f"{topic} Component B"},
                    {"id": "L3", "text": f"{topic} Component C"},
                    {"id": "L4", "text": f"{topic} Component D"},
                    {"id": "L5", "text": f"{topic} Component E"}
                ],
                "right_items": [
                    {"id": "R1", "text": f"Definition of Component C"},
                    {"id": "R2", "text": f"Definition of Component A"},
                    {"id": "R3", "text": f"Definition of Component E"},
                    {"id": "R4", "text": f"Definition of Component B"},
                    {"id": "R5", "text": f"Definition of Component D"}
                ],
                "correct_matches": [
                    {"left": "L1", "right": "R2"},
                    {"left": "L2", "right": "R4"},
                    {"left": "L3", "right": "R1"},
                    {"left": "L4", "right": "R5"},
                    {"left": "L5", "right": "R3"}
                ],
                "points": 20,
                "bloom_level": 3,
                "question_type": "matching"
            } for i in range(num)]
        
        elif question_type == "mcq":
            return [{
                "question_id": f"fallback_mcq_{i}",
                "question_text": f"What is a key concept in {topic}?",
                "options": [
                    {"key": "A", "text": f"Concept A about {topic}"},
                    {"key": "B", "text": f"Concept B about {topic}"},
                    {"key": "C", "text": f"Concept C about {topic}"},
                    {"key": "D", "text": f"Concept D about {topic}"}
                ],
                "correct_answer": "A",
                "explanation": "This is the correct answer based on core principles.",
                "points": 10,
                "bloom_level": 2,
                "question_type": "mcq"
            } for i in range(num)]
        
        else:  # open_ended
            return [{
                "question_id": f"fallback_open_{i}",
                "question_text": f"Explain the key aspects of {topic} (Question {i+1})",
                "sample_answer": f"A comprehensive explanation of {topic} covering main concepts and applications.",
                "keywords": [topic.lower(), "definition", "application"],
                "min_words": 30,
                "points": 15,
                "bloom_level": 2,
                "question_type": "open_ended"
            } for i in range(num)]