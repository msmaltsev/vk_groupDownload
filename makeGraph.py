# !usr/env/bin python3
# -*- coding: utf8 -*-

import os, json, random
import networkx as nx
import numpy
import matplotlib.pyplot as plt
import requests as req
from bs4 import BeautifulSoup as bs


def listPairs(l):
    res = []
    for i in l:
        for k in l:
            if i != k:
                if [k,i] not in res:
                    res.append([i,k])
    return res


def lenIntersection(li, li_):
    li, li_ = set(li), set(li_)
    return len(list(li & li_))



def randomCol():
    ind = []
    while len(ind) != 6:
        ind.append(random.randint(0,9))
    ind = [str(i) for i in ind]
    return '#' + ''.join(ind)


def folderColors(l, colors='rgbcmyk'):
    # print(l)
    res = {}
    cl = len(colors)
    # print(len(l),cl)
    if cl >= len(l):
        cl = len(l)
        # print('manycolors')
        res = {l[i]:colors[i] for i in range(0,cl)}
    else:
        # print('notmanycolors')
        while len(l) > cl:
            for i in range(cl):
                res[l[i]] = colors[i]
            l = l[cl:]
    # print(res)
    return res


def getGroupName(groupid):
    r = req.get('https://vk.com/public%s'%groupid)
    t = r.text
    soup = bs(t, "html.parser")
    ttl = soup.find('title')
    return ttl.text


def loadListFromFile(f = 'group_ids_list.txt'):
    a = open(f, encoding='utf8').read().split('\n')
    a = [i for i in a if i != '']
    return a


def collectFromList(list_of_lists):
    result = []
    for i in list_of_lists:
        if type(i) == list:
            result += collectFromList(i)
        else:
            result.append(i)
    return result


def plot_graph(graph, nodesizes, adjust_nodesize, cluster_map):

    clust = list(set(cluster_map.values()))
    colors = folderColors(clust)
    for i in colors:
        print(i, colors[i])

    pos=nx.spring_layout(graph, k=1)
    nodesize = [nodesizes[i]*0.005 for i in graph.nodes()]
    nodecolor = []
    for n in graph.nodes():
        nodecolor.append(colors[cluster_map[n]])

    edge_mean = numpy.mean([graph.edge[i[0]][i[1]]['weight'] for i in graph.edges()])
    edge_std_dev = numpy.std([graph.edge[i[0]][i[1]]['weight'] for i in graph.edges()])

    edgewidth = []

    for i in graph.edges():
        if graph.edge[i[0]][i[1]]['weight'] == 0:
            edgewidth.append(0)
        else:
            edgewidth.append(((graph.edge[i[0]][i[1]]['weight'] - edge_mean)/edge_std_dev*2))

    nx.draw_networkx_nodes(graph, pos,node_size=nodesize, node_color=nodecolor, alpha=0.6)
    nx.draw_networkx_edges(graph,pos,width=edgewidth,edge_color='#109474')
    nx.draw_networkx_labels(graph,pos,font_size=14,horizontalalignment='center', verticalalignment='top')
    plt.savefig(os.getcwd())
    plt.show()


def make_graph(matrix):
    graph = nx.Graph()
    nodes = list(matrix.keys())
    for n in range(len(nodes)):
        graph.add_node(nodes[n], size=5)
        rest = nodes[:n] + nodes[n+1:]
        for i in rest:
            oth = i
            we = lenIntersection(matrix[i],matrix[nodes[n]])
            graph.add_edge(nodes[n], oth, weight=we)

    return graph


def main(folders, groups_am):
    group_names = {}
    cluster_map = {}
    
    matrix = {}
    for f in folders:
        lists = os.listdir(os.getcwd()+'/folders/'+f)[:groups_am]
        for l in lists:
            lname = l[:-4]
            lname = '%s (%s)'%(getGroupName(lname), lname)
            cluster_map[lname] = f
            addr = os.getcwd() + '/folders/%s/%s'%(f, l)
            group_names[lname] = getGroupName(lname)
            ids = loadListFromFile(addr)
            matrix[lname] = ids

    m = matrix
    nodesizes = {i:len(collectFromList(m[i])) for i in m.keys()}
    graph = make_graph(m)
    plot_graph(graph, nodesizes, 5, cluster_map)


if __name__ == '__main__':
    f = os.listdir(os.getcwd()+'/folders')
    combs = listPairs(f)
    print(combs)
    for i in combs:
        main(i, 10)
    
