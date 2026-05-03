from flask import Flask, request, jsonify
from heap import PriorityQueue
from trie import Trie
from db import get_connection
from avl import insert, inorder

app = Flask(__name__)

pq = PriorityQueue()
trie = Trie()

# ✅ GLOBAL AVL ROOT
avl_root = None


# 🔁 REBUILD AVL TREE (IMPORTANT)
def rebuild_avl():
    global avl_root
    avl_root = None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, priority 
        FROM customers 
        WHERE status='waiting'
    """)

    rows = cursor.fetchall()

    for row in rows:
        avl_root = insert(avl_root, row[0], row[1], row[2])

    cursor.close()
    conn.close()


# 🔹 LOAD EXISTING DATA INTO TRIE + AVL
def load_existing_data():
    global avl_root

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, priority FROM customers")

    rows = cursor.fetchall()

    for row in rows:
        trie.insert(row[1])  # name
        avl_root = insert(avl_root, row[0], row[1], row[2])

    cursor.close()
    conn.close()


# 🔥 CALL FUNCTION
load_existing_data()


@app.route('/')
def home():
    return "Queue System Backend Running"


# 🔹 JOIN
@app.route('/join', methods=['GET'])
def join():
    global avl_root

    name = request.args.get('name')
    priority = request.args.get('priority')

    if not name or not priority:
        return jsonify({"error": "Missing name or priority"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    # INSERT CUSTOMER
    cursor.execute(
        "INSERT INTO customers (name, priority, status) VALUES (%s, %s, %s)",
        (name, priority, "waiting")
    )
    conn.commit()

    token = cursor.lastrowid

    # ✅ ADD TO AVL
    avl_root = insert(avl_root, token, name, priority)

    # COUNT AHEAD
    cursor.execute("""
        SELECT COUNT(*) FROM customers
        WHERE status = 'waiting'
        AND (
            CASE 
                WHEN priority = 'Emergency' THEN 1
                WHEN priority = 'VIP' THEN 2
                ELSE 3
            END
            <
            CASE 
                WHEN %s = 'Emergency' THEN 1
                WHEN %s = 'VIP' THEN 2
                ELSE 3
            END
            OR (priority = %s AND id < %s)
        )
    """, (priority, priority, priority, token))

    ahead = cursor.fetchone()[0]
    wait_time = ahead * 5

    cursor.close()
    conn.close()

    return jsonify({
        "token": token,
        "name": name,
        "priority": priority,
        "ahead": ahead,
        "wait_time": wait_time
    })


# 🔹 SERVE
@app.route('/serve', methods=['GET'])
def serve():
    global avl_root

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, priority 
        FROM customers
        WHERE status = 'waiting'
        ORDER BY 
            CASE 
                WHEN priority = 'Emergency' THEN 1
                WHEN priority = 'VIP' THEN 2
                ELSE 3
            END,
            id
        LIMIT 1
    """)

    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        return jsonify({"message": "Queue is empty"})

    token, name, priority = row

    cursor.execute(
        "UPDATE customers SET status='served' WHERE id=%s",
        (token,)
    )
    conn.commit()

    cursor.close()
    conn.close()

    # ✅ REBUILD AVL AFTER CHANGE
    rebuild_avl()

    return jsonify({
        "token": token,
        "name": name,
        "priority": priority,
        "message": f"Now serving Token {token} ({name})"
    })


# 🔹 CANCEL
@app.route('/cancel')
def cancel():
    global avl_root

    token = request.args.get('token')

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE customers SET status='cancelled' WHERE id=%s",
        (token,)
    )
    conn.commit()

    cursor.close()
    conn.close()

    # ✅ REBUILD AVL AFTER CHANGE
    rebuild_avl()

    return jsonify({"message": f"Token {token} cancelled"})


# 🔹 SEARCH (TOKEN + NAME)
@app.route('/search')
def search():
    prefix = request.args.get('prefix')

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name 
        FROM customers
        WHERE name LIKE %s
    """, (prefix + '%',))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "token": row[0],
            "name": row[1]
        })

    return jsonify({"results": results})


# 🔹 AVL FILTER (NEW FEATURE 🔥)
@app.route('/filter')
def filter_customers():
    result = []
    inorder(avl_root, result)
    return jsonify(result)


# 🔹 ADMIN VIEW
@app.route('/admin/customers')
def all_customers():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, priority, status FROM customers")
        rows = cursor.fetchall()

        data = []
        for row in rows:
            data.append({
                "id": row[0],
                "name": row[1],
                "priority": row[2],
                "status": row[3]
            })

        cursor.close()
        conn.close()

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)