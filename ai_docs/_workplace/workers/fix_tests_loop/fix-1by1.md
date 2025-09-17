# Test Fix Instructions - Step by Step Process

## ⚠️ GOLDEN RULE: NEVER BREAK WORKING CODE
**Before ANY change, ask yourself: "Am I about to break working production code to satisfy an obsolete test?"**

## Objective
Fix all failing tests systematically by addressing root causes based on **LATEST CODE VERSION**, not obsolete test expectations.

## 🚨 CRITICAL RULE: CODE OVER TESTS
**ALWAYS fix tests to match the current implementation - NEVER modify working code to match outdated tests!**

## 🔍 MANDATORY OBSOLESCENCE CHECK BEFORE ANY CHANGES

### Before Fixing ANY Test, You MUST Determine:
1. **Is the test obsolete?** (expecting old behavior that was intentionally changed)
2. **Is the code obsolete?** (legacy code that should be removed/updated)
3. **Which is the source of truth?** (current working production code vs test expectations)

### Decision Matrix:
| Scenario | Test Status | Code Status | Action | Priority |
|----------|------------|-------------|---------|----------|
| Test expects removed feature | OBSOLETE | CURRENT | Update/Remove test | HIGH |
| Test uses old API format | OBSOLETE | CURRENT | Update test to match new API | HIGH |
| Test imports old modules | OBSOLETE | CURRENT | Fix test imports | HIGH |
| Code has actual bug | CURRENT | BROKEN | Fix the code bug | HIGH |
| Code is deprecated | CURRENT | OBSOLETE | Consider removing both | MEDIUM |
| Both work but mismatch | UNCLEAR | UNCLEAR | Check git history & docs | LOW |

### How to Determine Obsolescence:
1. **Check Git History**:
   ```bash
   # See when the code was last modified
   git log -p --follow [source_file_path]

   # See when the test was last modified
   git log -p --follow [test_file_path]

   # Compare dates - newer code usually means test is obsolete
   ```

2. **Check Documentation**:
   - Look in `ai_docs/` for current API specs
   - Check CHANGELOG.md for breaking changes
   - Review migration guides if they exist

3. **Check Production Usage**:
   - Is the code actively used in production?
   - Are there other tests that pass with this code?
   - Would changing the code break other components?

4. **Check Dependencies**:
   - What depends on this code?
   - Would changing it cause cascade failures?
   - Is it part of a public API?

## Step-by-Step Process

### Step 1: Load and Analyze Failed Tests
1. View failed tests using test-menu.sh:
   ```bash
   # Option 8: List all cached tests (shows failed and passed)
   echo -e "8\nq" | timeout 10 scripts/test-menu.sh

   # Option 7: Show cache statistics (see how many failed)
   echo -e "7\nq" | timeout 10 scripts/test-menu.sh
   ```
2. Pick the FIRST failing test from the failed list (shown in red with ✗)
3. Note the exact file path and test name

### Step 2: Investigate Root Cause
1. Run the specific test in isolation to see the exact error:
   ```bash
   # Using test-menu.sh option 4 (Recommended)
   echo -e "4\n[test_file_path]\nq" | timeout 20 scripts/test-menu.sh

   # Or direct pytest if needed for more control
   timeout 20 bash -c "cd agenthub_main && python -m pytest [test_file_path]::[test_name] -xvs --tb=long"
   ```
2. **EXAMINE THE ACTUAL IMPLEMENTATION FIRST** - Read the current code, not the test expectations
3. Identify the root cause (not just the symptom):
   - Import errors → Find missing module/class in CURRENT codebase
   - Assertion errors → Check if test expects OBSOLETE behavior
   - Type errors → Verify current data types and interfaces
   - Method errors → Check if methods exist in CURRENT implementation
   - Dependency errors → Verify all dependencies in LATEST code

### Step 3: Fix the Root Cause (ALWAYS FAVOR CURRENT CODE)

#### 🛡️ PROTECTION CHECKLIST (Run Through BEFORE Any Change):
- [ ] Have I checked if the current code is working in production?
- [ ] Have I verified this isn't just an outdated test expectation?
- [ ] Have I checked git history to see which changed more recently?
- [ ] Have I looked for other passing tests that use the same code?
- [ ] Am I about to modify code that other components depend on?

#### DECISION FLOWCHART:
```
Test Fails
    ↓
Is code working in production/other tests?
    ├─ YES → Test is OBSOLETE → UPDATE TEST
    └─ NO → Check further
              ↓
         Was code recently changed intentionally?
              ├─ YES → Test is OBSOLETE → UPDATE TEST
              └─ NO → Check further
                        ↓
                   Is this a real bug?
                        ├─ YES → FIX CODE (rare case)
                        └─ NO/UNSURE → UPDATE TEST (safe default)
```

#### IMPLEMENTATION RULES:
1. **FIRST**: Check the CURRENT implementation to understand how it actually works
2. **SECOND**: Run the obsolescence check from Step 2
3. **DECISION MATRIX**:
   - Test expects OBSOLETE behavior → **UPDATE TEST** to match current implementation ✅
   - Test fails due to missing methods → Check if renamed/moved → **UPDATE TEST** ✅
   - Imports fail → Update imports to match current module structure → **UPDATE TEST** ✅
   - Assertions fail → Verify test data matches current API → **UPDATE TEST** ✅
   - **ONLY fix source code if**: There's a confirmed bug AND no other code depends on current behavior ⚠️
4. **DEFAULT ACTION**: When in doubt → **UPDATE THE TEST, NOT THE CODE**
5. **PRIORITY**: Current working code > Obsolete test expectations
6. Document what was changed and why (code fix vs test update)

### Step 4: Verify the Fix
1. Re-run the specific test to confirm it passes using test-menu.sh:
   ```bash
   # Use test-menu.sh option 4 for specific test file
   echo "4" | timeout 20 scripts/test-menu.sh
   # Then enter the test file path when prompted
   # Example: agenthub_main/src/tests/unit/test_file.py
   ```
2. **IMPORTANT**: Use `timeout 20` to prevent infinite loops (20 second max)
3. Run related tests in the same module to ensure no regression
4. Check `.test_cache/passed_tests.txt` to confirm test was moved there
5. If test passes, proceed to next step

### Step 5: Update Test Cache (AUTOMATIC with test-menu.sh)
**Note: test-menu.sh handles this automatically!**
- When test **PASSES**: Automatically moved from `failed_tests.txt` to `passed_tests.txt`
- When test **FAILS**: Remains in `failed_tests.txt`
- Test hash is automatically updated in `test_hashes.txt`

**Manual update only needed if NOT using test-menu.sh:**
1. Remove the fixed test from `.test_cache/failed_tests.txt`
2. Add the test to `.test_cache/passed_tests.txt`
3. Update test hash in `.test_cache/test_hashes.txt`

### Step 6: Document and Continue
1. Log the fix in a tracking file with:
   - Test name
   - Root cause identified
   - Fix applied
   - Verification status
2. Return to Step 1 with the next failing test

## 🚫 COMMON MISTAKES THAT BREAK PRODUCTION

### NEVER DO THESE (They Break Working Code):
1. **Adding a method just because a test expects it** - The method was likely renamed/moved
2. **Changing return types to match test assertions** - Tests should match current API
3. **Reverting recent code changes to pass old tests** - Tests need updating instead
4. **Modifying database schemas to match test fixtures** - Update test fixtures instead
5. **Changing API endpoints because tests use old URLs** - Update test URLs
6. **Adding deprecated parameters back** - Remove them from tests
7. **Downgrading library versions to match test mocks** - Update test mocks

### Real Examples of What NOT to Do:
```python
# ❌ WRONG: Test expects old method name
# DON'T add this to working code:
def get_user_by_id(self, id):  # Old method name
    return self.get_user(id)    # Just to satisfy test

# ✅ RIGHT: Update the test instead
# Change test from: user = service.get_user_by_id(123)
# To: user = service.get_user(123)  # Match current implementation
```

```python
# ❌ WRONG: Test expects old response format
# DON'T change working API:
return {"data": result, "status": "ok"}  # Old format for test

# ✅ RIGHT: Update test expectation
# Change test from: assert response["status"] == "ok"
# To: assert response["success"] == True  # Match current API
```

## Important Guidelines

### DO:
- **EXAMINE CURRENT CODE FIRST** - Always check the latest implementation before fixing
- **UPDATE TESTS** when they expect obsolete/removed functionality
- **FIX IMPORTS** to match current module structure and naming
- **ALIGN TEST DATA** with current API specifications and data formats
- **VERIFY METHOD NAMES** match current implementation (not old test assumptions)
- **ADDRESS ROOT CAUSES** based on current codebase, not historical expectations
- Run each test in isolation first
- Verify fixes don't break other tests
- Keep detailed logs of each fix (noting whether code or test was updated)

### DON'T:
- **NEVER modify working code to satisfy outdated tests**
- **NEVER add missing methods just because tests expect them** (check if they were renamed/moved)
- **NEVER downgrade current implementation** to match old test patterns
- Apply quick patches without understanding current implementation
- Skip verification steps
- Fix multiple tests simultaneously
- Ignore related test failures
- Assume test expectations are always correct

## Current Status
- Total failing tests: Check `.test_cache/failed_tests.txt`
- Progress tracking: See fix logs
- Next test to fix: [First line in failed_tests.txt]

## How test-menu.sh Auto-Manages Cache

### Automatic Cache Operations:
1. **Running Tests (Options 1-4)**:
   - Captures pytest output in real-time
   - Parses PASSED/FAILED status for each test
   - Updates cache files immediately after test completes

2. **Cache Updates**:
   - **PASSED**: `mark_test_passed()` function:
     - Removes from `failed_tests.txt`
     - Adds to `passed_tests.txt`
     - Updates MD5 hash in `test_hashes.txt`
   - **FAILED**: `mark_test_failed()` function:
     - Removes from `passed_tests.txt`
     - Adds to `failed_tests.txt`
     - Keeps test ready for next iteration

3. **Smart Skipping (Option 1)**:
   - Checks if test is in `passed_tests.txt`
   - Verifies MD5 hash hasn't changed
   - Skips if both conditions met
   - Re-runs if file modified

4. **Cache Management (Options 5-6)**:
   - Option 5: Clear all cache (force full rerun)
   - Option 6: Clear failed tests only

## Command Reference

### Using test-menu.sh for Smart Testing (RECOMMENDED)
```bash
# Run test-menu.sh option 4 with timeout wrapper
echo -e "4\n[test_file_path]\nq" | timeout 20 scripts/test-menu.sh

# Example for specific test file:
echo -e "4\nagenthub_main/src/tests/unit/database_config_test.py\nq" | timeout 20 scripts/test-menu.sh

# Run failed tests only (option 2) with timeout
echo -e "2\nq" | timeout 20 scripts/test-menu.sh

# Check test statistics (option 7)
echo -e "7\nq" | timeout 10 scripts/test-menu.sh

# View cached passed/failed tests (option 8)
echo -e "8\nq" | timeout 10 scripts/test-menu.sh
```

### Direct pytest commands (fallback if test-menu.sh fails)
```bash
# Run single test with timeout
timeout 20 bash -c "cd agenthub_main && python -m pytest [test_path]::[test_name] -xvs"

# Run all tests in a file
timeout 20 bash -c "cd agenthub_main && python -m pytest [test_path] -xvs"

# Check test with detailed traceback
timeout 20 bash -c "cd agenthub_main && python -m pytest [test_path]::[test_name] -xvs --tb=long"

# Run with coverage
timeout 60 bash -c "cd agenthub_main && python -m pytest [test_path] --cov=[module] --cov-report=term-missing"
```

### Timeout Prevention Strategy
- **Always use `timeout` command** to prevent infinite test loops
- **Standardized timeout: 20 seconds** for most operations
- **Extended timeout: 60 seconds** only for coverage reports
- **Quick operations: 10 seconds** for stats and cache viewing
- **If test hangs**: Kill with Ctrl+C or wait for timeout
- **Check `.test_cache/last_run.log`** for test output after timeout

### Test Cache Files Reference
- `.test_cache/passed_tests.txt` - Tests that have passed
- `.test_cache/failed_tests.txt` - Tests that need fixing
- `.test_cache/test_hashes.txt` - MD5 hashes to detect file changes
- `.test_cache/last_run.log` - Output from last test run
- `.test_cache/stats.txt` - Test statistics

## 📅 Code Version Priority Rules

### When Tests Fail Due to Code Changes:
1. **Check git history**: When was the failing functionality last modified?
2. **Examine current implementation**: What does the code actually do now?
3. **Update tests accordingly**: Align test expectations with current reality
4. **Document changes**: Note in fix logs whether issue was outdated test vs actual bug

### Common Patterns to Look For:
- **Method renames**: Tests calling `old_method()` but code has `new_method()`
- **Parameter changes**: Tests passing old parameter formats
- **Import paths**: Tests importing from old module locations
- **Data structure changes**: Tests expecting old JSON/dict formats
- **API changes**: Tests expecting old response formats
- **Removed features**: Tests for functionality that was intentionally removed

### Red Flags (Indicates Outdated Tests):
- Tests importing non-existent modules
- Tests calling methods that don't exist in current code
- Tests expecting data formats that current code doesn't produce
- Tests mocking methods that were removed/renamed
- Tests with hardcoded values that don't match current defaults