import os
from dotenv import load_dotenv
load_dotenv()

import speech_recognition as sr
from langgraph.checkpoint.mongodb import MongoDBSaver
from openai import BadRequestError
from .graph import create_chat_graph


MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://admin:admin@localhost:27018/")
THREAD_ID = os.getenv("THREAD_ID", "1")
EXIT_WORDS = {"exit", "quit", "stop", "goodbye", "bye"}


def check_thread_health(graph, config):
    """Test if the current thread's conversation history is valid."""
    try:
        # Try streaming a no-op to trigger loading existing state
        for _ in graph.stream({"messages": [("user", "health check")]}, config, stream_mode="values"):
            pass
        return True
    except BadRequestError as exc:
        if "tool_call_id" in str(exc):
            return False
        raise


def recover_thread(checkpointer, thread_id):
    """Delete corrupted thread and return."""
    print(f"Thread '{thread_id}' has corrupted conversation history. Clearing it...")
    checkpointer.delete_thread(thread_id)
    print("Thread cleared. Starting fresh conversation.")


def main():
    config = {"configurable": {"thread_id": THREAD_ID}}

    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        graph = create_chat_graph(checkpointer=checkpointer)

        # Check thread health on startup
        if not check_thread_health(graph, config):
            recover_thread(checkpointer, THREAD_ID)
            # Re-compile graph after clearing thread
            graph = create_chat_graph(checkpointer=checkpointer)

        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            r.pause_threshold = 3.0

            print("Voice assistant ready! Say something (say 'exit' to quit).")

            while True:
                print("\nListening...")
                try:
                    audio = r.listen(source)
                    text = r.recognize_google(audio)
                    print(f"You said: {text}")

                    # Check for exit keywords
                    if any(word in text.lower().split() for word in EXIT_WORDS):
                        print("Goodbye!")
                        break

                    for event in graph.stream({"messages": [("user", text)]}, config, stream_mode="values"):
                        if "messages" in event:
                            event["messages"][-1].pretty_print()

                except sr.WaitTimeoutError:
                    print("No speech detected. Try again.")
                except sr.UnknownValueError:
                    print("Could not understand audio. Please try again.")
                except sr.RequestError as exc:
                    print(f"Google Speech Recognition service error: {exc}")
                except BadRequestError:
                    # Thread got corrupted during this session
                    recover_thread(checkpointer, THREAD_ID)
                    graph = create_chat_graph(checkpointer=checkpointer)
                    print("Please repeat your request.")
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break
                except OSError as exc:
                    print(f"Microphone error: {exc}")
                    break


if __name__ == "__main__":
    main()