# Development Plan

Below is a **personalized solo project development plan (considering only development sequence)** tailored for you, targeting the "Mortal's Journey to Immortality Causal Event Knowledge Graph Generation System based on R2 framework," combining your architectural preferences, organized by **module priority, dependency relationships, and development granularity**, ensuring:

* Core functionality implemented first (event identification and causal reasoning)
* Single modules testable and tunable (decoupled, conducive to testing)
* Gradual integration and assembly, maintaining runnability

---

## 📌 Development Sequence Overview (By Stage)

| Stage | Development Goal | Modules/Files |
| -- | --------------------- | ------------------------------------- |
| 1 | Build core structure and interfaces (abstractions + data models) | common/ |
| 2 | Implement input end and event extraction main process (Reader) | text\_ingestion/ + event\_extraction/ |
| 3 | Connect hallucination repair module (HAR) | hallucination\_refine/ |
| 4 | Implement causal chain building module (CPC) | causal\_linking/ |
| 5 | Implement knowledge graph building and visualization output | graph\_builder/ |
| 6 | Build unified entry point (CLI interface/API interface) | api\_gateway/ |
| 7 | Unit testing & example graph testing | tests/ |

---

## ✅ Stage 1: Abstract Interfaces and Common Model Preparation (Basic Framework)

📁 `common/models/`

* `event.py`: Define `EventItem` data structure (including characters, treasures, descriptions, chapters, etc.)
* `chapter.py`: Define `Chapter` data structure
* `causal_edge.py`: Event causal edge structure
* `treasure.py`: Treasure structure (optional)

📁 `common/interfaces/`

* `extractor.py`: Define `AbstractExtractor` interface
* `refiner.py`: Define `AbstractRefiner` interface
* `linker.py`: Define `AbstractLinker` interface
* `graph_renderer.py`: Define `AbstractGraphRenderer`

📁 `common/utils/`

* `json_loader.py`: For reading configuration/chapter JSON files
* `text_splitter.py`: Chapter sentence splitter

📁 `common/config/`

* JSON configuration samples + prompt template examples

---

## ✅ Stage 2: Reader Main Process Development

📁 `text_ingestion/`

* `chapter_loader.py`: Load from txt files and split into chapter JSONs (test target input)
* `app.py`: Execution entry point for unit testing

📁 `event_extraction/`

* `domain/base_extractor.py`: Inherit from `AbstractExtractor`
* `service/extractor_service.py`: Build main logic, complete prompt concatenation and LLM calls
* `repository/llm_client.py`: Encapsulate OpenAI interface
* `di/provider.py`: Register extractor implementation classes
* `controller/extractor_controller.py`: Provide local running entry point (batch processing capable)

Target output: Ability to batch generate structured events and treasure data from chapter JSONs

---

## ✅ Stage 3: HAR Module Development (Hallucination Repair)

📁 `hallucination_refine/`

* `domain/base_refiner.py`: Define `AbstractRefiner` interface
* `service/har_service.py`: Implement iterative repair logic (reference paper pseudocode)
* `repository/llm_client.py`: Reuse LLM interface from event\_extraction module
* `di/provider.py`: Register refiner
* `controller/har_controller.py`: Local entry point for testing

Target output: Ability to detect and repair hallucinations and incorrect terminology in events

---

## ✅ Stage 4: Causal Chain Building Module (CPC)

📁 `causal_linking/`

* `domain/base_linker.py`: Define `AbstractLinker`
* `service/linker_service.py`: Determine causality between event pairs (prompt + LLM)
* `service/graph_filter.py`: Implement cycle removal, greedy algorithm to retain strong edges
* `di/provider.py`: Register Linker
* `controller/linker_controller.py`: Test entry point

Target output: Construct a Directed Acyclic Graph (DAG) from the event set

---

## ✅ Stage 5: Mermaid Graph Output

📁 `graph_builder/`

* `domain/base_renderer.py`: Define `AbstractGraphRenderer`
* `service/mermaid_renderer.py`: Implement Mermaid graph output logic
* `controller/graph_controller.py`: Input DAG → Output Mermaid text
* `utils/color_map.py`: Generate Mermaid node colors based on event types

Target output: Visualized output of `.mmd` Mermaid graph code

---

## ✅ Stage 6: Integration and Unified Call Interface (CLI or REST)

📁 `api_gateway/`

* `main.py`: Support CLI command-line execution process (e.g., from txt input → output graph)
* `router/` (optional):

  * FastAPI implementation of REST service entry (future expansion)

📁 `scripts/`

* `demo_run.py`: Run through the End-to-End process from input chapter → output graph with examples

---

## ✅ Stage 7: Testing and Sample Running

📁 `tests/`

* `test_event_extraction.py`: Event extraction module unit test
* `test_har_module.py`: HAR refinement module test
* `test_causal_linking.py`: Causal identification module test
* `test_mermaid_graph.py`: Mermaid rendering output test
* Use mock providers to implement module isolation testing

---

## 🚦 Development Path Roadmap (Summary)

```text
1️⃣ Establish models + ABC interfaces
2️⃣ Implement text_ingestion → event_extraction → CLI to complete event extraction
3️⃣ Add HAR repair → connect to event_extraction output
4️⃣ Implement causal judgment + graph filtering (DAG)
5️⃣ Implement Mermaid output format + rendering module
6️⃣ Integrate API/CLI unified calling
7️⃣ Add testing and experimental graphs
```

---

If you wish, I can:

* 🧱 Generate Python code file skeletons for all modules
* 🧪 Help you design test data and prompt templates
* 🖼️ Start building complete implementation code for any module (e.g., extractor)

Which step would you like me to start with now? Would you like me to generate the entire project code framework?
