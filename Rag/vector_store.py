import os

from dotenv import load_dotenv

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PayloadSchemaType,
)

from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings


load_dotenv()


# ============================================================
# CONFIG
# ============================================================

COLLECTION_NAME = "agrotech_knowledge_base"

# all-MiniLM-L6-v2 = 384 dimensions
EMBEDDING_DIM = 384

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ============================================================
# CUSTOM VECTOR STORE
# ============================================================

class CustomVectorStore:

    def __init__(self):

        # ----------------------------------------------------
        # Environment variables
        # ----------------------------------------------------

        self.qdrant_url = os.getenv("QDRANT_URL")

        self.qdrant_api_key = os.getenv(
            "QDRANT_API_KEY"
        )

        self.huggingface_api_key = os.getenv(
            "HUGGINGFACEHUB_API_TOKEN"
        )

        if not self.qdrant_url:
            raise ValueError(
                "QDRANT_URL is not set!"
            )

        if not self.qdrant_api_key:
            raise ValueError(
                "QDRANT_API_KEY is not set!"
            )

        if not self.huggingface_api_key:
            raise ValueError(
                "HUGGINGFACEHUB_API_TOKEN is not set!"
            )

        # ----------------------------------------------------
        # Hugging Face REMOTE embeddings
        # ----------------------------------------------------

        self.embeddings = HuggingFaceEndpointEmbeddings(

            model=EMBEDDING_MODEL,

            task="feature-extraction",

            huggingfacehub_api_token=(
                self.huggingface_api_key
            ),
        )

        print(
            f"Using HuggingFace remote embedding model: "
            f"{EMBEDDING_MODEL}"
        )

        # ----------------------------------------------------
        # Qdrant Cloud
        # ----------------------------------------------------

        self.client = QdrantClient(

            url=self.qdrant_url,

            api_key=self.qdrant_api_key,

            timeout=60,
        )

        # ----------------------------------------------------
        # Collection
        # ----------------------------------------------------

        self._ensure_collection_exists()

        # ----------------------------------------------------
        # Payload indexes
        # ----------------------------------------------------

        self._ensure_payload_indexes()


    # ========================================================
    # COLLECTION
    # ========================================================

    def _ensure_collection_exists(self):

        collections = (
            self.client
            .get_collections()
            .collections
        )

        collection_names = [
            collection.name
            for collection in collections
        ]

        if COLLECTION_NAME not in collection_names:

            print(
                f"Creating Qdrant collection: "
                f"{COLLECTION_NAME}"
            )

            self.client.create_collection(

                collection_name=COLLECTION_NAME,

                vectors_config=VectorParams(

                    size=EMBEDDING_DIM,

                    distance=Distance.COSINE,
                ),
            )

            print(
                "Qdrant collection created."
            )

        else:

            print(
                f"Qdrant collection already exists: "
                f"{COLLECTION_NAME}"
            )


    # ========================================================
    # PAYLOAD INDEXES
    # ========================================================

    def _ensure_payload_indexes(self):

        collection_info = (
            self.client.get_collection(
                COLLECTION_NAME
            )
        )

        payload_schema = (
            collection_info.payload_schema
        )

        # ----------------------------------------------------
        # metadata.crop
        # ----------------------------------------------------

        if "metadata.crop" not in payload_schema:

            print(
                "Creating index: metadata.crop"
            )

            self.client.create_payload_index(

                collection_name=COLLECTION_NAME,

                field_name="metadata.crop",

                field_schema=PayloadSchemaType.KEYWORD,
            )

            print(
                "Created index: metadata.crop"
            )

        else:

            print(
                "Index already exists: metadata.crop"
            )

        # ----------------------------------------------------
        # metadata.disease
        # ----------------------------------------------------

        if "metadata.disease" not in payload_schema:

            print(
                "Creating index: metadata.disease"
            )

            self.client.create_payload_index(

                collection_name=COLLECTION_NAME,

                field_name="metadata.disease",

                field_schema=PayloadSchemaType.KEYWORD,
            )

            print(
                "Created index: metadata.disease"
            )

        else:

            print(
                "Index already exists: metadata.disease"
            )


    # ========================================================
    # VECTOR STORE
    # ========================================================

    def vector_store(self):

        return QdrantVectorStore(

            client=self.client,

            collection_name=COLLECTION_NAME,

            embedding=self.embeddings,
        )


    # ========================================================
    # ADD DOCUMENTS
    # ========================================================

    def add_documents(
        self,
        vectorstore,
        split_docs,
    ):

        if not split_docs:

            print(
                "No documents to add."
            )

            return vectorstore

        print(
            f"Adding {len(split_docs)} documents "
            "to Qdrant..."
        )

        vectorstore.add_documents(
            split_docs
        )

        print(
            "Documents successfully added."
        )

        return vectorstore


    # ========================================================
    # TEST EMBEDDING
    # ========================================================

    def test_embedding(self):

        print(
            "\nTesting HuggingFace embedding..."
        )

        text = (
            "Northern Corn Leaf Blight "
            "in corn plants"
        )

        vector = self.embeddings.embed_query(
            text
        )

        print(
            "Embedding generated successfully."
        )

        print(
            "Embedding dimension:",
            len(vector)
        )

        print(
            "First 5 values:",
            vector[:5]
        )

        return vector


    # ========================================================
    # COLLECTION INFO
    # ========================================================

    def collection_info(self):

        info = self.client.get_collection(
            COLLECTION_NAME
        )

        print(
            "\n========== QDRANT COLLECTION =========="
        )

        print(
            "Collection:",
            COLLECTION_NAME
        )

        print(
            "Points:",
            info.points_count
        )

        print(
            "Vectors:",
            info.config.params.vectors
        )

        print(
            "Payload indexes:",
            info.payload_schema
        )

        print(
            "========================================\n"
        )

        return info


    # ========================================================
    # SAMPLE PAYLOAD
    # ========================================================

    def check_sample_payload(self):

        points, next_page = self.client.scroll(

            collection_name=COLLECTION_NAME,

            limit=1,

            with_payload=True,

            with_vectors=False,
        )

        if not points:

            print(
                "No points found in Qdrant."
            )

            return None

        print(
            "\n========== SAMPLE PAYLOAD =========="
        )

        print(
            points[0].payload
        )

        print(
            "====================================\n"
        )

        return points[0].payload


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    try:

        store = CustomVectorStore()

        # ----------------------------------------------------
        # TEST 1: HF embedding
        # ----------------------------------------------------

        store.test_embedding()

        # ----------------------------------------------------
        # TEST 2: Qdrant collection
        # ----------------------------------------------------

        store.collection_info()

        # ----------------------------------------------------
        # TEST 3: Payload
        # ----------------------------------------------------

        store.check_sample_payload()

        print(
            "\nQdrant + HuggingFace "
            "initialized successfully."
        )

    except Exception as e:

        print(
            "\nERROR:"
        )

        print(
            repr(e)
        )

        raise