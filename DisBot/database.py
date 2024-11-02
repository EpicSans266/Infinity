import sqlite3

# Инициализация базы данных и создание таблицы, если она еще не существует
def initialize_db():
    conn = sqlite3.connect('templates.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Templates (
                        template_id INTEGER PRIMARY KEY,
                        template_name VARCHAR(100) NOT NULL,
                        owner_id INT(100) NOT NULL,
                        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (template_id) REFERENCES Categories (server_id),
                        FOREIGN KEY (template_id) REFERENCES Channels (server_id)
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Categories ( 
                        category_id INTEGER PRIMARY KEY,
                        server_id INTEGER,
                        category_name VARCHAR(100) NOT NULL,
                        position INTEGER,
                        FOREIGN KEY (category_id) REFERENCES Channels (category_id)
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Channels (
                        channel_id INTEGER PRIMARY KEY,
                        server_id INTEGER,
                        category_id INTEGER,
                        channel_name VARCHAR(100) NOT NULL,
                        type VARCHAR(50),
                        position INTEGER
                    )''')
    conn.commit()
    conn.close()

def save_template(template_name, guild, owner_id):
    try:
        conn = sqlite3.connect('templates.db')
        cursor = conn.cursor()

        # Сохраняем шаблон с owner_id (дата добавится автоматически)
        cursor.execute("INSERT INTO Templates (template_name, owner_id) VALUES (?, ?)", 
                       (template_name, owner_id))
        template_id = cursor.lastrowid
        pos = 0
        
        for category in guild.categories:
            cursor.execute(
                "INSERT INTO Categories (server_id, category_name, position) VALUES (?, ?, ?)",
                (template_id, category.name, pos)
            )
            category_id = cursor.lastrowid
            pos += 1

            for channel in category.channels:
                cursor.execute(
                    "INSERT INTO Channels (server_id, category_id, channel_name, type, position) VALUES (?, ?, ?, ?, ?)",
                    (template_id, category_id, channel.name, str(channel.type), channel.position)
                )

        conn.commit()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        conn.close()

def load_template(template_id):
    conn = sqlite3.connect('templates.db')
    cursor = conn.cursor()

    # Получаем категории и каналы по template_id
    cursor.execute("SELECT * FROM Categories WHERE server_id = ?", (template_id,))
    categories = cursor.fetchall()

    cursor.execute("SELECT * FROM Channels WHERE server_id = ?", (template_id,))
    channels = cursor.fetchall()

    conn.close()
    return categories, channels

def list_templates(template_name, owner_id):
    conn = sqlite3.connect('templates.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Templates WHERE template_name = ? AND owner_id = ?", (template_name, owner_id))
    templates = cursor.fetchall()

    conn.close()

    return [{'template_id': t[0], 'template_name': t[1], 'data': t[3]} for t in templates]