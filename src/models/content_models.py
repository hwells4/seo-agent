"""
Data models for content generation workflow.

This module defines the data structures used throughout the content generation
pipeline, including input requests, intermediate agent outputs, and final results.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime


class WorkflowStatus(str, Enum):
    """Status of a content generation workflow."""
    PENDING = "pending"
    RESEARCH_IN_PROGRESS = "research_in_progress"
    RESEARCH_COMPLETE = "research_complete"
    BRIEF_IN_PROGRESS = "brief_in_progress"
    BRIEF_COMPLETE = "brief_complete"
    FACTS_IN_PROGRESS = "facts_in_progress"
    FACTS_COMPLETE = "facts_complete"
    CONTENT_IN_PROGRESS = "content_in_progress"
    CONTENT_COMPLETE = "content_complete"
    REVIEW_IN_PROGRESS = "review_in_progress"
    REVIEW_COMPLETE = "review_complete"
    COMPLETED = "completed"
    FAILED = "failed"


class ContentRequest(BaseModel):
    """Input request for content generation workflow."""
    keyword: str = Field(..., description="Primary target keyword for content generation")
    secondary_keywords: Optional[List[str]] = Field(None, description="Secondary keywords to target")
    content_type: str = Field(..., description="Type of content (blog, article, product, etc.)")
    target_audience: Optional[str] = Field(None, description="Description of target audience")
    tone: Optional[str] = Field("professional", description="Desired tone of the content")
    word_count: Optional[int] = Field(1500, description="Target word count for generated content")
    brand_voice_guidelines: Optional[str] = Field(None, description="Brand voice guidelines to follow")
    deadline: Optional[datetime] = Field(None, description="Deadline for content generation")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for notifications")
    extra_instructions: Optional[str] = Field(None, description="Additional instructions for content generation")

    @validator("keyword")
    def validate_keyword(cls, v: str) -> str:
        """Validate that keyword is not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Keyword cannot be empty")
        return v.strip()

    @validator("word_count")
    def validate_word_count(cls, v: Optional[int]) -> Optional[int]:
        """Validate that word count is reasonable."""
        if v is not None and (v < 300 or v > 10000):
            raise ValueError("Word count must be between 300 and 10000")
        return v


class ResearchTopic(BaseModel):
    """A topic identified in research."""
    title: str = Field(..., description="Topic title")
    frequency: int = Field(..., description="How frequently this topic appears")
    importance: float = Field(..., description="Importance score (0-1)")
    common_phrases: List[str] = Field(..., description="Common phrases related to this topic")
    sources: List[str] = Field(..., description="Source URLs where this topic was found")


class ResearchOutput(BaseModel):
    """Output from the research agent."""
    keyword: str = Field(..., description="Target keyword researched")
    serp_analysis: Dict[str, Any] = Field(..., description="Analysis of search results")
    total_sources: int = Field(..., description="Number of sources analyzed")
    total_words_analyzed: int = Field(..., description="Total word count analyzed")
    main_topics: List[ResearchTopic] = Field(..., description="Main topics identified")
    content_structure_patterns: List[Dict[str, Any]] = Field(..., description="Common content structures")
    writing_style_analysis: Dict[str, Any] = Field(..., description="Analysis of writing styles")
    authority_signals: List[Dict[str, Any]] = Field(..., description="Authority signals identified")
    execution_time: float = Field(..., description="Time taken for research in seconds")


class BriefTopic(BaseModel):
    """A topic recommended in the content brief."""
    title: str = Field(..., description="Topic title")
    description: str = Field(..., description="Detailed description")
    suggested_heading: str = Field(..., description="Suggested heading format")
    key_points: List[str] = Field(..., description="Key points to cover")
    word_count_suggestion: int = Field(..., description="Suggested word count")
    importance: float = Field(..., description="Importance score (0-1)")


class ContentBrief(BaseModel):
    """Output from the brief creation agent."""
    keyword: str = Field(..., description="Target keyword")
    content_title_suggestions: List[str] = Field(..., description="Suggested content titles")
    target_word_count: int = Field(..., description="Target word count")
    target_audience: str = Field(..., description="Target audience description")
    search_intent: str = Field(..., description="Identified search intent")
    content_structure: List[BriefTopic] = Field(..., description="Recommended content structure")
    differentiation_strategy: str = Field(..., description="How to differentiate from existing content")
    seo_recommendations: Dict[str, Any] = Field(..., description="SEO recommendations")
    metadata_suggestions: Dict[str, str] = Field(..., description="Suggested metadata")
    execution_time: float = Field(..., description="Time taken for brief creation in seconds")


class FactItem(BaseModel):
    """A fact or figure gathered for content enhancement."""
    content: str = Field(..., description="The fact or statistic")
    source: str = Field(..., description="Source URL or reference")
    date: Optional[str] = Field(None, description="Date of the information")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    related_topic: str = Field(..., description="Related topic from content brief")
    recommended_placement: Optional[str] = Field(None, description="Recommended content section")


class FactsOutput(BaseModel):
    """Output from the facts acquisition agent."""
    keyword: str = Field(..., description="Target keyword")
    collected_facts: List[FactItem] = Field(..., description="Collected facts and figures")
    social_trends: Dict[str, Any] = Field(..., description="Relevant social media trends")
    recent_developments: List[Dict[str, Any]] = Field(..., description="Recent developments in the topic")
    market_data: Optional[Dict[str, Any]] = Field(None, description="Relevant market data")
    execution_time: float = Field(..., description="Time taken for facts gathering in seconds")


class GeneratedContent(BaseModel):
    """Final generated content output."""
    title: str = Field(..., description="Content title")
    meta_description: str = Field(..., description="Meta description for SEO")
    content_sections: List[Dict[str, str]] = Field(..., description="Content sections with headings and text")
    word_count: int = Field(..., description="Actual word count")
    internal_link_suggestions: Optional[List[Dict[str, str]]] = Field(None, description="Suggested internal links")
    image_suggestions: Optional[List[Dict[str, str]]] = Field(None, description="Suggested images")
    tags: List[str] = Field(..., description="Suggested content tags")
    execution_time: float = Field(..., description="Time taken for content generation in seconds")

    @property
    def full_content(self) -> str:
        """Return the full content as a single string."""
        result = f"# {self.title}\n\n"
        for section in self.content_sections:
            result += f"## {section.get('heading', '')}\n\n{section.get('content', '')}\n\n"
        return result


class WorkflowResult(BaseModel):
    """Complete workflow result with outputs from all stages."""
    id: str = Field(..., description="Unique workflow ID")
    status: WorkflowStatus = Field(..., description="Current workflow status")
    request: ContentRequest = Field(..., description="Original content request")
    created_at: datetime = Field(..., description="Workflow creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    research_output: Optional[ResearchOutput] = Field(None, description="Research agent output")
    content_brief: Optional[ContentBrief] = Field(None, description="Brief creation agent output")
    facts_output: Optional[FactsOutput] = Field(None, description="Facts acquisition agent output")
    generated_content: Optional[GeneratedContent] = Field(None, description="Generated content")
    human_feedback: Optional[str] = Field(None, description="Human reviewer feedback")
    total_execution_time: Optional[float] = Field(None, description="Total workflow execution time in seconds")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="Errors encountered during workflow")


class HealthCheckResponse(BaseModel):
    """API health check response."""
    status: str = Field("ok", description="Service status")
    version: str = Field(..., description="API version")
    models: Dict[str, bool] = Field(..., description="LLM models availability")
    timestamp: datetime = Field(..., description="Current server timestamp")
