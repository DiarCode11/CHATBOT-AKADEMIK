import gevent
from flask_socketio import SocketIO, emit
from flask import Flask, request, jsonify, session
from graph import build_graph, build_naive_rag
from datetime import datetime
import uuid
import json
import traceback
from ..models import EmbedderSetting, LLMSetting, RetrievedChunks, ChatProcess, ModifiedDataset, db

# Membuat instance SocketIO
socketio = SocketIO(cors_allowed_origins="*")

def init_socket_event(socketio):
    clients = []

    @socketio.on('connect', namespace='/')
    def handle_connect():
        clients.append(request.remote_addr)
        print(f"\n{len(clients)} Klien unik terhubung.")
        user_amount = len(clients)
        total_chat = ChatProcess.query.count()
        non_updated_dataset_total = ModifiedDataset.query.filter(ModifiedDataset.action != None).count()
        print(f"IP client terhubung: {str(clients)}")
        emit('user_connected', {
            'amount': user_amount, 
            'message': 'klien terhubung', 
            'total_chat': total_chat, 
        }, broadcast=True)

    @socketio.on('disconnect', namespace='/')
    def handle_disconnect():
        print("\nKlien terputus.")
        clients.remove(request.remote_addr)
        print("Jumlah client terhubung (unique): ", len(clients))
        print("IP client terhubung: ", str(clients))
        user_amount = len(clients)
        emit('user_disconnected', {'amount': user_amount, 'message': 'klien terputus'}, broadcast=True)

    @socketio.on('send_message')
    def handle_message(data):
        socket_id = request.sid
        print("Data terkirim: ", data)
        latest_embedder_setting = EmbedderSetting.query.order_by(EmbedderSetting.created_at.desc()).first()
        latest_llm_setting = LLMSetting.query.order_by(LLMSetting.created_at.desc()).first()

        embedder_settings = latest_embedder_setting.to_dict()
        llm_settings = latest_llm_setting.to_dict()

        vector_db_name = embedder_settings["vector_db_name"]
        embedder = embedder_settings["embedder"]

        llm_model = llm_settings["llm"]
        candidates_size = llm_settings["candidate_size"]

        print("Embedder: ", embedder)
        print("Vector DB: ", vector_db_name)
        print("LLM Model: ", llm_model)
        print("Candidate Size: ", candidates_size)

        # Menangkap teks yang dikirimkan oleh klien
        print(f"ID klien: {socket_id}")
        print(f"Pesan dari klien: {data['message']}")
        query = data['message']  # Mengambil teks pesan yang dikirimkan
        history = data['history']

        try:
            new_id = str(uuid.uuid4())

            if 'Corrective-RAG' in data.get('mode'):
                full_response = build_graph(
                    question = query, 
                    embedder_model = embedder, 
                    vector_db_name = vector_db_name,
                    llm_model = llm_model,
                    candidates_size = candidates_size,
                    history=history
                )

            if 'Naive-RAG' in data.get('mode'):
                print(data.get('mode'))
                full_response = build_naive_rag(
                    question=query,
                    embedder_model = embedder, 
                    vector_db_name = vector_db_name,
                    llm_model = llm_model,
                    candidates_size = candidates_size
                )
                
            chunk_data = full_response["chunks_data"]
            new_chat_process = ChatProcess(
                id = new_id,
                question = query,
                vector_from_query = json.dumps(full_response["vector_from_query"]),
                expansion_result = full_response["expanded_question"],
                corrective_prompt = full_response["corrective_prompt"],
                corrective_result = full_response["cleaned_context"],
                generator_prompt = full_response["generator_prompt"],
                final_result = full_response["final_answer"],
                created_at = datetime.now()
            )

            db.session.add(new_chat_process)
            db.session.commit()

            def clean_text(text : str):
                return text.encode("utf-8", "ignore").decode("utf-8")

            new_retrieved_chunks = [
                RetrievedChunks(
                    id=str(uuid.uuid4()),
                    chat_process_id = new_id,
                    chunk = clean_text(str(data['chunk'])),
                    vector = json.dumps(data['vector'].tolist()),
                    similiarity_score = data['score']
                ) for data in chunk_data
            ]
            
            db.session.bulk_save_objects(new_retrieved_chunks)
            db.session.commit()

            length_chars: int = 4
            for i in range(0, len(full_response["final_answer"]), length_chars):
                chunk = full_response["final_answer"][i:i+length_chars]
                emit('response', {'chunk': chunk}, room=socket_id)
                gevent.sleep(0.08)

        except Exception as e:
            traceback.print_exc()
            print('\n\nTerdapat error ', str(e))
            error_response = "Sepertinya ada masalah dengan internal server. Mohon tunggu beberapa saat untuk maintenance"
            
            length_chars: int = 4

            for i in range(0, len(error_response), length_chars):
                chunk = error_response[i:i+length_chars]
                emit('response', {'chunk': chunk}, room=socket_id)
                gevent.sleep(0.08)
