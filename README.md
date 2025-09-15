📡 UO Package Guide

Este repositório contém uma versão navegável do Ultima Online Packet Guide, uma referência detalhada de todos os pacotes utilizados na comunicação entre cliente e servidor do Ultima Online.

O protocolo do UO é composto por mensagens binárias identificadas por opcodes, que podem ter tamanho fixo ou variável. Cada pacote é documentado com:

Opcode (código identificador)

Direção (Client → Server, Server → Client, ou ambos)

Tamanho em bytes

Descrição funcional

Formato detalhado dos campos

🔎 Conteúdo

A documentação cobre pacotes em diferentes categorias:

Client – pacotes enviados do cliente para o servidor (ex: movimento, fala, criação de personagem, login).

Server – pacotes enviados do servidor para o cliente (ex: status, lista de personagens, atualização de itens).

Both – pacotes bidirecionais (ex: war mode, target, ping).

No longer used – pacotes obsoletos que existiram em versões antigas.

God Client – pacotes exclusivos do cliente de administração.

Unknown – pacotes cuja função ainda não foi documentada.

📜 Histórico

Compilado originalmente por Wyatt

Design de Garret

Última atualização conhecida por Mutilador (15/09/2025)

🎯 Objetivo

Este projeto tem como finalidade:

Preservar a documentação histórica do protocolo de rede do Ultima Online.

Servir como guia para desenvolvedores de emuladores, ferramentas e servidores customizados.

Facilitar pesquisas e aprendizado sobre a estrutura interna de comunicação do UO.