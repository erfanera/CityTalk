from openai import OpenAI
api_key = "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"
client = OpenAI(api_key=api_key)

file_1 = client.files.create(
  file=open("CSV/air_pollution_levels.csv", "rb"),
  purpose='assistants'
)
file_2 = client.files.create(
  file=open("CSV/Bicing.csv", "rb"),
  purpose='assistants'
)

assistant = client.beta.assistants.create(
  name="Data visualizer",
  description="you're a urban data analyst you need to see what user is asking based on the files you have and your write a code to calculate and find the answer break down in steps write the code and run it and explain the reuslt",
  model="gpt-4.1",
  tools=[{"type": "code_interpreter"}],
  tool_resources={
    "code_interpreter": {
      "file_ids": [file_1.id, file_2.id]
    }

  }
)
thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content="Find the top 5 bicing stations that are close to the most polluted areas"
)


from typing_extensions import override
from openai import AssistantEventHandler, OpenAI

client = OpenAI(api_key=api_key)

class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    @override
    def on_message_done(self, message) -> None:
        # print a citation to the file searched
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(
                annotation.text, f"[{index}]"
            )
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        print(message_content.value)
        print("\n".join(citations))

# Then, we use the stream SDK helper.
# with the EventHandler class to create the Run.
# and stream the response.

with client.beta.threads.runs.stream(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Please address the user as Jane Doe. The user has a premium account.",
    event_handler=EventHandler(),
) as stream:
    stream.until_done()
