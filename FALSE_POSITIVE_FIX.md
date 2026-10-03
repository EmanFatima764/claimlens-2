# False Positive Fix - Preventing FALSE Claims Marked as TRUE

## New Problem Discovered

After fixing the "everything is unverified" issue, we now have the opposite problem:

**Example**: "Mango is a vegetable" → marked as **TRUE with 99% confidence**
- **Reality**: Mangoes are FRUITS, not vegetables
- **Evidence Found**: "mango is a tropical stone fruit"  
- **Wrong Classification**: Evidence marked as "NEUTRAL" instead of "CONTRADICTING"
- **Result**: System treats neutral as weak support → FALSE POSITIVE

## Root Cause Analysis

### Issue 1: LLM Not Detecting Contradictions
The evidence extraction agent found text saying "mango is a fruit" but marked it as **NEUTRAL** instead of **CONTRADICTING** because:
- The prompt didn't have explicit examples of what constitutes a contradiction
- The LLM focused on relevance ("it's about mangoes") rather than logical opposition ("fruit ≠ vegetable")

### Issue 2: Overly Aggressive Neutral→Support Conversion  
My previous fix converted ALL neutral evidence to weak support when there were no contradictions:
```python
if sup == 0 and con == 0 and neutral > 0:
    sup = neutral * 0.3  # Treated ANY neutral as support
```

This caused false claims with "neutral" evidence to be marked as TRUE!

## Solutions Applied

### Fix 1: Enhanced Contradiction Detection

**File**: `backend/app/agents/evidence_agent/agent.py`

#### Updated System Message
```python
SYSTEM = (
    "You extract evidence for fact-checking. You only report what the provided source text actually says. "
    "CRITICAL: Carefully compare the claim to the source. If they say DIFFERENT or OPPOSITE things, "
    "mark stance as 'contradicting'. For example: claim says 'fruit' but source says 'vegetable' = contradicting. "
    ...
)
```

#### Enhanced Prompt with Contradiction Examples
```python
CRITICAL STANCE RULES:
1. Read carefully - if the source says the OPPOSITE of the claim, mark it as "contradicting", NOT "supporting"
2. Examples:
   - Claim: "X is a vegetable" + Source: "X is a fruit" → stance: "contradicting" (opposite category)
   - Claim: "X is president" + Source: "X was president until 2021" → stance: "contradicting" (timing mismatch)
   - Claim: "X costs $50" + Source: "X costs $100" → stance: "contradicting" (different value)
3. If a source directly confirms the claim with matching facts, mark as "supporting" with high confidence
4. If a source directly refutes the claim or provides conflicting facts, mark as "contradicting" with high confidence
5. Only use "neutral" for tangentially related information that neither confirms nor refutes
```

This teaches the LLM to recognize:
- **Category mismatches**: fruit vs vegetable, animal vs plant
- **Timing mismatches**: is vs was, current vs past
- **Value contradictions**: different numbers, dates, names

### Fix 2: Stricter Neutral→Support Conversion

**File**: `backend/app/agents/verdict_agent/agent.py`

Changed from aggressive to conservative:

**Before** (Too Aggressive):
```python
if sup == 0 and con == 0 and neutral > 0:
    sup = neutral * 0.3  # Converted ANY neutral to support
```

**After** (Conservative):
```python
neutral_count = len([e for e in evidence if e["stance"] == "neutral"])
neutral_total = sum(weight(e) for e in evidence if e["stance"] == "neutral")

# Only treat neutral as weak support if:
# 1. There's NO contradicting evidence, AND
# 2. There's NO supporting evidence, AND  
# 3. We have at least 2 neutral items
if sup == 0 and con == 0 and neutral_count >= 2:
    sup = neutral_total * 0.2  # Very weak support (20% weight, was 30%)
```

Changes:
- **Requires 2+ neutral items** (not just 1)
- **Reduced weight** from 30% to 20%
- **Explicit checks** for no supporting/contradicting evidence

This prevents single neutral evidence from causing false positives.

## Expected Behavior After Fix

### Case 1: False Claim with Contradicting Evidence
```
Claim: "Mango is a vegetable"
Evidence: "Mango is a tropical stone fruit" (marked as CONTRADICTING)
Verdict: FALSE or MOSTLY_FALSE
Confidence: 70-90%
```

### Case 2: True Claim with Supporting Evidence
```
Claim: "Mango is a fruit"
Evidence: "Mango is a tropical stone fruit" (marked as SUPPORTING)
Verdict: TRUE
Confidence: 80-95%
```

### Case 3: Genuinely Uncertain Claim
```
Claim: "Company X has 50,000 users"
Evidence: Multiple sources with "50,000", "52,000", "around 50k" (NEUTRAL - no exact match)
Verdict: MOSTLY_TRUE
Confidence: 50-65% (from 2+ neutral items at 20% weight each)
```

### Case 4: Unverifiable Claim
```
Claim: "Secret government project exists"
Evidence: 1 vague mention (NEUTRAL)
Verdict: UNVERIFIED (doesn't meet 2+ neutral threshold)
Confidence: 10%
```

## Testing Strategy

Test these specific cases after restarting your backend:

### ✅ Should Be FALSE
- "Mango is a vegetable"
- "Earth is flat"
- "2+2=5"
- "Paris is the capital of Germany"

### ✅ Should Be TRUE
- "Mango is a fruit"
- "Earth is round"
- "2+2=4"
- "Paris is the capital of France"

### ✅ Should Be MIXED/UNCERTAIN
- "Company X is worth $1 billion" (when sources vary: $900M, $1.1B, etc.)
- "Product launched in 2023" (when sources say "late 2023" or "early 2024")

## Why This Approach Works

### 1. LLM Education Through Examples
By providing concrete examples of contradictions, the LLM learns patterns:
- Opposite categories (fruit ≠ vegetable)
- Temporal mismatches (is ≠ was)
- Numerical differences

### 2. Conservative Neutral Handling
The stricter rules prevent overconfidence:
- Single ambiguous mention → UNVERIFIED
- Multiple consistent mentions → MOSTLY_TRUE (moderate confidence)
- Clear contradiction → FALSE (high confidence)

### 3. Maintains Safety
The system remains cautious:
- Requires multiple pieces of neutral evidence
- Uses low weight (20%) for neutral evidence
- Still triggers review for uncertain verdicts

## Trade-offs

### What We Gain
✅ Eliminates false positives (false claims marked as true)
✅ Better contradiction detection
✅ More accurate verdicts for factual claims

### What We Might Lose
⚠️ Some genuinely uncertain claims might stay UNVERIFIED instead of MOSTLY_TRUE
- **Impact**: Low - these should require human review anyway
- **Mitigation**: The 2+ neutral threshold still helps genuinely ambiguous cases

## Files Modified

1. `backend/app/agents/evidence_agent/agent.py`
   - Enhanced SYSTEM message with contradiction warning
   - Added CRITICAL STANCE RULES with examples
   - Lines 17-21, 22-44

2. `backend/app/agents/verdict_agent/agent.py`
   - Stricter neutral→support conversion logic
   - Requires 2+ neutral items
   - Reduced weight from 30% to 20%
   - Lines 34-47

## Summary

The previous fix solved "everything is unverified" but created "false positives". This update:

✅ Teaches the LLM to recognize contradictions with concrete examples
✅ Requires higher threshold (2+ items) for neutral→support conversion
✅ Reduces neutral evidence weight (30% → 20%)
✅ Prevents single ambiguous evidence from causing false positives
✅ Maintains protection against false "unverified" verdicts for truly uncertain cases

**Restart your backend** and test with "Mango is a vegetable" - it should now correctly return **FALSE or MOSTLY_FALSE** with the evidence marked as **CONTRADICTING**! 🎯
