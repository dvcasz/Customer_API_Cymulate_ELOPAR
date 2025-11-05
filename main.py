import argparse
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from scripts.app import CollectCymulateData
from scripts.endpoints.EnvsAndHosts import CollectEnvData

def validate_date(date_string):
    """Valida se a data está no formato YYYY-MM-DD"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def load_environment():
    """Carrega as configurações do arquivo .env"""
    load_dotenv()
    
    xtoken = os.getenv('CYMULATE_XTOKEN')
    cliente = os.getenv('CLIENTE', 'ELOPAR')
    
    if not xtoken:
        raise ValueError("CYMULATE_XTOKEN não encontrado no arquivo .env")
    
    if xtoken == 'SUA_CHAVE_AQUI':
        raise ValueError("Por favor, configure a CYMULATE_XTOKEN no arquivo .env")
    
    return xtoken, cliente

def get_default_date_range():
    """Retorna o intervalo padrão de 6 meses (6 meses atrás até hoje)"""
    end_date = datetime.now()
    start_date = end_date - relativedelta(months=6)
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def parse_arguments():
    """Parse dos argumentos da linha de comando"""
    default_start, default_end = get_default_date_range()
    
    parser = argparse.ArgumentParser(
        description='Coleta dados dos relatórios Cymulate para ELOPAR',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
Exemplos de uso:
  # Usando intervalo padrão de 6 meses ({default_start} até {default_end})
  python main.py
  
  # Especificando datas customizadas
  python main.py --start-date 2024-01-01 --end-date 2024-01-31
  python main.py -s 2024-01-01 -e 2024-01-31
        '''
    )
    
    parser.add_argument(
        '--start-date', '-s',
        default=default_start,
        help=f'Data de início da coleta (formato: YYYY-MM-DD). Padrão: {default_start} (6 meses atrás)'
    )
    
    parser.add_argument(
        '--end-date', '-e',
        default=default_end,
        help=f'Data de fim da coleta (formato: YYYY-MM-DD). Padrão: {default_end} (hoje)'
    )
    
    return parser.parse_args()

def run():
    try:
        # Parse dos argumentos da linha de comando
        args = parse_arguments()
        
        # Validação das datas
        if not validate_date(args.start_date):
            print(f"Erro: Data de início '{args.start_date}' inválida. Use o formato YYYY-MM-DD")
            return 1
            
        if not validate_date(args.end_date):
            print(f"Erro: Data de fim '{args.end_date}' inválida. Use o formato YYYY-MM-DD")
            return 1
        
        # Carrega configurações do .env
        xtoken, cliente = load_environment()
        
        # Verifica se está usando intervalo padrão
        default_start, default_end = get_default_date_range()
        is_default_range = (args.start_date == default_start and args.end_date == default_end)
        
        print(f"Cliente: {cliente}")
        if is_default_range:
            print(f"Range de tempo: {args.start_date} até {args.end_date} (intervalo padrão de 6 meses)")
        else:
            print(f"Range de tempo: {args.start_date} até {args.end_date} (intervalo personalizado)")
        
        module_list = ["immediate-threats", "mail", "browsing", "waf", "edr", "dlp", "hopper"]

        for module in module_list:
            print(f"[...] Extração do relatório de {module} em andamento...")
            # Criar instância para cada módulo com todos os parâmetros necessários
            data_colector = CollectCymulateData(cliente, xtoken, args.start_date, args.end_date, module)
            data_colector.main()
            print(f"[!] Relatório de {module} extraído com sucesso!\n")

        # Obter lista dos environments e agentes
        print("[...] Coletando dados de environments e hosts...")
        env_data = CollectEnvData(cliente, xtoken)
        env_data.main()
        print("[!] Dados de environments e hosts coletados com sucesso!")

        print("\n[%] Os relatórios dos módulos foram salvos em ./unified_reports")
        print("[%] Os históricos dos assessments foram salvos em ./history")
        
        return 0
        
    except ValueError as e:
        print(f"Erro de configuração: {e}")
        return 1
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        return 1


if __name__ == '__main__':
    exit_code = run()
    exit(exit_code)
