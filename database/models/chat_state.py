from datetime import datetime
import json

class ChatState:
    """
    Classe para gerenciar o estado da conversa com o usuário
    """
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
    
    def save_state(self, phone_number, state_data):
        """
        Salva o estado da conversa no banco de dados
        
        Args:
            phone_number (str): Número do telefone do usuário
            state_data (dict): Dados do estado da conversa
        
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            if not self.db_connection:
                print("⚠️ Simulando salvamento de estado no banco de dados")
                print(f"📱 Telefone: {phone_number}")
                print(f"🗂️ Estado: {json.dumps(state_data, indent=2)}")
                return True
                
            # Timestamp atual
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Converte o state_data para JSON
            state_json = json.dumps(state_data)
            
            # Verifica se já existe um registro para este telefone
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM chat_states WHERE phone = ?", (phone_number,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                # Atualiza o registro existente
                cursor.execute(
                    "UPDATE chat_states SET state = ?, updated_at = ? WHERE phone = ?",
                    (state_json, now, phone_number)
                )
            else:
                # Insere um novo registro
                cursor.execute(
                    "INSERT INTO chat_states (phone, state, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    (phone_number, state_json, now, now)
                )
            
            self.db_connection.commit()
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar estado: {e}")
            return False
    
    def get_state(self, phone_number):
        """
        Recupera o estado da conversa do banco de dados
        
        Args:
            phone_number (str): Número do telefone do usuário
            
        Returns:
            dict: Dados do estado da conversa ou None se não encontrado
        """
        try:
            if not self.db_connection:
                print(f"⚠️ Simulando recuperação de estado para telefone: {phone_number}")
                return {"awaiting_park_choice": True, "last_action": "list_parks"}
                
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT state FROM chat_states WHERE phone = ?", (phone_number,))
            result = cursor.fetchone()
            
            if result:
                state_json = result[0]
                return json.loads(state_json)
            else:
                return None
        except Exception as e:
            print(f"❌ Erro ao recuperar estado: {e}")
            return None
    
    def clear_state(self, phone_number):
        """
        Remove o estado da conversa do banco de dados
        
        Args:
            phone_number (str): Número do telefone do usuário
            
        Returns:
            bool: True se removeu com sucesso, False caso contrário
        """
        try:
            if not self.db_connection:
                print(f"⚠️ Simulando remoção de estado para telefone: {phone_number}")
                return True
                
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM chat_states WHERE phone = ?", (phone_number,))
            self.db_connection.commit()
            return True
        except Exception as e:
            print(f"❌ Erro ao remover estado: {e}")
            return False