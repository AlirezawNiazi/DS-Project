import dataclasses
import matplotlib.pyplot as plt
import networkx as nx

# functions for hash
def right_rotate(value, shift):
    return (value >> shift) | (value << (32 - shift)) & 0xFFFFFFFF


def ch(x, y, z):
    return (x & y) ^ (~x & z)


def maj(x, y, z):
    return (x & y) ^ (x & z) ^ (y & z)


def sigma0(x):
    return right_rotate(x, 2) ^ right_rotate(x, 13) ^ right_rotate(x, 22)


def sigma1(x):
    return right_rotate(x, 6) ^ right_rotate(x, 11) ^ right_rotate(x, 25)


def gamma0(x):
    return right_rotate(x, 7) ^ right_rotate(x, 18) ^ (x >> 3)


def gamma1(x):
    return right_rotate(x, 17) ^ right_rotate(x, 19) ^ (x >> 10)


def hash(input):
    h = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]

    # طول پیام به بایت
    input_len = len(input)

    # افزودن 1 بیت '1' به پیام
    input += b'\x80'

    # تعداد صفرها برای تکمیل بلوک آخر
    zero_padding = (56 - (input_len + 1) % 64) % 64
    input += b'\x00' * zero_padding

    # افزودن طول پیام به پایان پیام
    input += (input_len * 8).to_bytes(8, 'big')

    # اجرای الگوریتم در بلوک‌های 512 بیتی
    for i in range(0, len(input), 64):
        chunk = input[i:i + 64]
        words = [int.from_bytes(chunk[j:j + 4], 'big') for j in range(0, 64, 4)]

        # تنظیمات اولیه
        a, b, c, d, e, f, g, h_temp = h

        # انجام عملیات در بلوک
        for t in range(64):
            if t in range(16):
                f_result = ch(e, f, g) + h_temp + sigma1(e) + words[t]
            else:
                f_result = gamma1(e) + maj(e, f, g) + h_temp + words[(t - 16) & 0x0F]

            temp1 = (f_result + d + sigma0(a) + gamma0(a)) & 0xFFFFFFFF
            temp2 = (a + b + sigma1(e)) & 0xFFFFFFFF

            h_temp = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF

        # به‌روزرسانی مقادیر نهایی
        h = [x + y & 0xFFFFFFFF for x, y in zip(h, [a, b, c, d, e, f, g, h_temp])]

    # تبدیل به رشته هش نهایی
    hash_result = ''.join(format(x, '08x') for x in h)

    return hash_result



@dataclasses.dataclass
class TreeNode:
    father: str = None  # father's hash
    children: list = dataclasses.field(default_factory=list)


people = {}


def add_person(parent_name, child_name):
    parent_node = find_person(parent_name)

    if parent_node is None:
        print(f"Error: Parent node '{parent_name}' not found.")
        return None

    parent_hash = hash(parent_name.encode('utf-8'))
    child_node = TreeNode(father=parent_hash)
    child_hash = hash(child_name.encode('utf-8'))

    people[child_hash] = child_node
    parent_node.children.append(child_hash)

    return child_node


def size_of_data(node):
    if node is None:
        return "sorry, this node is not found"
    if node.children == []:
        return 0

    count = len(node.children)
    for child in node.children:
        count += size_of_data(people.get(child))
    return count


def delete_person(name):
    hashed_key = hash(name.encode('utf-8'))

    if hashed_key not in people:
        print(f"sorry! '{name}' not found.")
        return
    node = people[hashed_key]
    if node.father is not None:  # check if it is not root
        father = people[node.father]
        father.children = [child for child in father.children if child != hashed_key]
    del people[hashed_key]


def find_person(name):
    hashed_name = hash(name.encode('utf-8'))
    if hashed_name not in people:
        return None
    return people.get(hashed_name)


def is_ancestor(name1, name2):
    hashed_name1 = hash(name1.encode('utf-8'))
    hashed_name2 = hash(name2.encode('utf-8'))

    if hashed_name1 not in people or hashed_name2 not in people:
        return False

    current = hashed_name2
    while current is not None:
        current_person = people.get(current)
        if current_person is None:
            # Current person is not in the people dictionary
            return False
        current = current_person.father
        if current == hashed_name1:
            return True

    return False


def are_siblings(name1, name2):
    hashed_name1 = hash(name1.encode('utf-8'))
    hashed_name2 = hash(name2.encode('utf-8'))

    if hashed_name1 not in people or hashed_name2 not in people:
        return False

    father1 = people[hashed_name1].father
    father2 = people[hashed_name2].father

    return father1 is not None and father1 == father2


def are_distantly_related(name1, name2):
    hashed_name1 = hash(name1.encode('utf-8'))
    hashed_name2 = hash(name2.encode('utf-8'))

    if hashed_name1 not in people or hashed_name2 not in people:
        return False

    ancestors1 = get_ancestors(hashed_name1)
    ancestors2 = get_ancestors(hashed_name2)
    common_ancestors = set(ancestors1).intersection(set(ancestors2))    #because intersection is not defined in list

    return len(common_ancestors) > 0 and hashed_name1 not in ancestors2 and hashed_name2 not in ancestors1


def find_common_ancestor(name1, name2):
    hashed_name1 = hash(name1.encode('utf-8'))
    hashed_name2 = hash(name2.encode('utf-8'))
    if hashed_name1 not in people or hashed_name2 not in people:
        return None
    ancestors1 = get_ancestors(hashed_name1)
    ancestors2 = get_ancestors(hashed_name2)
    common_ancestors = set(ancestors1).intersection(set(ancestors2))
    for ancestor in reversed(ancestors1):
        if ancestor in common_ancestors:
            return ancestor
    return "no common ancestor"


def get_ancestors(name):  # list of fathers
    ancestors = []
    current = name
    while current in people:
        current = people[current].father
        if current:
            ancestors.append(current)
    return ancestors


def find_farthest_descendant(name):
    hashed_name = hash(name.encode('utf-8'))
    if hashed_name not in people:
        print(f"Person '{name}' not found.")
        return 0
    return dfs_farthest_descendant(people[hashed_name], 0)


# we use dfs to find the furthest descendant , because it is located at the furthest nodes
def dfs_farthest_descendant(node, current_depth):
    if not node.children:
        return current_depth
    max_depth = current_depth
    for child in node.children:
        child_depth = dfs_farthest_descendant(people.get(child), current_depth + 1)
        max_depth = max(max_depth, child_depth)
    return max_depth


def find_farthest_relationship():
    max_distance = 0
    farthest_pair = (None, None)

    for person1 in people:
        for person2 in people:
            if person1 != person2:
                distance = calculate_distance(person1, person2)
                if distance == "no relationship":
                    continue
                if distance > max_distance:
                    max_distance = distance
                    farthest_pair = (person1, person2)
    return farthest_pair


def calculate_distance(name1, name2):
    ancestor = find_common_ancestor(name1, name2)
    if ancestor == "no common ancestor":
        return "no relationship"

    distance1 = 0
    distance2 = 0
    current1 = name1
    current2 = name2
    while current1 != ancestor:
        current1 = people[current1].father
        distance1 += 1

    while current2 != ancestor:
        current2 = people[current2].father
        distance2 += 1

    return distance2 + distance1


# visualization
def visualize_family_tree(root):
    if not root:
        print("The tree is empty")
        return

    G = nx.DiGraph()

    def add_nodes_and_edges(node_key):
        node = people.get(node_key)
        if node:
            G.add_node(node_key[:10])
            if node.father:
                G.add_edge(node.father[:10], node_key[:10])
            for child in node.children:
                add_nodes_and_edges(child)

    add_nodes_and_edges(root_hashed)
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)

    nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=10, font_weight="bold",
            arrows=True)
    plt.show()



    
# menu part
def menu():
    while True:
        activities = [
        "Add a new person to the family tree.",
        "Get the size of the family tree.",
        "Delete a person from the family tree.",
        "Find a person.",
        "Check if one person is an ancestor of another.",
        "Check if two people are siblings.",
        "Check if two people are distantly related.",
        "Find the common ancestor of two people.",
        "Find the farthest descendant of a person.",
        "Find the farthest relationship in the family tree.",
        "Visualize the family tree.",
        "Exit."]

        print('\n')
        for i, activity in enumerate(activities, start=1):
            print(f"{i}. {activity}")
        option =input("\nPlease choose an option (1-12):")
        if not option.isdigit():
          print("input is not digits")
          continue

        x = int(option)
        if x<1 or x>12:
           print("x is not a valid number")
           continue


        if x == 1:
            name1 = input("Enter parent name: ")
            name2 = input("Enter child name: ")
            add_person(name1, name2)

        elif x == 2:
            name = input("Enter name of node:")
            node = find_person(name)
            print(size_of_data(node))

        elif x == 3:
            name = input("Enter name: ")
            delete_person(name)

        elif x == 4:
            name = input("Enter name: ")
            print(find_person( name))
