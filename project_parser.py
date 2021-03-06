from graphviz import Digraph

def to_dot(tree):
    g = Digraph(format='svg')
    g.node_attr['shape'] = 'box'
    g.node_attr['style'] = 'rounded'
    g.graph_attr['rankdir'] = 'BT'
    g.graph_attr['splines'] = 'ortho'
    g.edge_attr['arrowhead'] = 'none'
    #leafs = set()
    #nonleafs = set()
    def draw_subtree(tree):
        for node in tree:
            if type(node) == str:
                yield node
                last_node = node
                continue
            for node in draw_subtree(node):
                g.edge(node, last_node)
                #leafs.add(node)
                #nonleafs.add(last_node)
    with g.subgraph() as s:
        s.attr(rank='same')
        for node in draw_subtree(tree):
            s.node(node)
    #leafs -= nonleafs
    #with g.subgraph() as s:
    #    s.attr(rank='same')
    #    for leaf in leafs:
    #        s.node(leaf)
    return g


def parse_tree(arg):
    lines = arg.split('\n') if type(arg) == str else arg
    tree_stack = []
    indent_stack = [0]
    tree = []
    indent = 0
    for line in lines:
        line = line.rstrip()
        sline = line.lstrip()
        if not sline:
            continue
        indent = len(line) - len(sline)
        while indent < indent_stack[-1]:
            tree_stack[-1].append(tree)
            tree = tree_stack.pop()
            indent_stack.pop()
        if indent > indent_stack[-1]:
            tree_stack.append(tree)
            indent_stack.append(indent)
            tree = [sline]
        elif indent == indent_stack[-1]:
            tree.append(sline)
    while tree_stack:
        tree_stack[-1].append(tree)
        tree = tree_stack.pop()
    return tree

if __name__ == '__main__':
    import sys
    fname = sys.argv[1]
    if len(sys.argv) >= 3:
        subproject = sys.argv[2]
    else:
        subproject = None
    with open(fname) as f:
        code = f.read()
    tree = parse_tree(code)
    if subproject:
        it_tree = iter(tree)
        projects = []
        for node in it_tree:
            if node == subproject:
                try:
                    subtree = next(it_tree)
                except StopIteration:
                    tree = [node]
                else:
                    tree = [node, subtree]
                break
            elif type(node) == str:
                projects.append(node)
        else:
            print(f'No subproject {subproject}.', file=sys.stderr)
            print('Choose from:', *projects, file=sys.stderr)
            sys.exit(1)
    g = to_dot(tree)
    print(g.source)
