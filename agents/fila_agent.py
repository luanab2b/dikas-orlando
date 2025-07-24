from interfaces.agents.agent_interface import AgentResponse, IAgent
from utils.orlando_parks import get_orlando_parks
from services.send_park_service import send_parks_list, send_message
# Removemos a importação do ChatState para evitar o erro
# from database.models.chat_state import ChatState 
import requests
import re
import json
from datetime import datetime, timezone

# Implementação simplificada do ChatState para modo simulação
class SimpleMemoryState:
    """Classe que simula o ChatState sem dependências de banco de dados"""
    _states = {}  # Armazena estados em memória
    
    def save_state(self, phone_number, state_data):
        """Salva estado em memória"""
        SimpleMemoryState._states[phone_number] = state_data
        print(f"⚠️ Estado simulado salvo para {phone_number}: {json.dumps(state_data, indent=2)}")
        return True
    
    def get_state(self, phone_number):
        """Recupera estado da memória"""
        state = SimpleMemoryState._states.get(phone_number, None)
        print(f"⚠️ Estado simulado recuperado para {phone_number}: {json.dumps(state, indent=2) if state else None}")
        return state
    
    def clear_state(self, phone_number):
        """Remove estado da memória"""
        if phone_number in SimpleMemoryState._states:
            del SimpleMemoryState._states[phone_number]
            print(f"⚠️ Estado simulado removido para {phone_number}")
        return True

class AgenteFilas(IAgent):
    """
    Agente especializado em consultar o tempo de filas dos parques de Orlando.
    """
    # --- Metadados e Configurações do Agente ---
    ID = "#5"
    NAME = "Agente_Filas"
    MODEL = "gpt-4o-mini"
    TEMPERATURE = 0.5
    MAX_TOKENS = 488
    
    def __init__(self, clients=None, repositories=None):
        self.clients = clients
        self.repositories = repositories
        # Usamos nosso SimpleMemoryState em vez do ChatState
        self.chat_state = SimpleMemoryState()
        
    # --- Implementação das Propriedades da Interface ---
    @property
    def id(self) -> str:
        return self.ID

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def instructions(self) -> str:
        return (
            "Você é um especialista em filas de parques de Orlando. "
            "Você NÃO fornece informações sobre filas de outros parques fora de Orlando. "
            "Ao receber uma solicitação, ofereça ao usuário uma lista de parques de Orlando para ele escolher. "
            "O usuário pode selecionar um parque pelo número (1, 2, 3, etc.). "
            "Após a escolha do parque, consulte os tempos de fila em tempo real usando a API do Queue-Times "
            "e envie essa informação para o usuário. "
            "Lembre-se de exibir o crédito obrigatório: Desenvolvido por Queue-Times.com."
        )
    
    def get_park_queues(self, park_id):
        """
        Consulta os tempos de fila de um parque específico de Orlando usando a API do Queue-Times
        
        Args:
            park_id (int): ID do parque na API Queue-Times
            
        Returns:
            tuple: (lands, rides) - Lands contém as áreas do parque e suas atrações,
                  rides contém todas as atrações em uma lista plana
        """
        url = f"https://queue-times.com/parks/{park_id}/queue_times.json"
        print(f"📊 Consultando filas de Orlando via API: {url}")
        
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            # Extrai as terras (lands) e seus passeios (rides)
            lands = data.get("lands", [])
            all_rides = data.get("rides", [])
            
            # Se há lands com rides, vamos processá-las
            processed_rides = []
            if lands:
                for land in lands:
                    land_rides = land.get("rides", [])
                    for ride in land_rides:
                        # Converte os campos para os nomes que nossa aplicação espera
                        processed_ride = {
                            "id": ride.get("id"),
                            "name": ride.get("name"),
                            "status": "open" if ride.get("is_open", False) else "closed",
                            "wait_time": ride.get("wait_time", 0),
                            "last_updated": ride.get("last_updated"),
                            "land": land.get("name")
                        }
                        processed_rides.append(processed_ride)
                        
            # Se há rides soltos (fora de lands), vamos adicioná-los
            if all_rides:
                for ride in all_rides:
                    processed_ride = {
                        "id": ride.get("id"),
                        "name": ride.get("name"),
                        "status": "open" if ride.get("is_open", False) else "closed",
                        "wait_time": ride.get("wait_time", 0),
                        "last_updated": ride.get("last_updated"),
                        "land": "Geral"
                    }
                    processed_rides.append(processed_ride)
                    
            print(f"✅ Filas de Orlando consultadas com sucesso! Encontradas {len(processed_rides)} atrações.")
            return lands, processed_rides
            
        except Exception as e:
            print(f"❌ Erro ao consultar filas de Orlando: {e}")
            return [], []
    
    def format_queue_message(self, park_name, lands, rides):
        """
        Formata a mensagem de filas de Orlando de modo amigável, agrupando por áreas
        
        Args:
            park_name (str): Nome do parque de Orlando
            lands (list): Lista de áreas do parque
            rides (list): Lista de atrações
            
        Returns:
            str: Mensagem formatada
        """
        # Obtém a data/hora atual em UTC
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        message = f"🎢 *Tempos de fila em {park_name} - Orlando* 🎢\n\n"
        
        # Se temos áreas definidas, vamos organizar por áreas
        if lands:
            # Criar um dicionário para organizar as atrações por área
            rides_by_land = {}
            for ride in rides:
                land_name = ride.get("land", "Outras Atrações")
                if land_name not in rides_by_land:
                    rides_by_land[land_name] = []
                rides_by_land[land_name].append(ride)
            
            # Para cada área, mostrar suas atrações ordenadas pelo tempo de espera
            for land_name, land_rides in rides_by_land.items():
                # Ordenar atrações por tempo de espera (do maior para o menor)
                sorted_rides = sorted(land_rides, key=lambda x: x.get("wait_time", 0), reverse=True)
                
                # Adicionar nome da área
                message += f"*📍 {land_name}*\n"
                
                # Adicionar atrações
                for ride in sorted_rides:
                    if ride.get("status") == "open":
                        wait = ride.get("wait_time", "?")
                        message += f"• {ride.get('name')}: *{wait} min*\n"
                    else:
                        message += f"• {ride.get('name')}: Fechada ❌\n"
                
                message += "\n"
        else:
            # Ordenar por tempo de espera (do maior para o menor)
            sorted_rides = sorted(rides, key=lambda x: x.get("wait_time", 0), reverse=True)
            
            # Adicionar todas as atrações sem agrupar por área
            for ride in sorted_rides:
                if ride.get("status") == "open":
                    wait = ride.get("wait_time", "?")
                    message += f"• {ride.get('name')}: *{wait} min*\n"
                else:
                    message += f"• {ride.get('name')}: Fechada ❌\n"
        
        message += f"\n⏰ *Atualizado em: {now}*"
        message += "\n📊 Desenvolvido por Queue-Times.com"
        return message
    
    def _identificar_numero_parque(self, mensagem):
        """
        Identifica se a mensagem contém apenas um número para seleção de parque de Orlando
        
        Args:
            mensagem (str): Mensagem do usuário
            
        Returns:
            int or None: Número do parque identificado ou None
        """
        # Procura um número único na mensagem
        match = re.search(r"^\s*(\d+)\s*$", mensagem)
        if match:
            try:
                numero = int(match.group(1))
                return numero
            except ValueError:
                return None
        return None
    
    async def execute(self, context: list[dict], phone: str, user: dict | None) -> AgentResponse:
        """
        Processa a mensagem do usuário e retorna uma resposta sobre filas de parques de Orlando.
        
        Args:
            context: Lista com o histórico da conversa
            phone: Número de telefone do usuário
            user: Informações do usuário (opcional)
            
        Returns:
            AgentResponse: Resposta estruturada do agente
        """
        # Busca a última mensagem do usuário no contexto
        last_user_message = ""
        for msg in reversed(context):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "").lower()
                break
        
        print(f"Última mensagem do usuário: '{last_user_message}'")
        
        # Recupera o estado atual da conversa
        state = self.chat_state.get_state(phone)
        if state is None:
            # Primeira interação, cria um estado vazio
            state = {"awaiting_park_choice": False}
        
        print(f"📱 Estado da conversa para {phone}: {state}")
        
        # Se a mensagem contiver referências a parques fora de Orlando, recusar
        fora_orlando = ["paris", "tokyo", "disneyland", "california", "europa", "asian", "shangai", "hong kong"]
        for termo in fora_orlando:
            if termo in last_user_message:
                return AgentResponse(
                    status="error",
                    message="Desculpe, sou especializado apenas em parques de Orlando. Não possuo informações sobre parques em outras localidades.",
                    tool_data={"non_orlando_request": termo}
                )
        
        # CASO 1: Usuário está aguardando seleção de parque e envia um número
        if state.get("awaiting_park_choice") and self._identificar_numero_parque(last_user_message) is not None:
            # Obtém a lista de parques
            parks, _ = get_orlando_parks()
            if not parks:
                return AgentResponse(
                    status="error",
                    message="Não foi possível obter a lista de parques de Orlando no momento. Por favor, tente novamente mais tarde.",
                    tool_data={}
                )
            
            numero_parque = self._identificar_numero_parque(last_user_message)
            
            # Verifica se o número está dentro do range de parques disponíveis
            if 1 <= numero_parque <= len(parks):
                # Acessa o parque pelo índice (índice 0 = parque 1)
                park = parks[numero_parque - 1]
                
                # Consulta as filas do parque usando o ID correto do Queue-Times
                print(f"🎯 Parque selecionado em Orlando: {park['nome']} (ID: {park['id']})")
                lands, rides = self.get_park_queues(park["id"])
                
                if not rides:
                    return AgentResponse(
                        status="error",
                        message=f"Não foi possível obter os tempos de fila para {park['nome']} em Orlando no momento.",
                        tool_data={"park_id": park["id"], "selected_by_number": numero_parque}
                    )
                
                # Formata a mensagem com as lands e rides
                queue_message = self.format_queue_message(park["nome"], lands, rides)
                
                # Envia via ZAPI
                status, _ = send_message(phone, queue_message)
                
                # Limpa o estado aguardando seleção
                state["awaiting_park_choice"] = False
                state["last_park_id"] = park["id"]
                state["last_park_name"] = park["nome"]
                self.chat_state.save_state(phone, state)
                
                return AgentResponse(
                    status="ok",
                    message=f"Informações sobre as filas em {park['nome']} (Orlando) foram enviadas para seu WhatsApp.",
                    tool_data={
                        "park_id": park["id"], 
                        "park_name": park["nome"], 
                        "queue_count": len(rides), 
                        "selected_by_number": numero_parque
                    }
                )
            else:
                # Número fora do range válido
                send_parks_list(phone)
                return AgentResponse(
                    status="error",
                    message=f"Número {numero_parque} inválido. Por favor, escolha um número entre 1 e {len(parks)} para ver as filas dos parques de Orlando.",
                    tool_data={"invalid_park_number": numero_parque}
                )
        
        # CASO 2: Usuário pede a lista de parques
        elif "parques" in last_user_message or "lista" in last_user_message or "filas" in last_user_message:
            status, mensagem = send_parks_list(phone)
            
            # Atualiza o estado para aguardar seleção de parque
            state["awaiting_park_choice"] = True
            state["last_action"] = "list_parks"
            self.chat_state.save_state(phone, state)
            
            return AgentResponse(
                status="ok",
                message="Lista de parques de Orlando enviada para seu WhatsApp. Digite apenas o número do parque para ver as filas em tempo real.",
                tool_data={"sent_via_zapi": True}
            )
        
        # CASO 3: Verificar se o usuário está selecionando um parque pelo número sem contexto prévio
        elif self._identificar_numero_parque(last_user_message) is not None:
            # Enviamos a lista de parques primeiro
            status, mensagem = send_parks_list(phone)
            
            # Atualiza o estado para aguardar seleção de parque
            state["awaiting_park_choice"] = True
            state["last_action"] = "list_parks"
            state["pending_number"] = self._identificar_numero_parque(last_user_message)
            self.chat_state.save_state(phone, state)
            
            return AgentResponse(
                status="ok",
                message="Para consultar as filas, primeiro enviei a lista de parques disponíveis em Orlando. Após verificar a lista, por favor, confirme sua escolha enviando o número novamente.",
                tool_data={"sent_parks_list": True, "detected_number": self._identificar_numero_parque(last_user_message)}
            )
        
        # CASO 4: Usuário menciona nome de parque
        else:
            parks, _ = get_orlando_parks()
            if not parks:
                return AgentResponse(
                    status="error",
                    message="Não foi possível obter a lista de parques de Orlando no momento. Por favor, tente novamente mais tarde.",
                    tool_data={}
                )
                
            # Verifica se o usuário está mencionando um parque específico pelo nome
            for park in parks:
                if park["nome"].lower() in last_user_message.lower():
                    try:
                        # Consulta as filas do parque
                        lands, rides = self.get_park_queues(park["id"])
                        
                        if not rides:
                            return AgentResponse(
                                status="error",
                                message=f"Não foi possível obter os tempos de fila para {park['nome']} em Orlando no momento.",
                                tool_data={"park_id": park["id"]}
                            )
                        
                        # Formata a mensagem
                        queue_message = self.format_queue_message(park["nome"], lands, rides)
                        
                        # Envia via ZAPI
                        status, _ = send_message(phone, queue_message)
                        
                        # Atualiza o estado
                        state["awaiting_park_choice"] = False
                        state["last_park_id"] = park["id"]
                        state["last_park_name"] = park["nome"]
                        self.chat_state.save_state(phone, state)
                        
                        return AgentResponse(
                            status="ok",
                            message=f"Informações sobre as filas em {park['nome']} (Orlando) foram enviadas para seu WhatsApp.",
                            tool_data={"park_id": park["id"], "park_name": park["nome"], "queue_count": len(rides)}
                        )
                    except Exception as e:
                        print(f"Erro ao processar parque {park['nome']} em Orlando: {e}")
                        return AgentResponse(
                            status="error",
                            message=f"Ocorreu um erro ao processar os dados de {park['nome']} em Orlando. Por favor, tente novamente.",
                            tool_data={"error": str(e), "park_id": park["id"]}
                        )
            
            # Nenhuma das opções acima, enviar a lista de parques
            status, mensagem = send_parks_list(phone)
            
            # Atualiza o estado para aguardar seleção de parque
            state["awaiting_park_choice"] = True
            state["last_action"] = "list_parks"
            self.chat_state.save_state(phone, state)
            
            return AgentResponse(
                status="ok",
                message="Para ver os tempos de fila dos parques de Orlando, digite apenas o número do parque conforme a lista enviada ao seu WhatsApp.",
                tool_data={"parks_count": len(parks)}
            )