
import os
from ollama import Client

# Dirección del servidor local de Ollama
client = Client(host="http://localhost:11434")

# Utilizaremos el modelo definido en nuestra terminal
model = os.environ["PRGUARD_MODEL"]

response = client.chat(
    model=model,
    messages=[
        {
            "role": "user",
            "content": "Explain in one sentence what static code analysis is. Tell me what model you are."
        }
    ]
)

print(response.message.content)
