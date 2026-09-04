import re
import sqlite3
import sys

import requests
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def validar_cpf(cpf):
    cpf = re.sub(r"\D", "", cpf)

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    for i in range(9, 11):
        soma = sum(int(cpf[j]) * (i + 1 - j) for j in range(i))
        digito = (soma * 10) % 11
        if digito == 10:
            digito = 0

        if int(cpf[i]) != digito:
            return False

    return True


def validar_cnpj(cnpj):
    cnpj = re.sub(r"\D", "", cnpj)

    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    def calcula_digito(valor, pesos):
        soma = sum(int(valor[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    if int(cnpj[12]) != calcula_digito(cnpj, pesos1):
        return False

    if int(cnpj[13]) != calcula_digito(cnpj, pesos2):
        return False

    return True


def validar_email(email):
    padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(padrao, email) is not None


def validar_celular(celular):
    celular = re.sub(r"\D", "", celular)
    return len(celular) in (10, 11)


def validar_cep(cep):
    cep = re.sub(r"\D", "", cep)
    return len(cep) == 8


def consultar_cep(cep):
    cep = re.sub(r"\D", "", cep)

    if not validar_cep(cep):
        return None

    url = f"https://viacep.com.br/ws/{cep}/json/"

    try:
        resposta = requests.get(url, timeout=5)
        resposta.raise_for_status()
        dados = resposta.json()

        if dados.get("erro"):
            return None

        return {
            "logradouro": dados.get("logradouro", ""),
            "bairro": dados.get("bairro", ""),
            "cidade": dados.get("localidade", ""),
            "estado": dados.get("uf", ""),
        }

    except requests.RequestException:
        return None
    except ValueError:
        return None


class Banco:
    def __init__(self, arquivo="cadastro.db"):
        self.conn = sqlite3.connect(arquivo)
        self.criar_tabela()

    def criar_tabela(self):
        sql = """
        CREATE TABLE IF NOT EXISTS pessoas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo_documento TEXT NOT NULL,
            documento TEXT NOT NULL,
            email TEXT NOT NULL,
            celular TEXT NOT NULL,
            cep TEXT NOT NULL,
            logradouro TEXT NOT NULL,
            numero TEXT NOT NULL,
            complemento TEXT,
            bairro TEXT NOT NULL,
            cidade TEXT NOT NULL,
            estado TEXT NOT NULL
        )
        """
        self.conn.execute(sql)
        self.conn.commit()

    def salvar(self, dados):
        sql = """
        INSERT INTO pessoas (
            nome, tipo_documento, documento, email, celular, cep,
            logradouro, numero, complemento, bairro, cidade, estado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.conn.execute(sql, dados)
        self.conn.commit()

    def fechar(self):
        self.conn.close()


class CadastroWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.banco = Banco()
        self.campos_erro = {}

        self.setWindowTitle("Cadastro de Pessoa")
        self.setFixedSize(750, 700)

        self.setup_ui()
        self.aplicar_estilo()

    def aplicar_estilo(self):
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f0f0f0;
            }

            QLabel {
                font-weight: bold;
                color: #333333;
            }

            QLabel.erro {
                color: #d32f2f;
                font-weight: normal;
                font-size: 10px;
                padding-left: 5px;
            }

            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }

            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #1976d2;
            }

            QPushButton {
                padding: 10px;
                font-weight: bold;
                border-radius: 4px;
                background-color: #1976d2;
                color: white;
                border: none;
            }

            QPushButton:hover {
                background-color: #1565c0;
            }

            QPushButton:pressed {
                background-color: #0d47a1;
            }

            QPushButton#btn_limpar {
                background-color: #757575;
            }

            QPushButton#btn_limpar:hover {
                background-color: #616161;
            }

            QPushButton#btn_consultar {
                background-color: #388e3c;
            }

            QPushButton#btn_consultar:hover {
                background-color: #2e7d32;
            }
            """
        )

    def setup_ui(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        layout = QGridLayout(widget_central)
        layout.setVerticalSpacing(5)
        layout.setHorizontalSpacing(15)

        def add_campo(linha, coluna, label_text, widget, coluna_span=1, obrigatorio=True):
            label = QLabel(label_text + (" *" if obrigatorio else ""))
            layout.addWidget(label, linha, coluna)
            layout.addWidget(widget, linha, coluna + 1, 1, coluna_span)

            erro_label = QLabel("")
            erro_label.setProperty("class", "erro")
            layout.addWidget(
                erro_label, linha + 1, coluna + 1, 1, coluna_span
            )

            return erro_label

        self.nome_edit = QLineEdit()
        self.nome_edit.setPlaceholderText("Digite o nome completo")
        self.nome_edit.setMaxLength(100)
        self.erro_nome = add_campo(0, 0, "Nome completo", self.nome_edit, 3)

        self.tipo_doc_combo = QComboBox()
        self.tipo_doc_combo.addItems(["CPF", "CNPJ"])
        layout.addWidget(QLabel("Tipo documento *"), 2, 0)
        layout.addWidget(self.tipo_doc_combo, 2, 1)

        self.doc_edit = QLineEdit()
        self.doc_edit.setPlaceholderText("000.000.000-00")
        self.doc_edit.setMaxLength(18)
        self.erro_doc = add_campo(2, 2, "Documento", self.doc_edit, 1)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("usuario@exemplo.com")
        self.email_edit.setMaxLength(100)
        self.erro_email = add_campo(4, 0, "E-mail", self.email_edit, 1)

        self.celular_edit = QLineEdit()
        self.celular_edit.setPlaceholderText("(99) 99999-9999")
        self.celular_edit.setMaxLength(15)
        self.erro_celular = add_campo(4, 2, "Celular", self.celular_edit, 1)

        self.cep_edit = QLineEdit()
        self.cep_edit.setPlaceholderText("00000-000")
        self.cep_edit.setMaxLength(9)
        self.cep_edit.textChanged.connect(self.limpar_endereco_auto)
        self.erro_cep = add_campo(6, 0, "CEP", self.cep_edit, 1)

        self.consultar_btn = QPushButton("Consultar CEP")
        self.consultar_btn.setObjectName("btn_consultar")
        self.consultar_btn.clicked.connect(self.buscar_endereco)
        layout.addWidget(self.consultar_btn, 6, 2, 1, 2)

        self.logradouro_edit = QLineEdit()
        self.logradouro_edit.setReadOnly(True)
        self.logradouro_edit.setMaxLength(100)
        self.erro_logradouro = add_campo(8, 0, "Logradouro", self.logradouro_edit, 3)

        self.numero_edit = QLineEdit()
        self.numero_edit.setMaxLength(10)
        self.erro_numero = add_campo(10, 0, "Número", self.numero_edit, 1)

        self.complemento_edit = QLineEdit()
        self.complemento_edit.setMaxLength(50)
        self.complemento_edit.setPlaceholderText("Opcional")
        self.erro_complemento = add_campo(
            10, 2, "Complemento", self.complemento_edit, 1, obrigatorio=False
        )

        self.bairro_edit = QLineEdit()
        self.bairro_edit.setReadOnly(True)
        self.bairro_edit.setMaxLength(50)
        self.erro_bairro = add_campo(12, 0, "Bairro", self.bairro_edit, 1)

        self.cidade_edit = QLineEdit()
        self.cidade_edit.setReadOnly(True)
        self.cidade_edit.setMaxLength(50)
        self.erro_cidade = add_campo(12, 2, "Cidade", self.cidade_edit, 1)

        self.estado_edit = QLineEdit()
        self.estado_edit.setReadOnly(True)
        self.estado_edit.setMaxLength(50)
        self.erro_estado = add_campo(14, 0, "Estado", self.estado_edit, 1)

        hbox = QHBoxLayout()

        self.cadastrar_btn = QPushButton("Cadastrar")
        self.cadastrar_btn.clicked.connect(self.cadastrar)

        self.limpar_btn = QPushButton("Limpar")
        self.limpar_btn.setObjectName("btn_limpar")
        self.limpar_btn.clicked.connect(self.limpar_campos)

        hbox.addWidget(self.cadastrar_btn)
        hbox.addWidget(self.limpar_btn)

        layout.addLayout(hbox, 16, 0, 1, 4)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 2)

        self._registrar_labels_de_erro()

    def _registrar_labels_de_erro(self):
        self.campos_erro = {
            "nome": self.erro_nome,
            "documento": self.erro_doc,
            "email": self.erro_email,
            "celular": self.erro_celular,
            "cep": self.erro_cep,
            "logradouro": self.erro_logradouro,
            "numero": self.erro_numero,
            "complemento": self.erro_complemento,
            "bairro": self.erro_bairro,
            "cidade": self.erro_cidade,
            "estado": self.erro_estado,
        }

    def limpar_endereco_auto(self):
        if not self.cep_edit.text().strip():
            self.logradouro_edit.clear()
            self.bairro_edit.clear()
            self.cidade_edit.clear()
            self.estado_edit.clear()

    def buscar_endereco(self):
        cep = self.cep_edit.text().strip()

        if not validar_cep(cep):
            self.erro_cep.setText("CEP inválido. Informe 8 dígitos.")
            return

        self.erro_cep.setText("")
        resultado = consultar_cep(cep)

        if resultado is None:
            QMessageBox.critical(
                self,
                "Erro na consulta",
                "Não foi possível obter o endereço.\n"
                "Verifique o CEP ou sua conexão com a internet.",
            )
            return

        self.logradouro_edit.setText(resultado["logradouro"])
        self.bairro_edit.setText(resultado["bairro"])
        self.cidade_edit.setText(resultado["cidade"])
        self.estado_edit.setText(resultado["estado"])

        QMessageBox.information(
            self,
            "Sucesso",
            "Endereço preenchido automaticamente!",
        )

    def validar_campos(self):
        valido = True

        for label in self.campos_erro.values():
            label.setText("")

        nome = self.nome_edit.text().strip()
        if not nome:
            self.erro_nome.setText("Nome é obrigatório.")
            valido = False

        tipo = self.tipo_doc_combo.currentText()
        doc = self.doc_edit.text().strip()

        if not doc:
            self.erro_doc.setText("Documento é obrigatório.")
            valido = False
        else:
            doc_limpo = re.sub(r"\D", "", doc)

            if tipo == "CPF":
                if len(doc_limpo) != 11:
                    self.erro_doc.setText("CPF deve ter 11 números.")
                    valido = False
                elif not validar_cpf(doc_limpo):
                    self.erro_doc.setText("CPF inválido.")
                    valido = False
            else:
                if len(doc_limpo) != 14:
                    self.erro_doc.setText("CNPJ deve ter 14 números.")
                    valido = False
                elif not validar_cnpj(doc_limpo):
                    self.erro_doc.setText("CNPJ inválido.")
                    valido = False

        email = self.email_edit.text().strip()
        if not email:
            self.erro_email.setText("E-mail é obrigatório.")
            valido = False
        elif not validar_email(email):
            self.erro_email.setText(
                "Formato inválido (usuario@dominio.com)."
            )
            valido = False

        celular = self.celular_edit.text().strip()
        if not celular:
            self.erro_celular.setText("Celular é obrigatório.")
            valido = False
        elif not validar_celular(celular):
            self.erro_celular.setText(
                "Formato inválido. Use 10 ou 11 dígitos."
            )
            valido = False

        cep = self.cep_edit.text().strip()
        if not cep:
            self.erro_cep.setText("CEP é obrigatório.")
            valido = False
        elif not validar_cep(cep):
            self.erro_cep.setText("CEP deve ter 8 dígitos.")
            valido = False

        if not self.logradouro_edit.text().strip():
            self.erro_logradouro.setText(
                "Consulte o CEP para preencher o logradouro."
            )
            valido = False

        if not self.bairro_edit.text().strip():
            self.erro_bairro.setText(
                "Consulte o CEP para preencher o bairro."
            )
            valido = False

        if not self.cidade_edit.text().strip():
            self.erro_cidade.setText(
                "Consulte o CEP para preencher a cidade."
            )
            valido = False

        if not self.estado_edit.text().strip():
            self.erro_estado.setText(
                "Consulte o CEP para preencher o estado."
            )
            valido = False

        if not self.numero_edit.text().strip():
            self.erro_numero.setText("Número é obrigatório.")
            valido = False

        return valido

    def cadastrar(self):
        if not self.validar_campos():
            QMessageBox.warning(
                self,
                "Dados inválidos",
                "Corrija os campos destacados antes de cadastrar.",
            )
            return

        dados = (
            self.nome_edit.text().strip(),
            self.tipo_doc_combo.currentText(),
            self.doc_edit.text().strip(),
            self.email_edit.text().strip(),
            self.celular_edit.text().strip(),
            self.cep_edit.text().strip(),
            self.logradouro_edit.text().strip(),
            self.numero_edit.text().strip(),
            self.complemento_edit.text().strip(),
            self.bairro_edit.text().strip(),
            self.cidade_edit.text().strip(),
            self.estado_edit.text().strip(),
        )

        try:
            self.banco.salvar(dados)
            QMessageBox.information(
                self,
                "Sucesso",
                "Cadastro realizado com sucesso!",
            )
            self.limpar_campos()
        except sqlite3.Error as erro:
            QMessageBox.critical(
                self,
                "Erro no banco",
                f"Não foi possível salvar o cadastro:\n{erro}",
            )

    def limpar_campos(self):
        self.nome_edit.clear()
        self.doc_edit.clear()
        self.email_edit.clear()
        self.celular_edit.clear()
        self.cep_edit.clear()
        self.logradouro_edit.clear()
        self.numero_edit.clear()
        self.complemento_edit.clear()
        self.bairro_edit.clear()
        self.cidade_edit.clear()
        self.estado_edit.clear()

        self.tipo_doc_combo.setCurrentIndex(0)

        for label in self.campos_erro.values():
            label.setText("")

    def closeEvent(self, event):
        self.banco.fechar()
        event.accept()


def main():
    app = QApplication(sys.argv)

    window = CadastroWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
