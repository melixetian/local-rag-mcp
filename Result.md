cd src && python main.py
============================================================
🤖 Company Knowledge Base Assistant
============================================================

Ask questions about company policies, procedures, and documentation.
Type 'exit' or 'quit' to stop


❓ Question: How much paid holiday does a permanent employee get?
────────────────────────────────────────────────────────────
🤖 Answer:

📚 Retrieved 5 relevant chunks from knowledge base
🔧 LLM decided to use MCP tool: read_document with args: {'file_path': 'docs/vacation-policy.md'}
✅ MCP tool returned result (length: 4 chars)
A permanent employee at Northstar Labs is entitled to **24 paid working days of annual leave per calendar year**. This allowance is credited monthly, and public holidays and weekends do not count toward the annual leave days.

📚 Sources:
  • docs/vacation-policy.md
  • docs/remote-work.md
  • docs/expense-policy.md
  • docs/deployment-guide.md
  • docs/data-retention.md

🔧 Used MCP tool: read_document
────────────────────────────────────────────────────────────

❓ Question: ❓ Question: What is HR-LV-204?
────────────────────────────────────────────────────────────
🤖 Answer:

📚 Retrieved 5 relevant chunks from knowledge base
HR-LV-204 is the **Annual Leave Policy** for permanent Northstar Labs employees. It outlines the rules for annual leave entitlement, request procedures, carry-over limits, and related guidelines. Specifically, it states that every permanent employee receives **24 paid working days of annual leave per calendar year**, with public holidays and weekends not counting toward this allowance. Unused days exceeding 10 are expiring on March 31 unless approved by People Operations.

📚 Sources:
  • docs/vacation-policy.md
  • docs/expense-policy.md
  • docs/security-policy.md
  • docs/remote-work.md
  • docs/incident-response.md
────────────────────────────────────────────────────────────

❓ Question: What is the office Wi-Fi password?
────────────────────────────────────────────────────────────
🤖 Answer:

📚 Retrieved 5 relevant chunks from knowledge base
🔧 LLM decided to use MCP tool: search_documents with args: {'query': 'office Wi-Fi password'}
✅ MCP tool returned result (length: 4 chars)
I don't have that information in the knowledge base.

📚 Sources:
  • docs/security-policy.md
  • docs/remote-work.md
  • docs/expense-policy.md
  • docs/incident-response.md
  • docs/vacation-policy.md

🔧 Used MCP tool: search_documents
────────────────────────────────────────────────────────────

❓ Question: What is 5 * 5
────────────────────────────────────────────────────────────
🤖 Answer:

📚 Retrieved 5 relevant chunks from knowledge base
I don't have that information in the knowledge base.

📚 Sources:
  • docs/expense-policy.md
  • docs/incident-response.md
  • docs/deployment-guide.md
  • docs/security-policy.md
  • docs/vacation-policy.md
────────────────────────────────────────────────────────────

❓ Question: How do I open the most severe production incident?
────────────────────────────────────────────────────────────
🤖 Answer:

📚 Retrieved 5 relevant chunks from knowledge base
To open the most severe production incident (P1), the on-call engineer must use the following command:  

```bash
opsctl incident declare --severity p1
```  

This command declares the incident, triggering the required response procedures (e.g., acknowledgment, status updates, and post-incident reviews).

📚 Sources:
  • docs/incident-response.md
  • docs/deployment-guide.md
  • docs/data-retention.md
  • docs/security-policy.md
  • docs/remote-work.md
────────────────────────────────────────────────────────────

❓ Question: q

👋 Goodbye!
