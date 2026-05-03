from models import order_model


def sales_report():
    relatorio = order_model.sales_report()
    return {"dados": relatorio, "sucesso": True}, 200
