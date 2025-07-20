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
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-2025-04-14")
        self.embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        
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

    async def generate_sub_questions(self, user_message: str, n: int = 3) -> List[str]:
        """
        Generate n sub-questions or reformulations for a user message using the LLM.
        Args:
            user_message (str): The original user message
            n (int): Number of sub-questions to generate
        Returns:
            List[str]: List of sub-questions
        """
        prompt = (
            f"Given the following user message, generate {n} different possible sub-questions or reformulations "
            f"that could help retrieve relevant information from a document knowledge base. "
            f"Return them as a numbered list.\n\nUser message: {user_message}\n\nSub-questions:"
        )
        messages = [
            {"role": "system", "content": "You are an expert assistant at reformulating user queries for document search."},
            {"role": "user", "content": prompt}
        ]
        response = await self.get_chat_completion(messages, temperature=0.3, max_tokens=256)
        # Parse the response as a numbered list
        sub_questions = []
        for line in response.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() and (line[1] == '.' or line[1] == ')')):
                # Remove leading number and dot/parenthesis
                sub_question = line[2:].strip()
                if sub_question:
                    sub_questions.append(sub_question)
            elif line:
                # If not numbered, just add the line
                sub_questions.append(line)
        # Ensure we only return up to n sub-questions
        return sub_questions[:n] 

    async def extract_keywords(self, text: str, n: int = 3) -> List[str]:
        """
        Extract the n most relevant keywords or entities from the text using OpenAI.
        Returns a list of keywords/entities.
        """
        prompt = (
            f"Extract the {n} most relevant keywords or entities from the following text. "
            "Return them as a comma-separated list.\n\n"
            f"{text}"
        )
        messages = [
            {"role": "system", "content": "You are an expert at extracting keywords and entities from text."},
            {"role": "user", "content": prompt}
        ]
        response = await self.get_chat_completion(messages, temperature=0.0, max_tokens=64)
        keywords = [kw.strip() for kw in response.split(",") if kw.strip()]
        return keywords[:n]

    async def rerank_chunks_with_threshold(self, user_message: str, chunks: List[Dict[str, Any]], threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Use OpenAI to re-rank chunks for relevance to the user_message. Only return chunks above the threshold.
        Each chunk is expected to have a 'content' field.
        """
        if not chunks:
            return []
        # Build a prompt for relevance scoring
        prompt = (
            "Given the following user message and a list of document chunks, score each chunk for relevance to the message on a scale from 0 (not relevant) to 1 (highly relevant). "
            "Return a JSON list of objects with 'index' and 'score'.\n\n"
            f"User message: {user_message}\n\n"
            "Chunks:\n" + "\n".join([f"{i+1}. {chunk['content']}" for i, chunk in enumerate(chunks)]) +
            "\n\nRespond with only the JSON list."
        )
        messages = [
            {"role": "system", "content": "You are an expert at evaluating document relevance."},
            {"role": "user", "content": prompt}
        ]
        import json
        response = await self.get_chat_completion(messages, temperature=0.0, max_tokens=256)
        try:
            scores = json.loads(response)
        except Exception:
            # fallback: if parsing fails, return all
            return chunks
        # Filter and sort chunks by score
        indexed_scores = {item['index']-1: item['score'] for item in scores if 'index' in item and 'score' in item}
        filtered = [chunk for i, chunk in enumerate(chunks) if indexed_scores.get(i, 0) >= threshold]
        # Optionally, sort by score descending
        filtered = sorted(filtered, key=lambda c: indexed_scores.get(chunks.index(c), 0), reverse=True)
        return filtered 