class AVLNode:
    def __init__(self, token, name, priority):
        self.token = token
        self.name = name
        self.priority = priority
        self.left = None
        self.right = None
        self.height = 1


def get_height(node):
    return node.height if node else 0


def get_balance(node):
    return get_height(node.left) - get_height(node.right)


def right_rotate(y):
    x = y.left
    T2 = x.right

    x.right = y
    y.left = T2

    y.height = 1 + max(get_height(y.left), get_height(y.right))
    x.height = 1 + max(get_height(x.left), get_height(x.right))

    return x


def left_rotate(x):
    y = x.right
    T2 = y.left

    y.left = x
    x.right = T2

    x.height = 1 + max(get_height(x.left), get_height(x.right))
    y.height = 1 + max(get_height(y.left), get_height(y.right))

    return y


def insert(root, token, name, priority):
    if not root:
        return AVLNode(token, name, priority)

    if token < root.token:
        root.left = insert(root.left, token, name, priority)
    else:
        root.right = insert(root.right, token, name, priority)

    root.height = 1 + max(get_height(root.left), get_height(root.right))

    balance = get_balance(root)

    # Rotations
    if balance > 1 and token < root.left.token:
        return right_rotate(root)

    if balance < -1 and token > root.right.token:
        return left_rotate(root)

    if balance > 1 and token > root.left.token:
        root.left = left_rotate(root.left)
        return right_rotate(root)

    if balance < -1 and token < root.right.token:
        root.right = right_rotate(root.right)
        return left_rotate(root)

    return root


def inorder(root, result):
    if root:
        inorder(root.left, result)
        result.append({
            "token": root.token,
            "name": root.name,
            "priority": root.priority
        })
        inorder(root.right, result)