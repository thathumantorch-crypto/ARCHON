"""
Milvus Knowledgebase for ARCHON AI
Provides vector database storage and retrieval for ARCHON's knowledge
"""

import os
import sys
import json
import time
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import numpy as np

# Try to import Milvus
try:
    from pymilvus import (
        connections,
        utility,
        FieldSchema,
        CollectionSchema,
        DataType,
        Collection,
        MilvusException
    )
    MILVUS_AVAILABLE = True
except ImportError:
    MILVUS_AVAILABLE = False
    print("Warning: Milvus not available. Knowledgebase features will be limited.")

class MilvusKnowledgebase:
    """
    Milvus-based knowledgebase for ARCHON AI
    Provides vector storage and retrieval capabilities
    """
    
    def __init__(self, collection_name: str = "archon_knowledge", 
                 dimension: int = 768, 
                 host: str = "localhost", 
                 port: int = 19530):
        """
        Initialize Milvus knowledgebase
        
        Args:
            collection_name: Name of the Milvus collection
            dimension: Dimension of embedding vectors
            host: Milvus server host
            port: Milvus server port
        """
        self.collection_name = collection_name
        self.dimension = dimension
        self.host = host
        self.port = port
        self.collection = None
        self.logger = logging.getLogger("ARCHON.MILVUS_KB")
        self.connected = False
        self.initialized = False
        
        # Initialize connection
        self._initialize_connection()
        
        # Initialize collection
        if self.connected:
            self._initialize_collection()
    
    def _initialize_connection(self):
        """Initialize connection to Milvus server"""
        try:
            if not MILVUS_AVAILABLE:
                self.logger.warning("Milvus not available, using fallback storage")
                return
            
            # Try to connect to Milvus
            connections.connect(host=self.host, port=self.port)
            self.connected = True
            self.logger.info(f"Connected to Milvus at {self.host}:{self.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Milvus: {e}")
            self.connected = False
    
    def _initialize_collection(self):
        """Initialize Milvus collection"""
        try:
            if not self.connected:
                return
            
            # Check if collection exists
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                self.logger.info(f"Loaded existing collection: {self.collection_name}")
            else:
                # Create new collection
                self._create_collection()
            
            self.initialized = True
            self.logger.info("Milvus knowledgebase initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize collection: {e}")
            self.initialized = False
    
    def _create_collection(self):
        """Create new Milvus collection"""
        try:
            # Define field schema
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=255),
                FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="timestamp", dtype=DataType.INT64),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension)
            ]
            
            # Create collection schema
            schema = CollectionSchema(
                fields=fields,
                description="ARCHON AI Knowledgebase"
            )
            
            # Create collection
            self.collection = Collection(
                name=self.collection_name,
                schema=schema,
                using='default'
            )
            
            # Create index for embedding field
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
            
            self.collection.create_index(
                field_name="embedding",
                index_params=index_params
            )
            
            self.logger.info(f"Created new collection: {self.collection_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to create collection: {e}")
            raise
    
    def add_knowledge(self, content: str, embedding: List[float], 
                     source: str = "user", category: str = "general") -> bool:
        """
        Add knowledge to the knowledgebase
        
        Args:
            content: Text content to store
            embedding: Vector embedding of the content
            source: Source of the knowledge
            category: Category of the knowledge
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.initialized:
                self.logger.warning("Knowledgebase not initialized")
                return False
            
            # Prepare data
            data = [{
                "content": content,
                "source": source,
                "category": category,
                "timestamp": int(time.time()),
                "embedding": embedding
            }]
            
            # Insert data
            insert_result = self.collection.insert(data)
            
            # Flush to ensure data is persisted
            self.collection.flush()
            
            self.logger.info(f"Added knowledge from {source} in category {category}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add knowledge: {e}")
            return False
    
    def search_knowledge(self, query_embedding: List[float], 
                        top_k: int = 5, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search knowledge from the knowledgebase
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            category: Optional category filter
            
        Returns:
            List of search results
        """
        try:
            if not self.initialized:
                self.logger.warning("Knowledgebase not initialized")
                return []
            
            # Load collection
            self.collection.load()
            
            # Prepare search parameters
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            # Prepare query
            query = [query_embedding]
            
            # Define output fields
            output_fields = ["content", "source", "category", "timestamp"]
            
            # Search
            results = self.collection.search(
                data=query,
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=output_fields
            )
            
            # Process results
            search_results = []
            for hits in results:
                for hit in hits:
                    search_results.append({
                        "content": hit.entity.get("content", ""),
                        "source": hit.entity.get("source", ""),
                        "category": hit.entity.get("category", ""),
                        "timestamp": hit.entity.get("timestamp", 0),
                        "score": hit.score,
                        "distance": hit.distance
                    })
            
            # Filter by category if specified
            if category:
                search_results = [
                    result for result in search_results 
                    if result.get("category") == category
                ]
            
            self.logger.info(f"Found {len(search_results)} knowledge items")
            return search_results
            
        except Exception as e:
            self.logger.error(f"Failed to search knowledge: {e}")
            return []
    
    def get_all_knowledge(self, category: Optional[str] = None, 
                         limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all knowledge from the knowledgebase
        
        Args:
            category: Optional category filter
            limit: Maximum number of results
            
        Returns:
            List of knowledge items
        """
        try:
            if not self.initialized:
                self.logger.warning("Knowledgebase not initialized")
                return []
            
            # Load collection
            self.collection.load()
            
            # Query all data
            results = self.collection.query(
                expr="",
                output_fields=["content", "source", "category", "timestamp"],
                limit=limit
            )
            
            # Process results
            knowledge_items = []
            for result in results:
                knowledge_items.append({
                    "content": result.get("content", ""),
                    "source": result.get("source", ""),
                    "category": result.get("category", ""),
                    "timestamp": result.get("timestamp", 0)
                })
            
            # Filter by category if specified
            if category:
                knowledge_items = [
                    item for item in knowledge_items 
                    if item.get("category") == category
                ]
            
            self.logger.info(f"Retrieved {len(knowledge_items)} knowledge items")
            return knowledge_items
            
        except Exception as e:
            self.logger.error(f"Failed to get all knowledge: {e}")
            return []
    
    def delete_knowledge(self, content: str) -> bool:
        """
        Delete knowledge from the knowledgebase
        
        Args:
            content: Content to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.initialized:
                self.logger.warning("Knowledgebase not initialized")
                return False
            
            # Find and delete by content
            # Note: This is a simplified implementation
            # In practice, you might want to use content hash or ID
            expr = f'content == "{content}"'
            
            self.collection.delete(expr)
            self.collection.flush()
            
            self.logger.info(f"Deleted knowledge: {content[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete knowledge: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get knowledgebase statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            if not self.initialized:
                return {
                    "connected": False,
                    "initialized": False,
                    "total_items": 0,
                    "categories": {}
                }
            
            # Get collection statistics
            stats = self.collection.describe()
            
            # Get all knowledge to calculate category statistics
            all_knowledge = self.get_all_knowledge()
            
            # Calculate category statistics
            category_stats = {}
            for item in all_knowledge:
                category = item.get("category", "general")
                category_stats[category] = category_stats.get(category, 0) + 1
            
            return {
                "connected": self.connected,
                "initialized": self.initialized,
                "collection_name": self.collection_name,
                "dimension": self.dimension,
                "total_items": len(all_knowledge),
                "categories": category_stats,
                "collection_stats": stats
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {
                "connected": self.connected,
                "initialized": self.initialized,
                "total_items": 0,
                "categories": {},
                "error": str(e)
            }
    
    def initialize_default_knowledge(self) -> bool:
        """
        Initialize the knowledgebase with default knowledge
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.initialized:
                self.logger.warning("Knowledgebase not initialized")
                return False
            
            # Default knowledge items
            default_knowledge = [
                {
                    "content": "ARCHON AI is an Autonomous Recursive Cognitive Heuristic Operations Network designed for advanced AI interactions and self-improvement.",
                    "source": "system",
                    "category": "about"
                },
                {
                    "content": "ARCHON can process natural language, write code, analyze systems, and learn from interactions.",
                    "source": "system",
                    "category": "capabilities"
                },
                {
                    "content": "Python is a high-level programming language known for its simplicity and readability. It's widely used for AI development, web development, data science, and automation.",
                    "source": "system",
                    "category": "programming"
                },
                {
                    "content": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
                    "source": "system",
                    "category": "ai_concepts"
                },
                {
                    "content": "Neural networks are computing systems inspired by biological neural networks, consisting of interconnected nodes that process information using connectionist approaches.",
                    "source": "system",
                    "category": "ai_concepts"
                },
                {
                    "content": "Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently, commonly used in AI applications for similarity search.",
                    "source": "system",
                    "category": "database"
                },
                {
                    "content": "Natural Language Processing (NLP) is a branch of AI that helps computers understand, interpret, and generate human language.",
                    "source": "system",
                    "category": "ai_concepts"
                },
                {
                    "content": "Self-healing systems can automatically detect, diagnose, and resolve issues without human intervention.",
                    "source": "system",
                    "category": "concepts"
                }
            ]
            
            # Generate embeddings (simplified - in practice, use a proper embedding model)
            for item in default_knowledge:
                # Create a simple embedding based on content hash
                content_hash = hashlib.md5(item["content"].encode()).hexdigest()
                embedding = [float(int(c, 16) % 100 / 100) for c in content_hash[:self.dimension * 2]]
                embedding = embedding[:self.dimension]  # Ensure correct dimension
                
                # Pad if necessary
                while len(embedding) < self.dimension:
                    embedding.append(0.0)
                
                self.add_knowledge(
                    content=item["content"],
                    embedding=embedding,
                    source=item["source"],
                    category=item["category"]
                )
            
            self.logger.info("Initialized default knowledge in knowledgebase")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize default knowledge: {e}")
            return False
    
    def close(self):
        """Close connection to Milvus"""
        try:
            if self.collection:
                self.collection.release()
            connections.disconnect("default")
            self.logger.info("Closed Milvus connection")
        except Exception as e:
            self.logger.error(f"Error closing connection: {e}")

# Fallback storage for when Milvus is not available
class FallbackKnowledgebase:
    """
    Fallback knowledgebase using in-memory storage
    """
    
    def __init__(self):
        self.knowledge = []
        self.logger = logging.getLogger("ARCHON.FALLBACK_KB")
        self.logger.info("Using fallback knowledgebase (in-memory storage)")
    
    def add_knowledge(self, content: str, embedding: List[float], 
                     source: str = "user", category: str = "general") -> bool:
        """Add knowledge to fallback storage"""
        try:
            self.knowledge.append({
                "content": content,
                "embedding": embedding,
                "source": source,
                "category": category,
                "timestamp": int(time.time())
            })
            return True
        except Exception as e:
            self.logger.error(f"Failed to add knowledge: {e}")
            return False
    
    def search_knowledge(self, query_embedding: List[float],
                        top_k: int = 5, category: Optional[str] = None,
                        query_text: str = "") -> List[Dict[str, Any]]:
        """Search knowledge using keyword overlap (embeddings are unreliable in fallback mode)."""
        try:
            # Build a set of meaningful query words for keyword matching
            stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what',
                          'how', 'why', 'who', 'where', 'when', 'do', 'does',
                          'can', 'could', 'tell', 'me', 'about', 'of', 'in',
                          'to', 'for', 'and', 'or', 'it', 'its', 'this', 'that',
                          'be', 'been', 'being', 'have', 'has', 'had', 'i', 'you',
                          'we', 'they', 'my', 'your', 'with', 'on', 'at', 'by'}
            query_words = set()
            for w in query_text.lower().split():
                cleaned = ''.join(c for c in w if c.isalnum())
                if cleaned and cleaned not in stop_words and len(cleaned) > 1:
                    query_words.add(cleaned)

            results = []
            for item in self.knowledge:
                if category and item.get("category") != category:
                    continue

                content_lower = item["content"].lower()
                if not query_words:
                    score = 0.1
                else:
                    matches = sum(1 for w in query_words if w in content_lower)
                    score = matches / len(query_words) if query_words else 0.0

                if score > 0:
                    results.append({
                        "content": item["content"],
                        "source": item["source"],
                        "category": item["category"],
                        "timestamp": item["timestamp"],
                        "score": score,
                        "distance": 1 - score,
                    })

            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]

        except Exception as e:
            self.logger.error(f"Failed to search knowledge: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
        except:
            return 0.0
    
    def get_all_knowledge(self, category: Optional[str] = None, 
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Get all knowledge from fallback storage"""
        try:
            results = self.knowledge
            
            if category:
                results = [item for item in results if item.get("category") == category]
            
            return results[:limit]
        except Exception as e:
            self.logger.error(f"Failed to get all knowledge: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get fallback knowledgebase statistics"""
        try:
            category_stats = {}
            for item in self.knowledge:
                category = item.get("category", "general")
                category_stats[category] = category_stats.get(category, 0) + 1
            
            return {
                "connected": False,
                "initialized": True,
                "type": "fallback",
                "total_items": len(self.knowledge),
                "categories": category_stats
            }
        except Exception as e:
            return {
                "connected": False,
                "initialized": True,
                "type": "fallback",
                "total_items": 0,
                "categories": {},
                "error": str(e)
            }
    
    def initialize_default_knowledge(self) -> bool:
        """Initialize default knowledge in fallback storage"""
        try:
            # Default knowledge items — broad coverage for factual Q&A
            default_knowledge = [
                # About ARCHON
                {"content": "ARCHON AI is an Autonomous Recursive Cognitive Heuristic Operations Network designed for advanced AI interactions and self-improvement.", "source": "system", "category": "about"},
                {"content": "ARCHON can process natural language, write code, analyze systems, manage files, control processes, and learn from interactions.", "source": "system", "category": "capabilities"},
                # Programming languages
                {"content": "Python is a high-level programming language known for its simplicity and readability. It's widely used for AI development, web development, data science, and automation.", "source": "system", "category": "programming"},
                {"content": "JavaScript is a versatile programming language primarily used for web development. It runs in browsers and on servers via Node.js, and is essential for interactive web applications.", "source": "system", "category": "programming"},
                {"content": "Java is a class-based, object-oriented programming language designed for portability. It's widely used for enterprise applications, Android development, and large-scale systems.", "source": "system", "category": "programming"},
                {"content": "C++ is a powerful systems programming language that extends C with object-oriented features. It's used for game engines, operating systems, embedded systems, and high-performance applications.", "source": "system", "category": "programming"},
                {"content": "Rust is a systems programming language focused on safety, speed, and concurrency. It prevents memory errors at compile time and is increasingly used for systems programming and WebAssembly.", "source": "system", "category": "programming"},
                {"content": "HTML (HyperText Markup Language) is the standard markup language for creating web pages. It defines the structure and content of a webpage using elements like headings, paragraphs, links, and images.", "source": "system", "category": "programming"},
                {"content": "CSS (Cascading Style Sheets) is a stylesheet language used to describe the presentation of HTML documents, controlling layout, colors, fonts, and responsive design.", "source": "system", "category": "programming"},
                # AI & ML concepts
                {"content": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. Common approaches include supervised, unsupervised, and reinforcement learning.", "source": "system", "category": "ai_concepts"},
                {"content": "Neural networks are computing systems inspired by biological neural networks, consisting of interconnected nodes organized in layers that process information. Deep learning uses neural networks with many layers.", "source": "system", "category": "ai_concepts"},
                {"content": "Natural Language Processing (NLP) is a branch of AI that helps computers understand, interpret, and generate human language. Applications include chatbots, translation, and sentiment analysis.", "source": "system", "category": "ai_concepts"},
                {"content": "Deep learning is a subset of machine learning using multi-layered neural networks to learn complex patterns. It powers image recognition, speech processing, and language models like GPT.", "source": "system", "category": "ai_concepts"},
                {"content": "Artificial intelligence (AI) is the simulation of human intelligence by computer systems. It includes learning, reasoning, problem-solving, perception, and language understanding.", "source": "system", "category": "ai_concepts"},
                {"content": "Reinforcement learning is a type of machine learning where an agent learns to make decisions by taking actions in an environment to maximize cumulative reward.", "source": "system", "category": "ai_concepts"},
                {"content": "A transformer is a deep learning architecture that uses self-attention mechanisms to process sequential data. It's the foundation of modern language models like GPT, BERT, and T5.", "source": "system", "category": "ai_concepts"},
                # Computer science concepts
                {"content": "Recursion is a programming technique where a function calls itself to solve a problem by breaking it into smaller subproblems. Every recursive function needs a base case to prevent infinite loops.", "source": "system", "category": "cs_concepts"},
                {"content": "An algorithm is a step-by-step procedure for solving a problem. Common types include sorting algorithms (quicksort, mergesort), search algorithms (binary search), and graph algorithms (Dijkstra's).", "source": "system", "category": "cs_concepts"},
                {"content": "A database is an organized collection of structured data. SQL databases use tables with relationships, while NoSQL databases use flexible schemas like documents, key-value pairs, or graphs.", "source": "system", "category": "cs_concepts"},
                {"content": "An API (Application Programming Interface) is a set of rules that allows different software applications to communicate. REST and GraphQL are common API architectures.", "source": "system", "category": "cs_concepts"},
                {"content": "Version control records changes to files over time. Git is the most popular system, used with platforms like GitHub and GitLab for collaborative software development.", "source": "system", "category": "cs_concepts"},
                {"content": "Object-oriented programming (OOP) is a paradigm based on objects containing data and methods. Key principles include encapsulation, inheritance, polymorphism, and abstraction.", "source": "system", "category": "cs_concepts"},
                {"content": "Data structures are ways of organizing data for efficient access. Common structures include arrays, linked lists, stacks, queues, hash tables, trees, and graphs.", "source": "system", "category": "cs_concepts"},
                # Technology
                {"content": "Vector databases store and query high-dimensional vectors efficiently, commonly used in AI for similarity search and recommendation systems.", "source": "system", "category": "technology"},
                {"content": "Self-healing systems can automatically detect, diagnose, and resolve issues without human intervention, improving reliability and reducing downtime.", "source": "system", "category": "technology"},
                {"content": "Cloud computing provides on-demand computing resources over the internet. Major providers include AWS, Azure, and Google Cloud.", "source": "system", "category": "technology"},
                {"content": "Docker is a platform for running applications in containers that package code and dependencies together, ensuring consistent behavior across environments.", "source": "system", "category": "technology"},
                {"content": "Linux is an open-source operating system kernel used in servers, desktops, mobile devices (Android), and embedded systems. Popular distributions include Ubuntu, Fedora, and Arch.", "source": "system", "category": "technology"},
                {"content": "The internet is a global network of interconnected computers that communicate using standardized protocols like TCP/IP, HTTP, and DNS.", "source": "system", "category": "technology"},
            ]
            
            # Add default knowledge to fallback storage
            for item in default_knowledge:
                # Create a simple embedding based on content hash
                import hashlib
                content_hash = hashlib.md5(item["content"].encode()).hexdigest()
                embedding = [float(int(c, 16) % 100 / 100) for c in content_hash[:768 * 2]]
                embedding = embedding[:768]
                
                # Pad if necessary
                while len(embedding) < 768:
                    embedding.append(0.0)
                
                self.add_knowledge(
                    content=item["content"],
                    embedding=embedding,
                    source=item["source"],
                    category=item["category"]
                )
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize default knowledge: {e}")
            return False

# Factory function to get appropriate knowledgebase
def get_knowledgebase(collection_name: str = "archon_knowledge", 
                      dimension: int = 768) -> Any:
    """
    Get appropriate knowledgebase (Milvus or fallback)
    
    Args:
        collection_name: Name of the Milvus collection
        dimension: Dimension of embedding vectors
        
    Returns:
        Knowledgebase instance
    """
    try:
        if MILVUS_AVAILABLE:
            kb = MilvusKnowledgebase(collection_name, dimension)
            if kb.initialized:
                return kb
            else:
                return FallbackKnowledgebase()
        else:
            return FallbackKnowledgebase()
    except Exception as e:
        logging.getLogger("ARCHON.KB_FACTORY").error(f"Failed to create knowledgebase: {e}")
        return FallbackKnowledgebase()
