# repositories/conversation_repository.py

from interfaces.repositories.conversation_repository_interface import IConversationRepository
from typing import List, Dict, Any, Optional
import json
import os
import datetime

class InMemoryConversationRepository(IConversationRepository):
    """
    Implementação em memória do repositório de conversas.
    """
    
    def __init__(self):
        self._conversations = {}  # session_id -> history
    
    def save_history(self, session_id: str, history: List[Dict[str, Any]]) -> bool:
        """
        Salva o histórico de conversas para uma sessão específica.
        
        Args:
            session_id: O ID da sessão
            history: O histórico de conversas
            
        Returns:
            True se o histórico foi salvo com sucesso, False caso contrário
        """
        try:
            # Cria uma cópia para evitar problemas de referência
            self._conversations[session_id] = history.copy()
            return True
        except Exception:
            return False
    
    def get_history(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Recupera o histórico de conversas para uma sessão específica.
        
        Args:
            session_id: O ID da sessão
            
        Returns:
            O histórico de conversas se encontrado, None caso contrário
        """
        history = self._conversations.get(session_id)
        # Retorna uma cópia para evitar problemas de referência
        return history.copy() if history else None
    
    def clear_history(self, session_id: str) -> bool:
        """
        Limpa o histórico de conversas para uma sessão específica.
        
        Args:
            session_id: O ID da sessão
            
        Returns:
            True se o histórico foi limpo com sucesso, False caso contrário
        """
        if session_id in self._conversations:
            del self._conversations[session_id]
            return True
        return False
    
    def list_sessions(self) -> List[str]:
        """
        Lista todas as sessões de conversa disponíveis.
        
        Returns:
            Uma lista com os IDs de todas as sessões disponíveis
        """
        return list(self._conversations.keys())


class FileSystemConversationRepository(IConversationRepository):
    """
    Implementação em sistema de arquivos do repositório de conversas.
    Salva as conversas em arquivos JSON no disco.
    """
    
    def __init__(self, storage_dir="./data/conversations"):
        # Cria o diretório de armazenamento se não existir
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def _get_file_path(self, session_id: str) -> str:
        """
        Obtém o caminho do arquivo para uma sessão específica.
        """
        # Sanitiza o session_id para garantir que seja um nome de arquivo válido
        safe_id = ''.join(c if c.isalnum() else '_' for c in session_id)
        return os.path.join(self.storage_dir, f"{safe_id}.json")
    
    def save_history(self, session_id: str, history: List[Dict[str, Any]]) -> bool:
        """
        Salva o histórico de conversas para uma sessão específica em um arquivo JSON.
        """
        try:
            file_path = self._get_file_path(session_id)
            
            # Adiciona timestamp à conversa para rastreamento
            metadata = {
                "session_id": session_id,
                "last_updated": datetime.datetime.now().isoformat(),
                "message_count": len(history)
            }
            
            data_to_save = {
                "metadata": metadata,
                "history": history
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            print(f"Erro ao salvar histórico: {str(e)}")
            return False
    
    def get_history(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Recupera o histórico de conversas para uma sessão específica de um arquivo JSON.
        """
        file_path = self._get_file_path(session_id)
        
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("history", [])
        except Exception as e:
            print(f"Erro ao ler histórico: {str(e)}")
            return None
    
    def clear_history(self, session_id: str) -> bool:
        """
        Remove o arquivo de histórico para uma sessão específica.
        """
        file_path = self._get_file_path(session_id)
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                print(f"Erro ao remover histórico: {str(e)}")
                return False
        return True  # Se o arquivo não existe, consideramos que a limpeza foi bem-sucedida
    
    def list_sessions(self) -> List[str]:
        """
        Lista todas as sessões de conversa disponíveis com base nos arquivos no diretório.
        """
        sessions = []
        
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith(".json"):
                    session_id = filename[:-5]  # Remove a extensão .json
                    sessions.append(session_id)
        except Exception as e:
            print(f"Erro ao listar sessões: {str(e)}")
        
        return sessions


class DatabaseConversationRepository(IConversationRepository):
    """
    Implementação em banco de dados do repositório de conversas.
    """
    
    def __init__(self, database_client):
        self.db = database_client
    
    def save_history(self, session_id: str, history: List[Dict[str, Any]]) -> bool:
        """
        Salva o histórico de conversas para uma sessão específica no banco de dados.
        
        Esta implementação é apenas um esboço e precisa ser adaptada para o seu ORM
        ou camada de acesso a dados específica.
        """
        try:
            with self.db.get_session() as session:
                # Limpa o histórico existente
                session.execute(
                    "DELETE FROM conversation_messages WHERE session_id = :session_id",
                    {"session_id": session_id}
                )
                
                # Insere as novas mensagens
                for i, message in enumerate(history):
                    session.execute(
                        """
                        INSERT INTO conversation_messages 
                        (session_id, sequence, role, content, created_at)
                        VALUES (:session_id, :sequence, :role, :content, :created_at)
                        """,
                        {
                            "session_id": session_id,
                            "sequence": i,
                            "role": message.get("role", "unknown"),
                            "content": json.dumps(message.get("content", "")),
                            "created_at": datetime.datetime.now()
                        }
                    )
                
                session.commit()
                return True
        except Exception as e:
            print(f"Erro ao salvar histórico no banco de dados: {str(e)}")
            return False
    
    def get_history(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Recupera o histórico de conversas para uma sessão específica do banco de dados.
        """
        try:
            with self.db.get_session() as session:
                result = session.execute(
                    """
                    SELECT role, content 
                    FROM conversation_messages 
                    WHERE session_id = :session_id 
                    ORDER BY sequence ASC
                    """,
                    {"session_id": session_id}
                )
                
                history = []
                for row in result:
                    content = row[1]
                    try:
                        # Tenta desserializar o conteúdo se for JSON
                        content = json.loads(content)
                    except:
                        pass
                        
                    history.append({
                        "role": row[0],
                        "content": content
                    })
                
                return history if history else None
        except Exception as e:
            print(f"Erro ao recuperar histórico do banco de dados: {str(e)}")
            return None
    
    def clear_history(self, session_id: str) -> bool:
        """
        Limpa o histórico de conversas para uma sessão específica no banco de dados.
        """
        try:
            with self.db.get_session() as session:
                session.execute(
                    "DELETE FROM conversation_messages WHERE session_id = :session_id",
                    {"session_id": session_id}
                )
                session.commit()
                return True
        except Exception as e:
            print(f"Erro ao limpar histórico no banco de dados: {str(e)}")
            return False
    
    def list_sessions(self) -> List[str]:
        """
        Lista todas as sessões de conversa disponíveis no banco de dados.
        """
        try:
            with self.db.get_session() as session:
                result = session.execute(
                    "SELECT DISTINCT session_id FROM conversation_messages"
                )
                return [row[0] for row in result]
        except Exception as e:
            print(f"Erro ao listar sessões no banco de dados: {str(e)}")
            return []