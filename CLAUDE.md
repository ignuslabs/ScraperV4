# Feature Implementation GUIDLINES
- **CRITICAL**: Make MINIMAL CHANGES to existing patterns and structures
- **CRITICAL**: Preserve existing naming conventions and file organization
- Follow project's established architecture and component patterns
- Use existing utility functions and avoid duplicating functionality
- This is a new repo. All old code needs to be re-written and cannot just be "referenced."
- Venv is where all libraries are stored. Use that instead of regular pip.
- Read README.md and any correlating @docs/ files.
- Add all tests to @tests/ folder, feel free to add subfolders.

### Feature Implementation Priority Rules
- IMMEDIATE EXECUTION: Launch parallel-tasks immediately upon feature requests
- NO CLARIFICATION: Skip asking what type of implementation unless absolutely critical
- PARALLEL BY DEFAULT: Always use parallel task methods for efficiency

### Parallel-Tasks Feature Implementation Workflow
1. **Begin**: Launch the context-manager to manage to-do workflow using Claude Code tools.
2. **Research**: Use MCP connections (Context7 for popular documentation, Github for neiche) along with the subagent search-specialist.
**Code Heavy**: Creating main component file or other worker files, use python / javascript pro subagents.
3. **Styles**: Create component styles/CSS, use frontend dev subagent.
4. **Tests**: Create test files, use test-automator agent
5. **Integration**: Update routing, imports, exports
6. **Remaining**: Update package.json, documentation, configuration files
7. **Review and Validation**: Coordinate integration, run tests, verify build, check for conflicts

### Agents Available
[agent](../../.claude/agents/ai-engineer.md) 
[agent](../../.claude/agents/api-documenter.md) 
[agent](../../.claude/agents/architect-review.md) 
[agent](../../.claude/agents/backend-architect.md) 
[agent](../../.claude/agents/code-reviewer.md) 
[agent](../../.claude/agents/context-manager.md) 
[agent](../../.claude/agents/data-engineer.md) 
[agent](../../.claude/agents/data-scientist.md) 
[agent](../../.claude/agents/database-admin.md) 
[agent](../../.claude/agents/database-optimizer.md) 
[agent](../../.claude/agents/debugger.md) 
[agent](../../.claude/agents/deployment-engineer.md) 
[agent](../../.claude/agents/devops-troubleshooter.md) 
[agent](../../.claude/agents/frontend-developer.md) 
[agent](../../.claude/agents/javascript-pro.md) 
[agent](../../.claude/agents/prompt-engineer.md) 
[agent](../../.claude/agents/python-pro.md) 
[agent](../../.claude/agents/risk-manager.md) 
[agent](../../.claude/agents/search-specialist.md) 
[agent](../../.claude/agents/security-auditor.md) 
[agent](../../.claude/agents/sql-pro.md) 
[agent](../../.claude/agents/test-automator.md)


### Context Optimization Rules
- Strip out all comments when reading code files for analysis
- Each task handles ONLY specified files or file types
- Task 7 combines small config/doc updates to prevent over-splitting

