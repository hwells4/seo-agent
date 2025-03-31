#!/usr/bin/env python3
"""
Content Creation Team - A coordinated team of specialized agents that work together
to create high-quality content following a multi-stage process.
"""

import os
import logging
import datetime
import re
import json
from textwrap import dedent
from dotenv import load_dotenv

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.models.deepseek import DeepSeek
from agno.models.xai import xAI
from agno.models.openrouter import OpenRouter
from agno.storage.json import JsonStorage
from agno.tools.duckduckgo import DuckDuckGoTools

# Import the token tracker
from agents.utils.token_tracker import token_tracker

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("content_creation")

def get_formatted_date():
    """Get current date formatted as Month Day, Year"""
    return datetime.datetime.now().strftime("%B %d, %Y")

def create_facts_prompt(topic, gap_analysis=None):
    """Create a structured system prompt for fetching real-time facts
    
    Args:
        topic (str): The topic to research
        gap_analysis (str, optional): Gap analysis from previous agent
        
    Returns:
        str: Formatted system prompt
    """
    current_date = get_formatted_date()
    
    prompt = f"""Fetch real-time data as of {current_date}, related to '{topic}' for an SEO-optimized blog. Include:
1. The latest statistics or facts from credible web sources (e.g., travel reports, news articles, industry blogs).
2. Trending discussions or insights from X posts, YouTube videos/comments, Reddit threads, Hacker News posts, and other relevant social platforms (e.g., hashtags, sentiments, key topics).
3. A concise summary linking the data to the keyword and suggesting how it can enhance SEO relevance.
"""

    # Add gap analysis if provided
    if gap_analysis:
        prompt += f"""If a content gap analysis is provided below, incorporate it to identify unique angles or underserved topics competitors may have missed. 

---BEGIN GAP ANALYSIS---
{gap_analysis}
---END GAP ANALYSIS---
"""

    prompt += """Return the response in JSON format with fields: 'stats' (list of facts with sources and dates), 'social_insights' (list of trends with platform, sentiment, and examples), and 'summary' (text tying it to the keyword and SEO goals).

Keep your response concise, with 3-5 stats and 2-3 social insights at most."""

    return prompt

def check_api_keys():
    """Check if required API keys are set"""
    missing_keys = []
    
    # Check for OpenRouter API key (for o3-mini)
    if not os.getenv("OPENROUTER_API_KEY"):
        missing_keys.append("OPENROUTER_API_KEY")
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        missing_keys.append("ANTHROPIC_API_KEY")
    
    if not os.getenv("DEEPSEEK_API_KEY"):
        missing_keys.append("DEEPSEEK_API_KEY")
    
    if not os.getenv("XAI_API_KEY"):
        missing_keys.append("XAI_API_KEY")
    
    if missing_keys:
        logger.error(f"Missing API keys: {', '.join(missing_keys)}")
        return False
    
    return True

def extract_gap_analysis(brief_content):
    """Extract gap analysis section from brief content using multiple fallback methods
    
    Args:
        brief_content (str): The content brief text
        
    Returns:
        str: Extracted gap analysis or default message if not found
    """
    # Try to extract gap analysis section with heading
    gap_section_pattern = r"(?i)(?:^|\n)#+\s*Gap Analysis\s*(?:\n|$)(.*?)(?=(?:^|\n)#+\s*|\Z)"
    match = re.search(gap_section_pattern, brief_content, re.DOTALL | re.MULTILINE)
    
    if match:
        gap_analysis = match.group(1).strip()
        logger.info(f"Gap Analysis extracted ({len(gap_analysis)} chars)")
        return gap_analysis
    
    # Try more lenient extraction with label
    gap_pattern = r"(?i)Gap Analysis:?\s*(.*?)(?:\n\n|\n#|\Z)"
    match = re.search(gap_pattern, brief_content, re.DOTALL)
    if match:
        gap_analysis = match.group(1).strip()
        logger.info(f"Gap Analysis extracted with fallback method ({len(gap_analysis)} chars)")
        return gap_analysis
    
    # Try to find any mentions of gaps or opportunities
    sentences = re.findall(r'[^.!?]*(?:gap|opportunity|missing|underserved)[^.!?]*[.!?]', brief_content, re.IGNORECASE)
    if sentences:
        gap_analysis = " ".join(sentences)
        logger.info(f"Generic gap analysis extracted ({len(gap_analysis)} chars)")
        return gap_analysis
    
    # Default message if no gap analysis found
    logger.warning("No gap analysis found in brief. Using default message.")
    return "No specific gap analysis found. Focus on gathering current facts and trends."

def create_content_team(brand_voice=None):
    """Create the content creation team with specialized agents.
    
    Args:
        brand_voice (dict, optional): Dictionary containing brand voice parameters.
            Can include tone, style, taboo_words, sentence_structure, etc.
            
    Returns:
        Team: Configured content creation team
    """
    # Check API keys first
    if not check_api_keys():
        logger.error("Missing API keys. Please set all required API keys in the .env file.")
        raise ValueError("Missing API keys for one or more required services")
    
    # Get API keys
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    xai_api_key = os.getenv("XAI_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")  # Still needed for coordinator
    
    # Create storage
    storage = JsonStorage(dir_path="./content_storage")
    
    # 1. Research & Analysis Engine (O3Mini via OpenRouter)
    research_agent = Agent(
        name="Research Engine",
        role="Analyze content to identify trends and patterns",
        model=OpenRouter(
            id="openai/o3-mini",  # Specify the o3-mini model
            max_tokens=1000,  # Increased token limit for research output
            temperature=0.7,
            api_key=openrouter_api_key  # Explicitly pass the API key
        ),
        storage=storage,
        tools=[DuckDuckGoTools()],
        markdown=True,
        instructions=dedent("""
            You are a content research specialist.
            
            When given a topic:
            1. Search for top-ranking content on this topic
            2. Analyze their structure, style, and coverage
            3. Identify common topics, subtopics, and patterns
            4. Determine content styles that perform well
            5. Provide a comprehensive analysis summary
            
            Your output should be a detailed analysis report that includes:
            - Key topics covered by top-performing content
            - Common content structures and formats
            - Typical tone and style elements
            - Depth of coverage in successful content
            - Notable authority signals used
        """),
    )
    
    # 2. Gap Analysis & Brief Creation (DeepSeek)
    brief_agent = Agent(
        name="Brief Creator",
        role="Create content briefs based on research analysis",
        model=DeepSeek(id="deepseek-chat", api_key=deepseek_api_key),  # Updated model ID with explicit API key
        storage=storage,
        instructions=dedent("""
            You are a content strategy specialist.
            
            When given a research analysis:
            1. Identify content gaps and opportunities
            2. Create a detailed content brief that includes:
               - Recommended structure and outline
               - Key topics to cover thoroughly
               - Content differentiation strategy
               - E-E-A-T signals to include
               - Target word count and depth
            
            Your brief should provide clear direction for content creation
            that will outperform existing content.
            
            IMPORTANT: Include a section clearly labeled "Gap Analysis" that summarizes the key content gaps
            and opportunities you've identified. This section will be used by the Facts Collector agent
            to gather targeted real-time data. Be specific about underserved topics, angles, or questions
            that competitors are not addressing adequately.
        """),
    )
    
    # 3. Facts & Figures Acquisition (Grok3)
    facts_agent = Agent(
        name="Facts Collector",
        role="Research current facts and figures for content",
        model=xAI(id="grok-beta", api_key=xai_api_key, base_url="https://api.x.ai/v1"),  # Added base_url with explicit API key
        storage=storage,
        tools=[DuckDuckGoTools()],
        instructions=create_facts_prompt(""),  # Initialize with empty prompt - will be populated by team at runtime
    )
    
    # Prepare brand voice instructions if provided
    content_instructions = dedent("""
        You are an expert content creator.
        
        When given a content brief and supporting facts:
        1. Create engaging, high-quality content that:
           - Follows the structure in the brief
           - Addresses all required topics thoroughly
           - Incorporates facts and figures naturally
           - Maintains a consistent, appropriate tone
           - Sounds authentically human, not AI-generated
           - Demonstrates expertise and authority
        
        Your content should be publication-ready and exceed
        the quality of competing content on the same topic.
    """)
    
    # Add brand voice customization if provided
    if brand_voice:
        brand_voice_details = dedent(f"""
            BRAND VOICE GUIDELINES:
            
            Tone: {brand_voice.get('tone', 'Professional and authoritative')}
            
            Style: {brand_voice.get('style', 'Clear, concise, and engaging')}
            
            Sentence Structure: {brand_voice.get('sentence_structure', 'Varied sentence length with a mix of simple and complex structures')}
            
            Language: {brand_voice.get('language', 'Use industry terminology appropriately, but explain complex concepts clearly')}
            
            Taboo Words/Phrases: {', '.join(brand_voice.get('taboo_words', ['clearly', 'obviously', 'simply', 'just']))}
            
            Persuasion Techniques: {brand_voice.get('persuasion', 'Use evidence-based arguments, social proof, and specific examples')}
            
            Content Format: {brand_voice.get('format', 'Use clear headings, bullet points for lists, and short paragraphs')}
            
            YOU MUST STRICTLY ADHERE TO THESE BRAND VOICE GUIDELINES IN ALL CONTENT YOU CREATE.
        """)
        
        content_instructions += "\n\n" + brand_voice_details
    
    # 4. Content Generation (Claude 3.7)
    content_agent = Agent(
        name="Content Creator",
        role="Create high-quality, human-sounding content",
        model=Claude(id="claude-3-sonnet-20240229", api_key=anthropic_api_key),  # Added explicit API key
        storage=storage,
        instructions=content_instructions,
    )
    
    # Improved team instructions with better gap analysis extraction logic
    team_instructions = [
        "You are the coordinator of a content creation team.",
        "Your job is to manage the entire content creation workflow:",
        "1. First, have the Research Engine analyze top content for the topic",
        "2. Next, have the Brief Creator develop a strategy based on the research and identify content gaps",
        "3. Then, have the Facts Collector gather supporting facts and figures, focused on the identified gaps",
        "4. Finally, have the Content Creator produce the final content",
        "Each step must build on the previous one's output.",
        "",
        "IMPORTANT: When delegating to the Facts Collector, you MUST follow these exact steps:",
        "1. Extract the Gap Analysis section from the Brief Creator's output using the extract_gap_analysis function",
        "2. Create a new message for the Facts Collector using the EXACT format below:",
        "",
        "```",
        "import datetime",
        "from content_creation_team import create_facts_prompt, extract_gap_analysis",  # Using the correct module path
        "",
        "# Get topic from the current context",
        "topic = '[INSERT MAIN TOPIC HERE]'",
        "",
        "# Extract gap analysis from the Brief Creator's output",
        "brief_content = '''",
        "[INSERT BRIEF CREATOR'S FULL OUTPUT HERE]",
        "'''",
        "",
        "# Extract gap analysis using the helper function",
        "gap_analysis = extract_gap_analysis(brief_content)",
        "",
        "# Generate the structured prompt",
        "structured_prompt = create_facts_prompt(topic, gap_analysis)",
        "",
        "# The prompt below ensures consistent formatting with dynamic date handling",
        "structured_prompt",
        "```",
        "",
        "This approach ensures the Facts Collector receives a properly structured prompt with real-time date information and the gap analysis from the Brief Creator."
    ]
    
    # Create the coordinated team
    content_team = Team(
        name="Content Creation Team",
        mode="coordinate",  # Use coordinate mode for sequential workflow
        model=OpenAIChat(id="gpt-4-turbo", api_key=openai_api_key),  # Added explicit API key
        members=[research_agent, brief_agent, facts_agent, content_agent],
        storage=storage,
        instructions=team_instructions,
        success_criteria="High-quality, comprehensive content that follows the brief and incorporates all necessary facts and figures",
        debug_mode=True,
        show_members_responses=True,
        share_member_interactions=True,  # Updated from send_team_context_to_members
        markdown=True
    )
    
    logger.info("Content creation team initialized")
    return (research_agent, brief_agent, facts_agent, content_agent)

def run_content_pipeline(topic, brand_voice=None, word_count=500, save_results=True):
    """Run the content creation pipeline using individual agents rather than a Team.
    
    Args:
        topic (str): The topic for content creation
        brand_voice (dict, optional): Dictionary containing brand voice parameters
        word_count (int, optional): Target word count for the content
        save_results (bool, optional): Whether to save the results to a JSON file
        
    Returns:
        dict: Results of the content creation pipeline
    """
    logger.info(f"Starting content creation pipeline for topic: {topic}")
    
    # Reset token tracker for this run
    token_tracker.reset()
    
    # Initialize all agents
    research_agent, brief_agent, facts_agent, content_agent = create_content_team(brand_voice)
    
    results = {
        "topic": topic,
        "steps": {}
    }
    
    # Step 1: Research topic with O3Mini through OpenRouter
    logger.info("Step 1: Running Research Engine with O3Mini via OpenRouter")
    research_prompt = f"Analyze content structure and trends for '{topic}' in 300 words or less"
    
    try:
        logger.info("Sending prompt to o3-mini via OpenRouter (non-streaming)...")
        research_response = research_agent.run(research_prompt, stream=False)
        
        # Extract the response text based on response format
        if hasattr(research_response, 'content'):
            research_result = research_response.content
        else:
            research_result = str(research_response)
            
        logger.info(f"Research output received ({len(research_result)} chars)")
    except Exception as e:
        logger.error(f"Error with OpenRouter research: {str(e)}")
        # Fallback message
        research_result = f"Error in research phase: {str(e)}"
    
    # Track token usage for research step
    token_tracker.track_step(
        step_name="research",
        provider="openrouter",
        model="o3-mini",
        input_text=research_prompt,
        output_text=research_result
    )
    
    results["steps"]["research"] = {
        "prompt": research_prompt,
        "output": research_result
    }
    
    # Step 2: Create brief based on research
    logger.info("Step 2: Running Brief Creator")
    brief_prompt = f"""
        You are a content strategy specialist. Based on the following research, create a brief content outline 
        with a focus on identifying content gaps:
        
        {research_result}
        
        Include a section clearly labeled "Gap Analysis" that identifies 2-3 content opportunities 
        competitors are missing. Keep your response under 300 words.
        """
    brief_response = brief_agent.run(brief_prompt)
    brief_result = brief_response.content if hasattr(brief_response, 'content') else str(brief_response)
    
    # Track token usage for brief creation step
    token_tracker.track_step(
        step_name="brief",
        provider="deepseek",
        model="deepseek-chat",
        input_text=brief_prompt,
        output_text=brief_result
    )
    
    # Extract gap analysis
    gap_analysis = extract_gap_analysis(brief_result)
    
    results["steps"]["brief"] = {
        "prompt": brief_prompt,
        "output": brief_result,
        "extracted_gap_analysis": gap_analysis
    }
    logger.info(f"Brief output received ({len(brief_result)} chars)")
    logger.info(f"Gap Analysis extracted ({len(gap_analysis)} chars)")
    
    # Step 3: Collect facts
    logger.info("Step 3: Running Facts Collector")
    facts_prompt = create_facts_prompt(topic, gap_analysis)
    
    # Update the instructions for the facts agent
    facts_agent.instructions = facts_prompt
    
    facts_response = facts_agent.run(facts_prompt)
    facts_result = facts_response.content if hasattr(facts_response, 'content') else str(facts_response)
    
    # Track token usage for facts collection step
    token_tracker.track_step(
        step_name="facts",
        provider="xai",
        model="grok-beta",
        input_text=facts_prompt,
        output_text=facts_result
    )
    
    results["steps"]["facts"] = {
        "prompt": facts_prompt,
        "output": facts_result
    }
    logger.info(f"Facts output received ({len(facts_result)} chars)")
    
    # Step 4: Create content
    logger.info("Step 4: Running Content Creator")
    content_prompt = f"""
        Create a {word_count}-word outline about {topic} based on:
        
        RESEARCH:
        {research_result}
        
        CONTENT BRIEF:
        {brief_result}
        
        FACTS AND STATISTICS:
        {facts_result}
        
        The content should be concise and practical. Focus on an outline only.
        """
    content_response = content_agent.run(content_prompt)
    content_result = content_response.content if hasattr(content_response, 'content') else str(content_response)
    
    # Track token usage for content creation step
    token_tracker.track_step(
        step_name="content",
        provider="anthropic",
        model="claude-3-sonnet-20240229",
        input_text=content_prompt,
        output_text=content_result
    )
    
    results["steps"]["content"] = {
        "prompt": content_prompt,
        "output": content_result
    }
    logger.info(f"Content output received ({len(content_result)} chars)")
    
    # Get token usage report
    token_usage = token_tracker.get_usage_report()
    results["token_usage"] = token_usage
    
    # Print token usage report
    token_tracker.print_usage_report()
    
    # Save results to a file
    if save_results:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"content_results_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Content results saved to {filename}")
        
        # Save token usage report separately
        token_tracker.save_report_to_file(f"token_usage_{timestamp}.json")
    
    logger.info("Content creation pipeline completed")
    return results

def main():
    """Run the content creation pipeline with a test query."""
    try:
        # Check if API keys are available
        if not check_api_keys():
            logger.error("Missing API keys. Please set all required API keys in .env file.")
            return
        
        # Sample brand voice configuration
        brand_voice = {
            "tone": "Friendly but professional, conversational but authoritative",
            "style": "Direct, practical, and solution-oriented",
            "sentence_structure": "Mix of short, punchy sentences with longer explanatory ones. Prefer active voice.",
            "language": "Accessible to general audience. Avoid jargon unless necessary and then explain it.",
            "taboo_words": ["obviously", "simply", "just", "clearly", "very", "really", "actually", "basically"],
            "persuasion": "Focus on benefits rather than features. Use social proof and expert opinions.",
            "format": "Use headers, bullet points, and numbered lists for scannability. Short paragraphs (2-3 sentences)."
        }
        
        # Topic for testing - small topic that won't take too long
        topic = "desk organization tips"
        
        # Run the content pipeline with individual agents
        results = run_content_pipeline(
            topic=topic,
            brand_voice=brand_voice,
            word_count=500,
            save_results=True
        )
        
        # Print the final content
        print("\n\n" + "=" * 50)
        print(f"FINAL CONTENT FOR: {topic}")
        print("=" * 50)
        print(results["steps"]["content"]["output"])
        print("=" * 50)
        
    except Exception as e:
        logger.exception(f"Error in content creation process: {str(e)}")

if __name__ == "__main__":
    main() 