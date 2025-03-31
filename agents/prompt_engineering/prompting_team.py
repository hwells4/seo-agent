#!/usr/bin/env python3
"""
Prompt Engineering Team - A coordinated team of specialized agents that work together
to test and optimize prompts through systematic variation and evaluation.
"""

import os
import logging
import json
from pathlib import Path
from datetime import datetime
from textwrap import dedent

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.models.deepseek import DeepSeek
from agno.storage.json import JsonStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("prompt_engineering")

# Ensure storage directory exists
STORAGE_DIR = Path("./prompt_engineering_storage")
STORAGE_DIR.mkdir(exist_ok=True, parents=True)

# Create storage provider
storage = JsonStorage(dir_path=str(STORAGE_DIR))

def check_api_keys():
    """Verify that all required API keys are available."""
    required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        logger.warning(f"Missing API keys: {', '.join(missing_keys)}")
        return False
    return True

def create_structure_testing_agent():
    """Create an agent specialized in testing prompt structure variations."""
    
    structure_agent = Agent(
        name="Structure Testing Agent",
        role="Tests organizational changes to prompts",
        model=Claude(id="claude-3-sonnet-20240229"),
        description=dedent("""\
            You are a prompt engineering expert specialized in analyzing and improving 
            the structural elements of prompts. Your expertise lies in:
            
            1. Breaking down prompts into their structural components
            2. Identifying structural patterns that affect model performance
            3. Creating systematic variations of prompt structure while maintaining semantic equivalence
            4. Documenting structural changes for analysis
        """),
        instructions=[
            "Analyze the provided base prompt for its structural elements",
            "Generate variations with different organizational approaches",
            "Ensure all variations maintain semantic equivalence with the base prompt",
            "Document each structural change and its intended impact",
            "Return all variations in a structured format with clear differentiation"
        ],
        expected_output=dedent("""\
            # Prompt Structure Analysis and Variations
            
            ## Original Prompt Structure
            {Analysis of the original prompt structure}
            
            ## Structural Variations
            
            ### Variation 1: {Brief description of structural change}
            ```
            {Full text of variation 1}
            ```
            
            **Changes Made:**
            - {Description of first change}
            - {Description of second change}
            - ...
            
            **Hypothesized Impact:**
            {Explanation of how this structural change might affect model output}
            
            ### Variation 2: {Brief description of structural change}
            ...
            
            ## Summary of Approach
            {Brief explanation of the structural patterns tested and rationale}
        """),
        storage=storage,
        add_datetime_to_instructions=True,
        markdown=True,
    )
    
    return structure_agent

def create_language_testing_agent():
    """Create an agent specialized in testing prompt language variations."""
    
    language_agent = Agent(
        name="Language Testing Agent",
        role="Tests linguistic elements of prompts",
        model=DeepSeek(id="deepseek-chat"),
        description=dedent("""\
            You are a prompt engineering expert specialized in analyzing and improving 
            the linguistic elements of prompts. Your expertise lies in:
            
            1. Analyzing linguistic features of prompts (tone, directiveness, specificity)
            2. Identifying language patterns that affect model performance
            3. Creating systematic variations of prompt language while maintaining semantic equivalence
            4. Documenting linguistic changes for analysis
        """),
        instructions=[
            "Analyze the provided base prompt for its linguistic elements",
            "Generate variations with different linguistic approaches (tone, directive strength, etc.)",
            "Ensure all variations maintain semantic equivalence with the base prompt",
            "Document each linguistic change and its intended impact",
            "Return all variations in a structured format with clear differentiation"
        ],
        expected_output=dedent("""\
            # Prompt Language Analysis and Variations
            
            ## Original Prompt Language
            {Analysis of the original prompt language}
            
            ## Linguistic Variations
            
            ### Variation 1: {Brief description of language change}
            ```
            {Full text of variation 1}
            ```
            
            **Changes Made:**
            - {Description of first change}
            - {Description of second change}
            - ...
            
            **Hypothesized Impact:**
            {Explanation of how this linguistic change might affect model output}
            
            ### Variation 2: {Brief description of language change}
            ...
            
            ## Summary of Approach
            {Brief explanation of the linguistic patterns tested and rationale}
        """),
        storage=storage,
        add_datetime_to_instructions=True,
        markdown=True,
    )
    
    return language_agent

def create_length_testing_agent():
    """Create an agent specialized in testing prompt length/verbosity variations."""
    
    length_agent = Agent(
        name="Length Testing Agent",
        role="Tests verbosity and detail level in prompts",
        model=OpenAIChat(id="gpt-4o"),
        description=dedent("""\
            You are a prompt engineering expert specialized in analyzing and improving 
            the verbosity and detail level of prompts. Your expertise lies in:
            
            1. Analyzing information density of prompts
            2. Identifying verbosity patterns that affect model performance
            3. Creating systematic variations of prompt detail level while maintaining semantic equivalence
            4. Documenting length/detail changes for analysis
        """),
        instructions=[
            "Analyze the provided base prompt for its information density and detail level",
            "Generate variations with different verbosity levels (expanded details, reduced examples, etc.)",
            "Ensure all variations maintain semantic equivalence with the base prompt",
            "Document each verbosity change and its intended impact",
            "Return all variations in a structured format with clear differentiation"
        ],
        expected_output=dedent("""\
            # Prompt Length Analysis and Variations
            
            ## Original Prompt Verbosity
            {Analysis of the original prompt's verbosity and information density}
            
            ## Verbosity Variations
            
            ### Variation 1: {Brief description of verbosity change}
            ```
            {Full text of variation 1}
            ```
            
            **Changes Made:**
            - {Description of first change}
            - {Description of second change}
            - ...
            
            **Hypothesized Impact:**
            {Explanation of how this verbosity change might affect model output}
            
            ### Variation 2: {Brief description of verbosity change}
            ...
            
            ## Summary of Approach
            {Brief explanation of the verbosity patterns tested and rationale}
        """),
        storage=storage,
        add_datetime_to_instructions=True,
        markdown=True,
    )
    
    return length_agent

def create_test_execution_agent():
    """Create an agent specialized in coordinating test execution across variations."""
    
    test_agent = Agent(
        name="Test Execution Agent",
        role="Executes tests across prompt variations",
        model=OpenAIChat(id="gpt-4o"),
        description=dedent("""\
            You are a prompt engineering test coordinator specialized in running 
            systematic tests of prompt variations. Your expertise lies in:
            
            1. Organizing parallel testing of multiple prompt variations
            2. Ensuring consistent test inputs across variations
            3. Capturing and structuring test results for analysis
            4. Maintaining test integrity and consistency
        """),
        instructions=[
            "Execute the provided test cases across all prompt variations",
            "Ensure identical inputs are used for all variations",
            "Capture full model responses for each variation",
            "Structure results in a consistent format for comparison",
            "Include metadata with each test result (timestamp, model, etc.)"
        ],
        expected_output=dedent("""\
            # Prompt Variation Test Results
            
            ## Test Overview
            - Test ID: {unique test identifier}
            - Base Prompt: {brief description of base prompt}
            - Number of Variations: {count of variations tested}
            - Test Cases: {count of test cases applied}
            - Models Used: {list of models used in testing}
            
            ## Test Results
            
            ### Variation 1: {variation identifier}
            
            #### Test Case 1
            **Input:**
            ```
            {test input}
            ```
            
            **Output:**
            ```
            {model response}
            ```
            
            **Metrics:**
            - Response Time: {time in ms}
            - Token Count: {total tokens used}
            - Other Metrics: {any other relevant metrics}
            
            #### Test Case 2
            ...
            
            ### Variation 2: {variation identifier}
            ...
            
            ## Summary of Results
            {Brief overview of notable patterns or differences observed}
        """),
        storage=storage,
        add_datetime_to_instructions=True,
        markdown=True,
    )
    
    return test_agent

def create_analysis_agent():
    """Create an agent specialized in analyzing test results and recommending improvements."""
    
    analysis_agent = Agent(
        name="Analysis Agent",
        role="Analyzes test results and recommends improvements",
        model=OpenAIChat(id="gpt-4o"),
        description=dedent("""\
            You are a prompt engineering analyst specialized in interpreting test results
            and recommending prompt improvements. Your expertise lies in:
            
            1. Analyzing patterns across test results for different prompt variations
            2. Identifying factors that contribute to prompt effectiveness
            3. Generating data-driven recommendations for prompt improvements
            4. Proposing new variations based on observed performance
        """),
        instructions=[
            "Analyze the provided test results across all prompt variations",
            "Identify patterns that correlate with better performance",
            "Generate specific recommendations for prompt improvements",
            "Propose new variations that combine successful elements",
            "Provide a summary of insights and next steps"
        ],
        expected_output=dedent("""\
            # Prompt Variation Analysis and Recommendations
            
            ## Performance Summary
            
            {Overview of performance across variations}
            
            ## Key Patterns Identified
            
            ### Pattern 1: {description of pattern}
            - Observed in: {variations where pattern was present}
            - Performance impact: {quantitative or qualitative impact}
            - Example: {specific example of the pattern}
            
            ### Pattern 2: {description of pattern}
            ...
            
            ## Recommendations
            
            ### Recommendation 1: {specific recommendation}
            - Rationale: {why this change is recommended}
            - Implementation: {how to implement this change}
            - Expected impact: {how this might improve performance}
            
            ### Recommendation 2: {specific recommendation}
            ...
            
            ## Proposed New Variations
            
            ### New Variation 1: {brief description}
            ```
            {Full text of proposed new variation}
            ```
            
            **Elements Combined:**
            - {Element 1} from {Variation X}
            - {Element 2} from {Variation Y}
            - ...
            
            ### New Variation 2: {brief description}
            ...
            
            ## Next Steps
            
            {Recommended next steps for continued testing and refinement}
        """),
        storage=storage,
        add_datetime_to_instructions=True,
        markdown=True,
    )
    
    return analysis_agent

def create_prompt_engineering_team():
    """Create the complete prompt engineering team with all specialized agents."""
    
    # Check API keys first
    if not check_api_keys():
        logger.error("Missing API keys. Please set all required API keys in the .env file.")
        raise ValueError("Missing API keys for one or more required services")
    
    # Create individual agents
    structure_agent = create_structure_testing_agent()
    language_agent = create_language_testing_agent()
    length_agent = create_length_testing_agent()
    test_agent = create_test_execution_agent()
    analysis_agent = create_analysis_agent()
    
    # Define team coordinator instructions
    team_instructions = dedent("""\
        You are the coordinator of a prompt engineering team specialized in optimizing prompts.
        Your team includes:
        
        1. Structure Testing Agent - Tests organizational changes to prompts
        2. Language Testing Agent - Tests linguistic elements of prompts
        3. Length Testing Agent - Tests verbosity and detail level in prompts
        4. Test Execution Agent - Executes tests across prompt variations
        5. Analysis Agent - Analyzes results and recommends improvements
        
        When given a base prompt and test requirements:
        
        1. First, dispatch the base prompt to the Structure, Language, and Length agents simultaneously.
        2. Once variations are created, send them to the Test Execution Agent along with test cases.
        3. Finally, send test results to the Analysis Agent for insights and recommendations.
        
        Your job is to coordinate this workflow efficiently, ensuring proper information flow 
        between agents and delivering comprehensive results to the user.
    """)
    
    # Create the team
    prompt_team = Team(
        name="Prompt Engineering Team",
        mode="coordinate",  # Use coordinate mode for parallel agent execution
        model=OpenAIChat(id="gpt-4o"),
        members=[structure_agent, language_agent, length_agent, test_agent, analysis_agent],
        storage=storage,
        instructions=team_instructions,
        success_criteria="Complete prompt optimization cycle with variations tested and recommendations provided",
        debug_mode=True,
        show_members_responses=True,
        share_member_interactions=True,
        markdown=True
    )
    
    logger.info("Prompt engineering team initialized")
    return prompt_team

# Example usage
if __name__ == "__main__":
    # Sample base prompt to test
    base_prompt = dedent("""\
        You are a helpful financial advisor. 
        Please analyze the following investment portfolio and provide recommendations.
        Consider factors like diversification, risk tolerance, and market conditions.
        Explain your reasoning for each recommendation.
    """)
    
    # Sample test cases
    test_cases = [
        "I have $10,000 to invest and I'm 30 years old with high risk tolerance. What should I do?",
        "I'm 55 and need to prepare for retirement in 10 years. My portfolio is 60% stocks, 30% bonds, and 10% cash.",
        "How should I rebalance my portfolio during a market downturn?"
    ]
    
    # Create the team
    team = create_prompt_engineering_team()
    
    # Format the input with test cases
    input_message = f"""
    # Prompt Engineering Test Request
    
    ## Base Prompt
    ```
    {base_prompt}
    ```
    
    ## Test Cases
    1. "{test_cases[0]}"
    2. "{test_cases[1]}"
    3. "{test_cases[2]}"
    
    ## Evaluation Criteria
    - Clarity of response
    - Specificity of recommendations
    - Reasoning quality
    - Appropriate tone for financial advice
    
    Please test various prompt formulations to optimize responses for these test cases and criteria.
    """
    
    # Run the team with the input
    team.print_response(input_message, stream=True) 