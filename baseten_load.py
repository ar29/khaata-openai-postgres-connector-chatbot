import baseten
import truss

llama = truss.load("truss-examples/model_library/llama-2-7b-chat/")
baseten.deploy(
  llama,
  model_name="Llama-2-chat 7B",
  is_trusted=True
)