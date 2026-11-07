# Pendiente en el API Gateway (api-gateway/nginx.conf)

Hoy el gateway solo enruta `/auth/` (8002) y `/cuentas` (8001); lo demás va al monolito.
Para que este frontend funcione completo, agregar:

    upstream transaction_service { server 127.0.0.1:8003; }

    location ~ ^/(transacciones|resumen|limites|balances) {
        proxy_pass http://transaction_service;
        proxy_set_header Host $host;
        proxy_set_header Authorization $http_authorization;
    }

Para `/uploads` hace falta el puerto del storage-service (confirmar con Diego).
