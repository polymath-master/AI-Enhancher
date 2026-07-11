"""
Accuracy Scoring Service - Evaluates response quality
"""

import re
import string
from typing import Dict, List, Optional, Tuple
from collections import Counter

from app.models.schemas import AccuracyScore
from app.utils.logger import logger

class AccuracyService:
    def __init__(self):
        self.threshold = 0.85
    
    async def score_response(
        self,
        prompt: str,
        response: str,
        context: Optional[str] = None
    ) -> AccuracyScore:
        """
        Score the accuracy/quality of a response
        Multiple metrics combined
        """
        try:
            # 1. Coherence score (sentence structure, grammar)
            coherence = self._score_coherence(response)
            
            # 2. Relevance score (how well it answers the prompt)
            relevance = self._score_relevance(prompt, response)
            
            # 3. Completeness score (covers key aspects)
            completeness = self._score_completeness(prompt, response)
            
            # 4. Factual consistency (self-consistency)
            factual = self._score_factual(response)
            
            # 5. Context adherence (if context provided)
            context_score = 1.0
            if context:
                context_score = self._score_context(context, response)
            
            # Weighted average
            weights = {
                "coherence": 0.25,
                "relevance": 0.30,
                "completeness": 0.20,
                "factual": 0.15,
                "context": 0.10
            }
            
            breakdown = {
                "coherence": coherence,
                "relevance": relevance,
                "completeness": completeness,
                "factual": factual,
                "context": context_score
            }
            
            score = sum(breakdown[k] * weights[k] for k in breakdown)
            
            # Generate suggestions if score is low
            suggestions = []
            if score < 0.7:
                suggestions = [
                    "Response could be more coherent",
                    "Consider adding more specific details",
                    "Review for factual accuracy"
                ]
            elif score < 0.85:
                suggestions = [
                    "Good but could be more concise",
                    "Add more supporting evidence"
                ]
            
            return AccuracyScore(
                score=score,
                confidence=self._calculate_confidence(breakdown),
                breakdown=breakdown,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Accuracy scoring failed: {e}")
            return AccuracyScore(
                score=0.5,
                confidence=0.0,
                breakdown={},
                suggestions=["Unable to score response"]
            )
    
    def _score_coherence(self, text: str) -> float:
        """Score coherence based on sentence structure"""
        try:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            if not sentences:
                return 0.0
            
            # Average sentence length (coherent text has varied length)
            lengths = [len(s.split()) for s in sentences]
            avg_len = sum(lengths) / len(lengths)
            variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
            
            # Normalize: ideal variance ~50-100
            coherence = 1 - min(1, abs(variance - 75) / 150)
            
            # Bonus for linking words
            linking_words = ['however', 'therefore', 'moreover', 'furthermore', 'although', 'because']
            linking_count = sum(text.lower().count(w) for w in linking_words)
            linking_bonus = min(0.2, linking_count * 0.02)
            
            return min(1.0, coherence + linking_bonus)
            
        except:
            return 0.5
    
    def _score_relevance(self, prompt: str, response: str) -> float:
        """Score how relevant the response is to the prompt"""
        try:
            # Word overlap (simple but effective)
            prompt_words = set(prompt.lower().split())
            response_words = set(response.lower().split())
            
            if not prompt_words:
                return 0.5
            
            overlap = len(prompt_words & response_words) / len(prompt_words)
            return min(1.0, overlap * 1.2)  # Slight boost
            
        except:
            return 0.5
    
    def _score_completeness(self, prompt: str, response: str) -> float:
        """Score completeness based on response length and structure"""
        try:
            # Check if response has intro, body, conclusion
            has_intro = any(word in response[:200].lower() for word in ['first', 'to begin', 'overview'])
            has_conclusion = any(word in response[-200:].lower() for word in ['finally', 'in conclusion', 'therefore'])
            
            structure_score = 0.5
            if has_intro:
                structure_score += 0.25
            if has_conclusion:
                structure_score += 0.25
            
            # Length: too short or too long reduces score
            word_count = len(response.split())
            if 50 < word_count < 500:
                length_score = 1.0
            elif 20 < word_count < 50 or 500 < word_count < 1000:
                length_score = 0.7
            else:
                length_score = 0.4
            
            return (structure_score + length_score) / 2
            
        except:
            return 0.5
    
    def _score_factual(self, text: str) -> float:
        """Score factual consistency (self-consistency)"""
        try:
            # Check for contradictions (simplified)
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            if len(sentences) < 2:
                return 0.5
            
            # Check for "I think", "maybe", "could" - indicates uncertainty
            uncertainty_words = ['maybe', 'perhaps', 'could be', 'might be', 'i think', 'i believe']
            uncertainty_count = sum(text.lower().count(w) for w in uncertainty_words)
            
            # More uncertainty = lower factual score
            uncertainty_penalty = min(0.5, uncertainty_count * 0.05)
            
            # Check for consistency of named entities (simple check)
            # If same entity referenced differently, penalty
            entity_consistency = 1.0
            
            return max(0.3, 1.0 - uncertainty_penalty) * entity_consistency
            
        except:
            return 0.5
    
    def _score_context(self, context: str, response: str) -> float:
        """Score how well the response adheres to context"""
        try:
            context_words = set(context.lower().split())
            response_words = set(response.lower().split())
            
            if not context_words:
                return 0.5
            
            overlap = len(context_words & response_words) / len(context_words)
            return min(1.0, overlap * 1.5)
            
        except:
            return 0.5
    
    def _calculate_confidence(self, breakdown: Dict[str, float]) -> float:
        """Calculate confidence based on metric agreement"""
        if not breakdown:
            return 0.0
        
        values = list(breakdown.values())
        if len(values) < 2:
            return 0.5
        
        # High confidence if scores are consistent
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        
        # Low variance = high confidence
        confidence = 1 - min(1, variance * 2)
        return confidence

accuracy_service = AccuracyService()
