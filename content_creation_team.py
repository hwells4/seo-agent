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
from agno.storage.json import JsonStorage
from agno.tools.duckduckgo import DuckDuckGoTools

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

    prompt += """Return the response in JSON format with fields: 'stats' (list of facts with sources and dates), 'social_insights' (list of trends with platform, sentiment, and examples), and 'summary' (text tying it to the keyword and SEO goals)."""

    return prompt

def check_api_keys():
    """Check if required API keys are set"""
    missing_keys = []
    
    if not os.getenv("OPENAI_API_KEY"):
        missing_keys.append("OPENAI_API_KEY")
    
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
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    xai_api_key = os.getenv("XAI_API_KEY")
    
    # Create storage
    storage = JsonStorage(dir_path="./content_storage")
    
    # 1. Research & Analysis Engine (O3Mini)
    research_agent = Agent(
        name="Research Engine",
        role="Analyze content to identify trends and patterns",
        model=OpenAIChat(id="gpt-3.5-turbo-1106", api_key=openai_api_key),  # O3Mini with explicit API key
        storage=storage,
        tools=[DuckDuckGoTools()],
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
        "from content_creation_team import create_facts_prompt, extract_gap_analysis",
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
        send_team_context_to_members=True,
        markdown=True
    )
    
    logger.info("Content creation team initialized")
    return content_team

def main():
    """Run the content creation team with a test query."""
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
        
        # Create and run the team with brand voice configuration
        team = create_content_team(brand_voice)
        
        # For testing with a small topic that won't take too long
        topic = "desk organization tips"
        
        logger.info(f"Starting content creation for topic: {topic}")
        
        # Run with print_response to see all the steps in the console
        result = team.print_response(
            message=f"Create content about {topic}. The content should be helpful, practical, and about 500 words.",
            stream=True,
            stream_intermediate_steps=True
        )
        
        # Save results to a file for reference
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"content_results_{timestamp}.json"
        
        with open(filename, "w") as f:
            # Convert result to a serializable format if needed
            result_data = {
                "topic": topic,
                "content": result if isinstance(result, str) else str(result),
                "timestamp": timestamp
            }
            json.dump(result_data, f, indent=2)
        
        logger.info(f"Content results saved to {filename}")
        logger.info("Content creation completed")
        
    except Exception as e:
        logger.exception(f"Error in content creation process: {str(e)}")

if __name__ == "__main__":
    main() 