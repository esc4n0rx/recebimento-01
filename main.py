import flet
from flet import (
    Page, Text, ElevatedButton, DataTable, DataColumn, DataRow, DataCell,
    Column, Row, Dropdown, TextField, IconButton,
    icons, Switch, colors, alignment, Container, padding, dropdown,
    AlertDialog, SnackBar
)
import pandas as pd
import os
import datetime
from outlook_handler import importar_agendamentos
from database_handler import DatabaseHandler
from image_generator import criar_imagem_pendencias

def main(page: Page):
    db = DatabaseHandler('pendencias.db')

    page.title = "Controle de Recebimento"
    page.theme_mode = 'light'
    page.padding = 20

    contador_mercearia = Text()
    contador_pereciveis = Text()

    tabela = DataTable(
        columns=[
            DataColumn(Text("Departamento")),
            DataColumn(Text("Fornecedor")),
            DataColumn(Text("Pedido")),
            DataColumn(Text("Hora")),
            DataColumn(Text("Status")),
            DataColumn(Text("Motivo")),
            DataColumn(Text("Ações")),
        ],
        rows=[]
    )

    def atualizar_tabela():
        pendencias = db.obter_pendencias()
        tabela.rows.clear()
        for p in pendencias:
            pendencia_id = p[0]
            tabela.rows.append(
                DataRow(cells=[
                    DataCell(Text(p[1])),
                    DataCell(Text(p[2])),
                    DataCell(Text(p[3])),
                    DataCell(Text(p[4])),
                    DataCell(Text(p[5])),
                    DataCell(Text(p[6])),
                    DataCell(
                        Row([
                            IconButton(
                                icon=icons.EDIT,
                                tooltip="Editar",
                                on_click=lambda e, pid=pendencia_id: editar_pendencia(e, pid)
                            ),
                            IconButton(
                                icon=icons.DELETE,
                                tooltip="Remover",
                                on_click=lambda e, pid=pendencia_id: remover_pendencia(e, pid)
                            ),
                        ])
                    ),
                ])
            )
        page.update()

    def contar_pendencias():
        pendencias = db.obter_pendencias()
        mercearia = 0
        pereciveis = 0
        for p in pendencias:
            departamento = p[1].strip().lower()
            if 'mercearia' in departamento:
                mercearia += 1
            elif 'pereciveis' in departamento or 'perecíveis' in departamento:
                pereciveis += 1
        contador_mercearia.value = f"Mercearia: {mercearia}"
        contador_pereciveis.value = f"Perecíveis: {pereciveis}"
        page.update()

    agendamento_existe = importar_agendamentos()
    if not agendamento_existe:
        def fechar_dialogo(e):
            aviso_dialog.open = False
            page.update()

        aviso_dialog = AlertDialog(
            title=Text("Aviso"),
            content=Text("O agendamento não foi encontrado."),
            actions=[ElevatedButton("OK", on_click=fechar_dialogo)],
            open=True
        )
        page.dialog = aviso_dialog
        page.update()

    def abrir_criar_pendencia(e):
        fornecedores_df = pd.read_csv('agendamentos.csv')

        # Verificar se há fornecedores extras
        if os.path.exists('fornecedores_extras.csv'):
            extras_df = pd.read_csv('fornecedores_extras.csv')
            fornecedores_df = pd.concat([fornecedores_df, extras_df], ignore_index=True)

        fornecedores_lista = fornecedores_df['Fornecedor'].unique().tolist()

        fornecedor_dropdown = Dropdown(
            label="Fornecedor",
            options=[dropdown.Option(f) for f in fornecedores_lista],
            on_change=lambda e: atualizar_pedidos()
        )

        pedido_dropdown = Dropdown(label="Pedido", options=[])

        hora_field = TextField(label="Hora (HH:MM:SS)")
        status_field = TextField(label="Status")
        motivo_field = TextField(label="Motivo")

        def atualizar_pedidos():
            pedidos = fornecedores_df[fornecedores_df['Fornecedor'] == fornecedor_dropdown.value]['Pedido'].tolist()
            pedido_dropdown.options = [dropdown.Option(str(p)) for p in pedidos]
            pedido_dropdown.value = None
            page.update()

        def salvar_pendencia(e):
            departamento = fornecedores_df[fornecedores_df['Fornecedor'] == fornecedor_dropdown.value]['Departamento'].iloc[0]
            fornecedor = fornecedor_dropdown.value
            pedido = pedido_dropdown.value
            hora = hora_field.value
            status = status_field.value
            motivo = motivo_field.value

            if not hora:
                page.snack_bar = SnackBar(Text("Por favor, insira a hora."), open=True)
                return

            db.inserir_pendencia(departamento, fornecedor, pedido, hora, status, motivo)
            criar_imagem_pendencias(db.obter_pendencias())
            criar_pendencia_dialog.open = False
            atualizar_tabela()
            contar_pendencias()
            page.update()

        criar_pendencia_dialog = AlertDialog(
            title=Text("Criar Pendência"),
            content=Column([
                fornecedor_dropdown,
                pedido_dropdown,
                hora_field,
                status_field,
                motivo_field
            ], tight=True),
            actions=[
                ElevatedButton("Salvar", on_click=salvar_pendencia),
                ElevatedButton("Cancelar", on_click=lambda e: setattr(criar_pendencia_dialog, 'open', False))
            ],
            open=True
        )
        page.dialog = criar_pendencia_dialog
        page.update()

    def editar_pendencia(e, pendencia_id):
        pendencia = db.obter_pendencia_por_id(pendencia_id)
        if not pendencia:
            return

        status_field = TextField(label="Status", value=pendencia[5])

        def salvar_edicao(e):
            novo_status = status_field.value
            db.atualizar_status_pendencia(pendencia_id, novo_status)
            editar_pendencia_dialog.open = False
            atualizar_tabela()
            criar_imagem_pendencias(db.obter_pendencias())
            contar_pendencias()
            page.update()
            page.snack_bar = SnackBar(Text("Pendência atualizada."), open=True)

        editar_pendencia_dialog = AlertDialog(
            title=Text("Editar Pendência"),
            content=Column([status_field], tight=True),
            actions=[
                ElevatedButton("Salvar", on_click=salvar_edicao),
                ElevatedButton("Cancelar", on_click=lambda e: setattr(editar_pendencia_dialog, 'open', False))
            ],
            open=True
        )
        page.dialog = editar_pendencia_dialog
        page.update()

    def remover_pendencia(e, pendencia_id):
        db.remover_pendencia(pendencia_id)
        atualizar_tabela()
        contar_pendencias()
        criar_imagem_pendencias(db.obter_pendencias())
        page.update()
        page.snack_bar = SnackBar(Text("Pendência removida."), open=True)

    botao_criar_pendencia = ElevatedButton("Criar Pendência", on_click=abrir_criar_pendencia)

    def abrir_configuracoes(e):
        modo_escuro_switch = Switch(label="Modo Escuro", value=page.theme_mode == 'dark')

        def alternar_modo_escuro(e):
            page.theme_mode = 'dark' if modo_escuro_switch.value else 'light'
            page.update()

        modo_escuro_switch.on_change = alternar_modo_escuro

        def limpar_agendamentos(e):
            if os.path.exists('agendamentos.csv'):
                os.remove('agendamentos.csv')
            config_dialog.open = False
            page.snack_bar = SnackBar(Text("Base de agendamentos limpa."), open=True)
            page.update()

        def adicionar_fornecedor_fora_agendamento(e):
            fornecedor_field = TextField(label="Fornecedor")
            pedido_field = TextField(label="Pedido")
            departamento_dropdown = Dropdown(
                label="Departamento",
                options=[dropdown.Option("Mercearia"), dropdown.Option("Perecíveis")]
            )

            def salvar_fornecedor(e):
                fornecedor = fornecedor_field.value
                pedido = pedido_field.value
                departamento = departamento_dropdown.value

                if not all([fornecedor, pedido, departamento]):
                    page.snack_bar = SnackBar(Text("Por favor, preencha todos os campos."), open=True)
                    return

                if os.path.exists('fornecedores_extras.csv'):
                    extras_df = pd.read_csv('fornecedores_extras.csv')
                else:
                    extras_df = pd.DataFrame(columns=['Departamento', 'Fornecedor', 'Pedido'])

                novo_fornecedor = {'Departamento': departamento, 'Fornecedor': fornecedor, 'Pedido': pedido}
                novo_fornecedor_df = pd.DataFrame([novo_fornecedor])
                extras_df = pd.concat([extras_df, novo_fornecedor_df], ignore_index=True)
                extras_df.to_csv('fornecedores_extras.csv', index=False)

                adicionar_fornecedor_dialog.open = False
                page.snack_bar = SnackBar(Text("Fornecedor adicionado."), open=True)
                page.update()

            adicionar_fornecedor_dialog = AlertDialog(
                title=Text("Adicionar Fornecedor Fora do Agendamento"),
                content=Column([
                    fornecedor_field,
                    pedido_field,
                    departamento_dropdown
                ], tight=True),
                actions=[
                    ElevatedButton("Salvar", on_click=salvar_fornecedor),
                    ElevatedButton("Cancelar", on_click=lambda e: setattr(adicionar_fornecedor_dialog, 'open', False))
                ],
                open=True
            )
            page.dialog = adicionar_fornecedor_dialog
            page.update()

        config_dialog = AlertDialog(
            title=Text("Configurações"),
            content=Column([
                modo_escuro_switch,
                ElevatedButton("Adicionar Fornecedor Fora do Agendamento", on_click=adicionar_fornecedor_fora_agendamento),
                ElevatedButton("Limpar Base de Agendamento", on_click=limpar_agendamentos),
            ], tight=True),
            actions=[
                ElevatedButton("Fechar", on_click=lambda e: setattr(config_dialog, 'open', False))
            ],
            open=True
        )
        page.dialog = config_dialog
        page.update()

    botao_configuracoes = IconButton(icon=icons.SETTINGS, on_click=abrir_configuracoes)

    page.add(
        Row([
            contador_mercearia,
            contador_pereciveis,
            botao_configuracoes
        ], alignment='spaceBetween'),
        tabela,
        botao_criar_pendencia
    )

    atualizar_tabela()
    contar_pendencias()

flet.app(target=main)
