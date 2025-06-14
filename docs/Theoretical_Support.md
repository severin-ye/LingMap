# Theoretical Support

## Abstract

Automatically adapting novels into screenplays is crucial for the television, film, or opera industries to promote products at low cost. The powerful performance of Large Language Models (LLMs) in long-text generation has prompted us to propose an LLM-based framework **Reader-Rewriter (R2)** to accomplish this task. However, there are two fundamental challenges. First, **hallucinations** in LLMs may lead to inconsistencies in plot extraction and screenplay generation. Second, there is a need to effectively extract causality-embedded plot lines for coherent rewriting. Consequently, we propose two corresponding strategies: 1) a **Hallucination-Aware Refinement method (HAR)** to iteratively discover and eliminate the impact of hallucinations; and 2) a **Causal Plot-graph Construction method (CPC)** based on a greedy cycle-breaking algorithm to effectively construct plot lines with event causalities.

The R2 framework leverages these efficient techniques through two modules to mimic the human screenplay rewriting process: the **Reader module** employs a sliding window and CPC to construct causal plot graphs, while the **Rewriter module** first generates scene outlines based on these graphs, and then generates screenplays. HAR is integrated into both modules to achieve accurate inferences with LLMs. Experimental results demonstrate the superiority of R2, with a significant advantage over three existing methods in overall win rate in GPT-4o pairwise comparisons (absolute increases of 51.3%, 22.6%, and 57.1% respectively).

---

## 1 Introduction

Screenplays are the foundation for forms such as TV dramas, films, or operas, and they are often adapted directly from novels. For example, 52% of the top 20 films produced in the UK between 2007 and 2016 were adapted from novels (Association & Economics, 2018), and the average number of adaptations for US TV or film per month exceeded 10 in the first nine months of 2024 (Vulture, 2024). Typically, adapting novels into screenplays requires prolonged efforts from professional writers. Automating this task could significantly reduce production costs and promote the dissemination of these works (Zhu et al., 2023). However, current work (Zhu et al., 2022; Mirowski et al., 2023; Han et al., 2024; Morris et al., 2023) can only generate screenplays from predefined outlines. Therefore, this automatic **novel-to-screenplay generation (N2SG)** task is highly anticipated.

Considering the excellent performance of Large Language Models (LLMs) in text generation and understanding tasks (Brown et al., 2020; Ouyang et al., 2022), we are interested in LLM-based approaches to perform the N2SG task. However, there are two fundamental challenges before building such a system.

1) **How to eliminate the impact of hallucinations in N2SG?** Current LLMs, such as GPT-4, struggle when handling an entire novel and often generate various inconsistent content due to LLM hallucinations (Liu et al., 2024; Ji et al., 2023; Shi et al., 2023) when processing lengthy inputs. Existing refinement methods can only roughly reduce such inconsistencies without handling long input data (Madaan et al., 2023; Peng et al., 2023).

2) **How to extract effective plot lines that capture complex causal relationships between events?** Simply eliminating inconsistencies does not ensure that the generated story has coherence and accurate plot lines consistent with the original novel. Existing plot graph-based methods (Weyhrauch, 1997; Li et al., 2013) depict plot lines with linearly ordered events. However, events can be intricately connected, and these methods cannot model complex causal relationships.

For the first challenge, we can only partially refine the context related to inconsistencies caused by hallucinations. Therefore, this study proposes a **Hallucination-Aware Refinement method (HAR)** to iteratively eliminate the impact of LLM hallucinations for better information extraction and generation from long texts.

For the second challenge, plot lines containing causalities need to be extracted for coherent rewriting. Plot graphs are convenient for representing sequential events and can be extended to **causal plot graphs** to embed causal relationships. Therefore, this paper proposes a **Causal Plot-graph Construction (CPC)** method to robustly extract causal relationships of events and construct causal plot graphs.

The question now is how to build an N2SG system using HAR and CPC. Observing human screenwriters (Figure 1), we find they can successfully complete this task through a combined process of reading and rewriting (McKee, 1999): first, they read the novel to extract key plot events and character profiles (i.e., character biographies and their relationships) to construct the novel's plot lines; then, they rewrite the novel into a screenplay based on these plot lines, which are adapted into story lines and scene goals as outlines guiding screenplay creation. The reading and rewriting steps may be performed multiple times with multiple refinements until satisfaction.

---

**Figure 1: Typical rewriting process of human screenwriters.** Screenwriters need multiple readings and rewritings with iterative refinements when adapting novels into screenplays.

---

Inspired by the iterative-refinement-based human rewriting process, we propose the **Reader-Rewriter (R2) framework** (Figure 2). The **Reader** employs a sliding window-based strategy to scan the entire novel, spanning chapter boundaries, to effectively capture events and character profiles for subsequent CPC process to construct causal plot graphs, where HAR is used to extract accurate events and character profiles. The **Rewriter** adopts a two-step strategy, first obtaining storylines and goals for all scenes as global guidance, and then generating screenplays scene by scene, ensuring coherence and consistency between scenes under HAR's precise refinement.

Experiments were conducted on R2 with a dataset consisting of several novel-screenplay pairs, evaluated based on seven aspects proposed. GPT-4o-based evaluation shows that R2 significantly outperforms existing methods in all aspects, with overall absolute improvements of 51.3%, 22.6%, and 57.1% over three comparative methods. Human evaluators similarly confirm R2's robust performance, demonstrating its superiority in the N2SG task.

In summary, the main contributions of this work are as follows:

1) **Hallucination-aware refinement method (HAR)**: for refining LLM outputs that can eliminate inconsistencies caused by LLM hallucinations and improve the applicability of LLMs.

2) **A causal plot-graph construction method (CPC)**: employing a greedy cycle-breaking algorithm to extract causality-embedded plot graphs that do not contain cycles and low-strength event relationships.

3) **LLM-based N2SG framework R2**: which adopts HAR and CPC, and mimics the human screenplay rewriting process through Reader and Rewriter modules to achieve automated causality-plot-graph-based screenplay generation.

---

**Figure 2: Structure of Reader-Rewriter (R2).** The overall flow of R2 (a) consists of two modules: Reader and Rewriter. Two strategies are integrated: Hallucination-Aware Refinement (HAR) (b) and Causal Plot-graph Construction (CPC) (c), to efficiently utilize LLMs and understand plot lines. Arrows indicate data flow between different modules. Examples in the figure are for better illustration only.

---

## 2 Foundations of LLM-based Novel-to-Screenplay Generation

There are two challenges in LLM-based N2SG. First, due to hallucinations, LLM outputs may differ greatly from expected results. Thus, LLMs may extract and generate non-existent events and screenplays. Second, understanding novel plot lines is crucial for generating coherent and consistent screenplays. Plot graphs commonly used to describe plot lines should capture complex causal relationships between events. To address the first challenge, a **hallucination-aware refinement method (HAR)** is introduced, which can significantly mitigate the impact of LLM hallucinations (Section 2.1). For the second challenge, a **causal plot-graph construction method** is proposed to effectively construct plot graphs embedded with causalities (Section 2.2).

### 2.1 Hallucination-Aware Refinement

HAR prompts LLM to identify intrinsic inconsistencies caused by hallucinations, locate where the hallucinations occur in LLM outputs, and provide suggestions for refinement.

We denote the Large Language Model as $\mathcal{M}$. In round $t$, HAR (Figure 2 (b)) first identifies hallucination locations $loc_t$ where intrinsic inconsistencies occur in input $x_t$, and generates suggestions $sug_t$, describing how $\mathcal{M}$ should refine them. Then, it extracts a **hallucination-aware context** $c_t$ from the input and corresponding support texts based on hallucination locations, and inputs it to $\mathcal{M}$ to refine hallucinated parts $r_t$ in $x_t$. Next, $r_t$ is merged into $x_t$ as $x_{t+1}$ for the self-refinement of round $t+1$. This self-refinement process continues until the initial input data is fully processed and remains consistent, resulting in the refined output. Algorithm 1 shows the complete process of HAR.

---

**Algorithm 1 Hallucination-Aware Refinement**

**Input:**
* $x_0$: Initial input
* $s$: Support text
* $\mathcal{M}$: Large Language Model
* $\{p_{fb}, p_{refine}\}$: Prompts, where $p_{fb}$ is task-specific feedback prompt, $p_{refine}$ is input-output-feedback refinement quadruple example
* $stop(\cdot)$: Stop condition function
* $retrieve(\cdot)$: Context retrieve function

**Output:**
* $x_t$: Refined and consistent output

0:  **Initialize:**
    * $x_0$, $s$, $\mathcal{M}$, $\{p_{fb}, p_{refine}\}$, $stop(\cdot)$, $retrieve(\cdot)$

1:  **For each iteration $t \in \{0, 1, \dots\}$ do:**
2:     $loc_t, sug_t \leftarrow \mathcal{M}(p_{fb} \parallel x_t)$
    * ▷ **Locate the hallucinations and provide suggestions**
    * _This step is like a proofreader, letting the LLM find where it made mistakes in $x_t$ and provide suggestions for corrections._
3:     $c_t \leftarrow retrieve(loc_t, s)$
    * ▷ **Retrieve the hallucination-aware context**
    * _Based on the found error location $loc_t$, extract the relevant part from the original support text $s$ to form the context $c_t$._
4:     **If $stop(loc_t, sug_t, t)$ is True, then:**
5:        **break**
    * ▷ **Check the stop condition**
    * _If the stop condition is met (e.g., few errors remain or the iteration count has reached its limit), stop refining._
6:     **Else:**
7:        $r_t \leftarrow \mathcal{M}(p_{refine} \parallel c_t \parallel sug_t)$
    * ▷ **Get the refined part of input**
    * _The LLM uses the refinement prompt $p_{refine}$, relevant context $c_t$, and previously given suggestions $sug_t$ to generate a corrected part $r_t$._
8:        $x_{t+1} \leftarrow Merge(r_t \text{ into } x_t)$
    * ▷ **Update the input with the refined part**
    * _Integrate the corrected part $r_t$ back into the original input $x_t$, forming new input $x_{t+1}$ for the next round of refinement._
9:     **End if**
10: **End for**

11: **Return** refined and consistent output $x_t$

---

### 2.2 Causal Plot Graph Construction

#### The Causal Plot Graph

**Causal plot graphs** (Figure 3) embed causalities of events through graphs. "Causal" here means the graph is constructed based on **critical connections** between key events, rather than just their sequence in the novel. Specifically, this type of plot graph is designed as a **Directed Acyclic Graph (DAG)** to represent causal relationships (edges) between plot events (nodes).

Formally, a causal plot graph is a tuple $G = \langle E, D, W \rangle$.
* $E$ represents **events**, consisting of place and time, background, and description.
* $D$ describes **causal relationships** between events.
* $W$ represents the **strengths** of causal relationships, divided into three levels:
    * **High**: indicating direct and significant impact.
    * **Medium**: indicating partial or indirect impact.
    * **Low**: indicating minimal or slight impact.

---

**Figure 3: Demonstration of causal plot graphs and character profiles.** Plot lines are represented as **Directed Acyclic Graphs (DAGs)** composed of events and their causal relationships. Thicker arrows indicate stronger relationships.

---

#### The Greedy Cycle-breaking Algorithm

The plot graphs initially extracted by LLMs often contain **cycles** and **low-strength relationships** due to LLM hallucinations. Therefore, we propose a variant of the Prim algorithm (Prim, 1957) to remove these cycles and unimportant relationships. The algorithm is called the **greedy cycle-breaking algorithm**, which breaks cycles based on relationship strength and the degrees of event nodes.

Specifically, causal relationships are first sorted according to their weights $W$ from high to low, forming $D$. If two relationships have the same strength level, they are sorted based on the lower of the sum of degrees of their connected event endpoints, which prioritizes more important edges between more important nodes. We denote each directional relationship as $d(a, b)$, where $a$ and $b$ are the start and end points of $d$ respectively. The **forward reachable set** of endpoint $x$ is $S_x$. If the endpoint $b$ of $d \in D$ is already reachable from its start point $a$ through previously selected causal relationship edges, $d$ is skipped to avoid forming a cycle. Otherwise, it is added to the edge set $F$, and $S_x$ for all endpoints $x$ of edges in $F$ is updated to reflect new connections, ensuring that the set $F$ remains acyclic. As a result, the set $F$ forms the edge set of a Directed Acyclic Graph (DAG) that preserves the most important causal relationships while preventing cycles. Algorithm 2 provides the details of this algorithm.

---

**Algorithm 2 Greedy Cycle-breaking Algorithm for Causal Plot Graph Construction**

**Input:**
* $E$: Set of plot events
* $D$: Set of causal relations
* $W$: Set of relation strengths

**Output:**
* $F$: Causal relation edge set of the DAG

0: **Initialize:** $E, D, W$

1: **Sort $D$:**
    * Sort by $W$ from high to low (relationship strength priority)
    * For relations with same $W$, sort by sum of degrees of their connected event endpoints from low to high (edges connecting more important nodes priority)
    * _This step is like creating a priority list for all causal relationships. More important relationships (high strength, connecting more important events) are placed higher._

2: **For each edge $d$ in $D$ with endpoints $a, b$ (where $a, b \in E$) do:**
    * _Here $d(a,b)$ represents a causal relationship from event $a$ to event $b$._
3:    **If $a \in S_b$ is True, then:**
    * _Here $S_b$ refers to the set of all events that can be reached from event $b$ in the currently selected edge set $F$. If $a$ is already in this set, it means $a$ can be visited again from $b$, forming a cycle._
4:       **continue**
    * ▷ **Skip if $a$ is reachable from $b$**
    * _To avoid cycles, if adding this edge would form a cycle (i.e., $a$ is already reachable from $b$), skip this edge._
5:    **End if**
6:    **Add $d$ to $F$**
    * ▷ **Add to acyclic edge set**
    * _If it doesn't form a cycle, add the edge $d$ to the final acyclic edge set $F$._
7:    **Update $S_x$ for each endpoint $x$ of all edges in $F$**
    * ▷ **Update the forward reachable sets**
    * _After adding a new edge, update the sets of reachable events for each event node to be used in future cycle detection._
8: **End for**

9: **Return $F$ as the causal relation edge set of the DAG**

---

Now we discuss the R2 framework built based on the two proposed fundamental techniques.

## 3 Proposed Reader-Rewriter Framework

R2 (Figure 2 (a)) consists of two main components based on the human rewriting process: the **Reader** and the **Rewriter**. The former extracts plot events and character profiles and constructs causal plot graphs, while the latter adapts the novel into a screenplay using these graphs and profiles.

### 3.1 LLM-based Reader

The LLM-based Reader contains two sub-modules: **character event extraction** and **plot graph extraction**.

#### Character Event Extraction

The Reader first identifies plot events from the novel and extracts them in a chapter-by-chapter manner, as LLMs have limited input context windows. Here, LLMs extract event elements such as description, place, and time (Figure 3). This is achieved by prompting LLMs to generate structured outputs (Bi et al., 2024).

To better handle the long text of novels, a **sliding window-based** technique is first introduced in the event extraction process. By sliding through the entire novel with a chapter-sized window, this strategy ensures that extracted events maintain consistency between chapters. It is also applied to extract character profiles for each chapter (Figure 2). Then, HAR (Section 2.1) is employed to reduce inconsistencies in plot events and character profiles caused by LLM hallucinations. Here, LLM is recursively prompted to identify inconsistencies and refine them based on relevant chapter context, significantly reducing inconsistencies between events and profiles.

#### Plot Graph Extraction

The extracted events are further used to construct causal plot graphs through the proposed CPC method. Specifically, LLM is recursively prompted to identify new causal relationships based on relevant chapter contexts. After the graph is connected and no new relations are added to it, CPC is executed to eliminate cycles and low-weight edges from the graph, allowing the obtained causal graph to reflect the plot lines in the novel more effectively and accurately.

### 3.2 LLM-based Rewriter

The Rewriter is divided into two subsequent steps: the first is to create screenplay outlines for all scenes, and the second is to iteratively generate the screenplay for each scene. These two steps are packaged as two corresponding sub-modules: **outline generation** and **screenplay generation**.

#### Outline Generation

The screenplay adaptation outline can be constructed with the plot graph and character profiles (Figure 2), including story core elements, screenplay structure, and a writing plan containing storylines and goals for each scene. Three different methods are employed to traverse the plot graph: **Depth-First Traversal (DFT)**, **Breadth-First Traversal (BFT)**, and **Original Chapter Order (Chapter)**, corresponding to three different screenplay adaptation modes:
* Adapting screenplays based on the main story plot (depth-first).
* Adapting screenplays based on the chronological order of events (breadth-first).
* Adapting screenplays based on the original narrative order of the novel.

During outline generation, particularly when generating scene writing plans, misalignment of events and characters often occurs. Therefore, R2 performs HAR (Section 2.1) to obtain the initial screenplay adaptation outline. This process focuses on the alignment of key events and main characters and returns the final adaptation outline.

#### Screenplay Generation

Each scene can now be written according to the writing plan for each scene (Figure 2), which includes storylines, goals, place and time, and character experiences. LLM is prompted to generate each scene, provided with context relevant to the scene, including relevant chapters and previously generated scenes. HAR then verifies if the generated scene adheres to the storyline goals outlined in the writing plan. This approach ensures consistency between generated screenplay scenes and maintains alignment with the relevant plot lines of the novel.

## 4 Experiments

### 4.1 Experimental Setup

#### Dataset and Evaluation

To assess N2SG performance, we created a **novel-to-screenplay dataset** by manually cleaning novel and screenplay pairs collected from public sources. Novels were categorized as popular and unpopular based on their ratings and number of reviews. To ensure fairness, both types are included in the test set. The dataset will be open for future research on both trainable and train-free applications.

For balanced evaluation, the proposed R2 method uses five novels as the test set, with two from the popular category and three from the unpopular category, without involving training samples. To further minimize subjective bias caused by one-time reading of long texts, we selected a total of 15 novel excerpts for each human evaluator, with each excerpt limited to approximately 1000 tokens.

In the evaluation, we employed 15 human evaluators focusing on seven aspects, including: **Interesting**, **Coherent**, **Human-like**, **Diction and Grammar**, **Transition**, **Script Format Compliance**, and **Consistency**. We designed **pairwise comparisons** conducted through questionnaires. Their responses were then aggregated to calculate the **win rate** for each aspect (Formula 1). However, as human evaluators often show significant variation in their judgments, we also employed GPT-4o as the primary evaluator, giving judgments based on the same questionnaire. This can enhance objectivity and reduce potential bias in the results. Appendix A provides further details on the dataset and evaluation.

#### Task Setup

The R2 framework uses the best parameters obtained from analysis experiments (Section 4.4), setting the refinement rounds to 4 and the plot graph traversal method to BFT, for comparison with competitors. It employs GPT-4o-mini3 as the backbone model because it is cost-effective and fast for inference, as we aim to build an effective practical N2SG system. During inference, the generation temperature is set to 0 for reproducible and stable generation.

#### Comparison Methods

R2 is compared with ROLLING, Dramatron (Mirowski et al., 2023), and Wawa Writer4.
* **ROLLING** is a regular SG (Screenplay Generation) method that generates 4096 tokens at once via GPT-4o-mini, using R2-extracted plot events and all previously generated screenplay text as prompts. Once generation reaches 4096 tokens, it is added to the prompt to iteratively generate the screenplay.
* **Dramatron** is a method for generating screenplays from loglines. Here we input R2-extracted plot events for comparison.
* **Wawa Writer** is a commercial AI writing tool; we adopt its novel-to-screenplay functionality for performance comparison.

---

**Table 1: Comparison of R2 with three methods in win rates (%) with GPT-4o evaluation.**

| Method    | Interesting | Coherent | Human-like | Dict & Gram | Transition | Format | Consistency | Overall |
| :-------- | :---------- | :------- | :--------- | :---------- | :--------- | :----- | :---------- | :------ |
| ROLLING   | 19.2        | 34.6     | 26.9       | 15.4        | 30.8       | 15.4   | 23.1        | 24.4    |
| R2        | 80.8 (↑61.6) | 65.4 (↑30.8) | 73.1 (↑46.2) | 84.6 (↑69.2) | 69.2 (↑38.4) | 84.6 (↑69.2) | 76.9 (↑53.8) | 75.6 (↑51.3) |
| Dramatron | 39.3        | 46.4     | 35.7       | 42.9        | 28.6       | 35.7   | 50.0        | 39.3    |
| R2        | 60.7 (↑21.4) | 57.1 (↑10.7) | 64.3 (↑28.6) | 57.1 (↑14.2) | 71.4 (↑42.8) | 64.3 (↑28.6) | 57.1 (↑7.1) | 61.9 (↑22.6) |
| Wawa Writer | 10.7      | 32.1     | 25.0       | 10.7        | 25.0       | 35.7   | 21.4        | 22.0    |
| R2        | 89.3 (↑78.6) | 75.0 (↑42.9) | 75.0 (↑50.0) | 89.3 (↑78.6) | 75.0 (↑50.0) | 64.3 (↑28.6) | 78.6 (↑57.1) | 79.2 (↑57.1) |

---

**Table 2: Comparison of R2 with three methods in win rates (%) with human evaluation.**

| Method    | Interesting | Coherent | Human-like | Dict & Gram | Transition | Format | Consistency | Overall |
| :-------- | :---------- | :------- | :--------- | :---------- | :--------- | :----- | :---------- | :------ |
| ROLLING   | 35.9        | 40.1     | 36.6       | 19.0        | 35.2       | 35.2   | 45.1        | 34.5    |
| R2        | 71.8 (↑35.9) | 66.9 (↑26.8) | 73.9 (↑37.3) | 83.1 (↑64.1) | 70.4 (↑35.2) | 88.7 (↑53.5) | 77.5 (↑32.4) | 74.9 (↑40.4) |
| Dramatron | 40.0        | 47.8     | 48.9       | 61.1        | 47.8       | 48.9   | 66.7        | 50.6    |
| R2        | 74.4 (↑34.4) | 52.2 (↑4.4) | 54.4 (↑5.5) | 40.0 (↓21.1) | 56.7 (↑8.9) | 77.8 (↑28.9) | 55.6 (↓11.1) | 57.4 (↑6.9) |
| Wawa Writer | 43.8      | 40.0     | 47.5       | 45.0        | 43.8       | 47.5   | 45.0        | 44.4    |
| R2        | 62.5 (↑18.7) | 67.5 (↑27.5) | 62.5 (↑15.0) | 62.5 (↑17.5) | 62.5 (↑18.7) | 60.0 (↑12.5) | 50.0 (↑5.0) | 62.1 (↑17.7) |

---

### 4.2 Main Results

The quantitative comparison in Table 1 shows that R2 consistently outperforms competitors (overall, R2 improves by 51.3% over ROLLING, 22.6% over Dramatron, and 57.1% over Wawa Writer). Notably, R2 shows marked superiority in **Dict & Gram** (69.2% higher than ROLLING) and **Interesting** (78.6% higher than Wawa Writer). These results indicate that R2 can generate linguistically accurate and captivating screenplays with smooth transitions. Additionally, human evaluation results in Table 2 suggest that R2 outperforms its competitors overall in most aspects, especially in **Interesting** and **Transition**, indicating its ability to generate captivating and smooth screenplays. Only compared to Dramatron, R2 performs slightly worse in **Dict & Gram** and **Consistency**. One possible reason is that humans prefer the lengthy narratives generated by Dramatron.

**Qualitative analysis** of generated screenplays indicates that competing methods have the following drawbacks: Due to lack of iterative refinement and limited understanding of novel plots, ROLLING-generated screenplays typically underperform R2 in **Interesting**, **Transition**, and **Consistency**. Dramatron tends to generate drama-like screenplays, often producing lengthy dialogues, leading to poor performance in **Interesting**, **Format**, and **Transition**. As for Wawa Writer, it often generates screenplays with plot inconsistencies between scenes and **Diction and Grammar** issues, suggesting its backbone model may lack deep understanding of novels.

### 4.3 Ablation Study

This study evaluated the effectiveness of relevant techniques through GPT-4o evaluation (Table 3). First, removing HAR led to significant drops in **Dict & Gram** (38.4% loss) and **Consistency** (46.1% loss), indicating HAR is crucial for improving language quality and consistency. Second, removing CPC caused significant drops in **Interesting** (64.2% loss) and **Consistency** (71.4% loss), suggesting CPC is vital for generating captivating and consistent screenplays. Finally, excluding all context support led to drastic drops in **Transition** (66.6% loss) and **Consistency** (77.8% loss), indicating it is essential for improving plot transitions and consistency.

---

**Table 3: Ablation results of R2 in win rates with GPT-4o evaluation.**

| Method     | Interesting | Coherent | Human-like | Dict & Gram | Transition | Format | Consistency | Overall |
| :--------- | :---------- | :------- | :--------- | :---------- | :--------- | :----- | :---------- | :------ |
| R2         | 61.5        | 61.5     | 65.4       | 69.2        | 61.5       | 61.5   | 76.9        | 77.7    |
| w/o HAR    | 38.5 (↓23.0) | 38.5 (↓23.0) | 38.5 (↓26.9) | 30.8 (↓38.4) | 38.5 (↓23.0) | 46.2 (↓15.3) | 30.8 (↓46.1) | 44.7 (↓33.0) |
| R2         | 82.1        | 64.3     | 78.6       | 71.4        | 82.1       | 78.6   | 85.7        | 92.1    |
| w/o CPC    | 17.9 (↓64.2) | 85.7 (↑21.4) | 21.4 (↓57.2) | 28.6 (↓42.8) | 28.6 (↓53.5) | 64.3 (↓14.3) | 14.3 (↓71.4) | 44.3 (↓47.8) |
| R2         | 66.7        | 77.8     | 77.8       | 66.7        | 83.3       | 88.9   | 88.9        | 92.2    |
| w/o Context | 33.3 (↓33.4) | 50.0 (↓27.8) | 22.2 (↓55.6) | 33.3 (↓33.4) | 16.7 (↓66.6) | 11.1 (↓77.8) | 11.1 (↓77.8) | 33.3 (↓58.9) |

---

### 4.4 Impact of Different Factors

#### The Plot Graph Traversal Methods

Figure 4 (a) explores the impact of different plot graph traversal methods on screenplay adaptation. Here, win rate differences compared to the Chapter method are shown directly, as the Chapter method's performance lags behind other methods. Overall, **Breadth-First Traversal (BFT)** outperforms **Depth-First Traversal (DFT)** and shows significant advantages in **Coherent**, **Transition**, **Format**, and **Consistency**. This suggests BFT is highly effective in narrating stories with intricate plots, while DFT maintains strong performance in creating captivating stories. These results confirm that BFT provides the best balance of plot coherence and overall quality in screenplay adaptation.

---

**Figure 4: Impact of traversal methods and refinement rounds.**
(a) Analysis of different traversal methods
(b) Analysis of different refinement rounds

---

#### The Rounds of Refinements

Figure 4 (b) shows that as the number of refinement rounds increases, the number of suggestions increases in the first four rounds and then begins to decrease, indicating diminishing room for improvement. The suggestion adoption rate shows a decreasing trend, stabilizing at around 60% between rounds 2 and 4, with a significant drop in round 5. Additionally, time cost gradually increases with the number of refinement rounds. Therefore, four rounds of refinement achieves the best balance between refinement quality and efficiency.

### 4.5 Case Study

This study also conducted a case study to demonstrate the effectiveness of R2, where Figure 5 shows screenplay fragments generated by R2 and three methods. R2 outperforms other methods in creating vivid settings, expressive dialogue, and combining music with character development. For instance, R2 effectively enhances atmosphere through elegant scene settings and emphasizes Wolfgang's passion and ambition through emotional dialogue. These elements make the screenplay more immersive and emotionally driven than the simpler treatments in other scripts.

---

**Figure 5: Case study of different methods.**

---

## 5 Related Work

### Long-form Generation

Recently, many studies (Yang & Klein, 2021; Yang et al., 2022; Lei et al., 2024) have emerged focusing on long-form generation with LLMs, aiming to address challenges such as long-range dependency, content coherence, premise relevance, and factual consistency in long-text generation. Re3 (Yang et al., 2022) introduced a four-stage process (plan, draft, rewrite, and edit) for long story generation using recursive reprompting and revisions; DOC (Yang et al., 2023) focused on stories generating detailed outlines associated with characters and used controllers to ensure coherence and control. Compared to these multi-stage generation frameworks driven by story outlines, our approach uniquely leverages condensed causal plot graphs and character profiles to achieve automated and consistent generation from novel to screenplay.

Other works focus on building human-AI collaboration frameworks for screenplay generation (Zhu et al., 2022; Mirowski et al., 2023; Han et al., 2024; Zhu et al., 2023). Dramatron (Mirowski et al., 2023) proposed a hierarchical story generation framework that uses prompt chaining to guide LLMs in generating key screenplay elements, building a human-AI collaborative system for long-form screenplay generation. IBSEN (Han et al., 2024) allows users to interact with director and character agents to control the screenplay generation process. These studies emphasize collaborative, multi-agent approaches with human-LLM interaction. In contrast, our approach addresses N2SG by automatically generating long-form screenplays from novels, minimizing user involvement.

### LLM-Based Self-Refine Approach

Iterative self-refinement is a fundamental feature of human problem solving (Simon, 1962). LLMs can also improve their generation quality through self-refinement (Madaan et al., 2023; Saunders et al., 2022; Scheurer et al., 2024; Shinn et al., 2023; Peng et al., 2023; Madaan et al., 2023). LLM-Augmenter (Peng et al., 2023) uses a plug-and-play module to enhance LLM outputs by integrating external knowledge and automated feedback. Self-Refine (Madaan et al., 2023) demonstrates that LLMs can improve their outputs on various generation tasks through multi-turn prompting. In this paper, R2 leverages LLM-based self-refinement approaches to address challenges in causal plot graph extraction and long-text generation.

## 6 Conclusion

This paper proposes an LLM-based framework R2 for the **novel-to-screenplay generation task (N2SG)**. Two techniques are first proposed: **Hallucination-Aware Refinement (HAR)** for better exploring LLMs' capabilities by eliminating the impact of hallucinations; and **Causal Plot-graph Construction (CPC)** for better capturing causal event relationships. R2 adopts these techniques and mimics the human rewriting process, building a system composed of a **Reader** and a **Rewriter** for plot graph extraction and scene-by-scene screenplay generation. Extensive experiments demonstrate that R2 significantly outperforms competitors. The success of R2 establishes a benchmark for the N2SG task and demonstrates the potential of LLMs in adapting lengthy novels into coherent screenplays. Future work can explore integrating control modules or multi-agent frameworks into R2 to impose more stringent constraints and extend it to broader long-form story generation tasks to further develop the capabilities of our framework.

### Ethics Statement

Our research uses publicly available data and does not involve human subjects or sensitive data. We ensure that our work does not raise ethical concerns such as bias, unfairness, or privacy issues. There are no conflicts of interest or legal issues in this study, and all procedures conform to ethical standards.

### Reproducibility Statement

We ensure the reproducibility of our results by providing comprehensive descriptions of the models, dataset, and experiments. Source code and data processing steps are provided as supplementary materials.
