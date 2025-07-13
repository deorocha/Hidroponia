import math
import matplotlib.pyplot as plt
import numpy as np

def calcular_parametros(p_inicial, p_final, dias):
    t0 = dias / 2.0
    K = p_final * 1.05
    tolerancia = 0.01
    max_iter = 1000
    
    for _ in range(max_iter):
        try:
            if K <= p_inicial:
                K = p_inicial * 1.1
                continue
                
            r = -math.log((K / p_inicial) - 1) / (1 - t0)
        except (ValueError, ZeroDivisionError):
            K *= 1.1
            continue
            
        exp_term = math.exp(-r * (dias - t0))
        p_final_calculado = K / (1 + exp_term)
        
        if abs(p_final_calculado - p_final) < tolerancia:
            return K, r, t0
        
        K *= p_final / p_final_calculado
    
    return K, r, t0

def classificar_fase(peso, K):
    if peso < 0.1 * K:
        return "Lenta"
    elif peso < 0.9 * K:
        return "Acelerada"
    else:
        return "Saturação"

def gerar_dados(p_inicial=5.0, p_final=260.0, dias=35):
    try:
        K, r, t0 = calcular_parametros(p_inicial, p_final, dias)
    except Exception as e:
        print(f"Erro ao calcular parâmetros: {e}")
        return None, None, None, None, None

    dias_list = list(range(1, dias + 1))
    pesos_list = []
    fases_list = []

    for t in dias_list:
        try:
            exp_term = math.exp(-r * (t - t0))
            peso = K / (1 + exp_term)
            fase = classificar_fase(peso, K)
            pesos_list.append(peso)
            fases_list.append(fase)
        except Exception as e:
            print(f"Erro no dia {t}: {e}")
            pesos_list.append(0)
            fases_list.append("Erro")

    return dias_list, pesos_list, fases_list, K, r

def plotar_grafico(dias_list, pesos_list, fases_list, K, p_inicial, p_final, dias):
    plt.figure(figsize=(10, 6))
    
    # 1. Define cores de fundo para cada fase
    cores_fundo = {
        "Lenta": (0.85, 0.92, 1.0),      # Azul claro
        "Acelerada": (0.85, 1.0, 0.85),   # Verde claro
        "Saturação": (1.0, 0.9, 0.85)     # Vermelho claro
    }
    
    # 2. Encontra pontos de transição entre as fases
    transicoes = []
    for i in range(1, len(fases_list)):
        if fases_list[i] != fases_list[i-1]:
            transicoes.append((dias_list[i-1] + dias_list[i]) / 2)
    
    # 3. Define limites das áreas
    limites = [dias_list[0] - 0.5] + transicoes + [dias_list[-1] + 0.5]
    
    # 4. Pinta as regiões de fundo PRIMEIRO (antes de plotar outros elementos)
    legenda_adicionada = set()
    for i in range(len(limites) - 1):
        # Determina a fase para este intervalo
        idx_fase = next(j for j, dia in enumerate(dias_list) if dia >= limites[i] and dia <= limites[i+1])
        fase_atual = fases_list[idx_fase]
        
        # Adiciona legenda apenas se for a primeira ocorrência da fase
        label = fase_atual if fase_atual not in legenda_adicionada else ""
        if label:
            legenda_adicionada.add(fase_atual)
        
        plt.axvspan(limites[i], limites[i+1], 
                    color=cores_fundo[fase_atual], 
                    alpha=0.4,
                    label=label)
    
    # 5. Divide os dados por fase para plotagem
    fase_lenta_x = [dias_list[i] for i, fase in enumerate(fases_list) if fase == "Lenta"]
    fase_lenta_y = [pesos_list[i] for i, fase in enumerate(fases_list) if fase == "Lenta"]
    
    fase_acelerada_x = [dias_list[i] for i, fase in enumerate(fases_list) if fase == "Acelerada"]
    fase_acelerada_y = [pesos_list[i] for i, fase in enumerate(fases_list) if fase == "Acelerada"]
    
    fase_saturacao_x = [dias_list[i] for i, fase in enumerate(fases_list) if fase == "Saturação"]
    fase_saturacao_y = [pesos_list[i] for i, fase in enumerate(fases_list) if fase == "Saturação"]

    # 6. Linha principal
    plt.plot(dias_list, pesos_list, 'k-', alpha=0.5, linewidth=2, label='Curva Sigmóide')
    
    # 7. Pontos coloridos por fase
    if fase_lenta_x:
        plt.plot(fase_lenta_x, fase_lenta_y, 'bo', markersize=6, label='Fase Lenta')
    if fase_acelerada_x:
        plt.plot(fase_acelerada_x, fase_acelerada_y, 'go', markersize=6, label='Fase Acelerada')
    if fase_saturacao_x:
        plt.plot(fase_saturacao_x, fase_saturacao_y, 'ro', markersize=6, label='Fase Saturação')

    # Configurações do gráfico
    plt.title(f'Crescimento: {p_inicial}g → {p_final}g em {dias} dias', fontsize=14)
    plt.xlabel('Dia', fontsize=12)
    plt.ylabel('Peso (g)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Linha horizontal para peso final
    plt.axhline(y=p_final, color='darkorange', linestyle='--', linewidth=1.5, 
                alpha=0.7, label='Peso Final')
    
    # Ponto de inflexão
    if pesos_list:
        idx_meio = min(range(len(pesos_list)), key=lambda i: abs(pesos_list[i] - K/2))
        plt.axvline(x=dias_list[idx_meio], color='purple', linestyle=':', linewidth=2,
                   label=f'Infleção (dia {dias_list[idx_meio]})')

    # Escala do eixo X
    plt.xticks(dias_list)
    if dias > 30:
        plt.xticks(rotation=45, ha='right')

    # Limites do eixo Y
    plt.ylim(0, max(pesos_list) * 1.15)

    # Legenda
    plt.legend(loc='best')

    plt.tight_layout()
    plt.savefig('crescimento.png', dpi=150)
    plt.show()

def main():
    try:
        p_inicial = float(input("Peso inicial (g) [5.0]: ") or 5.0)
        p_final = float(input("Peso final (g) [260.0]: ") or 260.0)
        dias = int(input("Dias [35]: ") or 35)
    except EOFError:
        print("\nUsando valores padrão: 5g inicial, 260g final, 35 dias")
        p_inicial, p_final, dias = 5.0, 260.0, 35
    except Exception as e:
        print(f"\nErro na entrada: {e}\nUsando valores padrão")
        p_inicial, p_final, dias = 5.0, 260.0, 35

    # Gerar dados
    dias_list, pesos_list, fases_list, K, r = gerar_dados(p_inicial, p_final, dias)
    
    if not dias_list:
        print("Não foi possível gerar dados. Verifique os parâmetros.")
        return

    # Imprimir tabela
    print("\nDia | Fase         | Peso (g)")
    print("-" * 30)
    for i, dia in enumerate(dias_list):
        print(f"{dia:3d} | {fases_list[i]:<12} | {pesos_list[i]:7.1f}")

    # Gerar gráfico
    try:
        plotar_grafico(dias_list, pesos_list, fases_list, K, p_inicial, p_final, dias)
        print("\nGráfico salvo como 'crescimento.png'")
    except Exception as e:
        print(f"\nErro ao gerar gráfico: {e}")

if __name__ == "__main__":
    main()