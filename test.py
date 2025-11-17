import requests
import time
import json


class StreamingTestClient:
    """Cliente interactivo para probar /ask con SSE y mantener historial."""

    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.message_history = []  # historial acumulado

    def test_connection(self):
        try:
            r = requests.get(f"{self.base_url}/docs")
            if r.status_code == 200:
                print("Conexión OK.")
                return True
            print("Error:", r.status_code)
            return False
        except Exception as e:
            print("No se pudo conectar:", e)
            return False

    def send_and_stream(self, question):
        print(f"\nPregunta: {question}")
        print("-" * 60)

        # Agregar al historial
        self.message_history.append({"role": "user", "content": question})

        payload = {
            "question": question,
            "message_history": self.message_history
        }

        try:
            response = requests.post(
                f"{self.base_url}/ask",
                json=payload,
                stream=True,
                headers={"Accept": "text/event-stream"},
                timeout=120
            )

            if response.status_code != 200:
                print("Error:", response.status_code, response.text)
                return False

            assistant_message = ""
            current_event = None
            current_data = []

            for raw in response.iter_lines():
                if not raw:
                    continue

                line = raw.decode("utf-8")

                # EVENT:
                if line.startswith("event:"):
                    # procesar el evento anterior
                    if current_event and current_data:
                        self._process_event(current_event, current_data, assistant_message)
                        # Si era parte de la respuesta, concatenar al mensaje final
                        if current_event == "answer":
                            for d in current_data:
                                try:
                                    pj = json.loads(d)
                                    assistant_message += pj.get("content", "")
                                except:
                                    pass

                    current_event = line.replace("event:", "").strip()
                    current_data = []
                    continue

                # DATA:
                if line.startswith("data:"):
                    current_data.append(line.replace("data:", "").strip())
                    continue

            # Procesar último evento
            if current_event and current_data:
                self._process_event(current_event, current_data, assistant_message)
                if current_event == "answer":
                    for d in current_data:
                        try:
                            pj = json.loads(d)
                            assistant_message += pj.get("content", "")
                        except:
                            pass

            # Guardar en historial como asistente
            if assistant_message.strip():
                self.message_history.append({"role": "assistant", "content": assistant_message})

            print("\n" + "-" * 60)
            print("Turno completado.")
            print("-" * 60)

            return True

        except Exception as e:
            print("Error:", e)
            return False

    def _process_event(self, event, data_lines, assistant_msg_ref):
        payload_raw = "\n".join(data_lines)

        try:
            payload = json.loads(payload_raw)
        except:
            print(f"[{event}] (no JSON): {payload_raw}")
            return

        if event == "answer":
            content = payload.get("content", "")
            print(content, end="", flush=True)

        elif event == "tool_usage":
            print(f"\n[TOOL] {payload.get('content')}")

        elif event == "tool_log":
           # print(f"\n[TOOL_LOG] {payload.get('content')}")
           pass

        elif event == "done":
            print("\nFIN DEL STREAM.")

    def run(self):
        if not self.test_connection():
            return

        print("\nChat interactivo. Escribe 'exit' para salir.")

        while True:
            question = input("\n>>> ").strip()
            if question.lower() in ("exit", "quit"):
                print("Saliendo.")
                break
            if not question:
                continue

            self.send_and_stream(question)


if __name__ == "__main__":
    StreamingTestClient().run()
