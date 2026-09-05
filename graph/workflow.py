from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from graph.state import AgroState

from nodes.language_node import LanguageNode
from nodes.vision_node import VisionNode
from nodes.retrieve_node import RetrieveNode
from nodes.reranked_node import RerankNode
from nodes.generate_node import GenerateNode

from tools.weather_api import get_coordinates, get_weather


class Workflow:

    def __init__(self):

        self.graph = StateGraph(AgroState)
        self.tools = [
            get_coordinates,
            get_weather
        ]
        self.tool_node = ToolNode(self.tools)

    def route_after_language(self, state: AgroState):

        if state.get("image"):
            return "vision_node"

        return "generate_node"

    def route_after_vision(self, state: AgroState):

        if state.get("needs_retrieval"):
            return "retrieve_node"

        return "generate_node"


    def route_after_generate(self, state: AgroState):

        messages = state.get("messages", [])

        if not messages:
            return END

        last_message = messages[-1]

        tool_calls = getattr(
            last_message,
            "tool_calls",
            []
        )

        if tool_calls:
            return "tool_node"

        return END

    def build_workflow(self):

        # Nodes

        self.graph.add_node(
            "language_node",
            LanguageNode().run
        )

        self.graph.add_node(
            "vision_node",
            VisionNode().run
        )

        self.graph.add_node(
            "retrieve_node",
            RetrieveNode().run
        )

        self.graph.add_node(
            "rerank_node",
            RerankNode().run
        )

        self.graph.add_node(
            "generate_node",
            GenerateNode().run
        )

        self.graph.add_node(
            "tool_node",
            self.tool_node
        )

        # START
        self.graph.add_edge(
            START,
            "language_node"
        )

        # Language → Vision / Generate

        self.graph.add_conditional_edges(
            "language_node",
            self.route_after_language,
            {
                "vision_node": "vision_node",
                "generate_node": "generate_node",
            }
        )

        # Vision → Retrieval / Generate

        self.graph.add_conditional_edges(
            "vision_node",
            self.route_after_vision,
            {
                "retrieve_node": "retrieve_node",
                "generate_node": "generate_node",
            }
        )

        # Retrieval → Rerank

        self.graph.add_edge(
            "retrieve_node",
            "rerank_node"
        )

        # Rerank → Generate

        self.graph.add_edge(
            "rerank_node",
            "generate_node"
        )

        # Generate → Tool / END

        self.graph.add_conditional_edges(
            "generate_node",
            self.route_after_generate,
            {
                "tool_node": "tool_node",
                END: END,
            }
        )

        # Tool → Generate

        self.graph.add_edge(
            "tool_node",
            "generate_node"
        )

        return self.graph.compile()