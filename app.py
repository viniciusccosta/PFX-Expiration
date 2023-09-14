import subprocess
import chardet
import re

import tkinter       as tk

from tkinter         import ttk
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
    def get_values_by_fieldname(self, *args) -> tuple:
        result = []
        
        for h in args:
            value = getattr(self, h, None)
            if isinstance(value, datetime):
                value = value.strftime("%d/%m/%Y %H:%M:%S")
            result.append(value)
        
        return result
    
    def __str__(self):
        return f'{self.nome}({self.cpf_cnpj}) - {self.hash}'

# ==================================================================
class App():
    def __init__(self, certificados, *args, **kwargs):
        self.root = tk.Tk()
        self.root.title('PFX Expiration')
        self.root.iconbitmap("icon.ico")
        self._center_window()
        
        # -------------------------------------------------------------------------
        fields      = [ 'hash', 'nome', 'cpf_cnpj', 'data_criacao', 'dias_para_expirar' ]
        data        = [c.get_values_by_fieldname(*fields) for c in certificados]
        data_sorted = sorted(data, key=lambda x: x[-1])
        
        # -------------------------------------------------------------------------
        frame = ttk.Frame(self.root)
        frame.pack(expand=True, fill='both')
        
        scroll_y = ttk.Scrollbar(frame)
        scroll_y.pack(side=tk.RIGHT, fill='y')
        
        scroll_x = ttk.Scrollbar(frame, orient='horizontal')
        scroll_x.pack(side=tk.BOTTOM, fill='x')
        
        self.table = ttk.Treeview(frame, yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.table.pack(expand=True, fill='both')
        
        scroll_y.config(command=self.table.yview)
        scroll_x.config(command=self.table.xview)
        
        # -------------------------------------------------------------------------
        self.table['columns'] = fields
        
        self.table.heading("#0",text="", anchor=tk.CENTER)
        self.table.column('#0', width=0, stretch=tk.NO)
        
        for f in fields:
            self.table.heading(f, text=Certificado.get_verbose_name(f), anchor=tk.CENTER)
            self.table.column(f, anchor=tk.CENTER, stretch=tk.YES)

        for i,d in enumerate(data_sorted):
            self.table.insert(
                parent  = "", 
                iid     = i,
                index   = "end", 
                text    = "", 
                values  = d
        )        
    
    def _center_window(self):       
        width         = 1000
        height        = 500
        
        screen_width  = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x_cordinate   = int((screen_width / 2) - (width / 2))
        y_cordinate   = int((screen_height / 2) - (height / 2))

        self.root.geometry("{}x{}+{}+{}".format(width, height, x_cordinate, y_cordinate))
        
    def run(self, *args, **kwargs):
        self.root.mainloop()

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
        try:
            numero_serie  = cert[1].split('Número de Série:')[-1].strip()
            hash_cert     = cert[7].split('Hash Cert(sha1):')[-1].strip()
            notbefore     = cert[3].split('NotBefore:')[-1].strip()
            notafter      = cert[4].split('NotAfter:')[-1].strip()
            requerente    = cert[5].split(',')[0].strip()
            nome,cpf_cnpj = requerente[15:].split(':')
        except Exception as e:
            print(i, cert, e)
            continue

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
    data        = [c.get_values_by_fieldname(*fields) for c in certificados]
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
    # imprimir_resultado(certificados)
    
    app = App(certificados)
    app.run()
