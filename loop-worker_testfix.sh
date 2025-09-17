#!/bin/bash

# Configuration
RESULTS_FILE="ai_docs/_workplace/workers/fix_tests_loop/fix-1by1-results.md"
CONTEXT_FILE="ai_docs/_workplace/workers/fix_tests_loop/fix-1by1-context.md"
COMMAND_FILE="ai_docs/_workplace/workers/fix_tests_loop/fix-1by1.md"
DELAY_SECONDS=15
LOG_FILE="ai_docs/_workplace/workers/fix_tests_loop/fix-1by1.log"

# Display options (set to true/false as needed)
SHOW_FULL_CONTEXT=true        # Show complete context content
SHOW_CONTEXT_PREVIEW=true     # Show preview with boxes
CONTEXT_PREVIEW_LINES=20      # How many lines to show in preview

# Docker cleanup configuration
RUN_DOCKER_CLEANUP=true       # Set to false to disable docker cleanup
DOCKER_MENU_SCRIPT="./docker-menu.sh"

# Function to run docker cleanup
cleanup_docker() {
    if [[ "$RUN_DOCKER_CLEANUP" == "true" ]] && [[ -f "$DOCKER_MENU_SCRIPT" ]]; then
        echo "🐳 Running Docker cleanup..." | tee -a "$LOG_FILE"
        echo "R" | "$DOCKER_MENU_SCRIPT" | tee -a "$LOG_FILE"
        echo "✅ Docker cleanup completed" | tee -a "$LOG_FILE"
    else
        echo "⚠️  Docker cleanup skipped (disabled or script not found)" | tee -a "$LOG_FILE"
    fi
}

# Function to handle script termination
cleanup_and_exit() {
    echo "" | tee -a "$LOG_FILE"
    echo "🛑 Script interrupted or terminated" | tee -a "$LOG_FILE"
    echo "📊 Final stats - Completed $ITERATION iterations" | tee -a "$LOG_FILE"
    echo "🕐 Script ended at: $(date)" | tee -a "$LOG_FILE"
    
    # Run docker cleanup once on exit
    cleanup_docker
    
    echo "👋 Goodbye!" | tee -a "$LOG_FILE"
    exit 0
}

# Set up trap to catch Ctrl+C and other termination signals
trap cleanup_and_exit SIGINT SIGTERM

# Initialize files
echo "# DDD Tracking Results" > "$RESULTS_FILE"
echo "Started: $(date)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

echo "DDD Tracking Log - Started: $(date)" > "$LOG_FILE"

echo "================================================"
echo "🔄 DYNAMIC RELOAD MODE + CONTEXT DISPLAY"
echo "================================================"
echo "✏️  Edit file: $COMMAND_FILE"
echo "👁️  Monitor: tail -f $LOG_FILE"
echo "📊 Results: tail -f $RESULTS_FILE"
echo ""
echo "Context Display Settings:"
echo "• Full context: $SHOW_FULL_CONTEXT"
echo "• Preview: $SHOW_CONTEXT_PREVIEW"
echo "• Preview lines: $CONTEXT_PREVIEW_LINES"
echo ""
echo "Docker Cleanup Settings:"
echo "• Cleanup enabled: $RUN_DOCKER_CLEANUP"
echo "• Cleanup script: $DOCKER_MENU_SCRIPT"
echo ""
echo "💡 Press Ctrl+C to stop the script and run cleanup"
echo "================================================"

# Function to show file changes
show_changes() {
    local prev_file="$1"
    local curr_file="$2"
    
    echo "📝 CHANGES DETECTED:" | tee -a "$LOG_FILE"
    if command -v colordiff >/dev/null 2>&1; then
        colordiff -u "$prev_file" "$curr_file" | head -20 | tee -a "$LOG_FILE"
    else
        diff -u "$prev_file" "$curr_file" | head -20 | tee -a "$LOG_FILE"
    fi
    echo "🔄 Updated instructions will be used in this iteration" | tee -a "$LOG_FILE"
    echo "---" | tee -a "$LOG_FILE"
}

# Function to display context with formatting
display_context() {
    local context_file="$1"
    local iteration="$2"
    
    if [[ "$SHOW_CONTEXT_PREVIEW" == "true" ]]; then
        echo "📋 CONTEXT PREVIEW:" | tee -a "$LOG_FILE"
        echo "┌─────────────────────────────────────────────────────────┐" | tee -a "$LOG_FILE"
        
        # Show current instructions
        echo "│ 📝 CURRENT INSTRUCTIONS:" | tee -a "$LOG_FILE"
        echo "│" | tee -a "$LOG_FILE"
        cat "$COMMAND_FILE" | head -15 | sed 's/^/│ /' | tee -a "$LOG_FILE"
        
        local cmd_lines=$(wc -l < "$COMMAND_FILE")
        if [[ $cmd_lines -gt 15 ]]; then
            echo "│ ... (showing first 15 of $cmd_lines lines)" | tee -a "$LOG_FILE"
        fi
        echo "│" | tee -a "$LOG_FILE"
        
        # Show previous results summary if available
        if [[ $iteration -gt 1 ]] && [[ -f "${CONTEXT_FILE}.results" ]]; then
            local results_lines=$(wc -l < "${CONTEXT_FILE}.results")
            echo "│ 📊 PREVIOUS RESULTS SUMMARY:" | tee -a "$LOG_FILE"
            echo "│" | tee -a "$LOG_FILE"
            
            # Show first few lines and last few lines
            head -5 "${CONTEXT_FILE}.results" | sed 's/^/│ /' | tee -a "$LOG_FILE"
            if [[ $results_lines -gt 10 ]]; then
                echo "│ ..." | tee -a "$LOG_FILE"
                tail -5 "${CONTEXT_FILE}.results" | sed 's/^/│ /' | tee -a "$LOG_FILE"
                echo "│ (Total: ${results_lines} lines of previous analysis)" | tee -a "$LOG_FILE"
            fi
            echo "│" | tee -a "$LOG_FILE"
        fi
        
        echo "└─────────────────────────────────────────────────────────┘" | tee -a "$LOG_FILE"
    fi
    
    if [[ "$SHOW_FULL_CONTEXT" == "true" ]]; then
        echo "" | tee -a "$LOG_FILE"
        echo "📄 FULL CONTEXT BEING SENT TO CLAUDE:" | tee -a "$LOG_FILE"
        echo "╔═══════════════════════════════════════════════════════════╗" | tee -a "$LOG_FILE"
        
        cat "$context_file" | sed 's/^/║ /' | tee -a "$LOG_FILE"
        
        echo "╚═══════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"
        echo "📏 Total context length: $(wc -l < "$context_file") lines, $(wc -c < "$context_file") characters" | tee -a "$LOG_FILE"
    fi
}

# Function for visual countdown
countdown_timer() {
    local duration=$1
    local message="$2"
    
    echo "" | tee -a "$LOG_FILE"
    echo "$message" | tee -a "$LOG_FILE"
    echo "💡 TIP: You can edit $COMMAND_FILE now to change instructions!" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    for ((i=duration; i>0; i--)); do
        local progress=$((duration - i))
        local total_bars=20
        local filled_bars=$((progress * total_bars / duration))
        local empty_bars=$((total_bars - filled_bars))
        
        local bar=""
        for ((j=0; j<filled_bars; j++)); do bar+="█"; done
        for ((j=0; j<empty_bars; j++)); do bar+="░"; done
        
        local emoji="⏳"
        if [[ $i -le 3 ]]; then emoji="🚨"
        elif [[ $i -le 5 ]]; then emoji="⚡"; fi
        
        printf "\r$emoji Countdown: %2ds [%s] Next iteration starting..." "$i" "$bar"
        
        if [[ $i -eq $duration ]] || [[ $((i % 5)) -eq 0 ]] || [[ $i -le 3 ]]; then
            echo "$emoji Countdown: ${i}s remaining..." >> "$LOG_FILE"
        fi
        
        sleep 1
    done
    
    printf "\r🚀 RUNNING - Starting analysis now!                              \n"
    echo "🚀 RUNNING - Starting analysis now!" >> "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# Counter for iterations
ITERATION=0
LAST_MODIFICATION=""

while :; do 
    ITERATION=$((ITERATION + 1))
    
    TIMESTAMP=$(date)
    echo "=== ITERATION $ITERATION - $TIMESTAMP ===" | tee -a "$LOG_FILE"
    
    # Check if command file exists
    if [[ ! -f "$COMMAND_FILE" ]]; then
        echo "❌ ERROR: Command file not found: $COMMAND_FILE" | tee -a "$LOG_FILE"
        echo "⏳ Waiting 5s for file to be created..." | tee -a "$LOG_FILE"
        sleep 5
        continue
    fi
    
    # Get current modification time
    if command -v stat >/dev/null 2>&1; then
        CURRENT_MODIFICATION=$(stat -c %Y "$COMMAND_FILE" 2>/dev/null || stat -f %m "$COMMAND_FILE" 2>/dev/null)
    else
        CURRENT_MODIFICATION=$(ls -l "$COMMAND_FILE")
    fi
    
    # Check if file was modified since last iteration
    if [[ -n "$LAST_MODIFICATION" ]] && [[ "$CURRENT_MODIFICATION" != "$LAST_MODIFICATION" ]]; then
        echo "🔔 File modification detected!" | tee -a "$LOG_FILE"
        if [[ -f "${COMMAND_FILE}.prev" ]]; then
            show_changes "${COMMAND_FILE}.prev" "$COMMAND_FILE"
        fi
    elif [[ $ITERATION -eq 1 ]]; then
        echo "📖 Loading initial command file..." | tee -a "$LOG_FILE"
    else
        echo "✓ No changes detected in command file" | tee -a "$LOG_FILE"
    fi
    
    LAST_MODIFICATION="$CURRENT_MODIFICATION"
    
    # Create fresh context combining current instructions + previous results (sent once per iteration)
    echo "🔄 Building context for iteration $ITERATION (will be sent ONCE to Claude)..." | tee -a "$LOG_FILE"
    CONTEXT_SENT_THIS_ITERATION=false  # Flag to track context sending
    {
        echo "# Current Instructions (Iteration $ITERATION - $(date))"
        echo "# NOTE: This context is sent ONCE per iteration, not on every chat message"
        echo ""
        cat "$COMMAND_FILE"
        echo ""
        echo "---"
        echo ""

        # Include previous results if available (but only send once per iteration)
        if [[ $ITERATION -gt 1 ]] && [[ -f "${CONTEXT_FILE}.results" ]]; then
            echo "# Previous Analysis Results (from prior iterations)"
            echo ""

            # Extract last 3 files with full content and others as relative paths
            echo "## Context Strategy: Last 3 files with full content, others as relative paths"
            echo ""

            # Create temp file to process the results
            TEMP_RESULTS=$(mktemp)
            cat "${CONTEXT_FILE}.results" > "$TEMP_RESULTS"

            # Extract file paths from results (looking for test file patterns)
            echo "### File References:"
            echo ""

            # Find all test file references in the results
            grep -oE "(agenthub_main/src/tests/[^[:space:]]+\.py|tests/[^[:space:]]+\.py)" "$TEMP_RESULTS" | sort -u > /tmp/test_files_list.txt 2>/dev/null || true

            # Count total files found
            TOTAL_FILES=$(wc -l < /tmp/test_files_list.txt 2>/dev/null || echo "0")

            if [[ $TOTAL_FILES -gt 3 ]]; then
                echo "#### Files to include by path only (${TOTAL_FILES} total, showing paths for all except last 3):"
                echo ""

                # Show all files except last 3 as paths only
                head -n $((TOTAL_FILES - 3)) /tmp/test_files_list.txt | while read -r file; do
                    echo "- \`$file\`"
                done
                echo ""

                echo "#### Last 3 files with detailed context:"
                echo ""

                # Get the last 3 files
                tail -n 3 /tmp/test_files_list.txt > /tmp/last_3_files.txt

                # Include full content for last 3 files from the results
                LAST_3_FILES=$(tail -n 3 /tmp/test_files_list.txt)
                for file in $LAST_3_FILES; do
                    echo "##### File: \`$file\`"
                    # Extract content related to this file from results
                    grep -A 10 -B 2 "$file" "$TEMP_RESULTS" | head -50 || true
                    echo ""
                done

            else
                echo "#### All ${TOTAL_FILES} files with context:"
                echo ""
                # If 3 or fewer files, include all with full context
                cat "${CONTEXT_FILE}.results"
            fi

            # Clean up temp files
            rm -f "$TEMP_RESULTS" /tmp/test_files_list.txt /tmp/last_3_files.txt 2>/dev/null || true

            echo ""
            echo "### Summary of Previous Analysis:"
            echo ""
            # Include just a summary of the last iteration's key findings
            tail -50 "${CONTEXT_FILE}.results" | grep -E "(PASSED|FAILED|ERROR|Success|Fixed|Issue)" | head -20 || echo "No specific test results found in previous iteration"
        fi
    } > "$CONTEXT_FILE"
    
    # Display the context content
    display_context "$CONTEXT_FILE" "$ITERATION"
    
    # Backup current command file for next iteration comparison
    cp "$COMMAND_FILE" "${COMMAND_FILE}.prev"
    
    # Show context stats
    CONTEXT_LINES=$(wc -l < "$CONTEXT_FILE")
    COMMAND_LINES=$(wc -l < "$COMMAND_FILE")
    CONTEXT_SIZE=$(wc -c < "$CONTEXT_FILE")
    echo "📊 Context Stats: ${CONTEXT_LINES} lines | ${CONTEXT_SIZE} chars | ${COMMAND_LINES} instruction lines" | tee -a "$LOG_FILE"
    
    echo "🚀 Starting Claude analysis (context will be sent ONCE)..." | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    # Add iteration header to results file
    {
        echo "## Iteration $ITERATION - $TIMESTAMP"
        echo ""
        echo "### Current Instructions:"
        echo '```markdown'
        cat "$COMMAND_FILE"
        echo '```'
        echo ""
        echo "### Claude Output:"
        echo '```'
    } >> "$RESULTS_FILE"
    
    # Create temporary file for this iteration's output
    TEMP_OUTPUT=$(mktemp)
    
    # Verify context is only sent once per iteration
    if [[ "$CONTEXT_SENT_THIS_ITERATION" == "true" ]]; then
        echo "⚠️  WARNING: Attempting to send context again in same iteration!" | tee -a "$LOG_FILE"
        echo "❌ SKIPPING duplicate context send" | tee -a "$LOG_FILE"
    else
        echo "✓ Sending context to Claude (first and only time this iteration)..." | tee -a "$LOG_FILE"
        CONTEXT_SENT_THIS_ITERATION=true
        
        # Run claude command - stream to BOTH log file AND temp file in real-time
        cat "$CONTEXT_FILE" | claude -p --dangerously-skip-permissions 2>&1 | tee "$TEMP_OUTPUT" | tee -a "$LOG_FILE"
        CLAUDE_EXIT_CODE=${PIPESTATUS[1]}
        
        echo "✓ Context sent successfully (will not be sent again until next iteration)" | tee -a "$LOG_FILE"
    fi
    
    echo "" | tee -a "$LOG_FILE"
    if [[ $CLAUDE_EXIT_CODE -eq 0 ]]; then
        echo "✅ Iteration $ITERATION completed successfully" | tee -a "$LOG_FILE"
    else
        echo "❌ ERROR: Claude command failed in iteration $ITERATION (exit code: $CLAUDE_EXIT_CODE)" | tee -a "$LOG_FILE"
    fi
    
    # Add output to results file
    cat "$TEMP_OUTPUT" >> "$RESULTS_FILE"
    
    # Close the code block in results file
    OUTPUT_LINES=$(wc -l < "$TEMP_OUTPUT")
    OUTPUT_SIZE=$(wc -c < "$TEMP_OUTPUT")
    {
        echo '```'
        echo ""
        echo "**Summary:** ${OUTPUT_LINES} lines, ${OUTPUT_SIZE} characters generated"
        echo ""
        echo "---"
        echo ""
    } >> "$RESULTS_FILE"
    
    # Save this iteration's results for next iteration
    {
        echo "## Analysis from Iteration $ITERATION ($(date))"
        echo ""
        cat "$TEMP_OUTPUT"
        echo ""
        echo "---"
        echo ""
    } > "${CONTEXT_FILE}.results.tmp"
    
    # Append to existing results (keep history)
    if [[ -f "${CONTEXT_FILE}.results" ]]; then
        cat "${CONTEXT_FILE}.results" >> "${CONTEXT_FILE}.results.tmp"
    fi
    mv "${CONTEXT_FILE}.results.tmp" "${CONTEXT_FILE}.results"
    
    # Log summary with context send confirmation
    echo "📊 Iteration $ITERATION Summary:" | tee -a "$LOG_FILE"
    echo "  • Output: ${OUTPUT_LINES} lines, ${OUTPUT_SIZE} chars" | tee -a "$LOG_FILE"
    echo "  • Context: ${CONTEXT_LINES} lines (sent ONCE at start)" | tee -a "$LOG_FILE"
    echo "  • Status: Context was sent exactly 1 time this iteration ✓" | tee -a "$LOG_FILE"
    
    # Clean up temp file
    rm "$TEMP_OUTPUT"
    
    # Reset the context sent flag for next iteration
    CONTEXT_SENT_THIS_ITERATION=false
    
    # Optional: Truncate results file if it gets too large
    RESULTS_LINES=$(wc -l < "${CONTEXT_FILE}.results" 2>/dev/null || echo "0")
    if [[ $RESULTS_LINES -gt 1000 ]]; then
        tail -800 "${CONTEXT_FILE}.results" > "${CONTEXT_FILE}.results.tmp"
        mv "${CONTEXT_FILE}.results.tmp" "${CONTEXT_FILE}.results"
        echo "🔄 Results history truncated to last 800 lines" | tee -a "$LOG_FILE"
    fi
    
    # Visual countdown before next iteration
    countdown_timer "$DELAY_SECONDS" "⏳ Iteration $ITERATION complete! Preparing for next iteration..."
done

# This should never be reached in normal operation, but just in case
cleanup_and_exit