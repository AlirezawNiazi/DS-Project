import dataclasses

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
