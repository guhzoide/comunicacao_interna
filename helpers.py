import cx_Oracle
import psycopg2
import mysql.connector
from telebot import TeleBot
from bin.configs import DB_CONFIG, NOME_POSTGRES, USUARIO_POSTGRES, SENHA_POSTGRES, HOST_POSTGRES, PORT_POSTGRES, TOKEN_BOT_SOLICITA

class consultas():
    def enviarConfirmacao(texto, chatid_solicitante):
        bot = TeleBot(TOKEN_BOT_SOLICITA)
        bot.send_message(chatid_solicitante, texto)
        print(f"Confirmação enviada")
        return

    def dadosUsuario(matricula):
        connectionOracle = cx_Oracle.connect(**DB_CONFIG)
        cursor = connectionOracle.cursor()
        cursor.execute("SELECT US_NOME, US_LOJA FROM APLICACAO.USUARIO WHERE US_IDUSUARIO = :matricula", {'matricula': matricula})
        result = cursor.fetchone()
        
        if result:
            nome, loja = result
            nome = nome.strip()
            cursor.close()
            return nome, loja
        else:
            print("Usuário não encontrado.")
            cursor.close()
            return None, None
        connectionOracle.close()
        connectionPostgresql.close()

    def inserirDados(nome, matricula, loja, orcamento, data_iniciar, hora_iniciar, chat_id):
        connectionOracle = cx_Oracle.connect(**DB_CONFIG)
        connectionPostgresql = psycopg2.connect(
            user=USUARIO_POSTGRES,
            password=SENHA_POSTGRES,
            host=HOST_POSTGRES,
            port=PORT_POSTGRES,
            database=NOME_POSTGRES
        )
        cursor = connectionOracle.cursor()
        cursor.execute("SELECT DIRETOR FROM APLICACAO.CADHOST WHERE CHS_IDLOJA = :loja", {'loja': loja})
        result = cursor.fetchone()

        for line in result:
            diretor = line
        
        cursor.close()

        if diretor != None or diretor != '':
            cursor = connectionPostgresql.cursor()
            cursor.execute(f"INSERT INTO aprovacao_cadastrosolicitacao (nome_solicitante, diretor, orcamento, loja, status, matricula_solicitante, data_hora, chatid_solicitante, autorizado) VALUES ('{nome}', '{diretor}', '{orcamento}', '{loja}', {False}, '{matricula}', '{data_iniciar} {hora_iniciar}', '{chat_id}', 'P')")
            connectionPostgresql.commit()
            cursor.close()

            print(f"Dados inseridos com sucesso")
            return
        print(f"Informações em branco")
        connectionOracle.close()
        connectionPostgresql.close()

    def atualizarDadosAprovacao(status, orcamento, loja, chatid_solicitante, matricula_solicitante, autorizacao):
        connectionPostgresql = psycopg2.connect(
            user=USUARIO_POSTGRES,
            password=SENHA_POSTGRES,
            host=HOST_POSTGRES,
            port=PORT_POSTGRES,
            database=NOME_POSTGRES
        )
        try:
            cursor = connectionPostgresql.cursor()
            cursor.execute(f"UPDATE aprovacao_cadastrosolicitacao SET status={status}, autorizado='{autorizacao}' WHERE orcamento='{orcamento}' AND loja='{loja}' AND chatid_solicitante='{chatid_solicitante}' AND matricula_solicitante='{matricula_solicitante}'")
            connectionPostgresql.commit()
            cursor.close()
            texto = f"Orçamento {orcamento} aprovado!"
            return texto
        except Exception as error:
            texto = f"Erro ao atualizar:\n{str(error)}"
            print(texto)
            return texto
        connectionOracle.close()
        connectionPostgresql.close()

    def consultarPendente():
        connectionOracle = cx_Oracle.connect(**DB_CONFIG)
        connectionPostgresql = psycopg2.connect(
            user=USUARIO_POSTGRES,
            password=SENHA_POSTGRES,
            host=HOST_POSTGRES,
            port=PORT_POSTGRES,
            database=NOME_POSTGRES
        )
        cursor = connectionPostgresql.cursor()
        cursor.execute(f"SELECT orcamento, loja, chatid_solicitante, matricula_solicitante FROM aprovacao_cadastrosolicitacao WHERE status={False} AND autorizado='P'")
        result_status = cursor.fetchone()
        if result_status == None:
            orcamento=''
            loja=''
            chatid_solicitante=''
            matricula_solicitante=''
            texto = False
            return texto, orcamento, loja, chatid_solicitante, matricula_solicitante
        
        orcamento, loja, chatid_solicitante, matricula_solicitante = result_status
        cursor.close()

        cursor = connectionOracle.cursor()
        cursor.execute(f"SELECT ID_PLANO, VL_TOTAL FROM ORCAMENTO o WHERE ID_LOJA = {loja} AND PEDIDO = {orcamento}")
        result_dados_orcamento = cursor.fetchone()

        plano, valor_total = result_dados_orcamento
        texto = (f"O orçamento: {orcamento} da loja {loja} está no plano: {plano}\nValor total: {valor_total}, deseja confirmar a liberação?")

        cursor.close()
        connectionOracle.close()
        connectionPostgresql.close()
        return texto, orcamento, loja, chatid_solicitante, matricula_solicitante
