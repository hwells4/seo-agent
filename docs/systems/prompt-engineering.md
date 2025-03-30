# Prompt Engineering Strategies

## Overview

This document outlines the prompt engineering strategies used for each agent in the SEO content creation workflow. Effective prompt engineering is critical for extracting optimal performance from each specialized language model.

## General Principles

1. **Structured Output**: Use JSON schema validation to ensure consistent structured outputs
2. **Clear Instructions**: Provide explicit, detailed instructions on expected behavior
3. **Few-shot Examples**: Include examples for complex tasks to guide the model
4. **Context Management**: Efficiently package relevant information within token limits
5. **Temperature Control**: Adjust temperature based on task creativity requirements

## Research Agent (O3Mini)

### Purpose
Extract patterns and insights from large volumes of content data.

### Prompt Structure
```
Analyze the following content sources for the keyword: "{keyword}"

SOURCES:
{json_sources}

Perform a comprehensive analysis to identify:
1. Common topics and subtopics
2. Content structure patterns 
3. Writing style and tone
4. Authority signals (citations, expert quotes, statistics)
5. Overall word count and content depth patterns

Provide a structured analysis in JSON format with these sections.
```

### Key Techniques
- Lower temperature (0.2) for analytical accuracy
- Structured JSON output schema for consistent results
- Explicit enumeration of analysis dimensions

### Optimization Tips
- Limit source data to essential information
- Use summarized metadata rather than full content
- Prompt for specific analysis categories to avoid omissions

## Brief Agent (DeepSeek)

### Purpose
Identify content gaps and create strategic content briefs.

### Prompt Structure
```
Based on the research analysis for keyword "{keyword}", create a comprehensive content brief.

RESEARCH ANALYSIS:
{research_json}

Your task is to:
1. Identify content gaps and opportunities
2. Create a detailed content structure
3. Recommend SEO strategies
4. Suggest title options
5. Define key points that must be covered

The brief should address search intent while providing a unique angle compared to existing content.
```

### Key Techniques
- Moderate temperature (0.3) for strategic creativity
- Clear instruction on competitive differentiation
- Chain-of-thought reasoning for brief justification

### Optimization Tips
- Structure the brief to emphasize E-E-A-T signals
- Include specific guidance on content differentiation
- Request title variations with different emotional appeals

## Facts Agent (Grok3)

### Purpose
Gather current, accurate facts and supporting evidence.

### Prompt Structure
```
Using the content brief for "{keyword}", find current facts, statistics, and supporting evidence.

CONTENT BRIEF:
{brief_json}

Search for:
1. Recent statistics and data (from the past year if possible)
2. Expert quotes or insights
3. Current industry trends
4. Supporting research findings
5. Relevant case studies

For each fact, include the source URL and date of publication. Verify information from multiple sources when possible.
```

### Key Techniques
- Low temperature (0.1) for factual accuracy
- Explicit guidance on source validation
- Structured format for fact organization

### Optimization Tips
- Set specific recency requirements for information
- Request validation across multiple sources
- Prompt for diverse fact types (statistics, quotes, studies)

## Content Agent (Claude 3.7)

### Purpose
Generate high-quality, human-sounding content integrating all previous outputs.

### Prompt Structure
```
Create engaging content for the keyword "{keyword}" using the following inputs:

RESEARCH ANALYSIS:
{research_summary}

CONTENT BRIEF:
{brief_summary}

SUPPORTING FACTS:
{facts_summary}

BRAND VOICE GUIDELINES:
{brand_voice}

Additional requirements:
- Target audience: {target_audience}
- Tone: {tone}
- Word count: ~{word_count} words
- Content type: {content_type}

Create content that demonstrates expertise, authoritativeness, and trustworthiness while engaging the target audience. The content should address search intent comprehensively while maintaining a natural, human-like writing style.
```

### Key Techniques
- Higher temperature (0.5) for creative expression
- Brand voice adaptation through detailed guidelines
- Audience-specific framing of technical concepts

### Optimization Tips
- Include sections for introduction, body, and conclusion
- Prompt for natural transitions between topics
- Request incorporation of specific engagement techniques

## Schema Validation

Each agent uses JSON schema validation to ensure consistent output structure:

### Research Output Schema
```json
{
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
          "common_phrases": {"type": "array", "items": {"type": "string"}}
        }
      }
    },
    "content_structure_patterns": {
      "type": "array",
      "items": {"type": "object"}
    },
    "writing_style_analysis": {"type": "object"},
    "authority_signals": {"type": "array", "items": {"type": "object"}},
    "total_words_analyzed": {"type": "integer"}
  }
}
```

Similar schema validation is applied to other agent outputs.

## Prompt Testing and Refinement

### Testing Process
1. Create baseline prompts for each agent
2. Test with diverse keywords from different domains
3. Analyze output quality and consistency
4. Refine prompts to address identified weaknesses
5. Re-test with the same inputs to measure improvement

### Evaluation Criteria
- **Completeness**: Does the output contain all required components?
- **Accuracy**: Are facts and analysis correct?
- **Relevance**: Does the output match the intended purpose?
- **Consistency**: Is the structure consistent across different inputs?
- **Creativity**: Does the output provide unique insights where appropriate?

## Troubleshooting Common Issues

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Missing sections in output | Schema validation failure | Add explicit instructions for required fields |
| Generic content | Insufficient context | Provide more specific examples and constraints |
| Hallucinated facts | Lack of validation guidance | Add instructions to cite sources and verify information |
| Inconsistent structure | Unclear formatting instructions | Use structured examples with clear headings |
| Token limit errors | Overly verbose prompts | Streamline instructions and use efficient context packaging | 