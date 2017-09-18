from node import Node
from collections import deque
import math
import parse

def ID3(examples, default):
    attributes = set(examples[0].keys())
    attributes.remove('Class')
    return build_tree(examples, attributes, default)

# reduce error pruning
def prune(node, examples):
    accuracy = test(node, examples)
    best = {'accuracy': 0, 'node': None}
    traverse(node, examples, best)
    if best['accuracy'] > accuracy:
        best['node'].label = MODE(examples)
        prune(node, examples)

def traverse(node, examples, best):
    if not node:
        return
    label = node.label
    node.label = MODE(examples)
    accuracy = test(node, examples)
    node.label = label
    if accuracy > best['accuracy']:
        best['accuracy'] = accuracy
        best['node'] = node
    for key in node.children:
        traverse(node.children[key], examples, best)

def test(node, examples):
    error = 0
    for example in examples:
        if evaluate(node, example) != example['Class']:
            error += 1
    return float(len(examples) - error) / len(examples)

def evaluate(node, example):
    while node.label == None:
        if example[node.attribute] not in node.children:
            node = node.children.values()[0]
        else:
            node = node.children[example[node.attribute]]
    return node.label

# handle missing value: just ignore it~~~
def build_tree(examples, attributes, default):
    if len(examples) == 0:
        leaf = Node()
        leaf.label = default
        return leaf
    if get_entropy(examples) == 0:
        leaf = Node()
        leaf.label = examples[0]['Class']
        return leaf
    if len(attributes) == 0:
        leaf = Node()
        leaf.label = MODE(examples)
        return leaf
    attributes = attributes.copy()
    best = choose_attribute(examples, attributes)
    values = set()
    for example in examples:
        #if example[best] != '?':
        values.add(example[best])
    attributes.remove(best)
    node = Node()
    node.examples = examples
    node.attribute = best
    default = MODE(examples)
    for value in values:
        node.children[value] = build_tree([example for example in examples if example[best] == value], attributes, default)
    return node

def choose_attribute(examples, attributes):
    best = None
    information_gain = 0
    for attribute in attributes:
        ig = get_information_gain(examples, attribute)
        if ig >= information_gain:
            information_gain = ig
            best = attribute
    return best

def get_entropy(examples):
    d = {}
    for example in examples:
        c = example['Class']
        if c not in d:
            d[c] = 1
        else:
            d[c] += 1
    entropy = 0
    for key in d:
        ratio = float(d[key]) / len(examples)
        entropy += -(ratio * math.log(ratio, 2))
    return entropy

def get_information_gain(examples, attribute):
    values = set()
    for example in examples:
        if example[attribute] != '?':
            values.add(example[attribute])
    s = 0
    for value in values:
        #if value != '?':
        l = [example for example in examples if example[attribute] == value]
        s += float(len(l) * get_entropy(l)) / len(examples)
    return get_entropy(examples) - s

def MODE(examples):
    d = {}
    for example in examples:
        c = example['Class']
        if c not in d:
            d[c] = 1
        else:
            d[c] += 1
    result = None
    count = 0
    for key in d:
        if d[key] > count:
            result = key
            count = d[key]
    return result


def postorderTraversal(root):
    traversal, stack = [], [(root, False)]
    while stack:
        node, visited = stack.pop()
        if node:
            if visited:
                # add to result if visited
                traversal.append(node)
            else:
                # post-order
                stack.append((node, True))
                for aNode in node.children.values():
                    stack.append((aNode, False))
    return traversal


data = parse.parse('house_votes_84.data')
tree = ID3(data, 'democrat')
traversal = postorderTraversal(tree)
for i in traversal:
    print i.attribute,i.label