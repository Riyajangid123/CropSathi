import base64
from pathlib import Path
from graph.workflow import Workflow


def image_to_data_uri(image_path: str) -> str:
    path = Path(image_path)
    ext = path.suffix.lstrip(".").lower()
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext  # normalize jpg -> jpeg

    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:image/{mime};base64,{encoded}"


if __name__ == "__main__":
    app = Workflow().build_workflow()

    image_data_uri = image_to_data_uri(
        r"C:\Users\DELL\OneDrive\Pictures\pulse_test.jpg"
    )

    result = app.invoke({
        "question": "What's affecting my cotton crop? Is this a pest or disease?",
        "image": image_data_uri,
    })

    print(result["answer"])