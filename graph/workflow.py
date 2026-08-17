from langgraph.graph import StateGraph, START, END
from graph.state import AgroState
from nodes.language_node import LanguageNode
from nodes.vision_node import VisionNode
from nodes.retrieve_node import RetrieveNode
from nodes.reranked_node import RerankNode
from nodes.generate_node import GenerateNode


class Workflow:
    def __init__(self):
        self.graph = StateGraph(AgroState)

    def route_after_language(self, state: AgroState):
        # Only run vision analysis if an actual image was sent
        return "vision_node" if state.get("image") else "route_no_image"

    def route_after_vision(self, state: AgroState):
        return "retrieve_node" if state.get("needs_retrieval") else "generate_node"

    def build_workflow(self):
        self.graph.add_node("language_node", LanguageNode().run)
        self.graph.add_node("vision_node", VisionNode().run)
        self.graph.add_node("retrieve_node", RetrieveNode().run)
        self.graph.add_node("rerank_node", RerankNode().run)
        self.graph.add_node("generate_node", GenerateNode().run)

        self.graph.add_edge(START, "language_node")

        self.graph.add_conditional_edges(
            "language_node",
            self.route_after_language,
            {
                "vision_node": "vision_node",
                "route_no_image": "generate_node",   # text-only: skip vision, go straight to generate
            },
        )

        self.graph.add_conditional_edges(
            "vision_node",
            self.route_after_vision,
            {
                "retrieve_node": "retrieve_node",
                "generate_node": "generate_node",
            },
        )

        self.graph.add_edge("retrieve_node", "rerank_node")
        self.graph.add_edge("rerank_node", "generate_node")
        self.graph.add_edge("generate_node", END)

        return self.graph.compile()