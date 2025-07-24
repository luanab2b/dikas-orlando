import os
import dotenv
from sqlalchemy import create_engine, inspect
import urllib.parse
from dotenv import load_dotenv
from database.config import Base
from models import User, Message, ConversationContext, ContextMessage, ContextDocument
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')

password = urllib.parse.quote_plus(DB_PASSWORD)

DATABASE_URL = f"postgresql://{DB_USERNAME}:{password}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

engine = create_engine(DATABASE_URL)

def create_tables():
    print("Criando tabelas para contexto de conversas...")
    try:
        # Verificar quais tabelas já existem
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print(f"Tabelas existentes: {', '.join(existing_tables)}")
        
        # Criar apenas as tabelas que não existem
        # Para evitar erros com tabelas users e messages que já existem
        if 'users' not in existing_tables:
            Base.metadata.tables['users'].create(bind=engine)
            print("✓ Tabela 'users' criada")
            
        if 'messages' not in existing_tables:
            Base.metadata.tables['messages'].create(bind=engine)
            print("✓ Tabela 'messages' criada")
            
        if 'conversation_contexts' not in existing_tables:
            Base.metadata.tables['conversation_contexts'].create(bind=engine)
            print("✓ Tabela 'conversation_contexts' criada")
            
        if 'context_messages' not in existing_tables:
            Base.metadata.tables['context_messages'].create(bind=engine)
            print("✓ Tabela 'context_messages' criada")
            
        if 'context_documents' not in existing_tables:
            Base.metadata.tables['context_documents'].create(bind=engine)
            print("✓ Tabela 'context_documents' criada")
        
        # Verificar tabelas após a criação
        inspector = inspect(engine)
        current_tables = inspector.get_table_names()
        print(f"Tabelas atuais no banco: {', '.join(current_tables)}")
        
        print("✅ Processo de criação de tabelas concluído com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {str(e)}")
        return False

if __name__ == "__main__":
    create_tables()