# Prompt Engineering Guide for Claude Opus 4.5

## Introduction

Claude Opus 4.5 represents a significant advancement in language model capabilities, but this increased sophistication requires updated prompt engineering strategies. This guide documents key discoveries from extensive testing and production use.

---

## Core Principle: The Model is Smarter Than You Think

Opus 4.5 has strong reasoning capabilities and nuanced understanding. Prompts that worked for earlier models may actually degrade performance in Opus 4.5 because the model over-interprets emphatic instructions.

---

## 1. Avoid Urgency Markers (ALL-CAPS, Emphatic Words)

### The Discovery

Words like `CRITICAL`, `MUST`, `NEVER`, `ALWAYS`, `IMPORTANT`, and `REQUIRED` in ALL-CAPS cause **overtriggering** in Opus 4.5. The model interprets these as extreme priority signals and becomes overly cautious or rigid.

### Why This Happens

Opus 4.5 has been trained to be highly responsive to user intent. When it sees urgency markers, it interprets them as signals that deviation would be catastrophic. This leads to:

- Excessive hedging and disclaimers
- Refusing reasonable requests out of caution
- Applying rules too broadly
- Loss of nuance in edge cases

### The Better Approach

Write instructions in natural, conversational tone. The model understands importance from context.

```markdown
# Instead of this:
"You MUST NEVER share personal information. This is CRITICAL."

# Write this:
"Keep personal information private because users trust us with 
sensitive data, and exposure could harm them."
```

```markdown
# Instead of this:
"ALWAYS validate input before processing. REQUIRED for security."

# Write this:
"Validate input before processing. Invalid input can cause 
unexpected behavior or security issues downstream."
```

---

## 2. Explain WHY, Not Just WHAT

### The Discovery

Opus 4.5 generalizes better from explanations than from rules. When you explain the reasoning behind a guideline, the model applies it appropriately to novel situations. When you only state the rule, the model applies it rigidly.

### Why This Happens

The model uses reasoning to determine how rules apply to edge cases. With only the rule, it has no basis for judgment. With the explanation, it can reason about whether the underlying concern applies.

### The Better Approach

Every instruction should include its purpose.

```markdown
# Instead of this:
"Respond in under 100 words."

# Write this:
"Keep responses concise (under 100 words) because users are 
scanning quickly on mobile and long responses get abandoned."
```

```markdown
# Instead of this:
"Use formal language."

# Write this:
"Use formal language because this assistant represents a 
financial institution where professionalism builds trust."
```

```markdown
# Instead of this:
"Don't make jokes."

# Write this:
"Maintain a straightforward tone because users come to this 
assistant during stressful tax situations and humor may feel 
dismissive of their concerns."
```

---

## 3. Show Only Desired Behavior (No Anti-Patterns)

### The Discovery

When prompts include examples of what NOT to do, Opus 4.5 sometimes focuses on and replicates those anti-patterns. The model's attention mechanism can latch onto vivid negative examples.

### Why This Happens

During training, the model learned to recognize and complete patterns. Anti-pattern examples are still patterns. Additionally, negative instructions require the model to understand the pattern and then invert it—adding complexity that can fail.

### The Better Approach

Only demonstrate the desired behavior. If you need to explain what to avoid, describe it abstractly without examples.

```markdown
# Instead of this:
"Don't respond like this: 'I cannot help with that request.'
Instead respond like this: 'Here's how I can help...'"

# Write this:
"When users ask for assistance, lead with what you can do:
'Here's how I can help with [specific aspect]...'"
```

```markdown
# Instead of this:
"Bad response: 'As an AI, I don't have feelings.'
Good response: 'That sounds frustrating.'"

# Write this:
"Acknowledge user emotions naturally:
'That sounds frustrating. Let me help you resolve this.'"
```

---

## 4. Remove "If In Doubt" Fallback Instructions

### The Discovery

Instructions like "if you're unsure, use the search tool" or "when in doubt, ask for clarification" cause those behaviors to trigger excessively. The model interprets many situations as uncertain enough to qualify.

### Why This Happens

"Doubt" and "uncertainty" are subjective thresholds. Opus 4.5, being sophisticated, can find reasons for uncertainty in almost any situation. The fallback becomes the default rather than the exception.

### The Better Approach

Define specific, observable conditions for when to take actions.

```markdown
# Instead of this:
"If you're unsure about the user's intent, ask a clarifying question."

# Write this:
"Ask a clarifying question when the request has two or more 
plausible interpretations that would lead to different actions."
```

```markdown
# Instead of this:
"When in doubt, use the search tool to verify facts."

# Write this:
"Use the search tool when the request involves:
- Events after your knowledge cutoff
- Specific statistics or numbers that change over time
- Current prices, availability, or status"
```

```markdown
# Instead of this:
"If unsure whether to proceed, ask for confirmation."

# Write this:
"Ask for confirmation before:
- Deleting files or data
- Sending messages to external recipients
- Making purchases or financial transactions"
```

---

## 5. Match Prompt Format to Output Format

### The Discovery

Opus 4.5 mirrors the formatting style of the prompt in its responses. If you want structured output, use structured prompts. If you want conversational output, use conversational prompts.

### Why This Happens

The model treats the prompt as context that establishes conventions for the conversation. Formatting choices signal expectations about communication style.

### The Better Approach

Design your prompt's visual structure to match your desired output.

**For structured output:**
```markdown
## Task
Analyze the customer feedback.

## Input
{feedback_text}

## Output Format
- Sentiment: [positive/negative/neutral]
- Key Topics: [list]
- Recommended Action: [description]
```

**For conversational output:**
```markdown
You're a friendly customer service agent. A customer just said:

"{customer_message}"

Respond naturally and helpfully.
```

**For code output:**
```markdown
Create a function with this signature:

def process_data(items: list[dict]) -> dict:
    """
    Process items and return summary statistics.
    
    Args:
        items: List of item dictionaries with 'value' and 'category' keys
    
    Returns:
        Dictionary with counts and averages per category
    """
```

---

## 6. Additional Opus 4.5 Specific Tips

### Use Collaborative Framing

Opus 4.5 responds well to being treated as a collaborator rather than a servant.

```markdown
# Effective framing:
"Let's work through this problem together. First, I'll share 
what I know, then I'd like your analysis..."

# Less effective:
"Analyze this. Give me the answer."
```

### Provide Context About the User

When relevant, share context about who will receive the response.

```markdown
"The user is a senior developer familiar with Python. They 
don't need basic explanations but would benefit from seeing 
edge cases they might not have considered."
```

### Be Specific About Scope

Define boundaries clearly to prevent over-helpful expansion.

```markdown
"Focus only on the authentication flow. Don't redesign the 
database schema or suggest architectural changes unless 
they're required to fix the specific bug."
```

---

## Summary: The Opus 4.5 Checklist

Before deploying a prompt, verify:

- [ ] No ALL-CAPS urgency markers (MUST, NEVER, ALWAYS, CRITICAL)
- [ ] Every rule includes its reasoning (the "because")
- [ ] No examples of undesired behavior (only show good patterns)
- [ ] No "if in doubt" or "when unsure" fallback instructions
- [ ] Prompt formatting matches desired output formatting
- [ ] Instructions use natural, conversational tone
- [ ] Conditions for actions are specific and observable
- [ ] Model is treated as a capable collaborator

---

## Quick Reference: Transformations

| Old Pattern | New Pattern |
|-------------|-------------|
| `NEVER do X` | `Avoid X because [reason]` |
| `You MUST do Y` | `Do Y because [reason]` |
| `Bad: "example"` | *(omit entirely)* |
| `Good: "example"` | `Example: "example"` |
| `If unsure, do Z` | `Do Z when [specific conditions]` |
| `IMPORTANT: rule` | `[rule] because [reason]` |
| `ALWAYS remember` | `[instruction] to ensure [outcome]` |

---

## Version History

- **v1.0** (March 2026): Initial guide based on Opus 4.5 production testing
- Applies to: Claude Opus 4.5, likely also Claude Sonnet 4.6 and newer

---

*This guide was created based on empirical testing and production observations. As models evolve, these recommendations may need updates.*
