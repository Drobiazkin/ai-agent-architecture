<!-- SPDX-FileCopyrightText: 2026 Aleksandr Drobiazkin
     SPDX-License-Identifier: CC-BY-SA-4.0 AND MIT
     Source: https://github.com/Drobiazkin/ai-agent-architecture
     Dual-licensed, and the boundary is exactly the fence: a fenced code block tagged
     with a language (python, java, sql, bash, yaml, xml, json), comments inside it
     included, is MIT. Everything else — the prose, the tables, the formulas, and the
     mermaid diagrams, which are illustrations expressed as text — is CC-BY-SA-4.0.
     Full terms: LICENSE, LICENSE-CODE, and NOTICE in the repository root. -->

# Table of Contents

**Part I. The Language Model as a Component**
- Chapter 1. The Language Model as an Architectural Component
    - 1.1 Why you need to understand the model's internals
    - 1.2 Tokenization
    - 1.3 Embeddings and vector space
    - 1.4 Attention and the transformer *(article-length section)*
    - 1.5 Dense vs. Mixture-of-Experts
    - 1.6 The generation loop and inference
    - 1.7 Decoding strategies
    - 1.8 The context window and how it fails
    - 1.9 Why the model hallucinates and what it means to "know"
    - 1.10 Summary: the component's contract
- Chapter 2. Economics and the Nonfunctional Properties of an LLM

**Part II. The Interface to the Model**
- Chapter 3. Prompt Engineering as Contract Design
    - 3.1 The framing: a prompt as an interface specification · 3.2 Anatomy of a prompt · 3.3 A catalog of prompting patterns · 3.4 Chain-of-Thought, in depth · 3.5 The system prompt as an invariant · 3.6 Prompts as code · 3.7 The limits of prompt engineering
- Chapter 4. Context Engineering and Context-Management Patterns *(article-length section)*
    - 4.1 Shifting the unit of design · 4.2 Anatomy of the context · 4.3 Forces: why this is nontrivial · 4.4 A catalog of context-management patterns · 4.5 Memory as long-term context · 4.6 The limits of context, and trust · 4.7 Summary
- Chapter 5. Structured Output and Reliable Parsing
    - 5.1 The boundary between probabilistic and deterministic · 5.2 The spectrum of techniques · 5.3 Constrained decoding (in depth) · 5.4 Schema design as contract design · 5.5 Reliability patterns · 5.6 Structure ≠ correctness · 5.7 Implementation on the JVM · 5.8 Summary

**Part III. Grounding Knowledge: RAG**
- Chapter 6. Retrieval-Augmented Generation: Framing the Problem *(article-length section)*
    - 6.1 The problem · 6.2 What RAG is · 6.3 RAG vs. the alternatives · 6.4 Anatomy of a RAG system · 6.5 Retrieval is the bottleneck · 6.6 A taxonomy of failures · 6.7 Grounding and faithfulness · 6.8 Implementing the retrieval layer · 6.9 Summary
- Chapter 7. A Catalog of Retrieval Patterns (Naive, Hybrid, Rerank, GraphRAG, Agentic, Adaptive)
    - 7.1 The pattern ladder · 7.2 Naive RAG · 7.3 Hybrid Search · 7.4 Reranking · 7.5 Query transformation · 7.6 Chunking (+ multimodal RAG, choosing an embedder) · 7.7 GraphRAG · 7.8 Agentic RAG · 7.9 Adaptive RAG · 7.10 Summary and a decision framework
- Chapter 8. Vector Indexes and Retrieval Infrastructure (ANN/HNSW, pgvector, Hybrid Search)
    - 8.1 Nearest-neighbor search · 8.2 The curse of dimensionality · 8.3 Families of ANN indexes · 8.4 The universal trade-off · 8.5 pgvector · 8.6 Hybrid search and filtering · 8.7 RBAC/ABAC at retrieval · 8.8 Operational concerns · 8.9 Summary
- Chapter 9. Evaluating RAG Quality
    - 9.1 Eval-driven RAG · 9.2 A two-axis metric framework · 9.3 The golden set · 9.4 LLM-as-judge for RAG · 9.5 The eval-driven RAG loop · 9.6 Online evaluation · 9.7 Summary

**Part IV. Action: Agents and Orchestration**
- Chapter 10. The Agent as a Distributed System
    - 10.1 What an agent is · 10.2 The Augmented LLM · 10.3 Workflow vs agent · 10.4 The agent as a distributed system · 10.5 The control loop and nontermination · 10.6 Reliability, reversibility, and the Human-in-the-Loop Gate · 10.7 Levels of agency · 10.8 Summary
- Chapter 11. A Catalog of Agent Patterns (Chaining, Routing, Parallelization, Orchestrator-Workers, Evaluator-Optimizer)
    - 11.1 The ladder and composition · 11.2 Prompt Chaining · 11.3 Routing · 11.4 Parallelization · 11.5 Orchestrator-Workers · 11.6 Evaluator-Optimizer · 11.7 Composing patterns · 11.8 What is a workflow and what is an agent · 11.9 Summary and a decision framework
- Chapter 12. Tools and Tool Calling as a Contract
    - 12.1 What tool calling is · 12.2 The mechanics · 12.3 The ACI as contract design · 12.4 Tool errors · 12.5 Tool security · 12.6 Code execution and Skills · 12.7 Implementation on the JVM · 12.8 Summary
- Chapter 13. Memory and Reasoning Strategies (ReAct, Plan-and-Execute, Reflection)
    - 13.1 Memory in the agent loop · 13.2 The family of strategies · 13.3 ReAct · 13.4 Plan-and-Execute · 13.5 Reflection · 13.6 Tree-of-Thought · 13.7 Choosing a strategy · 13.8 Reasoning models change the calculus · 13.9 Summary
- Chapter 14. Multi-Agent Systems and a Taxonomy of Failures
    - 14.1 When you need multi-agent · 14.2 Coordination patterns · 14.3 The cost of multi-agent · 14.4 A taxonomy of failures (MAST) · 14.5 Treating them with distributed-systems discipline · 14.6 Summary

**Part V. Integration: Embedding into the Architecture**
- Chapter 15. Model Context Protocol (MCP) *(article-length section)*
    - 15.1 The N×M problem · 15.2 Host, client, server · 15.3 Primitives · 15.4 The session lifecycle · 15.5 Transports · 15.6 MCP and tool calling (+ A2A) · 15.7 MCP security · 15.8 Implementation on the JVM · 15.9 Summary
- Chapter 16. Assembling the Stack on the JVM (Spring AI, LangChain4j)
    - 16.1 The two options · 16.2 Mapping concerns onto constructs · 16.3 Interceptors vs. declarative services · 16.4 Agents and workflows on the JVM · 16.5 Production concerns · 16.6 Choosing and combining · 16.7 Summary

**Part VI. Production: Operating the System**
- Chapter 17. Evaluation: Building an Eval System
    - 17.1 Evaluation is the central discipline · 17.2 Levels and types · 17.3 LLM-as-judge · 17.4 Judge biases · 17.5 Evaluating agents and trajectories · 17.6 Offline vs. online · 17.7 Statistical rigor · 17.8 The architecture of an eval system · 17.9 Summary
- Chapter 18. Observability
    - 18.1 Why it is harder · 18.2 The three signals · 18.3 Tracing an agent · 18.4 The OpenTelemetry GenAI conventions · 18.5 Metrics and cost attribution · 18.6 Content capture and privacy · 18.7 Debugging nondeterministic trajectories · 18.8 Observability and evaluation together · 18.9 Summary
- Chapter 19. Security: Prompt Injection and Defense in Depth *(article-length section)*
    - 19.1 Instructions and data in one channel · 19.2 Injection vs. jailbreaking · 19.3 The OWASP threat map · 19.4 The lethal trifecta and excessive agency · 19.5 Guardrails and their limits · 19.6 Architectural defense · 19.7 Defense in depth · 19.8 Summary
- Chapter 20. Cost and Latency
    - 20.1 Cost as a product constraint · 20.2 The economics of caching · 20.3 Routing and cascades · 20.4 Cutting tokens · 20.5 Latency · 20.6 Budgets, the gateway, and attribution · 20.7 The combined effect · 20.8 Summary

**Part VII. Your Own Models**
- Chapter 21. Fine-Tuning: Adapting the Model (LoRA, QLoRA, DPO, Distillation)
    - 21.1 When to fine-tune · 21.2 Full fine-tuning vs. PEFT · 21.3 LoRA · 21.4 QLoRA and memory · 21.5 DoRA and the Kronecker product · 21.6 RLHF and DPO · 21.7 Knowledge distillation · 21.8 Practice · 21.9 Summary
- Chapter 22. Serving Open Models
    - 22.1 Why · 22.2 The serving stack · 22.3 PagedAttention · 22.4 Continuous batching · 22.5 Prefill vs. decode and disaggregation · 22.6 Quantization for inference · 22.7 Speculative decoding · 22.8 Throughput vs. latency · 22.9 Summary
- Chapter 23. Pre-Training
    - 23.1 When it is justified · 23.2 The pipeline · 23.3 Scaling laws · 23.4 The C ≈ 6ND budget · 23.5 Compute-optimal vs. inference-optimal (+ test-time compute) · 23.6 Data and infrastructure · 23.7 Summary

**Part VIII. Synthesis**
- Chapter 24. The Reference Architecture
    - 24.1 The layers · 24.2 The full component schematic · 24.3 The request flow · 24.4 Boundaries and invariants (+ physical topology) · 24.5 Cross-cutting concerns · 24.6 Decisions by layer · 24.7 Summary
- Chapter 25. Organizational Adoption
    - 25.1 Why architecture is not enough · 25.2 Ownership and the lifecycle of AI artifacts · 25.3 The AI Gateway as a governance point · 25.4 The PII containment loop · 25.5 The regulatory landscape · 25.6 TCO and ROI · 25.7 Teams and process · 25.8 Summary
- Chapter 26. A Worked Example and a Package of Architectural Decisions
    - 26.1 The scenario and the functional requirements · 26.2 NFRs and budgets · 26.3 The ADR format · 26.4 The decision package (12 ADRs) · 26.5 The instantiated architecture · 26.6 How the system evolves · 26.7 Summary of the book

**Appendices**
- Appendix A. The Linear-Algebra Substrate
- Appendix B. Pattern Index
- Appendix C. Anatomy of a Single Trajectory
- Appendix D. The Architect's Pre-Flight Checklist
- Appendix E. Consolidated Bibliography

---
