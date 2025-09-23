import re
import json
import pdfplumber
from dataclasses import dataclass
from typing import Optional


@dataclass
class Vendedor:
    nome: Optional[str]
    renavam: Optional[str]
    cpf_cnpj: Optional[str]
    email: Optional[str]


@dataclass
class Veiculo:
    placa: Optional[str]
    municipio: Optional[str]
    uf: Optional[str]
    ano_fabricacao: Optional[str]
    ano_modelo: Optional[str]
    valor_venda: Optional[str]
    marca_modelo: Optional[str]
    cor: Optional[str]
    chassi: Optional[str]
    hodometro: Optional[str]


@dataclass
class Documento:
    numero_crv: Optional[str]
    codigo_seguranca_crv: Optional[str]
    numero_atpve: Optional[str]
    data_emissao: Optional[str]
    data_venda: Optional[str]


@dataclass
class Comprador:
    nome: Optional[str]
    cpf_cnpj: Optional[str]
    email: Optional[str]
    municipio: Optional[str]
    uf: Optional[str]
    endereco: Optional[str]


@dataclass
class CRLV:
    vendedor: Vendedor
    veiculo: Veiculo
    documento: Documento
    comprador: Comprador


def cast_pdf_to_text(file) -> str:
    with pdfplumber.open(file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


def search(text, pattern, default=None, flags=0):
    match = re.search(pattern, text, flags)
    return match.group(1).strip() if match else default


def parse_crlv_text(text: str) -> CRLV:
    # vendedor
    vendedor = {
        "nome": search(text, r"NOME\s+([\w\sÀ-ÿ]+)\s+CÓDIGO RENAVAM"),
        "renavam": search(text, r"CÓDIGO RENAVAM\s+(\d+)"),
        "cpf_cnpj": search(text, r"CPF/CNPJ.*?\s+([\d\.\-\/]+)"),
        "email": search(text, r"CPF/CNPJ.*?\s+[\d\.\-\/]+\s+([A-Z0-9@\.]+)", flags=re.I),
    }

    # veículo
    veiculo = {
        "placa": search(text, r"PLACA\s+([A-Z0-9]+)"),
        "municipio": search(text, r"PLACA.*?\n([A-Z\s]+)\s+PR"),
        "uf": search(text, r"UF\s*\n.*?\s+(PR|SP|RJ|[A-Z]{2})"),
        "ano_fabricacao": search(text, r"ANO FABRICAÇÃO\s+(\d{4})"),
        "ano_modelo": search(text, r"ANO MODELO\s+(\d{4})"),
        "valor_venda": search(text, r"Valor declarado na venda:\s*R\$ ([\d\.,]+)"),
        "marca_modelo": search(text, r"MARCA / MODELO / VERSÃO\s+(.+?)\s+Autorizo"),
        "cor": search(text, r"COR PREDOMINANTE.*\n+([A-Z]+)"),
        "chassi": search(text, r"CHASSI\s+([A-Z0-9]+)"),
        "hodometro": search(text, r"HODÔMETRO\s+(\d+)"),
    }

    # documento
    documento = {
        "numero_crv": search(text, r"NÚMERO CRV\s+(\d+)"),
        "codigo_seguranca_crv": search(text, r"CÓDIGO DE SEGURANÇA CRV\s+(\d+)"),
        "numero_atpve": search(text, r"NÚMERO ATPVe\s+(\d+)"),
        "data_emissao": search(text, r"DATA EMISSÃO DO CRV\s+(\d{2}/\d{2}/\d{4})"),
        "data_venda": search(text, r"DATA DECLARADA DA VENDA\s+(\d{2}/\d{2}/\d{4})"),
    }

    # comprador
    comprador = {
        "nome": search(text, r"IDENTIFICAÇÃO DO COMPRADOR.*?NOME\s+([A-Z\sÀ-ÿ]+)\s+CPF", flags=re.S),
        "cpf_cnpj": search(text, r"IDENTIFICAÇÃO DO COMPRADOR.*?CPF/CNPJ\s+([\d\.\-\/]+)", flags=re.S),
        "email": search(
            text, r"IDENTIFICAÇÃO DO COMPRADOR.*?CPF/CNPJ.*?\s+[\d\.\-\/]+\s+([A-Z0-9@\.]+)", flags=re.S | re.I
        ),
        "municipio": search(text, r"MUNICÍPIO DE DOMICÍLIO OU RESIDÊNCIA\s+([A-Z\s]+)\s+PR"),
        "uf": search(text, r"MUNICÍPIO DE DOMICÍLIO OU RESIDÊNCIA\s+[A-Z\s]+\s+([A-Z]{2})"),
        "endereco": search(text, r"ENDEREÇO DE DOMICÍLIO OU RESIDÊNCIA\s+(.+?CEP: \d{5}-\d{3})"),
    }

    return CRLV(
        vendedor=Vendedor(**vendedor),
        veiculo=Veiculo(**veiculo),
        documento=Documento(**documento),
        comprador=Comprador(**comprador),
    )
