import re

class TicketClassifier:
    def __init__(self):
        self.keywords_ai_patch = [
            "crash", "error", "exception", "bug", "failure",
            "update issue", "backend", "API", "database", "timeout", "code"
        ]
        self.keywords_vibe_script = [
            "reset", "configuration", "access issue", "workflow", "instructions",
            "payment delay", "verification", "customer onboarding", "UI navigation"
        ]

    def classify(self, ticket):
        summary = ticket.get("summary", "").lower()
        severity = ticket.get("severity", "").lower()
        channel = ticket.get("channel", "").lower()

        ai_score = sum(kw in summary for kw in self.keywords_ai_patch)
        vibe_score = sum(kw in summary for kw in self.keywords_vibe_script)

        if ai_score > vibe_score or "crash" in summary or "bug" in summary:
            decision = "AI_CODE_PATCH"
            reasoning = (
                "Detected system crash or code-related failure. "
                "Likely requires AI-generated code remediation."
            )
            actions = [
                "Reproduce issue in a controlled environment",
                "Generate patch suggestion using AI code assistant",
                "Run automated unit and integration tests",
                "Deploy patch to staging for QA verification"
            ]
        else:
            decision = "VIBE_SCRIPT"
            reasoning = (
                "Ticket describes a procedural or configuration issue, "
                "suitable for a guided troubleshooting workflow."
            )
            actions = [
                "Identify affected module or user flow",
                "Select appropriate Vibe-coded script template",
                "Customize workflow based on severity",
                "Deploy guided steps to customer support dashboard"
            ]

        return {
            "decision": decision,
            "reasoning": reasoning,
            "next_actions": actions,
            "metadata": {
                "channel": channel,
                "severity": severity
            }
        }
