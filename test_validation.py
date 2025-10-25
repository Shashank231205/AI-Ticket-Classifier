import json
from classifier import TicketClassifier

classifier = TicketClassifier()

test_cases = [
    {
        "channel": "Email",
        "severity": "High",
        "summary": "Mobile app crash during login after latest patch"
    },
    {
        "channel": "Chat",
        "severity": "Medium",
        "summary": "Customer unable to reset transaction PIN"
    }
]

for i, case in enumerate(test_cases, 1):
    result = classifier.classify(case)
    print(f"\nTest Case {i}: {json.dumps(result, indent=2)}")
