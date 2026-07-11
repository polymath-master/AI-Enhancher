"""
Multi-Perspective Debate Service
"""

import asyncio
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.ollama import ollama_service
from app.services.accuracy import accuracy_service
from app.models.schemas import DebateRequest, DebateRound, DebateResponse, ModelSettings
from app.utils.logger import logger

class DebateService:
    def __init__(self):
        self.debates = {}
    
    async def conduct_debate(self, request: DebateRequest) -> DebateResponse:
        """Orchestrate multi-round debate with deterministic settings"""
        start_time = datetime.now()
        request.settings.temperature = 0.0
        request.settings.seed = 40
        
        logger.info(f"🎭 Starting debate on '{request.topic}'")
        
        # Generate perspectives if not provided
        if not request.perspectives:
            request.perspectives = await self._generate_perspectives(
                request.topic,
                request.num_participants
            )
        
        rounds = []
        current_arguments = {}
        
        for round_num in range(1, request.num_rounds + 1):
            logger.info(f"  Round {round_num}/{request.num_rounds}")
            round_args = []
            
            for i, perspective in enumerate(request.perspectives):
                # Build context
                context = self._build_context(rounds, perspective)
                
                # Generate argument
                arg = await self._generate_argument(
                    request.topic,
                    perspective,
                    context,
                    request.settings
                )
                
                # Generate counter-arguments
                counters = []
                for j, other in enumerate(request.perspectives):
                    if i != j and other in current_arguments:
                        counter = await self._generate_counter(
                            request.topic,
                            perspective,
                            other,
                            current_arguments[other],
                            request.settings
                        )
                        counters.append({
                            "against": other,
                            "counter": counter
                        })
                
                round_args.append({
                    "speaker": perspective,
                    "argument": arg,
                    "counter_arguments": counters
                })
                current_arguments[perspective] = arg
            
            rounds.append(DebateRound(
                round_num=round_num,
                arguments=round_args
            ))
        
        # Generate summary and winner
        summary = await self._generate_summary(
            request.topic,
            rounds,
            request.perspectives
        )
        
        winner = await self._determine_winner(
            request.topic,
            rounds,
            request.perspectives
        )
        
        # Score accuracy
        accuracy = await accuracy_service.score_response(
            request.topic,
            summary or "Debate completed"
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return DebateResponse(
            request_id=str(id(request)),
            topic=request.topic,
            rounds=rounds,
            summary=summary,
            winner=winner,
            accuracy_score=accuracy.score,
            processing_time=processing_time,
            total_tokens=len(summary) // 4 if summary else 0
        )
    
    async def _generate_perspectives(self, topic: str, count: int) -> List[str]:
        """Generate diverse perspectives"""
        prompt = f"""Generate {count} distinct perspectives on '{topic}'.
        Each perspective should be a different stakeholder or viewpoint.
        Return as a numbered list with only the perspective names.
        Example:
        1. Environmentalist
        2. Economist
        3. Social Justice Advocate"""
        
        response = await ollama_service.generate(
            prompt=prompt,
            settings=ModelSettings(temperature=0.0, seed=40),
            system_prompt="You are a neutral debate moderator."
        )
        
        perspectives = []
        for line in response.response.split('\n'):
            line = line.strip()
            if line and any(c.isdigit() for c in line):
                parts = line.split('.', 1)
                if len(parts) > 1:
                    perspectives.append(parts[1].strip())
        
        return perspectives[:count] if perspectives else [f"Perspective {i+1}" for i in range(count)]
    
    async def _generate_argument(
        self,
        topic: str,
        perspective: str,
        context: str,
        settings: ModelSettings
    ) -> str:
        """Generate a debate argument"""
        prompt = f"""Topic: {topic}
        Your perspective: {perspective}
        Context from previous rounds: {context}
        
        Present a compelling argument from your perspective.
        Be specific, logical, and persuasive.
        Use evidence, reasoning, and examples.
        Length: 3-5 substantial paragraphs."""
        
        response = await ollama_service.generate(
            prompt=prompt,
            settings=settings,
            system_prompt=f"You are a skilled debater representing the {perspective} perspective. Be persuasive and logical."
        )
        return response.response
    
    async def _generate_counter(
        self,
        topic: str,
        my_perspective: str,
        target_perspective: str,
        target_argument: str,
        settings: ModelSettings
    ) -> str:
        """Generate counter-argument"""
        prompt = f"""Topic: {topic}
        Your perspective: {my_perspective}
        Opponent perspective: {target_perspective}
        Opponent's argument: {target_argument}
        
        Provide 3 strong counter-arguments against the opponent's position.
        Focus on logical flaws, missing evidence, and alternative interpretations.
        """
        
        response = await ollama_service.generate(
            prompt=prompt,
            settings=settings,
            system_prompt=f"You are a debater representing {my_perspective}"
        )
        return response.response
    
    async def _generate_summary(
        self,
        topic: str,
        rounds: List[DebateRound],
        perspectives: List[str]
    ) -> str:
        """Generate debate summary"""
        formatted_rounds = self._format_rounds(rounds)
        
        prompt = f"""Topic: {topic}
        Perspectives: {', '.join(perspectives)}
        
        Debate summary:
        {formatted_rounds}
        
        Provide a balanced, neutral summary of this debate.
        Highlight:
        1. Key arguments from each perspective
        2. Areas of agreement
        3. Most compelling points
        4. Unresolved questions
        """
        
        response = await ollama_service.generate(
            prompt=prompt,
            settings=ModelSettings(temperature=0.0, seed=40),
            system_prompt="You are a neutral debate analyst."
        )
        return response.response
    
    async def _determine_winner(
        self,
        topic: str,
        rounds: List[DebateRound],
        perspectives: List[str]
    ) -> str:
        """Determine the most persuasive perspective"""
        formatted_rounds = self._format_rounds(rounds)
        
        prompt = f"""Topic: {topic}
        Perspectives: {', '.join(perspectives)}
        
        Debate summary:
        {formatted_rounds}
        
        Based on logic, evidence, and persuasive power, which perspective won?
        Return ONLY the perspective name. If tie, say 'Tie'."""
        
        response = await ollama_service.generate(
            prompt=prompt,
            settings=ModelSettings(temperature=0.0, seed=40),
            system_prompt="You are a neutral debate judge."
        )
        return response.response.strip()
    
    def _format_rounds(self, rounds: List[DebateRound]) -> str:
        """Format rounds for context"""
        formatted = []
        for round_obj in rounds:
            formatted.append(f"Round {round_obj.round_num}:")
            for arg in round_obj.arguments:
                formatted.append(f"  {arg['speaker']}: {arg['argument'][:200]}...")
        return "\n".join(formatted)
    
    def _build_context(self, rounds: List[DebateRound], current_perspective: str) -> str:
        """Build context from previous rounds"""
        if not rounds:
            return "Opening round - present your initial argument."
        
        context = "Previous arguments:\n"
        last_round = rounds[-1]
        for arg in last_round.arguments:
            if arg.get('speaker') != current_perspective:
                arg_text = arg.get('argument', '')[:300]
                context += f"- {arg['speaker']}: {arg_text}...\n"
        
        return context

debate_service = DebateService()
