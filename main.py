# main.py

class AI_Assistant:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello, I am {self.name}, your AI assistant!"

if __name__ == "__main__":
    assistant = AI_Assistant("Assistant")
    print(assistant.greet())