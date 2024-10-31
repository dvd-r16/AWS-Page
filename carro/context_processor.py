from imaplib import _Authenticator


def importe_total_carro(request):
    total = 0
    # Verifica si el carrito existe en la sesión
    if "carro" in request.session:
        for key, value in request.session["carro"].items():
            total += float(value["precio"])
    
    # Retorna el total (o 0 si no existe el carrito)
    return {"importe_total_carro": total}