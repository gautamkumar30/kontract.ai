"""
Google Gemini Service

Integrates with Google Gemini API for:
- Semantic similarity scoring
- Change impact summarization
- Risk explanation generation
"""

import google.generativeai as genai
from typing import Optional, Dict
import asyncio
from functools import lru_cache
import time


class GeminiService:
    """Service for Google Gemini API integration."""
    
    def __init__(self, api_key: str):
        """
        Initialize Gemini service.
        
        Args:
            api_key: Google Gemini API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 4.0  # 15 requests/min = 4 seconds between requests
    
    async def _rate_limit(self):
        """Enforce rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    async def calculate_semantic_similarity(
        self,
        text1: str,
        text2: str
    ) -> Optional[float]:
        """
        Calculate semantic similarity between two texts using Gemini.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1) or None if API fails
        """
        try:
            await self._rate_limit()
            
            prompt = f"""Compare these two contract clauses and rate their semantic similarity on a scale of 0 to 1, where:
- 1.0 = Identical meaning, even if worded differently
- 0.7-0.9 = Very similar meaning with minor differences
- 0.4-0.6 = Somewhat similar, but with notable differences
- 0.1-0.3 = Different meanings
- 0.0 = Completely unrelated

Clause 1:
{text1}

Clause 2:
{text2}

Respond with ONLY a number between 0 and 1, nothing else."""

            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            # Extract score from response
            score_text = response.text.strip()
            score = float(score_text)
            
            return min(1.0, max(0.0, score))
        
        except Exception as e:
            print(f"Gemini API error (similarity): {e}")
            return None
    
    async def generate_change_summary(
        self,
        old_text: str,
        new_text: str,
        change_type: str
    ) -> Optional[str]:
        """
        Generate a summary of what changed between two clause versions.
        
        Args:
            old_text: Original clause text
            new_text: New clause text
            change_type: Type of change (added/removed/modified)
            
        Returns:
            Summary text or None if API fails
        """
        try:
            await self._rate_limit()
            
            if change_type == "added":
                prompt = f"""This clause was newly added to a contract. Summarize what it means in 1-2 sentences:

{new_text}"""
            
            elif change_type == "removed":
                prompt = f"""This clause was removed from a contract. Summarize what was removed in 1-2 sentences:

{old_text}"""
            
            else:  # modified or rewritten
                prompt = f"""These two versions of a contract clause show a change. Summarize what changed in 1-2 sentences:

Original:
{old_text}

New:
{new_text}"""

            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            return response.text.strip()
        
        except Exception as e:
            print(f"Gemini API error (summary): {e}")
            return None
    
    async def explain_risk(
        self,
        clause_text: str,
        category: str,
        change_description: str
    ) -> Optional[str]:
        """
        Generate an explanation of why a change matters.
        
        Args:
            clause_text: The clause text
            category: Clause category (liability, data_usage, etc.)
            change_description: Description of what changed
            
        Returns:
            Risk explanation or None if API fails
        """
        try:
            await self._rate_limit()
            
            prompt = f"""A contract clause in the "{category}" category has changed. Explain why this matters to a business user in 2-3 sentences. Focus on practical implications.

Clause:
{clause_text}

Change:
{change_description}

Explain why this matters:"""

            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            return response.text.strip()
        
        except Exception as e:
            print(f"Gemini API error (risk explanation): {e}")
            return None
    
    async def classify_clause_category(self, clause_text: str) -> Optional[str]:
        """
        Use Gemini to classify clause category.
        
        Args:
            clause_text: Clause text
            
        Returns:
            Category name or None
        """
        try:
            await self._rate_limit()
            
            prompt = f"""Classify this contract clause into ONE of these categories:
- liability
- data_usage
- termination
- jurisdiction
- payment
- intellectual_property
- service_level
- marketing
- other

Clause:
{clause_text}

Respond with ONLY the category name, nothing else."""

            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            category = response.text.strip().lower()
            
            # Validate category
            valid_categories = [
                "liability", "data_usage", "termination", "jurisdiction",
                "payment", "intellectual_property", "service_level",
                "marketing", "other"
            ]
            
            if category in valid_categories:
                return category
            
            return "other"
        
        except Exception as e:
            print(f"Gemini API error (classification): {e}")
            return None
