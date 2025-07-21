import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.logging.config import get_logger

logger = get_logger("memory_strategy")


"""
Memory Architecture Pattern: Hybrid Memory System
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Short-Term    │    │   Long-Term     │    │   Knowledge     │
│   Memory        │    │   Memory        │    │   Base          │
│   (Redis)       │    │   (Qdrant)      │    │   (Qdrant)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
│ • Recent convos │    │ • Important     │    │ • PDF content   │
│ • Session data  │    │   exchanges     │    │ • News feeds    │
│ • TTL: 24h      │    │ • User insights │    │ • Market data   │
│ • Fast access   │    │ • Persistent    │    │ • Static docs   │
└─────────────────┘    └─────────────────┘    └─────────────────┘

Strategy Pattern - Different memory strategies
Repository Pattern - Abstract memory storage
Factory Pattern - Memory item creation
"""

class MemoryStrategy(ABC):
    """Abstract base class for memory strategies."""
    
    @abstractmethod
    def should_store(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Determine if content should be stored in long-term memory."""
        pass
    
    @abstractmethod
    def get_memory_type(self) -> str:
        """Get the memory type for this strategy."""
        pass
    
    @abstractmethod
    def get_importance_score(self, content: str, metadata: Dict[str, Any]) -> float:
        """Calculate importance score (0.0 to 1.0) for the content."""
        pass

class ConversationMemoryStrategy(MemoryStrategy):
    """Strategy for storing important conversation exchanges."""
    
    def __init__(self):
        self.important_keywords = [
            "stock", "trading", "investment", "portfolio", "analysis", 
            "strategy", "risk", "market", "price", "earnings", "dividend",
            "technical", "fundamental", "chart", "pattern", "indicator"
        ]
        self.insight_keywords = [
            "learned", "discovered", "found", "realized", "understood",
            "important", "key", "critical", "essential", "valuable"
        ]
    
    def should_store(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Determine if conversation should be stored."""
        content_lower = content.lower()
        
        # Check for financial keywords
        has_financial_content = any(keyword in content_lower for keyword in self.important_keywords)
        
        # Check for insights or learning
        has_insight = any(keyword in content_lower for keyword in self.insight_keywords)
        
        # Check for specific user requests
        has_specific_request = any(phrase in content_lower for phrase in [
            "remember this", "save this", "important", "note this"
        ])
        
        # Check metadata for importance flag
        is_flagged_important = metadata.get("important", False)
        
        return has_financial_content or has_insight or has_specific_request or is_flagged_important
    
    def get_memory_type(self) -> str:
        return "conversation"
    
    def get_importance_score(self, content: str, metadata: Dict[str, Any]) -> float:
        """Calculate importance score based on content analysis."""
        content_lower = content.lower()
        score = 0.0
        
        # Base score for financial content
        financial_keywords = sum(1 for keyword in self.important_keywords if keyword in content_lower)
        score += min(financial_keywords * 0.2, 0.6)
        
        # Bonus for insights
        insight_keywords = sum(1 for keyword in self.insight_keywords if keyword in content_lower)
        score += min(insight_keywords * 0.15, 0.3)
        
        # Bonus for specific importance markers
        if any(phrase in content_lower for phrase in ["remember this", "save this", "important"]):
            score += 0.2
        
        # Metadata importance flag
        if metadata.get("important", False):
            score += 0.3
        
        # Length bonus (longer conversations might be more important)
        if len(content) > 200:
            score += 0.1
        
        return min(score, 1.0)

class InsightMemoryStrategy(MemoryStrategy):
    """Strategy for storing user insights and preferences."""
    
    def __init__(self):
        self.insight_patterns = [
            "i prefer", "i like", "i don't like", "i want", "i need",
            "my goal", "my target", "my risk tolerance", "my strategy",
            "i learned", "i discovered", "i realized", "i understand"
        ]
    
    def should_store(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Determine if content contains user insights."""
        content_lower = content.lower()
        
        has_insight_pattern = any(pattern in content_lower for pattern in self.insight_patterns)
        is_flagged_insight = metadata.get("insight", False)
        
        return has_insight_pattern or is_flagged_insight
    
    def get_memory_type(self) -> str:
        return "insight"
    
    def get_importance_score(self, content: str, metadata: Dict[str, Any]) -> float:
        """Calculate importance score for insights."""
        content_lower = content.lower()
        score = 0.0
        
        # Base score for insight patterns
        insight_patterns = sum(1 for pattern in self.insight_patterns if pattern in content_lower)
        score += min(insight_patterns * 0.3, 0.7)
        
        # Bonus for personal preferences
        if any(word in content_lower for word in ["prefer", "like", "want", "need"]):
            score += 0.2
        
        # Bonus for learning statements
        if any(word in content_lower for word in ["learned", "discovered", "realized"]):
            score += 0.2
        
        # Metadata insight flag
        if metadata.get("insight", False):
            score += 0.3
        
        return min(score, 1.0)

class RiskMemoryStrategy(MemoryStrategy):
    """Strategy for storing risk-related information."""
    
    def __init__(self):
        self.risk_keywords = [
            "risk", "danger", "warning", "caution", "careful",
            "loss", "lose", "downside", "volatile", "uncertainty",
            "avoid", "stay away", "problem", "issue", "concern"
        ]
    
    def should_store(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Determine if content contains risk information."""
        content_lower = content.lower()
        
        has_risk_keywords = any(keyword in content_lower for keyword in self.risk_keywords)
        is_flagged_risk = metadata.get("risk", False)
        
        return has_risk_keywords or is_flagged_risk
    
    def get_memory_type(self) -> str:
        return "risk"
    
    def get_importance_score(self, content: str, metadata: Dict[str, Any]) -> float:
        """Calculate importance score for risk information."""
        content_lower = content.lower()
        score = 0.0
        
        # Base score for risk keywords
        risk_keywords = sum(1 for keyword in self.risk_keywords if keyword in content_lower)
        score += min(risk_keywords * 0.25, 0.6)
        
        # High importance for warnings and cautions
        if any(word in content_lower for word in ["warning", "caution", "danger"]):
            score += 0.3
        
        # Metadata risk flag
        if metadata.get("risk", False):
            score += 0.4
        
        return min(score, 1.0)

class MemoryStrategyFactory:
    """Factory for creating memory strategies."""
    
    _strategies = {
        "conversation": ConversationMemoryStrategy,
        "insight": InsightMemoryStrategy,
        "risk": RiskMemoryStrategy
    }
    
    @classmethod
    def get_strategy(cls, strategy_name: str) -> MemoryStrategy:
        """Get a memory strategy by name."""
        if strategy_name not in cls._strategies:
            raise ValueError(f"Unknown memory strategy: {strategy_name}")
        
        return cls._strategies[strategy_name]()
    
    @classmethod
    def get_all_strategies(cls) -> List[MemoryStrategy]:
        """Get all available memory strategies."""
        return [strategy() for strategy in cls._strategies.values()]
    
    @classmethod
    def evaluate_content(cls, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate content using all strategies to determine storage decisions.
        
        Returns:
            Dict with strategy results and overall decision
        """
        results = {}
        max_score = 0.0
        best_strategy = None
        
        for strategy in cls.get_all_strategies():
            strategy_name = strategy.get_memory_type()
            
            should_store = strategy.should_store(content, metadata)
            importance_score = strategy.get_importance_score(content, metadata)
            
            results[strategy_name] = {
                "should_store": should_store,
                "importance_score": importance_score,
                "memory_type": strategy.get_memory_type()
            }
            
            if should_store and importance_score > max_score:
                max_score = importance_score
                best_strategy = strategy_name
        
        return {
            "strategies": results,
            "should_store_in_long_term": max_score > 0.5,
            "best_strategy": best_strategy,
            "overall_importance": max_score
        } 