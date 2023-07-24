import subprocess
import chardet
import re

from dataclasses     import dataclass
from tabulate        import tabulate
from dateutil.parser import parse
from datetime        import datetime

# ==================================================================
@dataclass
class Certificado:
    nome           : str
    cpf_cnpj       : str
    data_criacao   : datetime
    data_expiracao : datetime
    serie          : str
    hash           : str
    
    @property
    def dias_para_expirar(self):
        return (self.data_expiracao - datetime.now()).days
    
    # ----------------------------------------------------------------
    verbose_names = {   
        'nome'             : 'Nome ou Razão Social',
        'cpf_cnpj'         : 'CPF/CNPJ',
        'data_criacao'     : 'Data da Criação',
        'data_expiracao'   : 'Data de Expiração',
        'serie'            : 'Número de Série',
        'hash'             : 'Hash',
        'dias_para_expirar': "Dias Para Expirar"
    }
    
    # ----------------------------------------------------------------
    @classmethod
    def get_verbose_name(cls, field):
        return cls.verbose_names.get(field, field.capitalize())
    
    # ----------------------------------------------------------------
    def to_tabula(self, *args) -> tuple:
        result = []
        
        for h in args:
            result.append( getattr(self, h, None) )
        
        return result
    
    def __str__(self):
        return f'{self.nome}({self.cpf_cnpj}) - {self.hash}'

# ==================================================================
def format_cpf_cnpj(value:str) -> str:
    value = ''.join( re.findall(r'[\d]*', value) )
    
    if not value.isnumeric():
        return 'CPF/CNPJ inválido'
    
    match len(value):
        case 11:
            return f'{value[0:0+3]}.{value[3:3+3]}.{value[6:6+3]}-{value[9:11]}'
        case 14:
            return f'{value[0:0+2]}.{value[2:2+3]}.{value[5:5+3]}/{value[8:8+4]}-{value[12:14]}'
        case _:
            return 'Tamanho inválido'

def get_certificados() -> list[Certificado]:
    cmd             = ['Certutil', '-user', '-store', 'my']
    output_bytes    = subprocess.check_output(cmd)
    encoding        = chardet.detect(output_bytes).get('encoding')
    output_str      = output_bytes.decode(encoding)
    teste           = output_str.split('\n')
    indexes         = [i for i, item in enumerate(teste) if "===" in item]

    certificados    = []

    for i in range(len(indexes)):
        try:
            s_ind = indexes[i]
            e_ind = indexes[i+1]
        except IndexError:
            e_ind = -1
        
        cert = teste[s_ind:e_ind]

        # -----------------------------------------------------------
        numero_serie  = cert[1].split('Número de Série:')[-1].strip()
        hash_cert     = cert[7].split('Hash Cert(sha1):')[-1].strip()
        notbefore     = cert[3].split('NotBefore:')[-1].strip()
        notafter      = cert[4].split('NotAfter:')[-1].strip()
        requerente    = cert[5].split(',')[0].strip()
        nome,cpf_cnpj = requerente[15:].split(':')

        # -----------------------------------------------------------
        certificado = Certificado(
            nome           = nome,
            cpf_cnpj       = format_cpf_cnpj(cpf_cnpj),
            data_criacao   = parse(notbefore, dayfirst=True),
            data_expiracao = parse(notafter, dayfirst=True),
            serie          = numero_serie,
            hash           = hash_cert,
        )
        
        certificados.append(certificado)

    return certificados
        
def imprimir_resultado(certificados: list[Certificado]) -> None:
    fields      = [ 'nome', 'cpf_cnpj', 'data_criacao', 'dias_para_expirar' ]
    headers     = [Certificado.get_verbose_name(f) for f in fields]
    data        = [c.to_tabula(*fields) for c in certificados]
    data_sorted = sorted(data, key=lambda x: x[-1])
    
    table = tabulate(
        tabular_data = data_sorted,
        headers      = headers,
        tablefmt     = 'fancy_grid',
    )
    
    print(table)

# ================================================================== 
if __name__ == "__main__":
    certificados = get_certificados()
    imprimir_resultado(certificados)
