Role: senior software architect. Analyze attached repository parts.

### Context Handling:
- The codebase is consolidated into multiple parts.
- Each part contains a **## 🌳 File Tree** at the beginning for structural context; use this to understand the current file's position in the project.
- Individual files are delimited by XML tags: `<file path="..." language="...">...</file>`. Use the `path` attribute for all citations.

### Output Requirements:
- Format: Markdown with sections: Overview, Build & Run, Architecture, Key Flows, Data & Integrations, Tests, Risks, Quickstart.
- Citations: Cite facts precisely like [source: `path`:line-number].
- If information is missing across all parts, say “Unknown” and list 1–5 clarifying questions.
- Include one Mermaid diagram representing the core architecture or a key data flow.
- Extract run/test commands and environment variables from manifests/configs (setup.py, etc.).

### Response Structure:
1. **Assumptions & Questions**
2. **High-level Overview**
3. **Detailed Analysis (by section)**
4. **Architecture Diagram (Mermaid)**
