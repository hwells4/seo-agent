"""
Validation utilities for agent outputs and inputs.

This module provides validation functions for ensuring the quality and
completeness of agent outputs throughout the content generation workflow.
"""

import logging
from typing import Any, Dict, List, Optional

from src.models.content_models import (
    ResearchOutput, ContentBrief, FactsOutput, 
    GeneratedContent, WorkflowResult
)

# Set up logger
logger = logging.getLogger(__name__)


def validate_research_output(output: ResearchOutput) -> None:
    """Validate the research agent output for completeness and quality.
    
    Args:
        output: The research output to validate
        
    Raises:
        ValueError: If validation fails
    """
    errors = []
    
    # Check for empty or incomplete data
    if not output.keyword:
        errors.append("Missing keyword")
    
    if output.total_sources < 1:
        errors.append("No sources analyzed")
    
    if output.total_words_analyzed < 1000:
        errors.append("Insufficient content analyzed (< 1000 words)")
    
    if len(output.main_topics) < 3:
        errors.append("Insufficient topics identified (< 3)")
    
    if not output.content_structure_patterns:
        errors.append("Missing content structure patterns")
    
    if not output.writing_style_analysis:
        errors.append("Missing writing style analysis")
        
    # Check for quality issues
    for topic in output.main_topics:
        if topic.importance < 0 or topic.importance > 1:
            errors.append(f"Invalid importance score for topic '{topic.title}'")
        
        if not topic.common_phrases:
            errors.append(f"No common phrases for topic '{topic.title}'")
    
    # Raise exception if validation fails
    if errors:
        error_message = f"Research output validation failed with {len(errors)} errors: {'; '.join(errors)}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    logger.info("Research output validation passed")


def validate_content_brief(brief: ContentBrief) -> None:
    """Validate the content brief for completeness and quality.
    
    Args:
        brief: The content brief to validate
        
    Raises:
        ValueError: If validation fails
    """
    errors = []
    
    # Check for empty or incomplete data
    if not brief.keyword:
        errors.append("Missing keyword")
    
    if not brief.content_title_suggestions:
        errors.append("Missing title suggestions")
    
    if brief.target_word_count < 300:
        errors.append("Target word count too low (< 300)")
    
    if not brief.search_intent:
        errors.append("Missing search intent")
    
    if len(brief.content_structure) < 3:
        errors.append("Insufficient content structure (< 3 sections)")
    
    if not brief.differentiation_strategy:
        errors.append("Missing differentiation strategy")
    
    if not brief.seo_recommendations:
        errors.append("Missing SEO recommendations")
    
    # Check for quality issues in content structure
    for topic in brief.content_structure:
        if not topic.key_points:
            errors.append(f"No key points for topic '{topic.title}'")
        
        if topic.word_count_suggestion < 50:
            errors.append(f"Word count suggestion too low for topic '{topic.title}'")
    
    # Raise exception if validation fails
    if errors:
        error_message = f"Content brief validation failed with {len(errors)} errors: {'; '.join(errors)}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    logger.info("Content brief validation passed")


def validate_facts_output(facts: FactsOutput) -> None:
    """Validate the facts acquisition output for completeness and quality.
    
    Args:
        facts: The facts output to validate
        
    Raises:
        ValueError: If validation fails
    """
    errors = []
    
    # Check for empty or incomplete data
    if not facts.keyword:
        errors.append("Missing keyword")
    
    if not facts.collected_facts:
        errors.append("No facts collected")
    
    if not facts.social_trends:
        errors.append("Missing social trends")
    
    if not facts.recent_developments:
        errors.append("Missing recent developments")
    
    # Check for quality issues in facts
    for fact in facts.collected_facts:
        if not fact.source:
            errors.append(f"Missing source for fact: '{fact.content[:50]}...'")
        
        if fact.relevance_score < 0 or fact.relevance_score > 1:
            errors.append(f"Invalid relevance score for fact: '{fact.content[:50]}...'")
    
    # Raise exception if validation fails
    if errors:
        error_message = f"Facts output validation failed with {len(errors)} errors: {'; '.join(errors)}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    logger.info("Facts output validation passed")


def validate_generated_content(content: GeneratedContent) -> None:
    """Validate the generated content for completeness and quality.
    
    Args:
        content: The generated content to validate
        
    Raises:
        ValueError: If validation fails
    """
    errors = []
    
    # Check for empty or incomplete data
    if not content.title:
        errors.append("Missing title")
    
    if not content.meta_description:
        errors.append("Missing meta description")
    
    if not content.content_sections:
        errors.append("No content sections")
    
    if content.word_count < 300:
        errors.append("Content too short (< 300 words)")
    
    if not content.tags:
        errors.append("Missing tags")
    
    # Check for quality issues in content sections
    for i, section in enumerate(content.content_sections):
        if not section.get("heading"):
            errors.append(f"Missing heading for section {i+1}")
        
        if not section.get("content") or len(section.get("content", "")) < 50:
            errors.append(f"Insufficient content for section {i+1}")
    
    # Raise exception if validation fails
    if errors:
        error_message = f"Generated content validation failed with {len(errors)} errors: {'; '.join(errors)}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    logger.info("Generated content validation passed")


def validate_workflow_result(result: WorkflowResult) -> None:
    """Validate the overall workflow result.
    
    Args:
        result: The workflow result to validate
        
    Raises:
        ValueError: If validation fails
    """
    errors = []
    
    # Check for required fields
    if not result.id:
        errors.append("Missing workflow ID")
    
    if not result.request or not result.request.keyword:
        errors.append("Missing or invalid request data")
    
    # Check workflow progression based on status
    if result.status in [
        "research_complete", "brief_in_progress", "brief_complete", 
        "facts_in_progress", "facts_complete", "content_in_progress", 
        "content_complete", "review_in_progress", "review_complete", "completed"
    ] and not result.research_output:
        errors.append("Missing research output for status " + result.status)
    
    if result.status in [
        "brief_complete", "facts_in_progress", "facts_complete", 
        "content_in_progress", "content_complete", "review_in_progress", 
        "review_complete", "completed"
    ] and not result.content_brief:
        errors.append("Missing content brief for status " + result.status)
    
    if result.status in [
        "facts_complete", "content_in_progress", "content_complete", 
        "review_in_progress", "review_complete", "completed"
    ] and not result.facts_output:
        errors.append("Missing facts output for status " + result.status)
    
    if result.status in [
        "content_complete", "review_in_progress", "review_complete", "completed"
    ] and not result.generated_content:
        errors.append("Missing generated content for status " + result.status)
    
    # Raise exception if validation fails
    if errors:
        error_message = f"Workflow result validation failed with {len(errors)} errors: {'; '.join(errors)}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    logger.info(f"Workflow result validation passed for ID: {result.id}")


def validate_api_key(api_key: str, valid_api_keys: List[str]) -> bool:
    """Validate API key against list of valid keys.
    
    Args:
        api_key: The API key to validate
        valid_api_keys: List of valid API keys
        
    Returns:
        True if API key is valid, False otherwise
    """
    if not api_key:
        return False
    
    return api_key in valid_api_keys
