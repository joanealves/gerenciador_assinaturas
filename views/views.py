import matplotlib.pyplot as plt
import seaborn as sns
from models.database import engine
from sqlmodel import Session, select
from models.model import Subscription, Payments
from datetime import date

# Definir estilo para gráficos
sns.set(style="whitegrid")  

class SubscriptionService:
    def __init__(self, engine):
        self.engine = engine

    def create(self, subscription: Subscription):
        with Session(self.engine) as session:
            session.add(subscription)
            session.commit()
            session.refresh(subscription)
            return subscription

    def list_all(self):
        with Session(self.engine) as session:
            statement = select(Subscription)
            results = session.exec(statement).all()
            return results

    def total_value(self):
        with Session(self.engine) as session:
            statement = select(Subscription)
            results = session.exec(statement).all()

        total = sum(result.valor for result in results if result.valor)
        return float(total)

    def plot_total_values(self):
        """
        Gera um gráfico mostrando os valores totais de todas as assinaturas.
        """
        with Session(self.engine) as session:
            statement = select(Subscription)
            results = session.exec(statement).all()

        if not results:
            print("Nenhuma assinatura encontrada para gerar gráficos.")
            return

        # Preparar dados para o gráfico
        empresas = [sub.empresa for sub in results]
        valores = [float(sub.valor) for sub in results if sub.valor]

        # Criar o gráfico
        plt.figure(figsize=(10, 6))
        bars = plt.bar(empresas, valores, color=sns.color_palette("pastel")[2])  # Usando cores pastel para suavizar

        # Adicionar anotações no topo das barras
        for bar in bars:
            yval = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2, yval + 1, f'R${yval:.2f}', ha='center', va='bottom', fontsize=10, color="black"
            )

        plt.title("Valores Totais de Assinaturas", fontsize=14)
        plt.xlabel("Empresa", fontsize=12)
        plt.ylabel("Valor (R$)", fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()  
        plt.show()


class PaymentsService:
    def __init__(self, engine):
        self.engine = engine

    def create(self, payment: Payments):
        with Session(self.engine) as session:
            session.add(payment)
            session.commit()

    def list_all(self):
        with Session(self.engine) as session:
            statement = select(Payments)
            return session.exec(statement).all()

    def plot_payments(self):
        """
        Gera um gráfico de barras mostrando o número de pagamentos por mês.
        """
        with Session(self.engine) as session:
            statement = select(Payments.date)
            results = session.exec(statement).all()

        if not results:
            print("Nenhum pagamento encontrado para gerar gráficos.")
            return

        # Preparando dados para o gráfico
        payments_by_month = {}
        for payment_date in results:
            month_year = payment_date.strftime("%Y-%m")
            payments_by_month[month_year] = payments_by_month.get(month_year, 0) + 1

        # Criar o gráfico
        months = list(payments_by_month.keys())
        payments = list(payments_by_month.values())

        plt.figure(figsize=(10, 6))
        bars = plt.bar(months, payments, color=sns.color_palette("coolwarm")[1])  

        # Adicionar anotações no topo das barras
        for bar in bars:
            yval = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2, yval + 0.1, f'{yval}', ha='center', va='bottom', fontsize=10, color="black"
            )

        plt.title("Pagamentos por Mês", fontsize=14)
        plt.xlabel("Mês", fontsize=12)
        plt.ylabel("Número de Pagamentos", fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()  # Ajusta o layout para evitar sobreposição de texto
        plt.show()


# Ponto de entrada para testes
if __name__ == "__main__":
    subscription_service = SubscriptionService(engine)
    payments_service = PaymentsService(engine)

    sub1 = Subscription(empresa="Netflix", site="www.netflix.com", data_assinatura=date(2023, 1, 15), valor=39.90)
    sub2 = Subscription(empresa="Spotify", site="www.spotify.com", data_assinatura=date(2023, 2, 20), valor=19.90)

    # Criando assinaturas
    subscription_service.create(sub1)
    subscription_service.create(sub2)

    # Listando assinaturas
    assinaturas = subscription_service.list_all()
    print("Assinaturas cadastradas:")
    for assinatura in assinaturas:
        print(assinatura)

    # Gerando gráfico com o valor total de assinaturas
    subscription_service.plot_total_values()

    # Adicionando pagamentos
    payment1 = Payments(subscription_id=sub1.id, date=date(2023, 5, 15))
    payment2 = Payments(subscription_id=sub2.id, date=date(2023, 6, 20))

    payments_service.create(payment1)
    payments_service.create(payment2)

    # Gerando gráfico de pagamentos
    payments_service.plot_payments()