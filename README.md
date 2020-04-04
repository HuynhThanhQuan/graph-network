# **GRAPH NETWORK**

## **A. DEFINITION**
### **1. Graph Theory**
    Graph is defined as G = (V, E) where V is a set of all vertices and E is a set of all edges

---
*Vertex*

- ***V = {a, b, c, d}***

- Two vertices of the edge called ***endpoints***

- ***Isolated*** vertex has zero degree

- Two vertices are ***adjacent*** if they share a common edge

- ***Degree*** of vertex is the number of edges connected to the node (in/out-degree in directed graph)

- ***Pendant*** vertex has one degree 


---
*Edge*

- ***E = {(a, b), (b, c), (c, d)}***

- ***Loop*** is an edge formed by (a, a)

- ***Parallel*** edges has the same endpoints

- Edges are ***adjacent*** if they share a common vertex

- ***Pendant edge*** has an endpoint is pendant vertex

---

*Graph*

- ***Null graph*** in which both V and E are empty

- ***Empty graph*** in which E is empty

- ***Simple graph*** in which no parallel edges or loops

- ***Multigraph*** in which can contain multiple edges connect the same pair of endpoints

- Graph is ***trivial*** if has only one vertex


#### Graph variants
- CONNECTED-GRAPH
    - A graph that is enclosured by nodes and edges, all nodes must have at least 1 edge to the graph

- DISCONNECTED-GRAPH
    - A graph that can contains many sub-graphs or isolated nodes where subgraph can be a DISCONNECTED-GRAPH as well

- UNDIRECTED-GRAPH
    - A CONNECTED-GRAPH with a path from A to B can be traversed back from B to A

- DIRECTED-GRAPH
    - A CONNECTED-GRAPH with only has 1 path from A to B

- TREE
    - A DIRECTED-ACYCLIC-GRAPH but a child can have only one parent

- COMPLETED-GRAPH
    - A graph in which all vertices is linked together by an edge. Total edges is n*(n-1)/2


#### Graph traversal

1. ***Walk*** is a sequence of vertices and edges where vertices and edges can be repeated

    * *Opened* walk when starting vertex is not the same with ending vertex
    * *Closed* walk when starting vertex is the same with ending vertex

2. ***Trail*** is a walk but no repeated edges

3. ***Circuit*** is a closed trail (only repeated vertices)

4. ***Path*** is a trail but not repeated vertices (both vertices and edges not  repeated)

5. ***Cycle*** is a path but starting and ending vertex must be the same

#### Path

- EULER 

    - An Euler path is a path that uses **every edge exactly once**.

    - An Euler path starts and ends at **different vertices**.

- HAMILTONIAN

    - A simple path in a graph G that passes through **every vertex exactly once** is called a Hamiltonian path

<br>

### **2. Graph Representation**
- GRAPH
    - A superclass for all kind of graphs

- VERTEX 
    - Presentation of an entity or instance 

- EDGE
    - Presentation of a connection between nodes
    - Must have these attributes
        - source = node_id
        - target = node_id

### **3. Data Structure for Graph**
#### Input Format

Vertex


Edge
- Full Matrix
- Half Matrix (upper)
- List of pairs of endpoints


<br>

## **ALGORITHMS**



<br>

## **APPENDIX**
- DIRECTED-ACYCLIC-GRAPH
    - A DIRECTED-GRAPH without cycle. For a vertex A in DIRECTED-ACYCLIC-GRAPH, there is no directed edge starting and ending with vertex A

