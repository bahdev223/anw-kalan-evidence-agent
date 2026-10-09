# External MCP integration

The final challenge demo must include a second MCP server that this team did not author.

Current integration choice: an independently maintained filesystem MCP server, used only to read a small directory of synthetic learner artifacts for the demo.

Why keep it separate:

- judges can clearly distinguish first-party tools from external tools;
- the external server receives no production credentials or real learner data;
- the core learning state still comes from deterministic evidence rules;
- replacing the external MCP cannot silently alter the human-approval policy.

The exact package, version, invocation command and captured tool logs will be pinned here before final submission.
