import os
from typing import List, Optional
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.llm.prompts import PromptTemplates

class GPTClient:
    def __init__(self):
        """Initialize the GPT client with API key from settings."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def generate_answer(
        self,
        question: str,
        context_chunks: List[str],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Generate an answer using GPT based on the question and context.
        
        Args:
            question: The user's question
            context_chunks: List of relevant text chunks from the manual
            model: The GPT model to use
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum length of the response
            
        Returns:
            Generated answer as a string
        """
        try:
            # Format context chunks
            formatted_context = PromptTemplates.format_context(context_chunks)
            
            # Get formatted messages using templates
            messages = PromptTemplates.format_question_prompt(
                context=formatted_context,
                question=question
            )
            
            # Call GPT
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Log the error and return a fallback response
            print(f"Error generating answer: {str(e)}")
            fallback_text = context_chunks[0] if context_chunks else "No relevant information found."
            return PromptTemplates.format_error_prompt(fallback_text)

# Create a singleton instance
gpt_client = GPTClient() 