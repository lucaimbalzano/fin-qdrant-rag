import os
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from core.logging.config import get_logger

logger = get_logger("openai_client")

class OpenAIClient:
    """OpenAI API client wrapper for handling embeddings and chat completions."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
        
        logger.info(f"OpenAI client initialized with model: {self.model}")
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of texts.
        
        Args:
            texts (List[str]): List of texts to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            embeddings = [data.embedding for data in response.data]
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    async def get_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Get chat completion from OpenAI.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries
            temperature (float): Sampling temperature
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            str: The generated response
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"Generated chat completion with {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"Error generating chat completion: {e}")
            raise
    
    async def get_chat_completion_with_functions(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        function_call: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Get chat completion with function calling support.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries
            functions (List[Dict[str, Any]]): List of function definitions
            function_call (Optional[str]): Function call strategy
            temperature (float): Sampling temperature
            
        Returns:
            Dict[str, Any]: Response with function call if applicable
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=functions,
                function_call=function_call,
                temperature=temperature
            )
            
            choice = response.choices[0]
            result = {
                "content": choice.message.content,
                "function_call": choice.message.function_call
            }
            
            logger.info("Generated chat completion with function calling")
            return result
            
        except Exception as e:
            logger.error(f"Error generating chat completion with functions: {e}")
            raise 