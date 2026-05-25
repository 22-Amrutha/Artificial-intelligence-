import anthropic

client = anthropic.Anthropic(api_key="your-api-key-here")
history = []

print("Chatbot ready! Type 'quit' to exit, 'clear' to reset.\n")

while True:
    user_input = input("You: ").strip()
    
    if not user_input:
        continue
    if user_input.lower() == "quit":
        print("Goodbye!")
        break
    if user_input.lower() == "clear":
        history = []
        print("Chat cleared!\n")
        continue

    history.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system="You are a helpful assistant. Be concise and friendly.",
        messages=history
    )

    reply = response.content[0].text
    history.append({"role": "assistant", "content": reply})
    
    print(f"Bot: {reply}\n")