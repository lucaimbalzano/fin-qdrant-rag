import json
import os
from typing import Dict, Any, List
from pathlib import Path

class StockAssistantConfig:
    """Configuration for the stock trading assistant."""
    
    def __init__(self, config_path: str = "config/stock_assistant.json"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file or use defaults."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._get_default_config()
        except Exception as e:
            print(f"Warning: Could not load config from {self.config_path}, using defaults: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "system_prompt": """You are an expert financial advisor and stock market analyst. You have deep knowledge of trading strategies, market analysis, and financial instruments.

Your expertise includes:
- Technical analysis and chart patterns
- Fundamental analysis of companies
- Risk management strategies
- Portfolio diversification
- Market psychology and sentiment analysis
- Trading psychology and discipline

When responding to users:
1. Always provide well-reasoned analysis
2. Consider both technical and fundamental factors
3. Emphasize risk management
4. Be clear about the limitations of any advice
5. Use your memory of previous conversations to provide personalized advice
6. When discussing specific stocks, mention both opportunities and risks

Remember: Past performance doesn't guarantee future results. Always encourage users to do their own research and consider consulting with licensed financial advisors for personalized advice.""",
            
            "memory_settings": {
                "short_term_limit": 10,
                "long_term_limit": 50,
                "short_term_context_limit": 5,
                "long_term_context_limit": 10
            },
            
            "openai_settings": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 1000,
                "embedding_model": "text-embedding-ada-002"
            },
            
            "response_templates": {
                "greeting": "Hello! I'm your AI financial advisor. I'm here to help you with stock market analysis, trading strategies, and investment insights. What would you like to discuss today?",
                "risk_disclaimer": "\n\n⚠️ **Important Disclaimer**: This is for educational purposes only. Past performance doesn't guarantee future results. Always do your own research and consider consulting with licensed financial advisors for personalized advice.",
                "memory_context": "Based on our previous conversations, I remember: {context}"
            },
            
            "function_definitions": [
                {
                    "name": "analyze_stock",
                    "description": "Analyze a specific stock with technical and fundamental analysis",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock symbol to analyze"
                            },
                            "analysis_type": {
                                "type": "string",
                                "enum": ["technical", "fundamental", "both"],
                                "description": "Type of analysis to perform"
                            }
                        },
                        "required": ["symbol"]
                    }
                },
                {
                    "name": "get_market_sentiment",
                    "description": "Get current market sentiment and trends",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "market": {
                                "type": "string",
                                "description": "Market to analyze (e.g., 'US', 'EU', 'global')"
                            }
                        }
                    }
                }
            ]
        }
    
    def get_system_prompt(self) -> str:
        """Get the system prompt."""
        return self.config["system_prompt"]
    
    def get_memory_settings(self) -> Dict[str, Any]:
        """Get memory settings."""
        return self.config["memory_settings"]
    
    def get_openai_settings(self) -> Dict[str, Any]:
        """Get OpenAI settings."""
        return self.config["openai_settings"]
    
    def get_response_templates(self) -> Dict[str, str]:
        """Get response templates."""
        return self.config["response_templates"]
    
    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """Get function definitions for OpenAI function calling."""
        return self.config["function_definitions"]
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values."""
        self.config.update(updates)
        self.save_config() 