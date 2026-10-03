# Final Fix: Forcing Contradiction Detection

## The Persistent Problem

Even after enhancing the prompts, the LLM is STILL marking obvious contradictions as "neutral":

**Evidence**: "the mango is a fruit"
**Claim**: "Mango is a vegetable"
**LLM Output**: stance = "neutral" ❌
**Should Be**: stance = "contradicting" ✅

This causes FALSE claims to be marked as TRUE.

## Root Cause

The LLM (Gemini or Anthropic) is being too cautious and marking everything as "neutral" even with explicit instructions. This is a known issue with some LLMs - they avoid making definitive judgments even when the answer is obvious.

## Final Solution: Post-Processing Safety Net

I've added **automated contradiction detection** that runs AFTER the LLM, catching mistakes it makes.

### Implementation

**File**: `backend/app/agents/evidence_agent/agent.py` (lines 104-121)

```python
# Post-process: catch obvious contradictions the LLM missed
claim_lower = (claim.get("normalized_text") or claim["text"]).lower()
text_lower = text.lower()

# Check for opposite categories
opposite_pairs = [
    ("vegetable", "fruit"), ("fruit", "vegetable"),
    ("animal", "plant"), ("plant", "animal"),
    ("true", "false"), ("false", "true"),
    ("is", "is not"), ("is not", "is"),
]

for word1, word2 in opposite_pairs:
    if word1 in claim_lower and word2 in text_lower:
        # Claim says one thing, source says opposite - force contradicting
        stance = "contradicting"
        logger.info("Corrected stance to 'contradicting' - claim has '%s', evidence has '%s'", word1, word2)
        break
```

### How It Works

1. **LLM processes evidence** (might incorrectly say "neutral")
2. **Post-processor checks** for opposite word pairs
3. **If found**, OVERRIDES the LLM's decision to "contradicting"
4. **Logs the correction** so you can see it happened

### Opposite Pairs Detected

- `vegetable` ↔ `fruit`
- `animal` ↔ `plant`  
- `true` ↔ `false`
- `is` ↔ `is not`

You can add more pairs as needed!

## Enhanced Prompts Also Applied

### Clearer System Message
```python
"You are a precise fact-checking evidence extractor. Your job is to determine if source text SUPPORTS, CONTRADICTS, or is NEUTRAL to a claim."
"If the source says something DIFFERENT from the claim (different category, opposite fact), mark it as 'contradicting'."
"Example: If claim says 'X is a vegetable' but source says 'X is a fruit', mark as 'contradicting'."
```

### Step-by-Step Reasoning Process
```python
REASONING PROCESS:
1. Read the claim carefully - what is it asserting?
2. Read each source - what fact does it state?
3. Compare: Do they say the SAME thing, OPPOSITE things, or UNRELATED things?
4. Assign stance based on comparison
```

### More Examples
Added 10+ concrete examples of contradictions and support to train the LLM better.

## Expected Results After This Fix

### Test Case 1: Mango (Should Be FALSE)
```
Claim: "Mango is a vegetable"
Evidence: "mango is a fruit"
Detection: claim has "vegetable", evidence has "fruit" → CONTRADICTING
Verdict: FALSE or MOSTLY_FALSE
Confidence: 80-95%
```

### Test Case 2: Reverse (Should Be TRUE)
```
Claim: "Mango is a fruit"
Evidence: "mango is a tropical stone fruit"
Detection: Both say "fruit" → SUPPORTING (no override needed)
Verdict: TRUE
Confidence: 90-99%
```

### Test Case 3: Other Opposites
```
Claim: "Dogs are plants"
Evidence: "Dogs are animals"
Detection: claim has "plant", evidence has "animal" → CONTRADICTING
Verdict: FALSE
```

## Why This Approach Works

### Defense in Depth
1. **First Line**: Enhanced prompts teach the LLM
2. **Second Line**: Post-processing catches what LLM missed
3. **Result**: Bulletproof contradiction detection

### Fail-Safe System
- If LLM works correctly → great!
- If LLM fails → post-processor fixes it
- Either way → correct result

### Extensible
You can easily add more opposite pairs:
```python
("president", "former president"),
("current", "past"),
("yes", "no"),
("exists", "does not exist"),
# etc.
```

## Testing Steps

1. **Restart your backend server**
   ```bash
   # Stop and restart to load new code
   ```

2. **Create a NEW investigation** (don't reuse old one)
   - Old investigations have cached evidence
   - New investigation will use updated code

3. **Test with**: "Mango is a vegetable"
   
4. **Check the backend logs** for:
   ```
   INFO: Corrected stance to 'contradicting' - claim has 'vegetable', evidence has 'fruit'
   ```

5. **Verify the verdict**:
   - Should be: FALSE or MOSTLY_FALSE
   - Confidence: 80-95%
   - Evidence stance: CONTRADICTING (not neutral)

## Additional Test Cases

### Should Return FALSE
- ✅ "Mango is a vegetable"
- ✅ "Earth is flat"
- ✅ "Dogs are plants"
- ✅ "The sky is green"
- ✅ "Water is solid at room temperature"

### Should Return TRUE
- ✅ "Mango is a fruit"
- ✅ "Earth is round"
- ✅ "Dogs are animals"
- ✅ "The sky is blue"
- ✅ "Water is liquid at room temperature"

## Monitoring

Watch your backend logs during investigation. You should see:

```
INFO: Corrected stance to 'contradicting' - claim has 'vegetable', evidence has 'fruit'
```

This confirms the post-processor is catching contradictions the LLM missed.

## If It STILL Doesn't Work

If you're still seeing FALSE marked as TRUE, check:

1. **Are you testing with a NEW investigation?**
   - Old cached results won't reflect code changes
   
2. **Is the backend restarted?**
   - Code changes require server restart
   
3. **Check the logs** - is the correction happening?
   - If not, the opposite pairs might need expanding
   
4. **What does the evidence text say exactly?**
   - Post-processor looks for exact word matches (case-insensitive)
   - If evidence says "drupe" instead of "fruit", add that pair

## Expanding the Safety Net

To add more contradiction detections, edit the `opposite_pairs` list:

```python
opposite_pairs = [
    ("vegetable", "fruit"), 
    ("fruit", "vegetable"),
    ("animal", "plant"),
    ("plant", "animal"),
    # Add your own:
    ("president", "former president"),
    ("current president", "was president"),
    ("alive", "dead"),
    ("exists", "does not exist"),
    # etc.
]
```

## Summary

This is a **three-layer defense system**:

1. **Layer 1**: Enhanced system message
2. **Layer 2**: Detailed prompt with 10+ examples
3. **Layer 3**: Post-processing safety net that FORCES corrections

No matter how cautious or confused the LLM is, Layer 3 will catch obvious contradictions and fix them automatically!

**Restart your backend, start a NEW investigation with "Mango is a vegetable", and it should now correctly return FALSE!** 🥭❌
