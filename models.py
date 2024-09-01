import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import pool
import logging
from config import Config
from flask_login import UserMixin
from decimal import Decimal

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection pool
connection_pool = None

def init_db():
    global connection_pool
    try:
        connection_pool = pool.SimpleConnectionPool(
            1,  # Minimum number of connections
            20,  # Maximum number of connections
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            host=Config.DB_HOST,
            port=Config.DB_PORT
        )
        logger.info("Database connection pool initialized successfully")
    except (Exception, psycopg2.Error) as error:
        logger.error(f"Error while connecting to PostgreSQL: {error}")
        raise

def get_db_connection():
    global connection_pool
    return connection_pool.getconn()

def return_db_connection(conn):
    global connection_pool
    connection_pool.putconn(conn)

def execute_query(query, params=None):
    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = False  # Start a transaction
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, params)
            if query.lstrip().upper().startswith('SELECT'):
                result = cur.fetchall()
            elif 'RETURNING' in query.upper():
                result = cur.fetchone()
                result = dict(result) if result else None
            else:
                result = cur.rowcount
            conn.commit()  # Commit the transaction
            return result
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            if not conn.closed:
                conn.autocommit = True  # Reset autocommit
            return_db_connection(conn)

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

def get_user_by_username(username):
    query = "SELECT * FROM users WHERE username = %s"
    result = execute_query(query, (username,))
    if result:
        logger.info(f"User found: {username}")
        return result[0]
    else:
        logger.warning(f"User not found: {username}")
        return None

def get_user_by_id(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    result = execute_query(query, (user_id,))
    if result:
        user_data = result[0]
        return User(user_data['id'], user_data['username'])
    return None

def create_user(username, password):
    query = "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id"
    try:
        result = execute_query(query, (username, password))
        if result:
            logger.info(f"User created successfully: {username}, ID: {result['id']}")
            return result['id']
        else:
            logger.error(f"Failed to create user: {username}, no ID returned")
            return None
    except psycopg2.IntegrityError:
        logger.warning(f"Attempted to create duplicate user: {username}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating user {username}: {str(e)}")
        return None

def get_user_receipts(user_id):
    query = """
    SELECT r.*, c.name as category_name, v.name as vendor_name, pm.name as payment_method_name
    FROM receipts r
    LEFT JOIN categories c ON r.category_id = c.id
    LEFT JOIN vendors v ON r.vendor_id = v.id
    LEFT JOIN payment_methods pm ON r.payment_method_id = pm.id
    WHERE r.user_id = %s
    ORDER BY r.receipt_date DESC
    """
    return execute_query(query, (user_id,))

def get_receipt_by_id(receipt_id):
    query = """
    SELECT r.*, c.name as category_name, v.name as vendor_name, pm.name as payment_method_name
    FROM receipts r
    LEFT JOIN categories c ON r.category_id = c.id
    LEFT JOIN vendors v ON r.vendor_id = v.id
    LEFT JOIN payment_methods pm ON r.payment_method_id = pm.id
    WHERE r.id = %s
    """
    result = execute_query(query, (receipt_id,))
    return result[0] if result else None

def create_receipt(filename, description, amount, receipt_date, user_id, category_id, vendor_id, payment_method_id):
    query = """
    INSERT INTO receipts (filename, description, amount, receipt_date, user_id, category_id, vendor_id, payment_method_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    result = execute_query(query, (filename, description, amount, receipt_date, user_id, category_id, vendor_id, payment_method_id))
    return result['id'] if result else None

def update_receipt(receipt_id, description, amount, receipt_date, category_id, vendor_id, payment_method_id):
    query = """
    UPDATE receipts
    SET description = %s, amount = %s, receipt_date = %s, category_id = %s, vendor_id = %s, payment_method_id = %s
    WHERE id = %s
    """
    execute_query(query, (description, amount, receipt_date, category_id, vendor_id, payment_method_id, receipt_id))

def delete_receipt(receipt_id):
    queries = [
        "DELETE FROM receipt_tags WHERE receipt_id = %s",
        "DELETE FROM receipt_items WHERE receipt_id = %s",
        "DELETE FROM receipts WHERE id = %s"
    ]
    try:
        for query in queries:
            execute_query(query, (receipt_id,))
        return True
    except psycopg2.Error as e:
        logger.error(f"Error deleting receipt {receipt_id}: {e}")
        return False

def get_categories():
    query = "SELECT id, name, description FROM categories ORDER BY name"
    return execute_query(query)

def get_payment_methods():
    query = "SELECT id, name, description FROM payment_methods ORDER BY name"
    return execute_query(query)

def get_tags():
    query = "SELECT id, name FROM tags ORDER BY name"
    return execute_query(query)

def create_category(name, description):
    query = "INSERT INTO categories (name, description) VALUES (%s, %s) RETURNING id"
    result = execute_query(query, (name, description))
    return result['id'] if result else None

def create_payment_method(name, description):
    query = "INSERT INTO payment_methods (name, description) VALUES (%s, %s) RETURNING id"
    result = execute_query(query, (name, description))
    return result['id'] if result else None

def create_tag(name):
    query = "INSERT INTO tags (name) VALUES (%s) RETURNING id"
    result = execute_query(query, (name,))
    return result['id'] if result else None

def delete_category(category_id):
    query = "DELETE FROM categories WHERE id = %s"
    execute_query(query, (category_id,))

def delete_payment_method(payment_method_id):
    query = "DELETE FROM payment_methods WHERE id = %s"
    execute_query(query, (payment_method_id,))

def delete_tag(tag_id):
    query = "DELETE FROM tags WHERE id = %s"
    execute_query(query, (tag_id,))

def get_vendors():
    query = "SELECT id, name FROM vendors ORDER BY name"
    return execute_query(query)

def create_vendor(name, address=None, phone=None):
    query = """
    INSERT INTO vendors (name, address, phone)
    VALUES (%s, %s, %s)
    ON CONFLICT (name) DO NOTHING
    RETURNING id;
    """
    result = execute_query(query, (name, address, phone))
    return result['id'] if result else None

def delete_vendor(vendor_id):
    query = "DELETE FROM vendors WHERE id = %s"
    return execute_query(query, (vendor_id,))

def add_receipt_tags(receipt_id, tag_ids):
    query = "INSERT INTO receipt_tags (receipt_id, tag_id) VALUES (%s, %s)"
    for tag_id in tag_ids:
        execute_query(query, (receipt_id, tag_id))

def update_receipt_tags(receipt_id, tag_ids):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # First, remove all existing tags for this receipt
            cur.execute("DELETE FROM receipt_tags WHERE receipt_id = %s", (receipt_id,))
            # Then, add the new tags
            for tag_id in tag_ids:
                cur.execute("INSERT INTO receipt_tags (receipt_id, tag_id) VALUES (%s, %s)", (receipt_id, tag_id))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Error updating receipt tags: {e}")
        raise
    finally:
        return_db_connection(conn)

def get_receipt_tags(receipt_id):
    query = """
    SELECT t.id, t.name
    FROM tags t
    JOIN receipt_tags rt ON t.id = rt.tag_id
    WHERE rt.receipt_id = %s
    ORDER BY t.name
    """
    return execute_query(query, (receipt_id,))

def get_receipt_items(receipt_id):
    query = """
    SELECT id, item_name, quantity, price
    FROM receipt_items
    WHERE receipt_id = %s
    ORDER BY id
    """
    return execute_query(query, (receipt_id,))

def get_spending_by_category(user_id, start_date, end_date):
    query = """
    SELECT c.name as category, SUM(r.amount) as total
    FROM receipts r
    JOIN categories c ON r.category_id = c.id
    WHERE r.user_id = %s AND r.receipt_date BETWEEN %s AND %s
    GROUP BY c.name
    ORDER BY total DESC
    """
    return execute_query(query, (user_id, start_date, end_date))

def get_user_spending_by_category(user_id, start_date, end_date):
    query = """
    SELECT c.name as category, SUM(r.amount) as total
    FROM receipts r
    JOIN categories c ON r.category_id = c.id
    WHERE r.user_id = %s AND r.receipt_date BETWEEN %s AND %s
    GROUP BY c.name
    ORDER BY total DESC
    """
    return execute_query(query, (user_id, start_date, end_date))

def get_user_spending_by_vendor(user_id, start_date, end_date):
    query = """
    SELECT v.name as vendor, SUM(r.amount) as total
    FROM receipts r
    JOIN vendors v ON r.vendor_id = v.id
    WHERE r.user_id = %s AND r.receipt_date BETWEEN %s AND %s
    GROUP BY v.name
    ORDER BY total DESC
    """
    return execute_query(query, (user_id, start_date, end_date))

def get_total_spending(user_id):
    query = """
    SELECT SUM(amount) as total
    FROM receipts
    WHERE user_id = %s
    """
    result = execute_query(query, (user_id,))
    return result[0]['total'] if result and result[0]['total'] else Decimal('0.00')

def get_most_used_category(user_id):
    query = """
    SELECT c.name, COUNT(*) as usage_count
    FROM receipts r
    JOIN categories c ON r.category_id = c.id
    WHERE r.user_id = %s
    GROUP BY c.name
    ORDER BY usage_count DESC
    LIMIT 1
    """
    result = execute_query(query, (user_id,))
    return result[0] if result else None

# Initialize the database connection pool when this module is imported
init_db()