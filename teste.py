val1 = 1000000000
val2 = 1000000
val3 = 100000

lista = [val1, val2, val3]
formatado = []
sufixo = []

for l in lista:

    if l >= 1_000_000_000:
        numero = l / 1_000_000_000
        sufixo = "B"

    elif l >= 1_000_000:
        numero = l / 1_000_000
        sufixo = "M"

    elif l >= 1_000:
        numero = l / 1_000
        sufixo = "K"

    else:
        numero = l
        sufixo = ""

    print(f"{numero:.1f}{sufixo}")

    custo por mensagem, alcance, impressoes, total investido, custo por resultados
    









