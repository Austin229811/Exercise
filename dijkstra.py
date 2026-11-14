class Graph:
    def __init__(self,nodes):
        self.nodes=nodes
        self.neighbor={node:{} for node in nodes}

    def add_edge(self,node1,node2,weight):
        self.neighbor[node1][node2]=weight

    def dijkstra(self,node_start,node_end):
        dic_dist={node:float('inf') for node in self.nodes if node!=node_start}
        dic_dist[node_start]=0
        dic_parent={}
        curnode=node_start
        solved=[]
        sgn=1
        while node_end!=curnode:
            for node in self.neighbor[curnode].keys():
                if dic_dist[curnode]+self.neighbor[curnode][node]<dic_dist[node]:
                    dic_dist[node]=dic_dist[curnode]+self.neighbor[curnode][node]
                    dic_parent[node]=curnode
            solved.append(curnode)
            if sorted(dic_dist.items(),key=lambda x:x[1])[len(solved)][1]==float('inf'):
                sgn=0
                break
            elif curnode!=node_end:
                curnode=sorted(dic_dist.items(),key=lambda x:x[1])[len(solved)][0]
        if sgn:
            path_re=[]
            node=node_end
            while node!=node_start:
                path_re.append(f'{dic_parent[node]}->{node}')
                node=dic_parent[node]
            path=path_re[::-1]
            return dic_dist[node_end],path
        else:
            return "doesn't exist"

nodes = ["A", "B", "C", "D", "E"]
graph = Graph(nodes)
graph.add_edge("A", "B", 6)
graph.add_edge("A", "D", 1)
graph.add_edge("D", "B", 2)
graph.add_edge("B", "C", 5)
graph.add_edge("D", "E", 1)
graph.add_edge("E", "C", 5)

def dij():
    n1,n2=input().split()
    print(graph.dijkstra(n1,n2))
    dij()
dij()
