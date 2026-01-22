# QA Checklist: Story {{epic_num}}.{{story_num}} - {{story_title_readable}}

**Story:** {{story_title_readable}}
**Status:** Pending Testing
**Tester:** {{user_name}}
**Date:** _______________

---

## Prerequisites

Before testing, ensure the following are in place:

- [ ] {{prerequisite_1}}
- [ ] {{prerequisite_2}}
- [ ] {{prerequisite_3}}
<!-- Add more prerequisites as needed based on story requirements -->

---

## Environment Setup

### 1. Prepare Test Environment

```bash
# Navigate to project root
cd {{project_root}}

# {{setup_instruction_1}}
```

- [ ] {{setup_verification_1}}

### 2. Additional Setup (if needed)

```bash
# {{setup_instruction_2}}
```

- [ ] {{setup_verification_2}}

---

## Test Cases

<!-- Generate one TC for each Acceptance Criterion -->

### TC-1: {{test_case_1_name}}

**Acceptance Criterion:** #1 - {{ac_1_description}}

**Steps:**
1. {{step_1}}
   ```bash
   {{command_1}}
   ```

2. {{step_2}}

3. {{step_3}}

**Expected Results:**
- [ ] {{expected_result_1}}
- [ ] {{expected_result_2}}
- [ ] {{expected_result_3}}

**Actual Results:** _______________

---

### TC-2: {{test_case_2_name}}

**Acceptance Criterion:** #2 - {{ac_2_description}}

**Steps:**
1. {{step_1}}
2. {{step_2}}

**Expected Results:**
- [ ] {{expected_result_1}}
- [ ] {{expected_result_2}}

**Actual Results:** _______________

---

<!-- Continue for all acceptance criteria -->

## Edge Cases & Error Scenarios

### EC-1: {{edge_case_1_name}}

**Scenario:** {{edge_case_1_description}}

**Test:**
```bash
{{edge_case_1_command}}
```

**Expected:** {{edge_case_1_expected}}

**Result:** _______________

---

### EC-2: {{edge_case_2_name}}

**Scenario:** {{edge_case_2_description}}

**Test:**
```bash
{{edge_case_2_command}}
```

**Expected:** {{edge_case_2_expected}}

**Result:** _______________

---

## Rollback Steps

If testing fails or you need to reset:

### Full Rollback
```bash
# {{full_rollback_instructions}}
```

### Partial Rollback
```bash
# {{partial_rollback_instructions}}
```

### Environment Cleanup
```bash
# {{cleanup_instructions}}
```

---

## Sign-Off

### Test Summary

| Test Case | Status | Notes |
|-----------|--------|-------|
| TC-1: {{tc_1_name}} | [ ] Pass / [ ] Fail | |
| TC-2: {{tc_2_name}} | [ ] Pass / [ ] Fail | |
<!-- Add rows for all test cases -->
| EC-1: {{ec_1_name}} | [ ] Pass / [ ] Fail | |
| EC-2: {{ec_2_name}} | [ ] Pass / [ ] Fail | |

### Final Verdict

- [ ] **PASS** - All acceptance criteria met, ready to proceed
- [ ] **FAIL** - Issues found, requires dev attention

**Blocking Issues:** _______________

**Non-Blocking Notes:** _______________

**Tested By:** {{user_name}}
**Date:** _______________
**Signature:** _______________

---

## Next Story

Once this story passes QA:
1. Update sprint-status.yaml: `{{story_key}}: done`
2. Proceed to next story
