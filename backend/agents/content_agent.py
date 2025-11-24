import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("cleo.content_agent")


class ContentAgent:
    """
    Agent spécialisé dans la génération de contenu pédagogique adaptatif :
    - Explications détaillées de concepts
    - Exemples pratiques
    - Analogies et métaphores
    - Ressources complémentaires
    - Résumés de cours
    """
    
    def __init__(self, groq_client):
        self.groq_client = groq_client
        logger.info("ContentAgent initialized")
    
    def generate_concept_explanation(
        self, 
        concept: str, 
        subject: str,
        bloom_level: int = 2,
        learner_background: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère une explication détaillée d'un concept selon le niveau Bloom.
        
        Args:
            concept: Le concept à expliquer (ex: "MapReduce", "Neural Networks")
            subject: Le sujet parent (ex: "Big Data", "Machine Learning")
            bloom_level: Niveau Bloom ciblé (1=Remember, 2=Understand, etc.)
            learner_background: Contexte de l'apprenant (optionnel)
            
        Returns:
            dict avec explanation, examples, analogies, resources
        """
        bloom_instructions = {
            1: "Provide a clear definition with key terms. Focus on memorization and recall.",
            2: "Explain the concept in simple terms with examples. Help learner understand 'why' and 'how'.",
            3: "Show practical applications and how to use the concept in real scenarios.",
            4: "Break down the concept into components, compare with alternatives, analyze pros/cons.",
            5: "Provide critical evaluation criteria, help assess quality and effectiveness.",
            6: "Guide learner to create new solutions or combine concepts innovatively."
        }
        
        instruction = bloom_instructions.get(bloom_level, bloom_instructions[2])
        background_context = f"\nLearner background: {learner_background}" if learner_background else ""
        
        prompt = f"""You are an expert educator creating adaptive learning content.

Subject: {subject}
Concept: {concept}
Target Bloom Level: {bloom_level} ({['', 'Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create'][bloom_level]})
Instruction: {instruction}{background_context}

Generate educational content in JSON format:
{{
  "explanation": "A clear, engaging explanation (3-4 paragraphs) tailored to Bloom level {bloom_level}",
  "key_points": ["Point 1", "Point 2", "Point 3"],
  "examples": [
    {{
      "title": "Example 1 Title",
      "description": "Detailed example description",
      "code_snippet": "Optional code if relevant"
    }}
  ],
  "analogies": [
    {{
      "analogy": "Real-world analogy",
      "explanation": "How it relates to the concept"
    }}
  ],
  "common_misconceptions": ["Misconception 1", "Misconception 2"],
  "further_reading": [
    {{
      "title": "Resource title",
      "url": "https://example.com",
      "type": "article/video/tutorial"
    }}
  ]
}}

Make it engaging, clear, and pedagogically sound."""

        try:
            response = self.groq_client.chat(prompt, max_tokens=1200)
            import json
            
            # Parse JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            content = json.loads(json_str)
            logger.info("Concept explanation generated: %s (Bloom=%d)", concept, bloom_level)
            return content
        
        except Exception as e:
            logger.exception("Failed to generate concept explanation: %s", e)
            return self._get_fallback_explanation(concept, subject, bloom_level)
    
    def generate_lesson_summary(
        self,
        subject: str,
        lesson_title: str,
        key_concepts: List[str]
    ) -> Dict[str, Any]:
        """
        Génère un résumé de leçon structuré.
        
        Args:
            subject: Nom du sujet
            lesson_title: Titre de la leçon
            key_concepts: Liste des concepts abordés
            
        Returns:
            dict avec summary, objectives, takeaways
        """
        concepts_str = ", ".join(key_concepts)
        
        prompt = f"""Create a comprehensive lesson summary for:

Subject: {subject}
Lesson: {lesson_title}
Key Concepts Covered: {concepts_str}

Generate a JSON response:
{{
  "executive_summary": "2-3 sentence overview of the lesson",
  "learning_objectives": ["Objective 1", "Objective 2", "Objective 3"],
  "main_points": [
    {{
      "point": "Main point title",
      "explanation": "Brief explanation"
    }}
  ],
  "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
  "practical_applications": ["Application 1", "Application 2"],
  "next_steps": ["What to study next", "Practice recommendations"]
}}

Make it actionable and student-friendly."""

        try:
            response = self.groq_client.chat(prompt, max_tokens=1000)
            import json
            
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            summary = json.loads(json_str)
            logger.info("Lesson summary generated: %s", lesson_title)
            return summary
        
        except Exception as e:
            logger.exception("Failed to generate lesson summary: %s", e)
            return self._get_fallback_summary(lesson_title)
    
    def generate_study_guide(
        self,
        subject: str,
        topics: List[str],
        exam_type: str = "conceptual"
    ) -> Dict[str, Any]:
        """
        Génère un guide d'étude personnalisé.
        
        Args:
            subject: Nom du sujet
            topics: Liste des topics à réviser
            exam_type: Type d'évaluation (conceptual, practical, mixed)
            
        Returns:
            dict avec study_plan, review_questions, tips
        """
        topics_str = "\n- ".join(topics)
        
        prompt = f"""Create a study guide for an upcoming {exam_type} assessment.

Subject: {subject}
Topics to Review:
- {topics_str}

Generate a JSON study guide:
{{
  "study_plan": [
    {{
      "day": 1,
      "topic": "Topic name",
      "activities": ["Activity 1", "Activity 2"],
      "time_allocation": "2 hours"
    }}
  ],
  "review_questions": [
    {{
      "question": "Review question",
      "bloom_level": 2,
      "answer_hint": "Hint for self-check"
    }}
  ],
  "memory_techniques": ["Technique 1", "Technique 2"],
  "exam_tips": ["Tip 1", "Tip 2"],
  "recommended_practice": ["Practice item 1", "Practice item 2"]
}}

Make it practical and time-efficient."""

        try:
            response = self.groq_client.chat(prompt, max_tokens=1200)
            import json
            
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            guide = json.loads(json_str)
            logger.info("Study guide generated for %s (%d topics)", subject, len(topics))
            return guide
        
        except Exception as e:
            logger.exception("Failed to generate study guide: %s", e)
            return self._get_fallback_study_guide(subject)
    
    def generate_practice_scenarios(
        self,
        subject: str,
        concept: str,
        difficulty: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Génère des scénarios pratiques pour application des concepts.
        
        Args:
            subject: Nom du sujet
            concept: Concept à pratiquer
            difficulty: Niveau de difficulté (1-5)
            
        Returns:
            Liste de scénarios pratiques
        """
        prompt = f"""Create practical application scenarios for learning.

Subject: {subject}
Concept: {concept}
Difficulty Level: {difficulty}/5

Generate 3 realistic scenarios in JSON:
[
  {{
    "scenario_id": 1,
    "title": "Scenario title",
    "context": "Realistic problem context",
    "challenge": "What the learner needs to do",
    "hints": ["Hint 1", "Hint 2"],
    "success_criteria": ["Criterion 1", "Criterion 2"]
  }}
]

Make scenarios relevant to real-world applications."""

        try:
            response = self.groq_client.chat(prompt, max_tokens=1000)
            import json
            
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            scenarios = json.loads(json_str)
            logger.info("Practice scenarios generated: %s (%d scenarios)", concept, len(scenarios))
            return scenarios
        
        except Exception as e:
            logger.exception("Failed to generate scenarios: %s", e)
            return self._get_fallback_scenarios(concept)
    
    # Fallback methods
    
    def _get_fallback_explanation(self, concept: str, subject: str, bloom_level: int) -> Dict[str, Any]:
        """Fallback si génération échoue."""
        return {
            "explanation": f"{concept} is an important concept in {subject}. "
                          f"It involves understanding key principles and their practical applications.",
            "key_points": [
                f"Definition of {concept}",
                "Core principles",
                "Practical applications"
            ],
            "examples": [
                {
                    "title": f"Basic {concept} Example",
                    "description": "A simple example to illustrate the concept",
                    "code_snippet": None
                }
            ],
            "analogies": [
                {
                    "analogy": "Think of it like organizing a library",
                    "explanation": "Each piece of information has its place"
                }
            ],
            "common_misconceptions": [
                f"{concept} is not the same as related concepts",
                "Common confusion points"
            ],
            "further_reading": []
        }
    
    def _get_fallback_summary(self, lesson_title: str) -> Dict[str, Any]:
        """Fallback summary."""
        return {
            "executive_summary": f"This lesson covered key aspects of {lesson_title}.",
            "learning_objectives": [
                f"Understand core concepts of {lesson_title}",
                "Apply knowledge in practical scenarios"
            ],
            "main_points": [
                {
                    "point": "Introduction",
                    "explanation": "Overview of the topic"
                }
            ],
            "key_takeaways": [
                "Key concepts were introduced",
                "Practical applications were discussed"
            ],
            "practical_applications": ["Real-world use cases"],
            "next_steps": ["Review the material", "Complete practice exercises"]
        }
    
    def _get_fallback_study_guide(self, subject: str) -> Dict[str, Any]:
        """Fallback study guide."""
        return {
            "study_plan": [
                {
                    "day": 1,
                    "topic": f"Review {subject} fundamentals",
                    "activities": ["Read notes", "Practice problems"],
                    "time_allocation": "2 hours"
                }
            ],
            "review_questions": [
                {
                    "question": f"What are the key concepts in {subject}?",
                    "bloom_level": 2,
                    "answer_hint": "Think about main topics covered"
                }
            ],
            "memory_techniques": ["Use flashcards", "Create mind maps"],
            "exam_tips": ["Review regularly", "Practice problems"],
            "recommended_practice": ["Past exercises", "Sample questions"]
        }
    
    def _get_fallback_scenarios(self, concept: str) -> List[Dict[str, Any]]:
        """Fallback scenarios."""
        return [
            {
                "scenario_id": 1,
                "title": f"Basic {concept} Application",
                "context": "You need to apply this concept in a practical situation",
                "challenge": "Solve the problem using your knowledge",
                "hints": ["Start with fundamentals", "Break down the problem"],
                "success_criteria": ["Correct application", "Clear explanation"]
            }
        ]