import sqlite3
import threading

class DatabaseHandler:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()
        self.criar_tabela()

    def criar_tabela(self):
        with self.lock:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS pendencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    departamento TEXT,
                    fornecedor TEXT,
                    pedido TEXT,
                    hora TEXT,
                    status TEXT,
                    motivo TEXT
                )
            ''')
            self.conn.commit()

    def inserir_pendencia(self, departamento, fornecedor, pedido, hora, status, motivo):
        with self.lock:
            self.cursor.execute('''
                INSERT INTO pendencias (departamento, fornecedor, pedido, hora, status, motivo)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (departamento, fornecedor, pedido, hora, status, motivo))
            self.conn.commit()

    def obter_pendencias(self):
        with self.lock:
            self.cursor.execute('SELECT * FROM pendencias')
            return self.cursor.fetchall()

    def obter_pendencia_por_id(self, pendencia_id):
        with self.lock:
            self.cursor.execute('SELECT * FROM pendencias WHERE id = ?', (pendencia_id,))
            return self.cursor.fetchone()

    def atualizar_status_pendencia(self, pendencia_id, novo_status):
        with self.lock:
            self.cursor.execute('UPDATE pendencias SET status = ? WHERE id = ?', (novo_status, pendencia_id))
            self.conn.commit()

    def remover_pendencia(self, pendencia_id):
        with self.lock:
            self.cursor.execute('DELETE FROM pendencias WHERE id = ?', (pendencia_id,))
            self.conn.commit()

    def limpar_pendencias(self):
        with self.lock:
            self.cursor.execute('DELETE FROM pendencias')
            self.conn.commit()

    def fechar_conexao(self):
        self.conn.close()
