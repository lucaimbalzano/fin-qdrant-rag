# Memory System Design for fin-qdrant-rag

## 🏗️ System Architecture Overview

The memory system uses a **Hybrid Architecture** combining two storage systems:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Hybrid Memory System                         │
├─────────────────────────────────────────────────────────────────┤
│  Short-Term Memory (Redis)    │  Long-Term Memory (Qdrant)      │
│  • Recent conversations       │  • Important exchanges          │
│  • Session data               │  • User insights                │
│  • Fast access                │  • Vector embeddings            │
│  • TTL: 24h                   │  • Semantic search              │
│  • In-memory                  │  • Persistent storage           │
└─────────────────────────────────────────────────────────────────┘
```

## 🧠 Memory Types & Strategies

### 1. Short-Term Memory (Redis)
- **Purpose**: Recent conversation context
- **Storage**: Redis with TTL
- **Access**: Fast, in-memory
- **Content**: Last 5-10 conversation turns
- **TTL**: 24 hours

### 2. Long-Term Memory (Qdrant)
- **Purpose**: Important memories and insights
- **Storage**: Qdrant vector database
- **Access**: Semantic similarity search (Cosine Algo)
- **Content**: User insights, important conversations, risk information
- **Persistence**: Permanent storage

## 🎯 Design Patterns Used

### 1. Strategy Pattern
```python
class MemoryStrategy(ABC):
    @abstractmethod
    def should_store(self, content: str, metadata: Dict[str, Any]) -> bool
    @abstractmethod
    def get_importance_score(self, content: str, metadata: Dict[str, Any]) -> float
```

**Strategies:**
- `ConversationMemoryStrategy`: Financial conversations
- `InsightMemoryStrategy`: User preferences and learnings
- `RiskMemoryStrategy`: Risk-related information

### 2. Factory Pattern
```python
class MemoryStrategyFactory:
    @classmethod
    def get_strategy(cls, strategy_name: str) -> MemoryStrategy
    @classmethod
    def evaluate_content(cls, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]
```

### 3. Facade Pattern
```python
class HybridMemoryManager:
    """Unified interface for both memory systems"""
    async def add_conversation_turn(self, user_id: str, user_message: str, assistant_response: str)
    async def get_context_for_user(self, user_id: str) -> Dict[str, Any]
    async def search_memories(self, query: str, user_id: str = None) -> List[Dict[str, Any]]
```

## 🔄 Memory Processing Pipeline

### 1. Content Evaluation
```
User Message + Assistant Response
           ↓
   Strategy Evaluation
           ↓
   Importance Scoring
           ↓
   Storage Decision
```

### 2. Storage Decision Logic
```python
def evaluate_content(content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    # Apply all strategies
    for strategy in strategies:
        should_store = strategy.should_store(content, metadata)
        importance_score = strategy.get_importance_score(content, metadata)
    
    # Decision: Store if importance_score > 0.5
    return {
        "should_store_in_long_term": max_score > 0.5,
        "best_strategy": strategy_with_highest_score,
        "overall_importance": max_score
    }
```

### 3. Memory Storage Flow
```
1. Always store in Redis (short-term)
2. Evaluate importance using strategies
3. If important (score > 0.5):
   - Generate embedding
   - Store in Qdrant with metadata
4. Log memory type and importance score
```

## 📊 Memory Retrieval Strategy

### 1. Context Building
```python
async def get_context_for_user(user_id: str) -> Dict[str, Any]:
    # Get recent conversations (Redis)
    short_term = await redis.get_recent_context(user_id, limit=5)
    
    # Get important memories (Qdrant)
    long_term = await qdrant.get_user_memories(user_id, limit=3)
    
    # Get similar memories based on current conversation
    if short_term:
        recent_message = extract_recent_message(short_term)
        similar = await qdrant.search_similar_memories(
            query_embedding=embed(recent_message),
            user_id=user_id,
            limit=2
        )
    
    return combine_contexts(short_term, long_term, similar)
```

### 2. Context Combination
```
=== RECENT CONVERSATION ===
[14:30] User: What's your opinion on Tesla stock?
[14:31] Assistant: Tesla has strong fundamentals but high volatility...

=== IMPORTANT MEMORIES ===
[2024-01-15 10:30] User: I prefer conservative investments
[2024-01-10 14:20] User: My risk tolerance is low
```

## 🎯 Memory Strategies in Detail

### 1. ConversationMemoryStrategy
**Keywords**: stock, trading, investment, portfolio, analysis, strategy, risk, market
**Insight Keywords**: learned, discovered, found, realized, understood, important
**Scoring**:
- Financial keywords: +0.2 each (max 0.6)
- Insight keywords: +0.15 each (max 0.3)
- Explicit importance: +0.2
- Length bonus: +0.1 (if >200 chars)

### 2. InsightMemoryStrategy
**Patterns**: "i prefer", "i like", "i want", "my goal", "my strategy", "i learned"
**Scoring**:
- Insight patterns: +0.3 each (max 0.7)
- Personal preferences: +0.2
- Learning statements: +0.2
- Metadata insight flag: +0.3

### 3. RiskMemoryStrategy
**Keywords**: risk, danger, warning, caution, loss, volatile, avoid, problem
**Scoring**:
- Risk keywords: +0.25 each (max 0.6)
- Warning/caution: +0.3
- Metadata risk flag: +0.4

## 🔧 Implementation Details

### 1. Qdrant Collection Structure
```python
collection_name = "long_term_memory"
vector_size = 1536  # OpenAI ada-002
distance = Distance.COSINE

payload = {
    "content": "User: What about Tesla?\nAssistant: Tesla has...",
    "user_id": "user123",
    "memory_type": "conversation",
    "timestamp": "2024-01-20T14:30:00Z",
    "metadata": {
        "importance_score": 0.75,
        "strategy": "conversation",
        "evaluation": {...}
    }
}
```

### 2. Redis Structure
```python
# Conversation turns
conversation:user123 = [
    '{"user_message": "...", "assistant_response": "...", "timestamp": "..."}',
    ...
]

# Session data
session:user123 = {
    "preferences": '{"risk_tolerance": "low"}',
    "metadata": '{"last_activity": "..."}',
    "last_activity": "2024-01-20T14:30:00Z"
}
```

## 🚀 Benefits of This Design

### 1. Scalability
- **Redis**: Fast access for recent context
- **Qdrant**: Efficient vector search for large memory sets
- **Separation**: Independent scaling of short-term vs long-term

### 2. Intelligence
- **Automatic Importance Detection**: No manual tagging required
- **Semantic Search**: Find relevant memories even with different wording
- **Strategy-Based**: Different types of content handled appropriately

### 3. Flexibility
- **Strategy Pattern**: Easy to add new memory types
- **Factory Pattern**: Centralized strategy management
- **Facade Pattern**: Simple unified interface

### 4. Performance
- **Hybrid Approach**: Fast access for recent + semantic search for important
- **Embedding Caching**: Reuse embeddings when possible
- **Batch Operations**: Efficient bulk memory operations

## 🔮 Future Enhancements

### 1. Memory Compression
- Summarize old memories to save space
- Keep only most important parts of long conversations

### 2. Memory Expiration
- Automatic cleanup of old, less important memories
- Time-based importance decay

### 3. Memory Clustering
- Group similar memories together
- Create memory hierarchies

### 4. Memory Analytics
- Track memory usage patterns
- Optimize storage based on access patterns

### 5. Multi-Modal Memory
- Support for images, charts, documents
- Embeddings for different content types

## 📋 Task Reordering Impact

The original task order was:
1. Chatbot API ✅
2. Persistence Layer ✅
3. RAG Pipeline (PDF Ingestion)
4. RAG Chatbot
5. Dynamic Data Pipeline

**New order with memory system:**
1. Chatbot API ✅
2. **Persistence Layer + Memory System** ✅ (Now includes hybrid memory)
3. **RAG Pipeline** (Can now use long-term memory for context)
4. **RAG Chatbot** (Enhanced with memory-aware responses)
5. **Dynamic Data Pipeline** (Can store insights in long-term memory)

This reordering makes sense because:
- Long-term memory uses Qdrant (same as RAG pipeline)
- Memory system provides better context for RAG responses
- Dynamic data can be stored as memories for future reference 