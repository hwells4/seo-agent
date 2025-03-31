"""
Research Agent for content analysis.

This agent uses LLMs to analyze existing content for a target keyword,
identifying common topics, content structures, writing styles, and authority signals.
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional

import agno
from agno.agent import Agent
from agno.models.openai import OpenAIChat  # Use OpenAI instead of Groq
from agno.storage.base import Storage as StorageProvider

from src.config.settings import settings
from src.config.agno_config import get_knowledge_provider
from src.models.content_models import ResearchOutput, ResearchTopic
from src.utils.validation import validate_research_output
from src.utils.error_handling import async_retry_decorator, classify_llm_error

# Set up logger
logger = logging.getLogger(__name__)


class ResearchAgent(Agent):
    """Agent for researching and analyzing content for a target keyword."""

    def __init__(self, storage: Optional[StorageProvider] = None):
        """Initialize the research agent.
        
        Args:
            storage: Optional storage provider for persistent state
        """
        # Initialize with OpenAI model (GPT-4o for research capabilities)
        super().__init__(
            name="Research Agent",
            description="Analyzes existing content for a target keyword to identify patterns and opportunities.",
            model=OpenAIChat(id="gpt-4o"),  # Use GPT-4o for research
            storage=storage,
            knowledge=get_knowledge_provider()
        )
    
    async def validate_context(self, context: Dict[str, Any]) -> bool:
        """Validate that the context contains required information.
        
        Args:
            context: The agent context
            
        Returns:
            True if context is valid, False otherwise
        """
        if not context.get("keyword"):
            logger.error("Missing required keyword in context")
            return False
        
        return True
    
    async def run(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the research agent workflow.
        
        Args:
            context: The agent context containing the keyword to research
            
        Returns:
            Research analysis results
        """
        # Use the context passed or the agent's own context
        context = context or self.context
        
        # Start timing execution
        start_time = time.time()
        
        # Validate context
        if not await self.validate_context(context):
            raise ValueError("Invalid context for research agent")
        
        keyword = context.get("keyword")
        logger.info(f"Starting research for keyword: {keyword}")
        
        try:
            # Create a session state dictionary to persist intermediary results
            session = self.session_state or {}
            
            # Check knowledge store for existing research
            existing_research = await self._check_knowledge_store(keyword)
            if existing_research:
                logger.info(f"Found existing research for keyword: {keyword}")
                return existing_research
            
            # Collect content sources for analysis
            sources = await self._collect_content_sources(keyword, session)
            session["sources"] = sources
            
            # Update session state
            self.session_state = session
            
            # Analyze content
            analysis_results = await self._analyze_content(keyword, sources, session)
            session["analysis_results"] = analysis_results
            
            # Update session state
            self.session_state = session
            
            # Process topics
            topics = await self._process_topics(analysis_results)
            
            # Structure the final output
            execution_time = time.time() - start_time
            research_output = ResearchOutput(
                keyword=keyword,
                serp_analysis=analysis_results.get("serp_analysis", {}),
                total_sources=len(sources),
                total_words_analyzed=analysis_results.get("total_words_analyzed", 0),
                main_topics=topics,
                content_structure_patterns=analysis_results.get("content_structure_patterns", []),
                writing_style_analysis=analysis_results.get("writing_style_analysis", {}),
                authority_signals=analysis_results.get("authority_signals", []),
                execution_time=execution_time
            )
            
            # Validate output
            validate_research_output(research_output)
            
            # Store results in knowledge base if available
            await self._store_in_knowledge_base(keyword, research_output.dict())
            
            logger.info(f"Research completed for keyword '{keyword}' in {execution_time:.2f} seconds")
            
            # Update the context for other agents
            if context is not self.context:
                context["research_output"] = research_output.dict()
            else:
                self.add_context({"research_output": research_output.dict()})
            
            return research_output.dict()
        
        except Exception as e:
            logger.error(f"Error during research: {str(e)}")
            raise
    
    async def _check_knowledge_store(self, keyword: str) -> Optional[Dict[str, Any]]:
        """Check if research for this keyword exists in knowledge store.
        
        Args:
            keyword: The target keyword to research
            
        Returns:
            Existing research if found, None otherwise
        """
        if not self.knowledge:
            return None
            
        try:
            # Search for existing research
            results = await self.knowledge.search(
                collection=settings.agno.KNOWLEDGE_COLLECTION,
                query=f"research for keyword: {keyword}",
                limit=1
            )
            
            if results and len(results) > 0:
                return results[0].metadata
                
        except Exception as e:
            logger.warning(f"Error searching knowledge store: {str(e)}")
            
        return None
        
    async def _store_in_knowledge_base(self, keyword: str, research_data: Dict[str, Any]) -> None:
        """Store research results in knowledge base.
        
        Args:
            keyword: The target keyword
            research_data: Research results to store
        """
        if not self.knowledge:
            return
            
        try:
            # Create a metadata document
            await self.knowledge.add(
                collection=settings.agno.KNOWLEDGE_COLLECTION,
                text=f"Research analysis for keyword: {keyword}",
                metadata=research_data
            )
            logger.info(f"Stored research for keyword '{keyword}' in knowledge base")
        except Exception as e:
            logger.warning(f"Error storing in knowledge base: {str(e)}")
    
    @async_retry_decorator(max_retries=settings.agent.MAX_RETRIES)
    async def _collect_content_sources(self, keyword: str, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect content sources for analysis.
        
        Args:
            keyword: The target keyword to research
            session: Session dictionary for storing intermediary results
            
        Returns:
            List of content sources with metadata
        """
        logger.info(f"Collecting content sources for keyword: {keyword}")
        
        # If we have cached sources in the session, return them
        if "sources" in session:
            logger.info(f"Using cached sources from session for keyword: {keyword}")
            return session["sources"]
        
        # Use our own model for web search simulation
        try:
            prompt = f"""
            I need to analyze the top-ranking content for the keyword: "{keyword}"
            
            Please simulate search engine results and provide information about the top 10 search results, including:
            1. Title of the page
            2. URL
            3. A brief summary of the content (1-2 sentences)
            4. Estimated word count
            5. Content type (blog post, article, product page, etc.)
            
            Format the response as a JSON array of objects.
            """
            
            # Just use this agent's run method with JSON mode
            response = await super().run(
                user_message=prompt,
                use_json_mode=True
            )
            
            # Extract the JSON data
            if isinstance(response, dict) and "content" in response:
                sources = response["content"]
            else:
                sources = response
                
            # Validate and format the sources
            if not isinstance(sources, list):
                logger.warning(f"Invalid sources response format: {type(sources)}. Using simulated data.")
                sources = self._get_simulated_sources(keyword)
            
            # Limit the number of sources to analyze
            sources = sources[:settings.agent.RESEARCH_MAX_SOURCES]
            
            # Cache sources in session
            session["sources"] = sources
            
            return sources
            
        except Exception as e:
            logger.warning(f"Error collecting sources: {str(e)}. Using simulated data.")
            sources = self._get_simulated_sources(keyword)
            
            # Cache sources in session
            session["sources"] = sources
            
            return sources
    
    def _get_simulated_sources(self, keyword: str) -> List[Dict[str, Any]]:
        """Get simulated sources for testing and fallback.
        
        Args:
            keyword: Target keyword
            
        Returns:
            List of simulated content sources
        """
        return [
            {
                "title": f"Ultimate Guide to {keyword.title()}",
                "url": f"https://example.com/guide-to-{keyword.lower().replace(' ', '-')}",
                "summary": f"Comprehensive guide covering all aspects of {keyword}.",
                "word_count": 2500,
                "content_type": "guide"
            },
            {
                "title": f"10 Best {keyword.title()} Strategies",
                "url": f"https://example.com/best-{keyword.lower().replace(' ', '-')}-strategies",
                "summary": f"Listicle of the most effective strategies for {keyword}.",
                "word_count": 1800,
                "content_type": "listicle"
            },
            {
                "title": f"How to Master {keyword.title()} in 2023",
                "url": f"https://example.com/how-to-master-{keyword.lower().replace(' ', '-')}",
                "summary": f"Step-by-step tutorial on mastering {keyword}.",
                "word_count": 2200,
                "content_type": "tutorial"
            }
        ]
    
    @async_retry_decorator(max_retries=settings.agent.MAX_RETRIES)
    async def _analyze_content(
        self, 
        keyword: str, 
        sources: List[Dict[str, Any]],
        session: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze collected content sources.
        
        Args:
            keyword: Target keyword
            sources: List of content sources to analyze
            session: Session dictionary for storing intermediary results
            
        Returns:
            Analysis results
        """
        logger.info(f"Analyzing content for keyword: {keyword}")
        
        # If we have cached analysis in the session, return it
        if "analysis_results" in session:
            logger.info(f"Using cached analysis from session for keyword: {keyword}")
            return session["analysis_results"]
        
        # Construct prompt for the model
        prompt = f"""
        Analyze the following content sources for the keyword: "{keyword}"
        
        SOURCES:
        {json.dumps(sources, indent=2)}
        
        Perform a comprehensive analysis to identify:
        1. Common topics and subtopics
        2. Content structure patterns 
        3. Writing style and tone
        4. Authority signals (citations, expert quotes, statistics)
        5. Overall word count and content depth patterns
        
        Provide a structured analysis in JSON format with these sections.
        """
        
        schema = {
            "type": "object",
            "properties": {
                "serp_analysis": {
                    "type": "object",
                    "properties": {
                        "top_ranking_patterns": {"type": "array", "items": {"type": "string"}},
                        "average_word_count": {"type": "integer"},
                        "dominant_content_types": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "topic_analysis": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string"},
                            "frequency": {"type": "integer"},
                            "importance": {"type": "number"},
                            "common_phrases": {"type": "array", "items": {"type": "string"}},
                            "source_indices": {"type": "array", "items": {"type": "integer"}}
                        }
                    }
                },
                "content_structure_patterns": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "pattern_name": {"type": "string"},
                            "description": {"type": "string"},
                            "frequency": {"type": "integer"}
                        }
                    }
                },
                "writing_style_analysis": {
                    "type": "object",
                    "properties": {
                        "dominant_tone": {"type": "string"},
                        "formality_level": {"type": "string"},
                        "use_of_personal_pronouns": {"type": "boolean"},
                        "reading_level": {"type": "string"}
                    }
                },
                "authority_signals": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "signal_type": {"type": "string"},
                            "description": {"type": "string"},
                            "frequency": {"type": "integer"}
                        }
                    }
                },
                "total_words_analyzed": {"type": "integer"}
            }
        }
        
        # Use the agent's run method with JSON mode to get structured analysis
        response = await super().run(
            context={
                "keyword": keyword,
                "sources": sources,
                "task": "Analyze content sources"
            },
            user_message=prompt,
            response_model=None,  # Let Agno handle the response formatting
            use_json_mode=True  # Enable JSON mode for structured output
        )
        
        # Extract the JSON data from the response
        try:
            if isinstance(response, dict) and "content" in response:
                analysis = response["content"]
            else:
                analysis = response
                
            # Cache analysis in session
            session["analysis_results"] = analysis
            
            return analysis
        except Exception as e:
            logger.error(f"Error parsing analysis response: {str(e)}")
            raise
    
    async def _process_topics(self, analysis_results: Dict[str, Any]) -> List[ResearchTopic]:
        """Process topic analysis into ResearchTopic objects.
        
        Args:
            analysis_results: Content analysis results
            
        Returns:
            List of ResearchTopic objects
        """
        topics = []
        
        for topic_data in analysis_results.get("topic_analysis", []):
            # Map source indices to actual source URLs
            source_indices = topic_data.get("source_indices", [])
            sources = [f"source_{idx}" for idx in source_indices]  # Placeholder
            
            topic = ResearchTopic(
                title=topic_data.get("topic", ""),
                frequency=topic_data.get("frequency", 0),
                importance=topic_data.get("importance", 0.0),
                common_phrases=topic_data.get("common_phrases", []),
                sources=sources
            )
            
            topics.append(topic)
        
        return topics
