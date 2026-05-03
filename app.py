from flask import Flask, request, jsonify
from heap import PriorityQueue
from trie import Trie
from db import get_connection

app = Flask(__name__)

pq = PriorityQueue()
trie = Trie()

def load_existing_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM customers")

    rows = cursor.fetchall()

    for row in rows:
        trie.insert(row[0])  # insert name into trie

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
    name = request.args.get('name')
    priority = request.args.get('priority')

    if not name or not priority:
        return jsonify({"error": "Missing name or priority"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    # Step 1: Insert new customer
    cursor.execute(
        "INSERT INTO customers (name, priority, status) VALUES (%s, %s, %s)",
        (name, priority, "waiting")
    )
    conn.commit()

    # Step 2: Get token (auto increment id)
    token = cursor.lastrowid

    # Step 3: Count people ahead (priority + FIFO logic)
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

            OR (
                priority = %s AND id < %s
            )
        )
    """, (priority, priority, priority, token))

    ahead = cursor.fetchone()[0]

    # Step 4: Estimate wait time (5 min per person)
    wait_time = ahead * 5

    cursor.close()
    conn.close()

    # Step 5: Return response
    return jsonify({
        "token": token,
        "name": name,
        "priority": priority,
        "ahead": ahead,
        "wait_time": wait_time
    })

# 🔹 VIEW QUEUE
@app.route('/queue')
def queue():
    return jsonify(pq.view_queue())


# 🔹 SERVE
@app.route('/serve', methods=['GET'])
def serve():
    conn = get_connection()
    cursor = conn.cursor()

    # Step 1: Get highest priority customer
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

    # Step 2: If queue empty
    if not row:
        cursor.close()
        conn.close()
        return jsonify({"message": "Queue is empty"})

    token, name, priority = row

    # Step 3: Mark as served
    cursor.execute(
        "UPDATE customers SET status='served' WHERE id=%s",
        (token,)
    )

    conn.commit()

    # Step 4: Close DB
    cursor.close()
    conn.close()

    # Step 5: Return response
    return jsonify({
        "token": token,
        "name": name,
        "priority": priority,
        "message": f"Now serving Token {token} ({name})"
    })

# 🔹 SEARCH (Trie)
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


# 🔹 ADMIN: VIEW ALL
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
    

@app.route('/cancel')
def cancel():
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

    return jsonify({"message": f"Token {token} cancelled"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)