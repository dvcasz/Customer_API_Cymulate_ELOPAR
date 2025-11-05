import os
import json
import requests
import re
from concurrent.futures import ThreadPoolExecutor
from scripts.auth import authenticate

class CollectCymulateData():

	def __init__(self, cliente, xtoken, data_inicio, data_fim, module):
		self.dataInicio = data_inicio  # YYYY-MM-DD
		self.dataFim = data_fim  # YYYY-MM-DD
		self.module = module  # immediate-threats, mail, browsing, waf, edr, dlp, hopper
		self.cliente = cliente
		self.payload = {}
		self.auth = authenticate(xtoken)
	
	# Função para criar diretórios para cada environment name
	def create_directories(self, env_name):
		os.makedirs(f"{self.cliente}/environments/{env_name}/{self.module}/report", exist_ok=True)
		os.makedirs(f"{self.cliente}/history/{self.module}", exist_ok=True)

	# # Função para limpar o conteúdo dos diretórios
	def clear_directories(self, env_name):
		report_dir = f"{self.cliente}/environments/{env_name}/{self.module}/report" 
		for folder in [report_dir]:
			for filename in os.listdir(folder):
				file_path = os.path.join(folder, filename)
				try:
					if os.path.isfile(file_path) or os.path.islink(file_path):
						os.unlink(file_path)
					elif os.path.isdir(file_path):
						os.rmdir(file_path)
				except Exception as e:
					print(f"Falha ao deletar {file_path}. Motivo: {e}")

	# Função para processar cada ID de assessment
	def process_assessment_id(self, assessment_id, env_name, env_id, env_name_pure):
		if self.module == "immediate-threats" or self.module == "hopper":
			url_report = f"https://api.app.cymulate.com/v1/{self.module}/history/technical/{assessment_id}"
		else:
			url_report = f"https://api.app.cymulate.com/v1/{self.module}/history/executive/{assessment_id}"

		headers_ = self.auth.create_headers()

		try:
			response_report = requests.request("GET", url_report, headers=headers_, data=self.payload)
			response_report.raise_for_status()
			json_report = response_report.json()

			# Adiciona os cabeçalhos JSON adicionais
			json_report.update({
				"environment_name": env_name_pure,
				"environment_id": env_id,
				"assessment_id": assessment_id,
				"data-range-start-search": self.dataInicio,
				"data-range-end-search": self.dataFim
			})
			
			arquivo = f"{self.cliente}/environments/{env_name}/{self.module}/report/{self.module}_report-{assessment_id}.json"
			with open(arquivo, 'w') as json_file:
				json.dump(json_report, json_file, indent=4)
		except requests.RequestException as e:
			print(f"Erro ao obter relatório para assessment {assessment_id} no environment {env_name_pure}: {e}")
		except json.JSONDecodeError as e:
			print(f"Erro ao decodificar resposta JSON para assessment {assessment_id} no environment {env_name_pure}: {e}")

	# Função para processar cada arquivo JSON
	def process_file(self, file_path, env_name, env_id, env_name_pure):
		if not os.path.exists(file_path):
			print(f"Arquivo {file_path} não encontrado.")
			return
			
		if os.path.getsize(file_path) == 0:
			print(f"O arquivo {file_path} está vazio e foi ignorado.")
			return
			
		with open(file_path, 'r', encoding='utf-8') as file:
			try:
				data = json.load(file)
				
				# Verifica se a estrutura esperada existe
				if 'data' not in data or 'attack' not in data['data']:
					print(f"Estrutura JSON inválida no arquivo {file_path}. Esperado: 'data.attack'")
					return
					
				assessments = data['data']['attack']
				
				if not assessments:
					print(f"Nenhum assessment encontrado no arquivo {file_path}")
					return

				# Usa ThreadPoolExecutor para processar os IDs de assessment em paralelo
				with ThreadPoolExecutor() as executor:
					list(executor.map(lambda ids: self.process_assessment_id(ids['ID'], env_name, env_id, env_name_pure), assessments))
			except json.JSONDecodeError as e:
				print(f"Erro ao decodificar o JSON no arquivo {file_path}: {e}")
				print(f"Detalhes do erro: linha {e.lineno}, coluna {e.colno}")
			except KeyError as e:
				print(f"Chave ausente no JSON do arquivo {file_path}: {e}")
			except Exception as e:
				print(f"Erro inesperado ao processar o arquivo {file_path}: {e}")

	# Função para unificar os arquivos JSON
	def unify_json_files(self, env_name, env_id, env_name_pure):
		if env_id == "default" or env_name == "Default Environment":
			return  # Pula o environment "default"

		report_dir = f"{self.cliente}/environments/{env_name}/{self.module}/report"
		unified_data = []

		for file_name in os.listdir(report_dir):
			if file_name.endswith('.json'):
				file_path = os.path.join(report_dir, file_name)
				with open(file_path, 'r') as file:
					data = json.load(file)
					unified_data.append(data)

		# Adiciona cabeçalhos JSON adicionais ao final do arquivo unificado apenas se unified_data estiver vazio
		if not unified_data:
			unified_data.append({
				"environment_name": env_name_pure,
				"environment_id": env_id,
				"data-range-start-search": self.dataInicio,
				"data-range-end-search": self.dataFim
			})

		unified_file_path = f"{self.cliente}/unified_reports/{self.module}/unified_report-{env_name}.json"
		os.makedirs(f"{self.cliente}/unified_reports/{self.module}", exist_ok=True)

		with open(unified_file_path, 'w') as unified_file:
			json.dump(unified_data, unified_file, indent=4)


	# Usa ThreadPoolExecutor para processar os arquivos em paralelo
	def process_env(self, env):
		env_id = env['id']
		env_name_pure = env['name']
		env_name = re.sub(r'[^\w\s-]', '', env['name']).replace(' ', '_')
		file_path = f"{self.cliente}/history/{self.module}/{self.module}_history-{env_name}.json"

		self.process_file(file_path, env_name, env_id, env_name_pure)


	def main(self):
		# URL para obter os environments
		url_environments = "https://api.app.cymulate.com/v1/environments"

		headers_ = self.auth.create_headers()

		response = requests.request("GET", url_environments, headers=headers_)
		response.raise_for_status()
		json_url_environments = response.json()

		# Cria diretórios, limpa o conteúdo e salva os arquivos de history para cada environment name
		for env in json_url_environments['data']:
			env_id = env['id']
			env_name_pure = env['name']

			# Remove caracteres especiais e substitui espaços por underscores
			env_name = re.sub(r'[^\w\s-]', '', env['name']).replace(' ', '_')  

			self.create_directories(env_name)
			self.clear_directories(env_name)

			url_history = f"https://api.app.cymulate.com/v1/{self.module}/history/get-ids?fromDate={self.dataInicio}&toDate={self.dataFim}&env={env_id}"

			try:
				response_history = requests.request("GET", url_history, headers=headers_, data=self.payload)
				response_history.raise_for_status()
				json_history = response_history.json()

				# Adiciona os cabeçalhos JSON adicionais
				json_history.update({
					"environment_name": env_name_pure,
					"environment_id": env_id,
					"data-range-start-search": self.dataInicio,
					"data-range-end-search": self.dataFim
				})

				arquivo_history = f"{self.cliente}/history/{self.module}/{self.module}_history-{env_name}.json"

				with open(arquivo_history, 'w', encoding='utf-8') as json_file:
					json.dump(json_history, json_file, indent=4)
			except requests.RequestException as e:
				print(f"Erro ao obter histórico para environment {env_name_pure}: {e}")
			except json.JSONDecodeError as e:
				print(f"Erro ao decodificar resposta da API para environment {env_name_pure}: {e}")
			except Exception as e:
				print(f"Erro inesperado ao processar environment {env_name_pure}: {e}")

		with ThreadPoolExecutor() as executor:
			executor.map(self.process_env, json_url_environments['data'])


		# Unifica todos os arquivos JSON salvos em cada {env_name}/report em um único arquivo .json por environment name
		for env in json_url_environments['data']:
			env_name = re.sub(r'[^\w\s-]', '', env['name']).replace(' ', '_')
			env_id = env['id']
			env_name_pure = env['name']
			self.unify_json_files(env_name, env_id, env_name_pure)

# if __name__ == '__main__':

# 	data_colector = CollectCymulateData()

# 	data_colector.main()
