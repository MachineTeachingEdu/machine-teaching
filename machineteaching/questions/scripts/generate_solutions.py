import json
import sys

# Verifica se foi passado o path para a pasta onde está o solutions.json
if len(sys.argv) < 2:
    folder = "ui/data/"
    print("Buscando solutions.json na pasta ui/data...")
else:
    folder = sys.argv[1]
    if folder[-1] != "/":
        folder += "/"
    print(f"Buscando solutions.json na pasta {folder}...")


# Transforma o arquivo JSON em dicionario e pega a lista de soluções
with open(folder + "solutions.json") as f:
    solutions = json.load(f)
    solutions = solutions["questions_userlog"]

# Passa as soluções para arquivos python separados
# Itera pelas soluções, pegando o indice e o código
print(f"Transformando as soluções em arquivos python na pasta {folder}...")
for i, solution in enumerate(solutions):
    # Define o nome do arquivo
    filename = f"solution{i}.py"
    path = folder + filename
    with open(path, 'w') as f:
        f.write(solution["solution"])

print("Concluído!")
