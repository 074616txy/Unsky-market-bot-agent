# 实现简单的短期记忆系统
class SimpleMemory:
    def __init__(self, max_rounds: int = 5):
        self.max_rounds = max_rounds
        self.messages = []

    def add_user_message(self, content: str):
        self.messages.append({
            "role": "user",
            "content": content,
        })
        self._trim()

    def add_assistant_message(self, content: str):
        self.messages.append({
            "role": "assistant",
            "content": content,
        })
        self._trim()

    def get_context(self) -> str:
        if not self.messages:
            return ""

        lines = []

        for message in self.messages:
            role = "用户" if message["role"] == "user" else "Skybot"
            lines.append(f"{role}: {message['content']}")

        return "\n".join(lines)

    def clear(self):
        self.messages.clear()

    def _trim(self):
        max_messages = self.max_rounds * 2
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]