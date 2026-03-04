#!/usr/bin/env node
// PreToolUse hook: Block dangerous git commands on Bash tool calls.
// Exit code 2 + JSON { "decision": "block", "reason": "..." } = deny the command.
// Exit code 0 = allow (passthrough).

const DANGEROUS_PATTERNS = [
  { pattern: /git\s+push\s+.*--force.*(?:main|master)/i, reason: "Force-push to main/master blocked" },
  { pattern: /git\s+push\s+--force/i, reason: "Force-push blocked (specify branch explicitly if needed)" },
  { pattern: /git\s+reset\s+--hard/i, reason: "git reset --hard blocked (destructive)" },
  { pattern: /git\s+clean\s+-[a-zA-Z]*f/i, reason: "git clean -f blocked (destructive)" },
  { pattern: /git\s+branch\s+-D\s+(?:main|master)/i, reason: "Deleting main/master branch blocked" },
  { pattern: /rm\s+-rf\s+[\/\\]/i, reason: "rm -rf on root path blocked" },
];

function main() {
  let input = "";
  process.stdin.setEncoding("utf8");
  process.stdin.on("data", (chunk) => { input += chunk; });
  process.stdin.on("end", () => {
    try {
      const event = JSON.parse(input);
      const command = event?.tool_input?.command ?? "";

      for (const { pattern, reason } of DANGEROUS_PATTERNS) {
        if (pattern.test(command)) {
          const response = JSON.stringify({ decision: "block", reason });
          process.stdout.write(response);
          process.exit(2);
        }
      }

      // Allow the command
      process.exit(0);
    } catch {
      // On parse error, allow (don't block legitimate commands)
      process.exit(0);
    }
  });
}

main();
